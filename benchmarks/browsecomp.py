#!/usr/bin/env python3
import random
from typing import Dict, Any
from benchmarks.base_benchmark import BaseBenchmark

class BrowseCompBenchmark(BaseBenchmark):
    """BrowseComp+: Tests ability to browse and comprehend long documents."""
    
    def __init__(self):
        super().__init__(
            name="BrowseComp+",
            description="Tests ability to browse and comprehend information across long documents"
        )
        self.document_sections = [
            {
                "title": "Introduction",
                "content": "This document provides comprehensive information about the topic. It covers various aspects and details.",
            },
            {
                "title": "Background",
                "content": "The historical context is important for understanding the current state of affairs.",
            },
            {
                "title": "Methodology",
                "content": "The approach used involves systematic analysis and careful consideration of all factors.",
            },
            {
                "title": "Results",
                "content": "The findings indicate significant progress in the field with measurable improvements.",
            },
            {
                "title": "Discussion",
                "content": "These results have important implications for future research and development.",
            },
            {
                "title": "Conclusion",
                "content": "In summary, the work demonstrates clear advancement in the domain.",
            },
        ]
        
        self.questions = [
            ("What is the main topic?", "the topic"),
            ("What does the methodology involve?", "systematic analysis"),
            ("What do the results indicate?", "significant progress"),
            ("What are the implications?", "future research"),
        ]
    
    def generate_test_case(self, context_length: int, num_sections: int = None, **kwargs) -> Dict[str, Any]:
        """Generate a BrowseComp+ test case."""
        # Determine number of sections
        if num_sections is None:
            # Estimate: each section is ~30 tokens, target context length
            num_sections = max(3, min(len(self.document_sections), context_length // 30))
        
        # Select sections
        selected_sections = random.sample(self.document_sections, min(num_sections, len(self.document_sections)))
        
        # Add detail sentences to each section
        detail_sentences = [
            "Additional details are provided in this section.",
            "More information follows in the subsequent paragraphs.",
            "Further explanations clarify the concepts discussed.",
            "The section continues with relevant information.",
            "Additional context is included for completeness.",
        ]
        
        # Build document
        document_parts = []
        key_facts = {}
        
        for i, section in enumerate(selected_sections):
            # Add section with details
            section_text = f"{section['title']}\n{section['content']}"
            
            # Add a unique fact to each section for questions
            fact_key = f"fact_{i}"
            fact_value = f"Section {i+1} contains important information about {section['title'].lower()}."
            key_facts[fact_key] = fact_value
            section_text += f" {fact_value}"
            
            # Add filler
            section_text += " " + " ".join(random.choices(detail_sentences, k=3))
            
            document_parts.append(section_text)
        
        document_text = "\n\n".join(document_parts)
        
        # Select a question
        question_text, expected_part = random.choice(self.questions)
        
        # Find the section that contains the answer
        answer_section = None
        for section in selected_sections:
            if expected_part.lower() in section['content'].lower():
                answer_section = section
                break
        
        if answer_section:
            expected_answer = answer_section['content']
        else:
            # Fallback: use a fact from the document
            fact_key = random.choice(list(key_facts.keys()))
            expected_answer = key_facts[fact_key]
        
        # Build context
        self.context_manager.clear()
        self.context_manager.create("user", document_text)
        
        return {
            "context": document_text,
            "question": question_text,
            "expected_answer": expected_answer,
            "num_sections": len(selected_sections),
            "metadata": {
                "context_length": self.get_context_length(),
                "sections": [s['title'] for s in selected_sections]
            }
        }
    
    def evaluate(self, response: str, expected: str, **kwargs) -> Dict[str, Any]:
        """Evaluate comprehension of the document."""
        response_lower = response.lower().strip()
        expected_lower = expected.lower().strip()
        
        # Check for key phrases from expected answer
        expected_words = set(expected_lower.split())
        response_words = set(response_lower.split())
        common_words = expected_words.intersection(response_words)
        
        # Calculate overlap
        if len(expected_words) > 0:
            word_overlap = len(common_words) / len(expected_words)
        else:
            word_overlap = 0
        
        # Check for semantic similarity (simple: key terms)
        key_terms = [w for w in expected_words if len(w) > 4]  # Longer words are more meaningful
        found_terms = sum(1 for term in key_terms if term in response_lower)
        term_score = found_terms / len(key_terms) if key_terms else 0
        
        # Combined score
        score = max(word_overlap, term_score * 0.8)
        
        # Consider it correct if score > 0.7
        correct = score > 0.7
        
        return {
            "correct": correct,
            "score": score,
            "response": response,
            "expected": expected,
            "word_overlap": word_overlap,
            "term_score": term_score
        }

