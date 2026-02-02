# Context Window Lab

A lab project for experimenting with context window management, conversation visualization, and RAG operations for LLM interactions.

## Project Structure

```
lab/
├── chatgpt_client.py      # Simple ChatGPT client (the "boss")
├── smithers.py            # Assistant LLM with context management tools
├── context_manager.py     # CRUD operations for context windows
├── visualizer.py          # Conversation graph visualizer
├── example_usage.py       # Usage examples
├── demo_visualizer.py     # Visualization demo
├── requirements.txt       # Python dependencies
├── .env                   # API keys (create this file)
└── README.md             # This file
```

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file:**
   ```bash
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

## Components

### 1. ChatGPT Client (`chatgpt_client.py`)
Simple client for direct ChatGPT interactions.

**Usage:**
```bash
# Command line
python chatgpt_client.py "Hello, how are you?"

# Interactive mode
python chatgpt_client.py
```

### 2. Context Manager (`context_manager.py`)
Core library for managing context windows with full CRUD operations.

**Features:**
- Create, Read, Update, Delete context entries
- Search context by text
- Compact/summarize context ranges
- Save/load context to JSON
- Statistics and analytics

**Usage:**
```python
from context_manager import ContextManager

cm = ContextManager()
cm.create("user", "Hello")
cm.create("assistant", "Hi there!")
entry = cm.read(index=0)
cm.update(0, content="Hello world")
cm.delete(index=1)
```

### 3. Smithers (`smithers.py`)
Assistant LLM that helps manage context windows and performs RAG operations.

**Features:**
- Chat with automatic context management
- RAG (Retrieval-Augmented Generation)
- Context compaction using AI
- Full CRUD operations via CLI
- Integration with visualizer

**Usage:**
```bash
python smithers.py
```

**Commands:**
- `chat <message>` - Chat with Smithers
- `create <role> <content>` - Add context entry
- `read [index|start:end|role]` - Read context
- `update <index> <field> <value>` - Update entry
- `delete <index|start:end|role>` - Delete entries
- `search <query>` - Search context
- `compact [start:end]` - Compact context
- `stats` - Show context statistics
- `save <filepath>` - Save context to file
- `load <filepath>` - Load context from file
- `rag <query>` - RAG-enhanced chat
- `visualize [output.png] [start:end]` - Visualize conversation graph
- `exit/quit` - Exit

**Programmatic Usage:**
```python
from smithers import Smithers

smithers = Smithers()
response = smithers.chat("What is 2+2?")
cm = smithers.get_context_manager()
```

### 4. Visualizer (`visualizer.py`)
Creates graph visualizations of conversations with node sizes based on word count.

**Features:**
- Top-down hierarchical layout
- Node size = word count
- Color-coded by role (user/assistant/system)
- Save to PNG/PDF or display interactively

**Usage:**
```bash
# From saved context file
python visualizer.py context.json output.png

# Programmatically
from visualizer import ConversationVisualizer
from context_manager import ContextManager

cm = ContextManager()
# ... add context ...
viz = ConversationVisualizer(cm)
viz.visualize(output_file="graph.png")
```

**From Smithers:**
```bash
python smithers.py
> visualize conversation.png
> visualize output.png 0:10  # Specific range
```

## Quick Start

1. **Set up environment:**
   ```bash
   pip install -r requirements.txt
   echo "OPENAI_API_KEY=your_key" > .env
   ```

2. **Try the simple client:**
   ```bash
   python chatgpt_client.py "Hello!"
   ```

3. **Use Smithers with context management:**
   ```bash
   python smithers.py
   > chat Hello, I'm working on a project
   > chat Tell me about context windows
   > stats
   > visualize conversation.png
   ```

4. **See examples:**
   ```bash
   python example_usage.py
   python demo_visualizer.py
   ```

## Workflow Example

```bash
# 1. Start Smithers
python smithers.py

# 2. Have a conversation
> chat What are context windows?
> chat How do I manage large contexts?
> chat Explain RAG

# 3. Check your context
> stats
> read

# 4. Search for specific topics
> search RAG

# 5. Visualize the conversation
> visualize conversation_graph.png

# 6. Save for later
> save my_conversation.json

# 7. Load and continue
> load my_conversation.json
> chat Continue our discussion
```

## Dependencies

- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management
- `networkx` - Graph creation (for visualizer)
- `matplotlib` - Plotting (for visualizer)

**Note:** Visualization features are optional. The rest of the system works without `networkx` and `matplotlib` installed.

## Notes

- This is a **lab project** for experimentation
- Context is stored in memory by default (use `save`/`load` for persistence)
- All tools are designed to be simple and understandable
- The visualizer requires networkx and matplotlib (install separately if needed)

## File Descriptions

- **chatgpt_client.py**: Simple ChatGPT interface (the "boss")
- **smithers.py**: Assistant with context management tools
- **context_manager.py**: Core CRUD operations for context arrays
- **visualizer.py**: Graph visualization of conversations
- **example_usage.py**: Code examples for all features
- **demo_visualizer.py**: Demo script for visualization


