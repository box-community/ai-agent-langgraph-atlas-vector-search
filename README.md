# AI Agent with LangGraph, Atlas Vector Search, and Box Integration

A complete demonstration of building an AI agent that can answer questions about enterprise documents stored in Box using MongoDB Atlas vector search and LangGraph workflows.

## 🎯 What This Project Does

This project shows you how to:
1. **Connect to Box** and upload documents
2. **Process documents** with LangChain and create text chunks
3. **Store embeddings** in MongoDB Atlas with vector search capabilities
4. **Build AI tools** for vector and full-text search
5. **Create a LangGraph agent** that can intelligently use these tools
6. **Enable conversational memory** with MongoDB checkpointing

## 🏗️ Architecture Overview

```
Box Documents → LangChain Processing → MongoDB Atlas Vector Store → LangGraph Agent → AI Responses
     ↑                                          ↓
Sample Data (5 Tech Earnings Reports)    Vector + Full-Text Search
```

## 🚀 Quick Start

### Prerequisites

You'll need accounts and API keys for:
- **Box Developer Account** (for document storage)
- **MongoDB Atlas** (for vector search)
- **OpenAI** (for embeddings and language models)

### 1. Clone and Setup

```bash
git clone https://github.com/box-community/ai-agent-langgraph-atlas-vector-search.git
cd ai-agent-langgraph-atlas-vector-search
uv sync  # This installs all dependencies
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# Box Configuration
BOX_CLIENT_ID=your_box_client_id
BOX_CLIENT_SECRET=your_box_client_secret
BOX_SUBJECT_ID=your_box_user_id

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# MongoDB Configuration
MONGODB_URI=your_mongodb_connection_string
```

### 3. Run the Complete Demo

Execute the scripts in order:

```bash
# Step 1: Initialize data and create indexes
python src/a_init_data.py

# Step 2: Test the search tools
python src/b_agent_tools.py

# Step 3: Test basic agent functionality
python src/c_agent_demo.py

# Step 4: Run the full LangGraph workflow
python src/d_langgraph.py
```

## 📁 Project Structure

```
├── sample_data/
│   └── Q4 Tech earnings-Demo/          # Sample financial documents
├── rag_demo/
│   ├── README.md                       # Jupyter notebook example
│   └── rag_demo.ipynb                  # Interactive demo notebook
├── src/
│   ├── a_init_data.py                  # Data initialization and indexing
│   ├── b_agent_tools.py                # Search tools definition
│   ├── c_agent_demo.py                 # Basic agent setup
│   └── d_langgraph.py                  # Complete LangGraph workflow
└── README.md                           # This file
```

## 🔧 Step-by-Step Breakdown

### Step 1: Data Initialization (`a_init_data.py`)

**What it does:**
- Connects to Box using Client Credentials Grant (CCG) authentication
- Uploads sample earnings reports to Box
- Downloads and processes documents with LangChain
- Creates vector embeddings using OpenAI
- Sets up MongoDB Atlas vector and full-text search indexes

**Key functions:**
- `get_box_client()` - Initializes Box connection
- `upload_sample_data()` - Uploads documents to Box
- `load_documents_from_box()` - Processes documents with LangChain
- `create_vector_index()` - Creates MongoDB vector search index

### Step 2: Search Tools (`b_agent_tools.py`)

**What it does:**
- Defines LangChain tools for vector and full-text search
- Implements semantic search using MongoDB Atlas Vector Search
- Implements keyword search using MongoDB Atlas Full-Text Search

**Tools created:**
- `vector_search()` - Finds semantically similar content
- `full_text_search()` - Finds exact text matches

### Step 3: Agent Setup (`c_agent_demo.py`)

**What it does:**
- Creates a ChatOpenAI model with tool binding
- Defines system prompts for the agent
- Tests tool selection and invocation

**Key components:**
- `get_llm_with_tools()` - Configures LLM with search tools
- System prompt that guides tool usage

