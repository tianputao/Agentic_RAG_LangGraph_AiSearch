# 🚀 Deployment Guide for Azure Agentic RAG System

This guide provides comprehensive instructions for deploying the Agentic RAG chatbot system in various environments.

## 📋 Prerequisites

### Azure Services Required

1. **Azure OpenAI Service**
   - GPT-4 model deployment
   - Text embedding model deployment (optional)
   - Valid API endpoint and key

2. **Azure AI Search Service**
   - Search service with semantic search enabled
   - Configured search index with documents
   - Valid endpoint and admin key

3. **Azure Subscription**
   - Active Azure subscription
   - Appropriate permissions to access the services

### Development Environment

- Python 3.9 or higher
- Git (for version control)
- Text editor or IDE
- Terminal/Command prompt access

## 🛠️ Installation Methods

### Method 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd Agentic_Rag

# Run automated setup
./setup.sh

# Edit environment configuration
nano .env

# Run the application
./run.py
```

### Method 2: Manual Setup

```bash
# Clone and navigate
git clone <repository-url>
cd Agentic_Rag

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Run the application
python run.py
```

### Method 3: Docker Deployment

```bash
# Build Docker image
docker build -t agentic-rag .

# Run container
docker run -p 8501:8501 --env-file .env agentic-rag
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following configuration:

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
CONVERSATION_MEMORY_WINDOW=5
```

### Azure AI Search Index Requirements

Your search index should contain the following fields:

```json
{
  "fields": [
    {
      "name": "content",
      "type": "Edm.String",
      "searchable": true,
      "retrievable": true,
      "analyzer": "standard.lucene"
    },
    {
      "name": "title", 
      "type": "Edm.String",
      "searchable": true,
      "retrievable": true
    },
    {
      "name": "source",
      "type": "Edm.String",
      "retrievable": true
    },
    {
      "name": "metadata",
      "type": "Edm.String",
      "retrievable": true
    },
    {
      "name": "chunk_id",
      "type": "Edm.String",
      "key": true,
      "retrievable": true
    }
  ]
}
```

## 🌐 Deployment Options

### 1. Local Development

**Requirements:**
- Python 3.9+
- All dependencies installed

**Steps:**
```bash
source venv/bin/activate
streamlit run app.py
```

**Access:** http://localhost:8501

### 2. Azure Container Apps

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Deploy to Azure Container Apps:**
```bash
# Create resource group
az group create --name rg-agentic-rag --location eastus

# Create container app environment
az containerapp env create \
  --name aca-env-agentic-rag \
  --resource-group rg-agentic-rag \
  --location eastus

# Deploy container app
az containerapp create \
  --name aca-agentic-rag \
  --resource-group rg-agentic-rag \
  --environment aca-env-agentic-rag \
  --image your-registry/agentic-rag:latest \
  --target-port 8501 \
  --ingress 'external' \
  --env-vars \
    AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
    AZURE_OPENAI_KEY="$AZURE_OPENAI_KEY" \
    AZURE_OPENAI_CHAT_DEPLOYMENT="$AZURE_OPENAI_CHAT_DEPLOYMENT" \
    AZURE_SEARCH_ENDPOINT="$AZURE_SEARCH_ENDPOINT" \
    AZURE_SEARCH_KEY="$AZURE_SEARCH_KEY" \
    AZURE_SEARCH_INDEX_NAME="$AZURE_SEARCH_INDEX_NAME"
```

### 3. Azure App Service

**Deploy using Azure CLI:**
```bash
# Create App Service plan
az appservice plan create \
  --name asp-agentic-rag \
  --resource-group rg-agentic-rag \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group rg-agentic-rag \
  --plan asp-agentic-rag \
  --name webapp-agentic-rag \
  --runtime "PYTHON|3.9" \
  --deployment-container-image-name your-registry/agentic-rag:latest

# Configure app settings
az webapp config appsettings set \
  --resource-group rg-agentic-rag \
  --name webapp-agentic-rag \
  --settings \
    AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
    AZURE_OPENAI_KEY="$AZURE_OPENAI_KEY" \
    AZURE_OPENAI_CHAT_DEPLOYMENT="$AZURE_OPENAI_CHAT_DEPLOYMENT" \
    AZURE_SEARCH_ENDPOINT="$AZURE_SEARCH_ENDPOINT" \
    AZURE_SEARCH_KEY="$AZURE_SEARCH_KEY" \
    AZURE_SEARCH_INDEX_NAME="$AZURE_SEARCH_INDEX_NAME"
```

### 4. Azure Kubernetes Service (AKS)

**Kubernetes Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentic-rag-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agentic-rag
  template:
    metadata:
      labels:
        app: agentic-rag
    spec:
      containers:
      - name: agentic-rag
        image: your-registry/agentic-rag:latest
        ports:
        - containerPort: 8501
        env:
        - name: AZURE_OPENAI_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: azure-secrets
              key: openai-endpoint
        - name: AZURE_OPENAI_KEY
          valueFrom:
            secretKeyRef:
              name: azure-secrets
              key: openai-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: agentic-rag-service
spec:
  selector:
    app: agentic-rag
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8501
  type: LoadBalancer
```

## 🔒 Security Configuration

### 1. Azure Key Vault Integration

