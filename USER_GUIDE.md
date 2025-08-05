# User Guide

## 🚀 Quick Start

### 1. Initial Installation
```bash
# Recommended: Use automated installation script
./setup.sh

# If issues occur, use quick fix
./quick_fix.sh
```

### 2. Diagnose Issues
```bash
# Run system diagnosis
./diagnose.sh

# View detailed troubleshooting guide
cat TROUBLESHOOTING.md
```

### 3. Start Application
```bash
# Activate virtual environment
source venv/bin/activate

# Start Streamlit application
streamlit run src/app.py
```

## 📚 Script Documentation

### `setup.sh` - Main Installation Script
Comprehensive automated installation and configuration script.

```bash
# Complete installation
./setup.sh

# Install dependencies only
./setup.sh install

# Run tests only
./setup.sh test

# Validate environment
./setup.sh validate

# Clean environment
./setup.sh clean

# Fix common issues
./setup.sh fix

# View help
./setup.sh help
```

### `quick_fix.sh` - Quick Fix Script
Specifically designed to solve common installation and configuration issues.

```bash
# Run quick fix
./quick_fix.sh
```

**Issues Resolved:**
- setuptools.build_meta import errors
- pip installation failures
- Virtual environment issues
- Dependency conflicts

### `diagnose.sh` - System Diagnosis Script
Detects system status and potential issues.

```bash
# Run complete diagnosis
./diagnose.sh
```

**Check Items:**
- Python version compatibility
- Project structure integrity
- Dependency installation status
- Configuration file verification
- Network port status
- Basic functionality tests

## 🔧 Configuration Guide

### Environment Variable Configuration

Create `.env` file:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Azure AI Search Configuration
AZURE_SEARCH_SERVICE_NAME=your_search_service_name_here
AZURE_SEARCH_API_KEY=your_search_api_key_here
AZURE_SEARCH_INDEX_NAME=your_index_name_here

# Application Configuration
USE_MOCK=false  # Set to true to use mock data for development
LOG_LEVEL=INFO
```

### Development Mode
Develop without Azure services:

```bash
# Set in .env
USE_MOCK=true

# Or via environment variable
export USE_MOCK=true
streamlit run src/app.py
```

## 🧪 Testing Guide

### Run System Tests
```bash
# Activate virtual environment
source venv/bin/activate

# Run complete test suite
python test_script/test_system.py

# Using pytest (if installed)
pytest test_script/test_system.py -v
```

### Test Specific Functions
```bash
# Test configuration management
python -c "import sys; sys.path.insert(0, 'src'); from config import ConfigManager; print('Config test:', ConfigManager())"

# Test Azure Search client
python -c "import sys; sys.path.insert(0, 'src'); from azure_search import AzureSearchClient; print('Search test: OK')"

# Test RAG agent
python -c "import sys; sys.path.insert(0, 'src'); from rag_agent import AgenticRAGAgent; print('Agent test: OK')"
```

## 🚀 Deployment Guide

### Local Deployment
```bash
# Run in production mode
streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0
```

### Docker Deployment
```bash
# Build image
docker build -t agentic-rag .

# Run container
docker run -p 8501:8501 --env-file .env agentic-rag
```

### Azure Deployment
Refer to `DEPLOYMENT.md` file for detailed Azure deployment guide.

## 🛠️ Common Commands

### Environment Management
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Deactivate virtual environment
deactivate

# Update dependencies
pip install --upgrade -r requirements.txt
```

### Application Management
```bash
# Start application (default port 8501)
streamlit run src/app.py

# Use custom port
streamlit run src/app.py --server.port 8080

# Allow external access
streamlit run src/app.py --server.address 0.0.0.0

# Debug mode
LOG_LEVEL=DEBUG streamlit run src/app.py
```

### Logging and Monitoring
```bash
# View application logs
tail -f logs/app.log

# Monitor system resources
htop  # or top

# Check port usage
netstat -tulpn | grep 8501
```

## 🔍 Troubleshooting Quick Reference

### Installation Issues
```bash
# setuptools errors
./quick_fix.sh

# Dependency conflicts
pip install --force-reinstall -r requirements.txt

# Permission issues
sudo chown -R $USER:$USER venv/
```

### Runtime Issues
```bash
# Module import errors
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Azure connection issues
# Check API keys and endpoints in .env file

# Port occupation
# Use different port or stop occupying process
```

### Performance Issues
```bash
# Memory usage monitoring
ps aux | grep python

# Clear cache
rm -rf __pycache__/ .pytest_cache/

# Restart application
pkill -f streamlit
streamlit run src/app.py
```

## 📞 Getting Help

1. **View Script Help**
   ```bash
   ./setup.sh help
   ./diagnose.sh  # Automatic diagnosis
   ```

2. **View Detailed Documentation**
   ```bash
   cat TROUBLESHOOTING.md  # Troubleshooting
   cat DEPLOYMENT.md       # Deployment guide
   cat PROJECT_SUMMARY.md  # Project overview
   ```

3. **Run Diagnosis**
   ```bash
   ./diagnose.sh  # System health check
   python test_script/test_system.py  # Function tests
   ```

4. **Reset Environment**
   ```bash
   ./setup.sh clean
   ./quick_fix.sh
   ```

## 💡 Best Practices

1. **Development Environment**
   - Always use virtual environment
   - Regularly run `./diagnose.sh` to check system status
   - Use `USE_MOCK=true` for local development

2. **Production Environment**
   - Ensure all Azure services are configured correctly
   - Regularly backup `.env` file
   - Monitor application logs and performance

3. **Troubleshooting**
   - First run `./diagnose.sh` to identify issues
   - Check `TROUBLESHOOTING.md` for solutions
   - Use `./quick_fix.sh` to reset environment when necessary
