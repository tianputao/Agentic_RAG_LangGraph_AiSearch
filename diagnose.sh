#!/bin/bash

# System Diagnostic Script for Agentic RAG
# This script helps identify common issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}       Agentic RAG System Diagnostics${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_section() {
    echo -e "\n${BLUE}$1${NC}"
    echo "----------------------------------------"
}

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

main() {
    print_header
    
    # System Requirements
    print_section "1. System Requirements"
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
            check_pass "Python $python_version (Compatible)"
        else
            check_fail "Python $python_version (Requires 3.9+)"
        fi
    else
        check_fail "Python 3 not found"
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
        check_pass "pip is available"
    else
        check_fail "pip not found"
    fi
    
    # Check virtual environment
    if [ -n "$VIRTUAL_ENV" ]; then
        check_pass "Virtual environment activated: $(basename $VIRTUAL_ENV)"
    else
        check_warning "Virtual environment not activated"
        echo "  Run: source venv/bin/activate"
    fi
    
    # Project Structure
    print_section "2. Project Structure"
    
    [ -f "requirements.txt" ] && check_pass "requirements.txt exists" || check_fail "requirements.txt missing"
    [ -f ".env" ] && check_pass ".env file exists" || check_warning ".env file missing (will use mock data)"
    [ -d "src" ] && check_pass "src directory exists" || check_fail "src directory missing"
    [ -f "src/app.py" ] && check_pass "app.py exists" || check_fail "app.py missing"
    [ -f "src/config.py" ] && check_pass "config.py exists" || check_fail "config.py missing"
    [ -f "src/rag_agent.py" ] && check_pass "rag_agent.py exists" || check_fail "rag_agent.py missing"
    [ -f "src/azure_search.py" ] && check_pass "azure_search.py exists" || check_fail "azure_search.py missing"
    [ -f "src/mock_dependencies.py" ] && check_pass "mock_dependencies.py exists" || check_fail "mock_dependencies.py missing"
    [ -f "src/test_system.py" ] && check_pass "test_system.py exists" || check_fail "test_system.py missing"
    
    # Python Dependencies
    print_section "3. Python Dependencies"
    
    if [ -n "$VIRTUAL_ENV" ] || command -v python &> /dev/null; then
        # Test critical imports
        python -c "import streamlit" 2>/dev/null && check_pass "Streamlit" || check_fail "Streamlit not installed"
        python -c "import pydantic" 2>/dev/null && check_pass "Pydantic" || check_fail "Pydantic not installed"
        python -c "import dotenv" 2>/dev/null && check_pass "python-dotenv" || check_fail "python-dotenv not installed"
        
        # Test optional dependencies
        python -c "import azure.ai.formrecognizer" 2>/dev/null && check_pass "Azure Form Recognizer SDK" || check_warning "Azure Form Recognizer SDK not available (will use mock)"
        python -c "import azure.search.documents" 2>/dev/null && check_pass "Azure Search SDK" || check_warning "Azure Search SDK not available (will use mock)"
        python -c "import openai" 2>/dev/null && check_pass "OpenAI SDK" || check_warning "OpenAI SDK not available (will use mock)"
        python -c "import langgraph" 2>/dev/null && check_pass "LangGraph" || check_warning "LangGraph not available (will use mock)"
    else
        check_fail "Cannot test Python dependencies - no Python environment"
    fi
    
    # Configuration
    print_section "4. Configuration"
    
    if [ -f ".env" ]; then
        if grep -q "AZURE_OPENAI_API_KEY.*your_.*key" .env; then
            check_warning "Azure OpenAI API key needs to be updated"
        elif grep -q "AZURE_OPENAI_API_KEY" .env; then
            check_pass "Azure OpenAI API key configured"
        else
            check_warning "Azure OpenAI API key not found in .env"
        fi
        
        if grep -q "AZURE_SEARCH_API_KEY.*your_.*key" .env; then
            check_warning "Azure Search API key needs to be updated"
        elif grep -q "AZURE_SEARCH_API_KEY" .env; then
            check_pass "Azure Search API key configured"
        else
            check_warning "Azure Search API key not found in .env"
        fi
        
        if grep -q "USE_MOCK=true" .env; then
            check_warning "Mock mode enabled (good for testing)"
        else
            check_pass "Production mode (Azure services required)"
        fi
    else
        check_warning "No .env file found - will use mock data"
    fi
    
    # Test Basic Functionality
    print_section "5. Basic Functionality Test"
    
    if [ -n "$VIRTUAL_ENV" ] || command -v python &> /dev/null; then
        # Add src to Python path and test imports
        export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
        
        if python -c "import sys; sys.path.insert(0, 'src'); from config import ConfigManager; ConfigManager()" 2>/dev/null; then
            check_pass "Configuration loading works"
        else
            check_fail "Configuration loading failed"
        fi
        
        if python -c "import sys; sys.path.insert(0, 'src'); from mock_dependencies import MockOpenAIClient; MockOpenAIClient()" 2>/dev/null; then
            check_pass "Mock dependencies available"
        else
            check_fail "Mock dependencies not working"
        fi
    fi
    
    # Network and Ports
    print_section "6. Network Check"
    
    if command -v netstat &> /dev/null; then
        if netstat -tuln | grep -q ":8501"; then
            check_warning "Port 8501 is in use (may conflict with Streamlit)"
        else
            check_pass "Port 8501 is available for Streamlit"
        fi
    else
        check_warning "Cannot check port availability (netstat not found)"
    fi
    
    # Recommendations
    print_section "7. Recommendations"
    
    if [ ! -f ".env" ]; then
        echo "• Create .env file with your Azure credentials"
    fi
    
    if [ ! -n "$VIRTUAL_ENV" ]; then
        echo "• Activate virtual environment: source venv/bin/activate"
    fi
    
    if ! python -c "import streamlit" 2>/dev/null; then
        echo "• Install dependencies: pip install -r requirements.txt"
    fi
    
    echo ""
    echo -e "${BLUE}Quick Fix Commands:${NC}"
    echo "• For setup issues: ./quick_fix.sh"
    echo "• For clean reinstall: ./setup.sh clean && ./setup.sh"
    echo "• For detailed help: cat TROUBLESHOOTING.md"
    echo ""
    
    print_section "8. Next Steps"
    
    if python -c "import streamlit" 2>/dev/null && [ -f "src/app.py" ]; then
        echo "Your system appears ready! Try running:"
        echo "  streamlit run src/app.py"
        echo "  OR"
        echo "  python run.py"
    else
        echo "Please address the issues above, then run:"
        echo "  ./quick_fix.sh"
        echo "  streamlit run src/app.py"
    fi
}

# Run diagnostics
main "$@"