```python
# Example: config.py with Key Vault
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def get_secret_from_keyvault(secret_name: str) -> str:
    credential = DefaultAzureCredential()
    client = SecretClient(
        vault_url="https://your-keyvault.vault.azure.net/",
        credential=credential
    )
    return client.get_secret(secret_name).value
```

### 2. Managed Identity Configuration

```bash
# Enable managed identity for Container App
az containerapp identity assign \
  --name aca-agentic-rag \
  --resource-group rg-agentic-rag \
  --system-assigned

# Grant permissions to Azure OpenAI
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Cognitive Services OpenAI User" \
  --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP
```

### 3. Network Security

```bash
# Create virtual network
az network vnet create \
  --name vnet-agentic-rag \
  --resource-group rg-agentic-rag \
  --address-prefix 10.0.0.0/16 \
  --subnet-name subnet-apps \
  --subnet-prefix 10.0.1.0/24

# Configure private endpoints for Azure services
az network private-endpoint create \
  --name pe-openai \
  --resource-group rg-agentic-rag \
  --vnet-name vnet-agentic-rag \
  --subnet subnet-apps \
  --private-connection-resource-id $OPENAI_RESOURCE_ID \
  --group-id account \
  --connection-name openai-connection
```

## 📊 Monitoring and Logging

### Application Insights Integration

```python
# Add to your application
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging

# Configure Application Insights
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string="InstrumentationKey=your-key"
))

# Custom telemetry
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module

# Track custom metrics
response_time_measure = measure_module.MeasureFloat(
    "response_time", "Response time", "ms"
)
```

### Log Analytics Workspace

```bash
# Create Log Analytics workspace
az monitor log-analytics workspace create \
  --resource-group rg-agentic-rag \
  --workspace-name law-agentic-rag

# Enable diagnostic settings
az monitor diagnostic-settings create \
  --name diag-agentic-rag \
  --resource $CONTAINER_APP_ID \
  --workspace $WORKSPACE_ID \
  --logs '[{"category":"ContainerAppConsoleLogs","enabled":true}]' \
  --metrics '[{"category":"AllMetrics","enabled":true}]'
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

```yaml
name: Deploy Agentic RAG

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: python -m pytest test_system.py
    
    - name: Build Docker image
      run: |
        docker build -t ${{ secrets.REGISTRY }}/agentic-rag:${{ github.sha }} .
        docker push ${{ secrets.REGISTRY }}/agentic-rag:${{ github.sha }}
    
    - name: Deploy to Azure
      run: |
        az containerapp update \
          --name aca-agentic-rag \
          --resource-group rg-agentic-rag \
          --image ${{ secrets.REGISTRY }}/agentic-rag:${{ github.sha }}
```

## 🧪 Testing and Validation

### Smoke Tests

```bash
# Test endpoint health
curl -f http://your-app-url/_stcore/health

# Test basic functionality
python test_system.py

# Load testing
python -c "
from rag_agent import AgenticRAGAgent
agent = AgenticRAGAgent()
for i in range(10):
    response = agent.process_question('Test question')
    print(f'Test {i+1}: OK')
"
```

### Performance Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 100 -c 10 http://your-app-url/

# Monitor Azure metrics
az monitor metrics list \
  --resource $RESOURCE_ID \
  --metric "Requests" \
  --interval PT1M
```

## 🔧 Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Check Azure credentials
   az account show
   az ad signed-in-user show
   ```

2. **Search Index Issues**
   ```bash
   # Verify search service
   curl -H "api-key: $SEARCH_KEY" \
     "$SEARCH_ENDPOINT/indexes?api-version=2023-11-01"
   ```

3. **Container App Issues**
   ```bash
   # Check logs
   az containerapp logs show \
     --name aca-agentic-rag \
     --resource-group rg-agentic-rag
   ```

### Debug Mode

```bash
# Run with debug logging
export LOG_LEVEL=DEBUG
python run.py --cli
```

### Health Checks

```python
# Add health check endpoint
@app.route('/health')
def health_check():
    try:
        # Test Azure connections
        agent = AgenticRAGAgent()
        return {"status": "healthy"}, 200
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500
```

## 📈 Scaling Considerations

### Horizontal Scaling

```bash
# Scale Container App replicas
az containerapp update \
  --name aca-agentic-rag \
  --resource-group rg-agentic-rag \
  --min-replicas 2 \
  --max-replicas 10
```

### Performance Optimization

1. **Caching**: Implement Redis cache for frequent queries
2. **Connection Pooling**: Use connection pooling for Azure services
3. **Async Processing**: Implement async operations for concurrent requests
4. **CDN**: Use Azure CDN for static assets

### Cost Optimization

1. **Azure Reserved Instances**: Use reserved capacity for predictable workloads
2. **Auto-scaling**: Configure auto-scaling based on CPU/memory metrics
3. **Resource Tagging**: Implement proper tagging for cost tracking

## 📚 Additional Resources

- [Azure OpenAI Documentation](https://docs.microsoft.com/azure/cognitive-services/openai/)
- [Azure AI Search Documentation](https://docs.microsoft.com/azure/search/)
- [Azure Container Apps Documentation](https://docs.microsoft.com/azure/container-apps/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/)

---

For support and questions, please refer to the project README.md or create an issue in the repository.
