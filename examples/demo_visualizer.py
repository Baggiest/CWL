#!/usr/bin/env python3
from context_manager import ContextManager
from visualizer import ConversationVisualizer

print("Creating sample conversation...\n")

cm = ContextManager()

cm.create("user", "Hello! I'm working on a project about context windows.")
cm.create("assistant", "That sounds interesting! What specifically are you trying to accomplish?")
cm.create("user", "I want to build a system that can manage and visualize conversations. The system needs to handle large context windows efficiently and provide tools for compacting and searching through conversation history.")
cm.create("assistant", "Great idea! For managing large context windows, you'll want to implement techniques like summarization, chunking, and retrieval-augmented generation. Visualization can help you understand the flow and structure of conversations.")
cm.create("user", "Can you explain more about RAG?")
cm.create("assistant", "RAG stands for Retrieval-Augmented Generation. It combines information retrieval with language generation. The system first retrieves relevant context from a knowledge base, then uses that context to generate more accurate and contextually relevant responses.")
cm.create("user", "Thanks!")
cm.create("assistant", "You're welcome! Good luck with your project.")

print(f"Created {cm.size()} conversation entries\n")

print("Visualizing conversation graph...")
print("(Node size represents word count)\n")

viz = ConversationVisualizer(cm)
result = viz.visualize(output_file="conversation_graph.png", show_labels=True)

if result:
    print("\nGraph saved to conversation_graph.png")
    print("You can also view it interactively by running:")
    print("  python visualizer.py")
elif result is False:
    print("\nNote: Install visualization libraries to generate graph:")
    print("  pip install networkx matplotlib")

