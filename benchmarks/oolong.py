#!/usr/bin/env python3
import random
from typing import Dict, Any, List
from benchmarks.base_benchmark import BaseBenchmark

class OOLONGBenchmark(BaseBenchmark):
    """OOLONG: Out-Of-LOng-context Needle benchmark."""
    
    def __init__(self):
        super().__init__(
            name="OOLONG",
            description="Tests ability to handle information at various positions in long contexts"
        )
        self.facts = [
            ("The capital of France is", "Paris"),
            ("The largest planet in our solar system is", "Jupiter"),
            ("The speed of light is approximately", "300,000 km/s"),
            ("The author of '1984' is", "George Orwell"),
            ("The chemical symbol for gold is", "Au"),
            ("The tallest mountain on Earth is", "Mount Everest"),
            ("The smallest country in the world is", "Vatican City"),
            ("The longest river in the world is", "the Nile"),
            ("The first person to walk on the moon was", "Neil Armstrong"),
            ("The programming language Python was created by", "Guido van Rossum"),
        ]
    
    def generate_test_case(self, context_length: int, fact_position: str = "random", **kwargs) -> Dict[str, Any]:
        """Generate an OOLONG test case."""
        # Select a fact
        fact_question, fact_answer = random.choice(self.facts)
        
        # Generate filler text
        filler_sentences = [
            "This is contextual information that serves as padding.",
            "The following paragraphs contain various details.",
            "Additional context is provided here for length.",
            "More information follows in subsequent sentences.",
            "These sentences add to the overall context length.",
            "Further details are included in this section.",
            "Additional padding text is inserted here.",
            "More contextual information follows.",
            "This paragraph contains supplementary details.",
            "Further information is provided in this section.",
        ]
        
        # Estimate number of filler blocks needed
        # Each fact + question is ~20 tokens, filler is ~10 tokens per sentence
        target_tokens = context_length
        fact_tokens = 20
        filler_per_sentence = 10
        
        num_filler_sentences = max(5, (target_tokens - fact_tokens) // filler_per_sentence)
        
        # Build context with fact at specified position
        context_parts = []
        
        if fact_position == "start":
            context_parts.append(f"{fact_question} {fact_answer}.")
            context_parts.extend(random.choices(filler_sentences, k=num_filler_sentences))
        elif fact_position == "middle":
            half = num_filler_sentences // 2
            context_parts.extend(random.choices(filler_sentences, k=half))
            context_parts.append(f"{fact_question} {fact_answer}.")
            context_parts.extend(random.choices(filler_sentences, k=num_filler_sentences - half))
        elif fact_position == "end":
            context_parts.extend(random.choices(filler_sentences, k=num_filler_sentences))
            context_parts.append(f"{fact_question} {fact_answer}.")
        else:  # random
            pos = random.randint(0, num_filler_sentences)
            context_parts.extend(random.choices(filler_sentences, k=pos))
            context_parts.append(f"{fact_question} {fact_answer}.")
            context_parts.extend(random.choices(filler_sentences, k=num_filler_sentences - pos))
        
        context_text = " ".join(context_parts)
        
        # Build context
        self.context_manager.clear()
        self.context_manager.create("user", context_text)
        
        question = fact_question.rstrip(" is")
        expected_answer = fact_answer
        
        return {
            "context": context_text,
            "question": question,
            "expected_answer": expected_answer,
            "fact_position": fact_position,
            "metadata": {
                "context_length": self.get_context_length(),
                "num_sentences": len(context_parts)
            }
        }
    
    def evaluate(self, response: str, expected: str, **kwargs) -> Dict[str, Any]:
        """Evaluate the response."""
        response_lower = response.lower().strip()
        expected_lower = expected.lower().strip()
        
        # Exact match
        exact_match = expected_lower == response_lower
        
        # Contains match
        contains_match = expected_lower in response_lower or response_lower in expected_lower
        
        # Partial match (check for key words)
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

