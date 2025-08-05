# Troubleshooting Guide

## Common Issues and Solutions

### 1. Installation Issues

#### Issue: "Cannot import 'setuptools.build_meta'"
```bash
# Solution 1: Use quick fix script
./quick_fix.sh

# Solution 2: Manual fix
rm -rf venv
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel build
pip install -r requirements.txt
```

#### Issue: pip installation fails
```bash
# Upgrade pip and build tools
python -m pip install --upgrade pip setuptools wheel

# Use --no-cache-dir parameter
pip install --no-cache-dir -r requirements.txt

# Install packages one by one
pip install streamlit python-dotenv pydantic
```

#### Issue: Python version incompatibility
```bash
# Check Python version
python3 --version

# Requires Python 3.9 or higher
# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev

# On CentOS/RHEL:
sudo yum install python39 python39-venv python39-devel
```

### 2. Runtime Issues

#### Issue: Azure service connection failed
```bash
# Check .env file configuration
cat .env

# Ensure correct environment variables are set:
# AZURE_OPENAI_API_KEY
# AZURE_OPENAI_ENDPOINT
# AZURE_SEARCH_API_KEY
# AZURE_SEARCH_SERVICE_NAME
```

#### Issue: Streamlit cannot start
```bash
# Check if port is already in use
netstat -tulpn | grep :8501

# Start with different port
streamlit run src/app.py --server.port 8502

# Check firewall settings
sudo ufw allow 8501
```

#### Issue: Module import error
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Check Python path
python -c "import sys; print(sys.path)"

# Ensure in project root directory
pwd
ls -la src/
```

### 3. Azure Configuration Issues

#### Issue: Azure OpenAI quota exceeded
```bash
# Check quota usage
az cognitiveservices account list-usage \
  --name YOUR_OPENAI_RESOURCE_NAME \
  --resource-group YOUR_RESOURCE_GROUP
```

#### Issue: Azure Search index does not exist
```bash
# List all indexes
az search index list \
  --service-name YOUR_SEARCH_SERVICE \
  --resource-group YOUR_RESOURCE_GROUP
```

#### Issue: Invalid API key
```bash
# Get Azure OpenAI key
az cognitiveservices account keys list \
  --name YOUR_OPENAI_RESOURCE_NAME \
  --resource-group YOUR_RESOURCE_GROUP

# Get Azure Search key
az search admin-key show \
  --service-name YOUR_SEARCH_SERVICE \
  --resource-group YOUR_RESOURCE_GROUP
```

### 4. Development Mode

#### Using mock data for development
```bash
# Set in .env file
USE_MOCK=true

# Or via environment variable
export USE_MOCK=true
streamlit run src/app.py
```

#### Enable debug mode
```bash
# Set in .env file
LOG_LEVEL=DEBUG

# View detailed logs
tail -f logs/app.log
```

### 5. Testing Issues

#### Run system tests
```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
python test_script/test_system.py

# Run specific test
python -m pytest test_script/test_system.py::test_config_creation -v
```

#### Test Azure connections
```bash
# Test Azure OpenAI connection
python -c "
from src.config import ConfigManager
config = ConfigManager()
print('Azure OpenAI Config:', config.azure_openai)
"

# Test Azure Search connection
python -c "
from src.azure_search import AzureSearchClient
from src.config import ConfigManager
config = ConfigManager()
client = AzureSearchClient(config.azure_search)
print('Search client created successfully')
"
```

## Quick Diagnostic Script

```bash
#!/bin/bash
# Run this script for quick diagnosis

echo "=== System Diagnosis ==="

echo "1. Python version:"
python3 --version

echo "2. Virtual environment status:"
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✓ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "✗ Virtual environment not activated"
fi

echo "3. Key package check:"
python -c "import streamlit; print('✓ Streamlit')" 2>/dev/null || echo "✗ Streamlit"
python -c "import pydantic; print('✓ Pydantic')" 2>/dev/null || echo "✗ Pydantic"
python -c "import dotenv; print('✓ Python-dotenv')" 2>/dev/null || echo "✗ Python-dotenv"

echo "4. Configuration file check:"
[ -f ".env" ] && echo "✓ .env file exists" || echo "✗ .env file not found"
[ -f "requirements.txt" ] && echo "✓ requirements.txt exists" || echo "✗ requirements.txt not found"

echo "5. Project structure check:"
[ -d "src" ] && echo "✓ src directory exists" || echo "✗ src directory not found"
[ -f "src/app.py" ] && echo "✓ app.py exists" || echo "✗ app.py not found"

echo "=== Diagnosis Complete ==="
```

## Contact Support

If the above solutions cannot resolve the issue, please collect the following information:

1. Operating system and version
2. Python version
3. Complete error stack trace
4. .env file content (hide sensitive information)
5. Output of `pip list`

### Get detailed error information
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run application and capture errors
python src/app.py 2>&1 | tee error.log
```

### Reset to initial state
```bash
# Complete project reset
./setup.sh clean
./quick_fix.sh
```
