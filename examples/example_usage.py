#!/usr/bin/env python3
from context_manager import ContextManager
from smithers import Smithers

print("=== Context Manager CRUD Example ===\n")

cm = ContextManager()

cm.create("user", "Hello, I'm working on a project")
cm.create("assistant", "Great! What kind of project?")
cm.create("user", "It's a context window management system")
cm.create("assistant", "Interesting! Tell me more about it.")

print("Created 4 entries")
print(f"Total entries: {cm.size()}\n")

print("Read all entries:")
for i, entry in enumerate(cm.read()):
    print(f"  [{i}] {entry['role']}: {entry['content']}")

print("\nRead entry at index 1:")
entry = cm.read(index=1)
print(f"  {entry['role']}: {entry['content']}")

print("\nSearch for 'project':")
results = cm.search("project")
for entry in results:
    print(f"  {entry['role']}: {entry['content']}")

print("\nUpdate entry 0:")
cm.update(0, content="Hello, I'm working on an awesome project")
print(f"  Updated: {cm.read(index=0)['content']}")

print("\nDelete entry at index 2:")
cm.delete(index=2)
print(f"Remaining entries: {cm.size()}")

print("\nStats:")
stats = cm.stats()
print(f"  {stats}")

print("\n=== Smithers Assistant Example ===\n")

smithers = Smithers()

print("Chat with Smithers:")
response = smithers.chat("What is 2+2?")
print(f"Smithers: {response}\n")

print("Context after chat:")
print(f"  Entries: {smithers.get_context_manager().size()}")

print("\nRAG search example:")
smithers.get_context_manager().create("user", "Python is a programming language")
smithers.get_context_manager().create("assistant", "Yes, Python is great for data science")
smithers.get_context_manager().create("user", "I love using Python for web development")

results = smithers.rag_search("Python", limit=2)
print(f"Found {len(results)} relevant entries")

print("\nRAG enhanced chat:")
response = smithers.rag_enhanced_chat("What can Python be used for?")
print(f"Smithers: {response}\n")

