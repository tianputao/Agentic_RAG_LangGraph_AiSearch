# Azure Agentic RAG Chatbot

An enterprise-grade Agentic RAG (Retrieval-Augmented Generation) chatbot system designed for automotive industry knowledge retrieval and Q&A, powered by Azure OpenAI GPT-4o, Azure AI Search, LangGraph, and Streamlit.

## 🚗 Features

- **Multi-step Agent Orchestration**: Uses LangGraph for sophisticated query planning, document retrieval, and answer generation
- **Hybrid Search**: Leverages Azure AI Search's semantic search + keyword search capabilities with built-in AI reranker
- **Multi-threaded Retrieval**: Concurrent search execution for complex queries with automatic result aggregation
- **Conversation Memory**: Maintains context across multiple conversation turns
- **Interactive Web Interface**: Clean Streamlit-based chat interface with source citations and metadata display

## 🏗️ Architecture

### Core Components

1. **Query Planning Node** (`rag_agent.py`)
   - Analyzes user questions using GPT-4o
   - Breaks complex questions into optimized search queries
   - Handles typo correction and query refinement

2. **Document Retrieval Node** (`azure_search.py`)
   - Multi-threaded hybrid search using Azure AI Search
   - Semantic search + keyword search combination
   - Built-in AI reranking for top 20 relevant results
   - Result deduplication and aggregation

3. **Answer Generation Node** (`rag_agent.py`)
   - Synthesizes final answers using retrieved context
   - GPT-4o powered response generation
   - Source attribution and citation

4. **Web Interface** (`app.py`)
   - Streamlit-based chat interface
   - Example questions and conversation history
   - Source document display and metadata insights

### Workflow Diagram

```
User Question → Query Planning → Document Retrieval → Answer Generation → Response
      ↓              ↓                   ↓                    ↓             ↓
   Streamlit     GPT-4o Analysis    Azure AI Search      GPT-4o Synthesis  Web UI
     UI         Query Breaking     Hybrid Search        Context Integration Display
```

## 🛠️ Installation

### 🚨 Quick Start - If You Encounter Issues

If you experience installation problems, use our quick fix script:

```bash
# For immediate issue resolution
./quick_fix.sh

# For detailed troubleshooting
cat TROUBLESHOOTING.md
```

### Prerequisites

- Python 3.9+
- Azure OpenAI service with GPT-4o and Embedding model deployment
- Azure AI Search service with configured index
- Azure subscription with appropriate permissions

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Agentic_Rag
   ```

2. **Run automated setup** (Recommended)
   ```bash
   # Full setup with error handling
   ./setup.sh


3. **Manual installation** (If automated setup fails)
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Upgrade tools
   pip install --upgrade pip setuptools wheel build
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   
   Create a `.env` file with the following variables example:
   
   ```bash
   # Azure OpenAI Configuration
   AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
   AZURE_OPENAI_KEY=your-openai-key
   AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4
   AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-ada-002
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   
   # Azure AI Search Configuration
   AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
   AZURE_SEARCH_KEY=your-search-key
   AZURE_SEARCH_INDEX_NAME=your-index-name
   AZURE_SEARCH_API_VERSION=2023-11-01
   
   # Application Configuration
   LOG_LEVEL=INFO
   MAX_SEARCH_RESULTS=20
   MAX_CONCURRENT_SEARCHES=5
   ENABLE_CONVERSATION_MEMORY=true
   

   # Citation URL
   DOC_BASEURL=
   DOC_SAS=
   ```
## 🚀 Usage

### Running the Application

1. **Start the Streamlit app**
   ```bash
   # Method 1: Using Streamlit directly
   streamlit run src/app.py
   
   # Method 2: Using the run script (recommended)
   python run.py
   ```

2. **Access the interface**
   - Open your browser to `http://localhost:8501`
   - Start asking questions using the chat interface
   - Try the example questions to get started

### Example Questions

The system comes with pre-configured example questions:

