#!/usr/bin/env python3
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from context_manager import ContextManager

class BaseBenchmark(ABC):
    """Base class for all long-context benchmarks."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.context_manager = ContextManager()
    
    @abstractmethod
    def generate_test_case(self, context_length: int, **kwargs) -> Dict[str, Any]:
        """Generate a test case with specified context length.
        
        Returns:
            Dict with keys: 'context', 'question', 'expected_answer', 'metadata'
        """
        pass
    
    @abstractmethod
    def evaluate(self, response: str, expected: str, **kwargs) -> Dict[str, Any]:
        """Evaluate the model's response against expected answer.
        
        Returns:
            Dict with 'correct', 'score', and other metrics
        """
        pass
    
    def get_context_messages(self) -> List[Dict[str, str]]:
        """Get context in OpenAI message format."""
        return self.context_manager.get_messages()
    
    def clear_context(self):
        """Clear the context manager."""
        self.context_manager.clear()
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation: 1 token ≈ 4 chars)."""
        return len(text) // 4
    
    def get_context_length(self) -> int:
        """Get total context length in tokens."""
        total = 0
        for entry in self.context_manager.read():
            total += self.count_tokens(entry.get("content", ""))
        return total

