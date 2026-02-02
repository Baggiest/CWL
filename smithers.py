#!/usr/bin/env python3
import os
import sys
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv
from context_manager import ContextManager

try:
    from visualizer import ConversationVisualizer
    VISUALIZER_AVAILABLE = True
except ImportError:
    VISUALIZER_AVAILABLE = False

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY not found in .env file")
    sys.exit(1)

client = OpenAI(api_key=api_key)

class Smithers:
    def __init__(self):
        self.client = client
        self.context_manager = ContextManager()
        self.model = "gpt-4o"
    
    def chat(self, message: str, use_context: bool = True) -> str:
        """Chat with Smithers. Optionally uses context."""
        try:
            messages = []
            if use_context and self.context_manager.size() > 0:
                messages = self.context_manager.get_messages()
            
            messages.append({"role": "user", "content": message})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            assistant_message = response.choices[0].message.content
            
            if use_context:
                self.context_manager.create("user", message)
                self.context_manager.create("assistant", assistant_message)
            
            return assistant_message
        except Exception as e:
            return f"Error: {str(e)}"
    
    def compact_context(self, start: Optional[int] = None, end: Optional[int] = None) -> str:
        """Ask Smithers to help compact context."""
        context_preview = self.context_manager.compact(start, end, max_length=200)
        
        prompt = f"""You are helping to compact and summarize context. Here's the current context:

{context_preview}

Please provide a concise summary that captures the key information. Keep it brief and actionable."""
        
        summary = self.chat(prompt, use_context=False)
        return summary
    
    def rag_search(self, query: str, limit: int = 5) -> List[Dict]:
        """RAG: Retrieve relevant context entries."""
        return self.context_manager.search(query, limit=limit)
    
    def rag_enhanced_chat(self, message: str, retrieval_limit: int = 3) -> str:
        """Chat with RAG - retrieves relevant context first."""
        relevant = self.rag_search(message, limit=retrieval_limit)
        
        if relevant:
            context_str = "\n".join([
                f"[{entry['role']}]: {entry['content'][:300]}"
                for entry in relevant
            ])
            enhanced_message = f"""Relevant context:
{context_str}

User question: {message}"""
            return self.chat(enhanced_message, use_context=True)
        else:
            return self.chat(message, use_context=True)
    
    def get_context_manager(self) -> ContextManager:
        """Get the context manager for direct CRUD operations."""
        return self.context_manager