- 乘用车国家标准的主要内容是什么？ (What are the main contents of passenger car national standards?)
- 电动汽车续航测试标准? (Electric vehicle range testing standard?)
- What are the recall criteria for defective automotive products?
- How does Audi use a light sensor to activate dipped headlights?

### API Usage

You can also use the agent programmatically:

```python
from rag_agent import AgenticRAGAgent

# Initialize agent
agent = AgenticRAGAgent()

# Process a question
response = agent.process_question("What are the safety standards for electric vehicles?")

print(f"Answer: {response['answer']}")
print(f"Sources: {len(response['sources'])} documents")
print(f"Planned queries: {response['planned_queries']}")
```

## 🔧 Configuration

### Semantic Search Configuration

Ensure your Azure AI Search service has:
- Semantic search enabled
- Semantic configuration named "default"
- Appropriate field mappings for title, content, and keyword fields

## 🔒 Security Best Practices

- **Credential Management**: All Azure credentials are managed through environment variables
- **Access Control**: Use Azure RBAC for fine-grained permission control
- **Network Security**: Configure Azure services with VNet integration when possible
- **Logging**: Comprehensive logging for audit and debugging purposes
- **Error Handling**: Graceful error handling with user-friendly messages

## 🎯 Features Deep Dive

### Multi-threaded Search
- Concurrent execution of multiple search queries
- Automatic result aggregation and deduplication
- Configurable thread pool size for optimal performance

### Conversation Memory
- Maintains context across conversation turns
- Automatic conversation summarization
- Configurable memory window size

### Hybrid Search
- Combines semantic and keyword search capabilities
- Built-in AI reranking for relevance optimization
- Support for extractive answers and highlights

### Response Quality
- Source citation for transparency
- Confidence scoring for search results
- Metadata tracking for debugging and optimization


## 📊 Monitoring and Debugging

The application provides comprehensive logging and metadata:

- **Search Performance**: Query execution times and result counts
- **Agent Workflow**: Step-by-step execution tracking
- **Error Handling**: Detailed error messages and fallback responses
- **Conversation Analytics**: Turn-by-turn conversation tracking

Enable metadata display in the Streamlit interface to see:
- Query planning results
- Document retrieval statistics
- Answer generation metrics
- Source document scores

## 🔄 Extending the System

### Adding New Agent Nodes

To add new processing nodes to the LangGraph workflow:

1. Define the node function in `rag_agent.py`
2. Add the node to the workflow graph
3. Configure appropriate edges and conditions
4. Update the state schema if needed

### Custom Prompts

Modify prompts in `prompts.py` to:
- Adjust query planning strategies
- Change answer generation style
- Add domain-specific instructions
- Support additional languages

### Additional Data Sources

Extend `azure_search.py` to:
- Support multiple search indexes
- Integrate additional Azure services
- Add custom ranking algorithms
- Implement caching mechanisms

## 🚀 Deployment Options

### Local Development
```bash
streamlit run src/app.py
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Azure Container Apps
Deploy using Azure Container Apps for scalable cloud hosting with Azure integration.

### Azure App Service
Deploy as a web app with easy scaling and monitoring capabilities.


## 🆘 Support

For issues and questions:
1. Check the troubleshooting section below
2. Review the logs for error messages
3. Verify your Azure service configurations
4. Create an issue with detailed information

## 🔧 Troubleshooting

### Common Issues

**Agent initialization fails**
- Verify Azure OpenAI endpoint and key
- Check deployment names match your Azure OpenAI service
- Ensure proper API version configuration

**Search returns no results**
- Verify Azure AI Search endpoint and key
- Check index name and field mappings
- Ensure semantic search is enabled

**Streamlit interface errors**
- Check Python dependencies are installed
- Verify environment variables are loaded
- Review browser console for JavaScript errors

### Performance Optimization

**Slow response times**
- Adjust `MAX_CONCURRENT_SEARCHES` setting
- Optimize search index configuration
- Use appropriate Azure service tiers

**Memory usage**
- Configure conversation memory window size
- Implement result caching
- Monitor resource usage in production

---

Built with ❤️ for enterprise automotive knowledge management using Azure AI services.
