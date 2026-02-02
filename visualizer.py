#!/usr/bin/env python3
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import networkx as nx
    VISUALIZATION_AVAILABLE = True
except ImportError as e:
    VISUALIZATION_AVAILABLE = False
    print(f"Warning: Visualization libraries not available. Install with: pip install networkx matplotlib")
    print(f"Error: {e}")

from typing import List, Dict, Optional
from context_manager import ContextManager

class ConversationVisualizer:
    def __init__(self, context_manager: Optional[ContextManager] = None):
        self.context_manager = context_manager or ContextManager()
        if VISUALIZATION_AVAILABLE:
            self.G = nx.DiGraph()
        else:
            self.G = None
    
    def count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())
    
    def normalize_size(self, word_count: int, min_size: int = 100, max_size: int = 3000) -> int:
        """Normalize word count to node size."""
        if word_count == 0:
            return min_size
        return max(min_size, min(max_size, word_count * 10))
    
    def build_graph(self, start: Optional[int] = None, end: Optional[int] = None):
        """Build graph from context entries."""
        if not VISUALIZATION_AVAILABLE:
            return
        self.G.clear()
        
        entries = self.context_manager.read(start=start, end=end)
        if not entries:
            return
        
        for i, entry in enumerate(entries):
            node_id = f"node_{i}"
            role = entry.get("role", "unknown")
            content = entry.get("content", "")
            word_count = self.count_words(content)
            
            self.G.add_node(node_id, 
                          role=role,
                          content=content[:100] + "..." if len(content) > 100 else content,
                          word_count=word_count,
                          index=i)
            
            if i > 0:
                prev_node = f"node_{i-1}"
                self.G.add_edge(prev_node, node_id)
    
    def visualize(self, output_file: Optional[str] = None, 
                  start: Optional[int] = None, end: Optional[int] = None,
                  figsize: tuple = (12, 16), show_labels: bool = True):
        """Visualize the conversation graph."""
        if not VISUALIZATION_AVAILABLE:
            print("Error: Visualization libraries (networkx, matplotlib) are not installed.")
            print("Install with: pip install networkx matplotlib")
            return False
        
        self.build_graph(start=start, end=end)
        
        if len(self.G.nodes()) == 0:
            print("No context to visualize")
            return False
        
        fig, ax = plt.subplots(figsize=figsize)
        
        pos = self._hierarchical_layout()
        
        node_colors = []
        node_sizes = []
        node_labels = {}
        
        for node_id in self.G.nodes():
            node_data = self.G.nodes[node_id]
            role = node_data.get("role", "unknown")
            word_count = node_data.get("word_count", 0)
            
            if role == "user":
                node_colors.append("#4A90E2")
            elif role == "assistant":
                node_colors.append("#50C878")
            elif role == "system":
                node_colors.append("#FF6B6B")
            else:
                node_colors.append("#95A5A6")
            
            node_sizes.append(self.normalize_size(word_count))
            
            if show_labels:
                label = f"{role[0].upper()}\n{word_count}w"
                node_labels[node_id] = label
        
        nx.draw_networkx_nodes(self.G, pos, 
                             node_color=node_colors,
                             node_size=node_sizes,
                             alpha=0.8,
                             ax=ax)
        
        nx.draw_networkx_edges(self.G, pos,
                             edge_color="#BDC3C7",
                             arrows=True,
                             arrowsize=20,
                             alpha=0.6,
                             connectionstyle="arc3,rad=0.1",
                             ax=ax)
        
        if show_labels:
            nx.draw_networkx_labels(self.G, pos, 
                                  labels=node_labels,
                                  font_size=8,
                                  font_weight="bold",
                                  ax=ax)
        
        legend_elements = [
            mpatches.Patch(color="#4A90E2", label="User"),
            mpatches.Patch(color="#50C878", label="Assistant"),
            mpatches.Patch(color="#FF6B6B", label="System"),
            mpatches.Patch(color="#95A5A6", label="Other")
        ]
        ax.legend(handles=legend_elements, loc="upper right")
        
        ax.set_title("Conversation Graph\n(Node size = word count)", 
                    fontsize=14, fontweight="bold", pad=20)
        ax.axis("off")
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            print(f"Graph saved to {output_file}")
        else:
            plt.show()
        
        return True
    
    def _hierarchical_layout(self) -> Dict:
        """Create top-down hierarchical layout."""
        if not VISUALIZATION_AVAILABLE or self.G is None:
            return {}
        pos = {}
        
        nodes = list(self.G.nodes())
        if not nodes:
            return pos
        
        nodes_sorted = sorted(nodes, key=lambda n: self.G.nodes[n].get("index", 0))
        
        y_spacing = 2.0
        x_center = 0
        
        for i, node_id in enumerate(nodes_sorted):
            y_pos = -i * y_spacing
            pos[node_id] = (x_center, y_pos)
        
        return pos
    
    def visualize_from_file(self, filepath: str, output_file: Optional[str] = None):
        """Load context from file and visualize."""
        cm = ContextManager()
        cm.load(filepath)
        self.context_manager = cm
        self.visualize(output_file=output_file)

def main():
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        output = sys.argv[2] if len(sys.argv) > 2 else None
        viz = ConversationVisualizer()
        viz.visualize_from_file(filepath, output_file=output)
    else:
        print("Conversation Visualizer")
        print("Usage:")
        print("  python visualizer.py <context_file.json> [output_image.png]")
        print("  Or use programmatically:")
        print("    from visualizer import ConversationVisualizer")
        print("    from context_manager import ContextManager")
        print("    cm = ContextManager()")
        print("    # ... add context ...")
        print("    viz = ConversationVisualizer(cm)")
        print("    viz.visualize()")

if __name__ == "__main__":
    main()

