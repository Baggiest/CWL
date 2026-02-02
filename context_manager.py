#!/usr/bin/env python3
from typing import List, Dict, Any, Optional, Union
import json

class ContextManager:
    def __init__(self):
        self.context: List[Dict[str, Any]] = []
    
    def create(self, role: str, content: str, metadata: Optional[Dict] = None) -> int:
        """Add a new context entry. Returns the index."""
        entry = {
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        self.context.append(entry)
        return len(self.context) - 1
    
    def read(self, index: Optional[int] = None, start: Optional[int] = None, 
             end: Optional[int] = None, role: Optional[str] = None) -> Union[Dict, List[Dict]]:
        """Read context entries.
        
        Args:
            index: Get single entry by index
            start, end: Get range of entries
            role: Filter by role
        """
        if index is not None:
            if 0 <= index < len(self.context):
                return self.context[index]
            return None
        
        result = self.context
        if start is not None or end is not None:
            result = result[start:end]
        
        if role:
            result = [entry for entry in result if entry.get("role") == role]
        
        return result
    
    def update(self, index: int, role: Optional[str] = None, 
               content: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        """Update a context entry by index."""
        if not 0 <= index < len(self.context):
            return False
        
        if role:
            self.context[index]["role"] = role
        if content:
            self.context[index]["content"] = content
        if metadata:
            self.context[index]["metadata"].update(metadata)
        
        return True
    
    def delete(self, index: Optional[int] = None, start: Optional[int] = None,
               end: Optional[int] = None, role: Optional[str] = None) -> int:
        """Delete context entries. Returns number of deleted entries.
        
        Args:
            index: Delete single entry
            start, end: Delete range
            role: Delete all entries with this role
        """
        if index is not None:
            if 0 <= index < len(self.context):
                del self.context[index]
                return 1
            return 0
        
        if start is not None or end is not None:
            deleted = len(self.context[start:end])
            del self.context[start:end]
            return deleted
        
        if role:
            original_len = len(self.context)
            self.context = [entry for entry in self.context if entry.get("role") != role]
            return original_len - len(self.context)
        
        return 0
    
    def clear(self):
        """Clear all context."""
        self.context.clear()
    
    def size(self) -> int:
        """Get total number of context entries."""
        return len(self.context)
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get context in OpenAI message format."""
        return [{"role": entry["role"], "content": entry["content"]} 
                for entry in self.context]
    
    def search(self, query: str, limit: Optional[int] = None) -> List[Dict]:
        """Simple text search in context content."""
        results = []
        query_lower = query.lower()
        for entry in self.context:
            if query_lower in entry["content"].lower():
                results.append(entry)
                if limit and len(results) >= limit:
                    break
        return results
    
    def compact(self, start: Optional[int] = None, end: Optional[int] = None,
                max_length: int = 500) -> str:
        """Get compacted/summarized view of context range."""
        target = self.context[start:end] if start is not None or end is not None else self.context
        
        if not target:
            return "No context to compact."
        
        compacted = []
        for entry in target:
            content = entry["content"]
            if len(content) > max_length:
                content = content[:max_length] + "..."
            compacted.append(f"[{entry['role']}]: {content}")
        
        return "\n".join(compacted)
    
    def save(self, filepath: str):
        """Save context to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.context, f, indent=2)
    
    def load(self, filepath: str):
        """Load context from JSON file."""
        with open(filepath, 'r') as f:
            self.context = json.load(f)
    
    def stats(self) -> Dict[str, Any]:
        """Get statistics about the context."""
        roles = {}
        total_chars = 0
        for entry in self.context:
            role = entry.get("role", "unknown")
            roles[role] = roles.get(role, 0) + 1
            total_chars += len(entry.get("content", ""))
        
        return {
            "total_entries": len(self.context),
            "total_characters": total_chars,
            "roles": roles,
            "average_length": total_chars / len(self.context) if self.context else 0
        }

