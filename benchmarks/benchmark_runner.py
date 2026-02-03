#!/usr/bin/env python3
"""Benchmark runner for long-context evaluation."""
import json
import time
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
import os

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.base_benchmark import BaseBenchmark
from benchmarks.needle_in_haystack import NeedleInHaystackBenchmark
from benchmarks.oolong import OOLONGBenchmark
from benchmarks.oolong_pairs import OOLONGPairsBenchmark
from benchmarks.codeqa import CodeQABenchmark
from benchmarks.browsecomp import BrowseCompBenchmark

load_dotenv()

class BenchmarkRunner:
    """Runs benchmarks and collects results."""
    
    def __init__(self, model: str = "gpt-4o", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        self.client = OpenAI(api_key=self.api_key)
        
        self.benchmarks = {
            "needle_in_haystack": NeedleInHaystackBenchmark(),
            "oolong": OOLONGBenchmark(),
            "oolong_pairs": OOLONGPairsBenchmark(),
            "codeqa": CodeQABenchmark(),
            "browsecomp": BrowseCompBenchmark(),
        }
    
    def run_benchmark(self, benchmark_name: str, context_lengths: List[int], 
                     num_runs: int = 3, **kwargs) -> Dict[str, Any]:
        """Run a benchmark across multiple context lengths.
        
        Args:
            benchmark_name: Name of benchmark to run
            context_lengths: List of context lengths (in tokens) to test
            num_runs: Number of runs per context length
            **kwargs: Additional parameters for benchmark generation
        """
        if benchmark_name not in self.benchmarks:
            raise ValueError(f"Unknown benchmark: {benchmark_name}")
        
        benchmark = self.benchmarks[benchmark_name]
        results = {
            "benchmark": benchmark_name,
            "model": self.model,
            "results": []
        }
        
        for context_length in context_lengths:
            print(f"\nRunning {benchmark_name} at {context_length} tokens...")
            
            length_results = {
                "context_length": context_length,
                "runs": []
            }
            
            for run in range(num_runs):
                print(f"  Run {run + 1}/{num_runs}...", end=" ", flush=True)
                
                # Generate test case
                test_case = benchmark.generate_test_case(context_length, **kwargs)
                
                # Get messages
                messages = benchmark.get_context_messages()
                messages.append({
                    "role": "user",
                    "content": test_case["question"]
                })
                
                # Call model
                start_time = time.time()
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages
                    )
                    model_response = response.choices[0].message.content
                    success = True
                    error = None
                except Exception as e:
                    model_response = ""
                    success = False
                    error = str(e)
                
                elapsed_time = time.time() - start_time
                
                # Evaluate
                if success:
                    evaluation = benchmark.evaluate(
                        model_response,
                        test_case["expected_answer"],
                        **kwargs
                    )
                else:
                    evaluation = {
                        "correct": False,
                        "score": 0.0,
                        "error": error
                    }
                
                run_result = {
                    "run": run + 1,
                    "test_case": {
                        "question": test_case["question"],
                        "expected_answer": test_case["expected_answer"],
                        "metadata": test_case.get("metadata", {})
                    },
                    "response": model_response,
                    "evaluation": evaluation,
                    "latency": elapsed_time,
                    "success": success
                }
                
                length_results["runs"].append(run_result)
                print(f"Score: {evaluation['score']:.2f}")
            
            # Calculate averages
            scores = [r["evaluation"]["score"] for r in length_results["runs"] if r["success"]]
            latencies = [r["latency"] for r in length_results["runs"] if r["success"]]
            
            length_results["summary"] = {
                "avg_score": sum(scores) / len(scores) if scores else 0.0,
                "avg_latency": sum(latencies) / len(latencies) if latencies else 0.0,
                "success_rate": sum(1 for r in length_results["runs"] if r["success"]) / num_runs
            }
            
            results["results"].append(length_results)
        
        return results
    
    def run_all_benchmarks(self, context_lengths: List[int], num_runs: int = 3) -> Dict[str, Any]:
        """Run all benchmarks."""
        all_results = {
            "model": self.model,
            "benchmarks": {}
        }
        
        for benchmark_name in self.benchmarks.keys():
            print(f"\n{'='*60}")
            print(f"Running {benchmark_name} benchmark")
            print(f"{'='*60}")
            
            try:
                results = self.run_benchmark(benchmark_name, context_lengths, num_runs)
                all_results["benchmarks"][benchmark_name] = results
            except Exception as e:
                print(f"Error running {benchmark_name}: {e}")
                all_results["benchmarks"][benchmark_name] = {"error": str(e)}
        
        return all_results
    
    def save_results(self, results: Dict[str, Any], filepath: str):
        """Save results to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {filepath}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print a summary of results."""
        print("\n" + "="*60)
        print("BENCHMARK SUMMARY")
        print("="*60)
        
        if "benchmarks" in results:
            for benchmark_name, benchmark_results in results["benchmarks"].items():
                if "error" in benchmark_results:
                    print(f"\n{benchmark_name}: ERROR - {benchmark_results['error']}")
                    continue
                
                print(f"\n{benchmark_name}:")
                print("-" * 40)
                
                for length_result in benchmark_results.get("results", []):
                    ctx_len = length_result["context_length"]
                    summary = length_result["summary"]
                    print(f"  {ctx_len} tokens: "
                          f"Score={summary['avg_score']:.2f}, "
                          f"Latency={summary['avg_latency']:.2f}s, "
                          f"Success={summary['success_rate']:.2%}")
        else:
            # Single benchmark result
            print(f"\n{results.get('benchmark', 'Unknown')}:")
            for length_result in results.get("results", []):
                ctx_len = length_result["context_length"]
                summary = length_result["summary"]
                print(f"  {ctx_len} tokens: "
                      f"Score={summary['avg_score']:.2f}, "
                      f"Latency={summary['avg_latency']:.2f}s")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Run long-context benchmarks")
    parser.add_argument("--benchmark", choices=["all", "needle_in_haystack", "oolong", 
                                                "oolong_pairs", "codeqa", "browsecomp"],
                       default="all", help="Benchmark to run")
    parser.add_argument("--context-lengths", type=int, nargs="+",
                       default=[1000, 5000, 10000, 20000],
                       help="Context lengths to test (in tokens)")
    parser.add_argument("--runs", type=int, default=3,
                       help="Number of runs per context length")
    parser.add_argument("--model", default="gpt-4o",
                       help="Model to use")
    parser.add_argument("--output", help="Output file for results (JSON)")
    
    args = parser.parse_args()
    
    runner = BenchmarkRunner(model=args.model)
    
    if args.benchmark == "all":
        results = runner.run_all_benchmarks(args.context_lengths, args.runs)
    else:
        results = runner.run_benchmark(args.benchmark, args.context_lengths, args.runs)
    
    runner.print_summary(results)
    
    if args.output:
        runner.save_results(results, args.output)

if __name__ == "__main__":
    main()