### Step 4: LangGraph Workflow (`d_langgraph.py`)

**What it does:**
- Builds a complete conversational agent using LangGraph
- Implements state management and tool routing
- Adds conversation memory with MongoDB checkpointing
- Enables multi-turn conversations

**Graph nodes:**
- `agent` - Makes decisions and calls tools
- `tools_node` - Executes search tools
- Conditional routing between nodes

## 🎮 Interactive Demo

For a hands-on experience, use the Jupyter notebook RAG demo:

```bash
jupyter notebook rag_demo/rag_demo.ipynb
```

The notebook walks through each step interactively and shows the results at each stage.

## 💡 Example Interactions

**Question:** "What are the biggest challenges facing tech companies?"

**Agent Process:**
1. Receives user question
2. Decides to use `vector_search` tool
3. Retrieves relevant document chunks
4. Synthesizes answer from search results
5. Provides response with context

**Sample Response:**
```
Based on the earnings reports, major tech companies face several challenges:

1. **China Macro Environment**: Challenging macroeconomic conditions affecting operations
2. **Infrastructure Costs**: Significant growth in infrastructure expenses
3. **AI Investment Requirements**: Need for continued investment in data centers and AI
4. **Shifting Technology Preferences**: Changes in consumer preferences for Western technology

Sources: Apple_analysis.docx, Meta_analysis.docx, NVIDIA_analysis.docx
```

## 🔍 Key Features

### Document Processing
- **Automatic chunking** with configurable size and overlap
- **Metadata preservation** including source URLs and titles
- **Error handling** for duplicate files and API issues

### Search Capabilities
- **Vector search** for semantic similarity
- **Full-text search** for exact matches
- **Hybrid approach** combining both search types

### Conversational Memory
- **Thread-based conversations** using MongoDB checkpointing
- **State persistence** across multiple interactions
- **Context retention** for follow-up questions

### Enterprise Integration
- **Box CCG authentication** for secure enterprise access
- **MongoDB Atlas** for production-scale vector search
- **Configurable chunking** and retrieval parameters

## 🛠️ Customization Options

### Modify Document Processing
```python
# In a_init_data.py, adjust chunking parameters
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Increase for larger chunks
    chunk_overlap=50     # Adjust overlap as needed
)
```

### Adjust Search Behavior
```python
# In b_agent_tools.py, modify retrieval parameters
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 10},  # Return more results
)
```

### Change AI Models
```python
# In c_agent_demo.py, switch models
llm = ChatOpenAI(model="gpt-3.5-turbo")  # Use different model
```

## 🔒 Security Considerations

- **API Keys**: Store all credentials in environment variables
- **Box Permissions**: Documents extracted lose Box security controls
- **MongoDB Access**: Use MongoDB Atlas built-in security features
- **Rate Limits**: Monitor OpenAI API usage and costs

## 🐛 Troubleshooting

### Common Issues

**Box Authentication Failed**
```bash
# Check your credentials in .env file
# Ensure Box app has correct permissions
# Verify user ID is correct
```

**MongoDB Connection Error**
```bash
# Verify connection string format
# Check network access to Atlas cluster
# Ensure cluster is running
```

**OpenAI API Errors**
```bash
# Check API key validity
# Monitor rate limits and quotas
# Verify model availability
```

## 📚 Additional Resources

- **LangChain Documentation**: https://python.langchain.com/
- **LangGraph Guide**: https://langchain-ai.github.io/langgraph/
- **MongoDB Atlas Vector Search**: https://www.mongodb.com/docs/atlas/atlas-vector-search/
- **Box Developer Documentation**: https://developer.box.com/
- **OpenAI API Reference**: https://platform.openai.com/docs/

## 🤝 Contributing

This is a demonstration project designed for learning. Feel free to:
- Experiment with different models and parameters
- Add new document types and processing methods
- Implement additional search strategies
- Extend the agent capabilities

## 📄 License

This project is provided as-is for educational and development purposes.