def main():
    smithers = Smithers()
    cm = smithers.get_context_manager()
    
    print("Smithers Assistant - Context Window Manager")
    print("Commands:")
    print("  chat <message> - Chat with Smithers")
    print("  create <role> <content> - Add context entry")
    print("  read [index|start:end|role] - Read context")
    print("  update <index> <role|content|metadata> <value> - Update entry")
    print("  delete <index|start:end|role> - Delete entries")
    print("  search <query> - Search context")
    print("  compact [start:end] - Compact context")
    print("  stats - Show context statistics")
    print("  clear - Clear all context")
    print("  save <filepath> - Save context to file")
    print("  load <filepath> - Load context from file")
    print("  rag <query> - RAG search")
    print("  visualize [output.png] [start:end] - Visualize conversation graph")
    print("  exit/quit - Exit")
    print()
    
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
            
            parts = user_input.split(' ', 1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if command == "chat":
                if args:
                    response = smithers.chat(args)
                    print(f"Smithers: {response}\n")
                else:
                    print("Usage: chat <message>")
            
            elif command == "create":
                create_parts = args.split(' ', 1)
                if len(create_parts) == 2:
                    role, content = create_parts
                    idx = cm.create(role, content)
                    print(f"Created entry at index {idx}\n")
                else:
                    print("Usage: create <role> <content>")
            
            elif command == "read":
                if not args:
                    entries = cm.read()
                    for i, entry in enumerate(entries):
                        print(f"[{i}] {entry['role']}: {entry['content'][:100]}...")
                elif ':' in args:
                    start, end = args.split(':')
                    entries = cm.read(start=int(start), end=int(end))
                    for i, entry in enumerate(entries):
                        print(f"[{i}] {entry['role']}: {entry['content'][:100]}...")
                elif args.isdigit():
                    entry = cm.read(index=int(args))
                    if entry:
                        print(f"{entry['role']}: {entry['content']}")
                    else:
                        print("Entry not found")
                else:
                    entries = cm.read(role=args)
                    for i, entry in enumerate(entries):
                        print(f"[{i}] {entry['role']}: {entry['content'][:100]}...")
                print()
            
            elif command == "update":
                update_parts = args.split(' ', 2)
                if len(update_parts) >= 3:
                    idx, field, value = update_parts
                    success = False
                    if field == "role":
                        success = cm.update(int(idx), role=value)
                    elif field == "content":
                        success = cm.update(int(idx), content=value)
                    elif field == "metadata":
                        import json
                        try:
                            metadata = json.loads(value)
                            success = cm.update(int(idx), metadata=metadata)
                        except:
                            print("Invalid JSON for metadata")
                    if success:
                        print(f"Updated entry {idx}\n")
                    else:
                        print("Update failed\n")
                else:
                    print("Usage: update <index> <field> <value>")
            
            elif command == "delete":
                if not args:
                    print("Usage: delete <index|start:end|role>")
                elif ':' in args:
                    start, end = args.split(':')
                    deleted = cm.delete(start=int(start), end=int(end))
                    print(f"Deleted {deleted} entries\n")
                elif args.isdigit():
                    deleted = cm.delete(index=int(args))
                    print(f"Deleted {deleted} entry\n")
                else:
                    deleted = cm.delete(role=args)
                    print(f"Deleted {deleted} entries\n")
            
            elif command == "search":
                if args:
                    results = cm.search(args)
                    for entry in results:
                        print(f"{entry['role']}: {entry['content'][:100]}...")
                    print(f"Found {len(results)} results\n")
                else:
                    print("Usage: search <query>")
            
            elif command == "compact":
                if ':' in args:
                    start, end = args.split(':')
                    summary = smithers.compact_context(start=int(start), end=int(end))
                else:
                    summary = smithers.compact_context()
                print(f"Compacted summary:\n{summary}\n")
            
            elif command == "stats":
                stats = cm.stats()
                print(f"Context Statistics:")
                print(f"  Total entries: {stats['total_entries']}")
                print(f"  Total characters: {stats['total_characters']}")
                print(f"  Average length: {stats['average_length']:.1f}")
                print(f"  Roles: {stats['roles']}\n")
            
            elif command == "clear":
                cm.clear()
                print("Context cleared\n")
            
            elif command == "save":
                if args:
                    cm.save(args)
                    print(f"Saved to {args}\n")
                else:
                    print("Usage: save <filepath>")
            
            elif command == "load":
                if args:
                    cm.load(args)
                    print(f"Loaded from {args}\n")
                else:
                    print("Usage: load <filepath>")
            
            elif command == "rag":
                if args:
                    response = smithers.rag_enhanced_chat(args)
                    print(f"Smithers (RAG): {response}\n")
                else:
                    print("Usage: rag <query>")
            
            elif command == "visualize" or command == "viz":
                if not VISUALIZER_AVAILABLE:
                    print("Visualization not available. Install with: pip install networkx matplotlib\n")
                else:
                    viz = ConversationVisualizer(cm)
                    output_file = None
                    start = None
                    end = None
                    
                    if args:
                        parts = args.split()
                        for part in parts:
                            if part.endswith('.png') or part.endswith('.jpg') or part.endswith('.pdf'):
                                output_file = part
                            elif ':' in part:
                                start_str, end_str = part.split(':')
                                try:
                                    start = int(start_str) if start_str else None
                                    end = int(end_str) if end_str else None
                                except:
                                    pass
                    
                    try:
                        viz.visualize(output_file=output_file, start=start, end=end)
                        if output_file:
                            print(f"Visualization saved to {output_file}\n")
                        else:
                            print("Visualization displayed\n")
                    except Exception as e:
                        print(f"Visualization error: {str(e)}\n")
            
            else:
                print(f"Unknown command: {command}\n")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}\n")

if __name__ == "__main__":
    main()

