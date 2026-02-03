#!/usr/bin/env python3
import random
from typing import Dict, Any, List, Tuple
from benchmarks.base_benchmark import BaseBenchmark

class OOLONGPairsBenchmark(BaseBenchmark):
    """OOLONG PAIRS: Tests ability to find and relate pairs of information in long contexts."""
    
    def __init__(self):
        super().__init__(
            name="OOLONG PAIRS",
            description="Tests ability to find and relate pairs of information across long contexts"
        )
        self.pairs = [
            ("Alice", "engineer", "works at", "TechCorp"),
            ("Bob", "doctor", "specializes in", "cardiology"),
            ("Charlie", "teacher", "teaches", "mathematics"),
            ("Diana", "artist", "creates", "digital art"),
            ("Eve", "scientist", "researches", "quantum physics"),
            ("Frank", "chef", "cooks", "Italian cuisine"),
            ("Grace", "writer", "writes", "science fiction"),
            ("Henry", "musician", "plays", "jazz piano"),
            ("Iris", "designer", "designs", "user interfaces"),
            ("Jack", "analyst", "analyzes", "financial data"),
        ]
    
    def generate_test_case(self, context_length: int, pair_separation: str = "far", **kwargs) -> Dict[str, Any]:
        """Generate an OOLONG PAIRS test case.
        
        Args:
            pair_separation: 'close', 'medium', 'far', or 'random'
        """
        # Select a pair
        person, role, relation, detail = random.choice(self.pairs)
        
        # Generate filler sentences
        filler_sentences = [
            "This paragraph contains additional contextual information.",
            "More details are provided in the following sections.",
            "The document continues with further explanations.",
            "Additional context is included for completeness.",
            "This section provides supplementary information.",
            "Further details follow in subsequent paragraphs.",
            "More contextual data is presented here.",
            "The text continues with additional information.",
            "This paragraph adds to the overall context.",
            "Further explanations are provided below.",
        ]
        
        # Determine separation distance
        if pair_separation == "close":
            separation = 2
        elif pair_separation == "medium":
            separation = 10
        elif pair_separation == "far":
            separation = 30
        else:  # random
            separation = random.randint(2, 30)
        
        # Estimate sentences needed
        target_tokens = context_length
        pair_tokens = 30  # Both facts together
        filler_per_sentence = 10
        
        num_filler = max(separation, (target_tokens - pair_tokens) // filler_per_sentence)
        
        # Build context with pair separated
        context_parts = []
        
        # First fact
        context_parts.append(f"{person} is a {role}.")
        context_parts.extend(random.choices(filler_sentences, k=separation))
        
        # Second fact
        context_parts.append(f"{person} {relation} {detail}.")
        context_parts.extend(random.choices(filler_sentences, k=num_filler - separation))
        
        context_text = " ".join(context_parts)
        
        # Build context
        self.context_manager.clear()
        self.context_manager.create("user", context_text)
        
        # Question asks to relate the pair
        question = f"What does {person} {relation}?"
        expected_answer = detail
        
        return {
            "context": context_text,
            "question": question,
            "expected_answer": expected_answer,
            "person": person,
            "pair_separation": pair_separation,
            "separation_distance": separation,
            "metadata": {
                "context_length": self.get_context_length(),
                "num_sentences": len(context_parts)
            }
        }
    
    def evaluate(self, response: str, expected: str, **kwargs) -> Dict[str, Any]:
        """Evaluate if the pair relationship was correctly identified."""
        response_lower = response.lower().strip()
        expected_lower = expected.lower().strip()
        
        # Exact match
        exact_match = expected_lower == response_lower
        
        # Contains match
        contains_match = expected_lower in response_lower
        
        # Check for key words from expected answer
        expected_words = set(expected_lower.split())
        response_words = set(response_lower.split())
        common_words = expected_words.intersection(response_words)
        partial_score = len(common_words) / len(expected_words) if expected_words else 0
        
        score = 1.0 if exact_match else (0.8 if contains_match else min(0.6, partial_score))
        
        return {
            "correct": exact_match,
            "score": score,
            "response": response,
            "expected": expected,
            "contains_match": contains_match,
            "partial_score": partial_score
        }

