#!/usr/bin/env python3
import random
from typing import Dict, Any
from benchmarks.base_benchmark import BaseBenchmark

class CodeQABenchmark(BaseBenchmark):
    """CodeQA: Tests ability to answer questions about code in long contexts."""
    
    def __init__(self):
        super().__init__(
            name="CodeQA",
            description="Tests ability to understand and answer questions about code in long contexts"
        )
        self.code_snippets = [
            {
                "code": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
""",
                "question": "What does this function calculate?",
                "answer": "Fibonacci numbers"
            },
            {
                "code": """
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
""",
                "question": "What sorting algorithm is this?",
                "answer": "Quicksort"
            },
            {
                "code": """
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
""",
                "question": "What data structure does this implement?",
                "answer": "Linked list"
            },
            {
                "code": """
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
""",
                "question": "What is the time complexity of this algorithm?",
                "answer": "O(log n)"
            },
        ]
    
    def generate_test_case(self, context_length: int, **kwargs) -> Dict[str, Any]:
        """Generate a CodeQA test case."""
        # Select a code snippet
        snippet_data = random.choice(self.code_snippets)
        code = snippet_data["code"]
        question = snippet_data["question"]
        answer = snippet_data["answer"]
        
        # Generate documentation/filler text
        doc_sentences = [
            "This code implements a common algorithm.",
            "The function is well-documented and follows best practices.",
            "Error handling is included for edge cases.",
            "The implementation is efficient and readable.",
            "This code can be used in various applications.",
            "The algorithm has been tested extensively.",
            "Performance optimizations have been applied.",
            "The code follows standard coding conventions.",
            "Additional helper functions may be needed.",
            "This implementation is suitable for production use.",
        ]
        
        # Estimate filler needed
        code_tokens = self.count_tokens(code)
        target_tokens = context_length
        filler_per_sentence = 10
        
        num_filler = max(5, (target_tokens - code_tokens) // filler_per_sentence)
        
        # Build context
        filler_text = " ".join(random.choices(doc_sentences, k=num_filler))
        
        context_text = f"""
{filler_text}

Here is the code:

{code}

{filler_text}
""".strip()
        
        # Build context
        self.context_manager.clear()
        self.context_manager.create("user", context_text)
        
        return {
            "context": context_text,
            "question": question,
            "expected_answer": answer,
            "code": code,
            "metadata": {
                "context_length": self.get_context_length(),
                "code_tokens": code_tokens
            }
        }
    
    def evaluate(self, response: str, expected: str, **kwargs) -> Dict[str, Any]:
        """Evaluate the code-related answer."""
        response_lower = response.lower().strip()
        expected_lower = expected.lower().strip()
        
        # Exact match
        exact_match = expected_lower == response_lower
        
        # Contains match
        contains_match = expected_lower in response_lower
        
        # Check for key terms
        expected_terms = set(expected_lower.split())
        response_terms = set(response_lower.split())
        common_terms = expected_terms.intersection(response_terms)
        partial_score = len(common_terms) / len(expected_terms) if expected_terms else 0
        
        score = 1.0 if exact_match else (0.8 if contains_match else min(0.6, partial_score))
        
        return {
            "correct": exact_match,
            "score": score,
            "response": response,
            "expected": expected,
            "contains_match": contains_match,
            "partial_score": partial_score
        }

