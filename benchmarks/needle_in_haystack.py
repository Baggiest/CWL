#!/usr/bin/env python3
import random
import string
from typing import Dict, Any
from benchmarks.base_benchmark import BaseBenchmark

class NeedleInHaystackBenchmark(BaseBenchmark):
    """Needle in a Haystack: Find specific information in long context."""
    
    def __init__(self):
        super().__init__(
            name="Needle in Haystack",
            description="Tests ability to find specific information in very long contexts"
        )
        self.needle_template = "The special code is: {code}"
        self.haystack_sentences = [
            "This is a sample sentence for context generation.",
            "The weather today is quite pleasant and sunny.",
            "Machine learning models require extensive training data.",
            "Python is a versatile programming language.",
            "Context windows are crucial for language models.",
            "Natural language processing enables many applications.",
            "Deep learning has revolutionized artificial intelligence.",
            "Data structures are fundamental to computer science.",
            "Algorithms help solve complex computational problems.",
            "Software engineering practices improve code quality.",
        ]
    
    def generate_haystack(self, length: int, needle: str, needle_position: str = "random") -> str:
        """Generate a long text with needle inserted at specific position.
        
        Args:
            length: Approximate number of sentences
            needle: The information to find
            needle_position: 'start', 'middle', 'end', or 'random'
        """
        sentences = []
        
        # Determine needle position
        if needle_position == "random":
            needle_pos = random.randint(0, length - 1)
        elif needle_position == "start":
            needle_pos = 0
        elif needle_position == "middle":
            needle_pos = length // 2
        elif needle_position == "end":
            needle_pos = length - 1
        else:
            needle_pos = random.randint(0, length - 1)
        
        for i in range(length):
            if i == needle_pos:
                sentences.append(needle)
            else:
                sentences.append(random.choice(self.haystack_sentences))
        
        return " ".join(sentences)
    
    def generate_test_case(self, context_length: int, needle_position: str = "random", **kwargs) -> Dict[str, Any]:
        """Generate a needle-in-haystack test case."""
        # Generate unique code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        needle = self.needle_template.format(code=code)
        
        # Estimate sentences needed for target context length
        # Rough estimate: ~50 tokens per sentence
        num_sentences = max(10, context_length // 50)
        
        haystack = self.generate_haystack(num_sentences, needle, needle_position)
        
        # Build context
        self.context_manager.clear()
        self.context_manager.create("user", haystack)
        
        question = "What is the special code mentioned in the text?"
        expected_answer = code
        
        return {
            "context": haystack,
            "question": question,
            "expected_answer": expected_answer,
            "needle": needle,
            "needle_position": needle_position,
            "metadata": {
                "context_length": self.get_context_length(),
                "num_sentences": num_sentences
            }
        }
    
    def evaluate(self, response: str, expected: str, **kwargs) -> Dict[str, Any]:
        """Evaluate if the code was found in the response."""
        response_upper = response.upper()
        expected_upper = expected.upper()
        
        # Check for exact match
        exact_match = expected_upper in response_upper
        
        # Check if any part of the code appears
        code_found = False
        for char in expected:
            if char in response_upper:
                code_found = True
                break
        
        score = 1.0 if exact_match else (0.5 if code_found else 0.0)
        
        return {
            "correct": exact_match,
            "score": score,
            "response": response,
            "expected": expected,
            "partial_match": code_found and not exact_match
        }

