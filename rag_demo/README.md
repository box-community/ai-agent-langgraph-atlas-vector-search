# Box RAG System Demo

This Jupyter notebook demonstrates how to build a **Retrieval-Augmented Generation (RAG)** system that integrates Box document storage, MongoDB Atlas vector search, and OpenAI's language models to answer questions about your enterprise documents.

## Overview

The system allows you to:
- Connect to Box and upload sample financial analysis documents
- Process and chunk documents using LangChain
- Store document embeddings in MongoDB Atlas Vector Search
- Query documents using natural language and get AI-powered responses with source citations

## Architecture

```
Box Documents → LangChain Loader → Text Splitting → OpenAI Embeddings → MongoDB Atlas → RAG Chain → AI Response
```

## Prerequisites

### Required Services
- **Box Developer Account**: For document storage and API access
- **MongoDB Atlas Account**: For vector search capabilities  
- **OpenAI API Key**: For embeddings and language model

### Python Dependencies
From the roo of the project run:
```bash
uv sync
```
In the Jupyter notebook select the created `.venv` folder

## Setup Instructions

### 1. Box Configuration
1. Create a Box Developer App with **Server Authentication (CCG)**
2. Note down your `CLIENT_ID`, `CLIENT_SECRET`, and `USER_ID`
3. Ensure your app has appropriate scopes for reading/writing files

### 2. MongoDB Atlas Setup
1. Create a MongoDB Atlas cluster
2. Get your connection string
3. The system will automatically create the vector search index

### 3. Environment Variables
Create a `.env` file with:
```env
BOX_CLIENT_ID=your_box_client_id
BOX_CLIENT_SECRET=your_box_client_secret
BOX_SUBJECT_ID=your_box_user_id
OPENAI_API_KEY=your_openai_api_key
MONGODB_URI=your_mongodb_connection_string
```

## Sample Data

This project includes a set of demo files:
```
sample_data/Q4 Tech earnings-Demo/
├── Apple_analysis.docx
├── Tesla_analysis.docx
├── Microsoft_analysis.docx
├── Meta_analysis.docx
└── NVIDIA_analysis.docx
```

These are financial analysis documents that will be used to demonstrate the RAG system.

## How It Works

### Box Client Initialization
- Establishes connection to Box using CCG (Client Credentials Grant) authentication
- Verifies connection by retrieving user information

### Document Upload
- Creates a new folder in Box root directory
- Uploads all documents from the local sample data folder
- Handles duplicate files gracefully

### Document Processing
- Uses `BoxLoader` from LangChain to load documents from Box
- Splits documents into chunks (200 characters with 20 character overlap)
- Generates embeddings using OpenAI's embedding model

### Vector Store Setup
- Stores document chunks and embeddings in MongoDB Atlas
- Creates a vector search index with 1536 dimensions (OpenAI embedding size)
- Enables semantic search capabilities

### RAG Chain Creation
- Combines document retrieval with language model generation
- Uses a custom prompt template for context-aware responses
- Returns both answers and source document citations

## Usage Example

The notebook demonstrates querying the system:

```python
question = "What are the major tech companies challenges for 2026?"
answer = rag_chain.invoke(question)
```

**Sample Response:**
The system identifies challenges like China macro environment, shifting preferences for Western technology, and the transition to accelerated computing and AI, with proper source citations.

## Key Features

- **Enterprise Integration**: Seamless connection to Box for document management
- **Scalable Vector Search**: MongoDB Atlas provides production-ready vector search
- **Source Attribution**: All responses include source document references
- **Flexible Chunking**: Configurable text splitting for optimal retrieval
- **Error Handling**: Robust handling of duplicate files and API errors

## Customization Options

- **Chunk Size**: Adjust `chunk_size` and `chunk_overlap` in text splitter
- **Embedding Model**: Switch between different OpenAI embedding models
- **Language Model**: Change from GPT-4o to other OpenAI models
- **Retrieval Parameters**: Modify retriever settings for different search behaviors

## Security Considerations

- Store API keys securely in environment variables
- Use Box CCG authentication for enterprise security
- MongoDB Atlas provides built-in security features
- Consider implementing access controls for production use
- Once you extract the tokens from documents stored in Box, **Box security and permissions management do not apply**.

## Troubleshooting

### Common Issues
- **Box Authentication**: Ensure your app has proper permissions and user ID is correct
- **MongoDB Connection**: Verify connection string and network access
- **File Upload Conflicts**: The system handles duplicate files automatically
- **Embedding Limits**: Be aware of OpenAI API rate limits for large document sets

## Next Steps

To extend this system:
- Add support for more file formats (PDF, HTML, etc.)
- Implement user authentication and access controls
- Add document versioning and updates
- Create a web interface for non-technical users
- Implement advanced retrieval strategies (hybrid search, re-ranking)

## License

This demo is provided as-is for educational and development purposes.