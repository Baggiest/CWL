#!/usr/bin/env python3
"""Example of using individual benchmarks."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.needle_in_haystack import NeedleInHaystackBenchmark
from benchmarks.oolong import OOLONGBenchmark
from benchmarks.codeqa import CodeQABenchmark

print("=" * 60)
print("Benchmark Examples")
print("=" * 60)

# Example 1: Needle in Haystack
print("\n1. Needle in Haystack Benchmark")
print("-" * 60)
benchmark = NeedleInHaystackBenchmark()
test_case = benchmark.generate_test_case(context_length=1000, needle_position="middle")
print(f"Context length: {test_case['metadata']['context_length']} tokens")
print(f"Question: {test_case['question']}")
print(f"Expected answer: {test_case['expected_answer']}")
print(f"Needle position: {test_case['needle_position']}")

# Simulate a response
response = f"The special code is: {test_case['expected_answer']}"
evaluation = benchmark.evaluate(response, test_case['expected_answer'])
print(f"\nResponse: {response}")
print(f"Evaluation: Score={evaluation['score']:.2f}, Correct={evaluation['correct']}")

# Example 2: OOLONG
print("\n2. OOLONG Benchmark")
print("-" * 60)
oolong = OOLONGBenchmark()
test_case = oolong.generate_test_case(context_length=2000, fact_position="end")
print(f"Context length: {test_case['metadata']['context_length']} tokens")
print(f"Question: {test_case['question']}")
print(f"Expected answer: {test_case['expected_answer']}")

# Example 3: CodeQA
print("\n3. CodeQA Benchmark")
print("-" * 60)
codeqa = CodeQABenchmark()
test_case = codeqa.generate_test_case(context_length=1500)
print(f"Context length: {test_case['metadata']['context_length']} tokens")
print(f"Question: {test_case['question']}")
print(f"Expected answer: {test_case['expected_answer']}")
print(f"\nCode snippet (first 200 chars):")
print(test_case['code'][:200] + "...")

print("\n" + "=" * 60)
print("To run full benchmarks with API calls:")
print("  python benchmarks/benchmark_runner.py --benchmark all")
print("=" * 60)

