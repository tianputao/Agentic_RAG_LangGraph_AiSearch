#!/bin/bash

# Azure Agentic RAG System Setup Script
# This script helps set up the development environment and dependencies

set -e  # Exit on any error

echo "🚀 Setting up Azure Agentic RAG System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
check_python() {
    print_status "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d "." -f 1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d "." -f 2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
            print_status "Python $PYTHON_VERSION found ✓"
            
            # Warn about Python 3.12 specific considerations
            if [ "$PYTHON_MINOR" -eq 12 ]; then
                print_warning "Python 3.12 detected - using compatible package versions"
            fi
        else
            print_error "Python 3.9+ required. Found Python $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.9+"
        exit 1
    fi
}

# Create virtual environment
setup_virtual_env() {
    print_status "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created ✓"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_status "Virtual environment activated ✓"
    
    # Upgrade pip and install build tools with retry logic
    print_status "Installing build tools..."
    
    # First try to install essential build tools
    pip install --upgrade pip
    
    # Install build dependencies with specific versions for Python 3.12
    pip install setuptools>=69.0.0 wheel>=0.42.0
    
    # Try to install build tools, with fallback
    if ! pip install build>=1.0.0; then
        print_warning "Failed to install 'build' package, continuing without it"
    fi
    
    print_status "Build tools installed ✓"
}

# Install dependencies with fallback
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        # Try installing with updated requirements first
        if ! pip install -r requirements.txt; then
            print_warning "Some packages failed to install. Trying minimal installation..."
            
            # Try minimal installation
            if [ -f "requirements-minimal.txt" ]; then
                pip install -r requirements-minimal.txt
            else
                # Install core packages manually
                print_status "Installing core packages manually..."
                pip install streamlit>=1.30.0
                pip install azure-search-documents>=11.4.0
                pip install azure-identity>=1.15.0
                pip install openai>=1.12.0
                pip install python-dotenv>=1.0.0
                pip install pydantic>=2.6.0
                pip install requests>=2.31.0
                pip install "numpy>=1.26.0"
                pip install "pandas>=2.2.0"
                
                # Try to install LangChain components
                if ! pip install langchain>=0.1.0 langchain-openai>=0.0.8; then
                    print_warning "LangChain installation failed - will use mock implementation"
                fi
                
                if ! pip install langgraph>=0.0.30; then
                    print_warning "LangGraph installation failed - will use mock implementation"
                fi
            fi
        fi
        print_status "Dependencies installation completed ✓"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        # Check if .env.example exists to copy from
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_status "Created .env file from .env.example template ✓"
        else
            # Create a basic .env file with template
            cat > .env << 'EOF'
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_openai_endpoint_here
AZURE_OPENAI_KEY=your_openai_key_here
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-ada-002

# Azure AI Search Configuration  
AZURE_SEARCH_ENDPOINT=your_search_endpoint_here
AZURE_SEARCH_KEY=your_search_key_here
AZURE_SEARCH_INDEX_NAME=your_index_name_here

# Application Configuration
LOG_LEVEL=INFO
MAX_SEARCH_RESULTS=20
ENABLE_MOCK_MODE=true

# Citation URL Configuration
DOC_BASEURL=
DOC_SAS=
EOF
            print_status "Created .env file with template values ✓"
        fi
        print_warning "Please edit .env file with your Azure credentials before running the application"
    else
        print_status ".env file already exists ✓"
    fi
}

# Validate environment
validate_environment() {
    print_status "Validating environment configuration..."
    
    if [ -f ".env" ]; then
        source .env
        
        # Check required variables
        REQUIRED_VARS=(
            "AZURE_OPENAI_ENDPOINT"
            "AZURE_OPENAI_KEY" 
            "AZURE_OPENAI_CHAT_DEPLOYMENT"
            "AZURE_SEARCH_ENDPOINT"
            "AZURE_SEARCH_KEY"
            "AZURE_SEARCH_INDEX_NAME"
        )
        
        MISSING_VARS=()
        
        for var in "${REQUIRED_VARS[@]}"; do
            if [ -z "${!var}" ] || [[ "${!var}" == *"your_"* ]]; then
                MISSING_VARS+=("$var")
            fi
        done
        
        if [ ${#MISSING_VARS[@]} -eq 0 ]; then
            print_status "All required environment variables are set ✓"
        else
            print_warning "Missing or template values found for:"
            for var in "${MISSING_VARS[@]}"; do
                echo "  - $var"
            done
            print_warning "Application will run in mock mode until Azure credentials are configured"
        fi
    else
        print_error ".env file not found"
        exit 1
    fi
}

# Run tests
run_tests() {
    print_status "Running basic tests..."
    
    # Set Python path to include src directory
    export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
    
    # Test configuration loading
    python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from config import ConfigManager
    config = ConfigManager()
    print('✓ Configuration loading test passed')
except Exception as e:
    print(f'✗ Configuration test failed: {e}')
    exit(1)
"
    
    # Run comprehensive test suite if available
    if [ -f "test_script/test_system.py" ]; then
        print_status "Running comprehensive test suite..."
        cd test_script && python3 test_system.py && cd ..
    fi
    
    print_status "Basic tests completed ✓"
}

# Create necessary directories
create_directories() {
    print_status "Ensuring runtime directories exist..."
    
    # Only create directories that are needed at runtime but might be empty in git
    # These directories are typically in .gitignore or empty
    RUNTIME_DIRS=("logs" "cache" "data")
    
    for dir in "${RUNTIME_DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created $dir directory ✓"
        else
            print_status "$dir directory already exists ✓"
        fi
    done
    
    # Create subdirectories that might be needed
    mkdir -p logs/app
    mkdir -p cache/embeddings
    mkdir -p data/exports
    
    print_status "Runtime directories ready ✓"
    
    # Note: src directory should already exist from git clone/fork
    # If src doesn't exist, something is wrong with the repository
    if [ ! -d "src" ]; then
        print_error "src directory missing! Please ensure you've cloned the complete repository."
        exit 1
    fi
}

# Main setup function
main() {
    echo "================================================"
    echo "  Azure Agentic RAG System Setup"
    echo "================================================"
    echo ""
    
    # Run setup steps
    check_python
    setup_virtual_env
    install_dependencies
    setup_environment
    create_directories
    validate_environment
    run_tests
    
    echo ""
    echo "================================================"
    echo "  Setup Complete! 🎉"
    echo "================================================"
    echo ""
    print_status "Next steps:"
    echo "1. Edit the .env file with your Azure credentials"
    echo "2. Activate the virtual environment: source venv/bin/activate"
    echo "3. Run the application: python run.py"
    echo "   or: streamlit run src/app.py"
    echo ""
    print_status "For troubleshooting, run: ./diagnose.sh"
    print_status "For more information, see README.md"
}

# Handle command line arguments
case "${1:-setup}" in
    "setup")
        main
        ;;
    "install")
        source venv/bin/activate 2>/dev/null || true
        install_dependencies
        ;;
    "test")
        source venv/bin/activate 2>/dev/null || true
        run_tests
        ;;
    "validate")
        validate_environment
        ;;
    "clean")
        print_status "Cleaning up..."
        rm -rf venv
        rm -rf __pycache__
        rm -rf src/__pycache__
        rm -rf *.pyc
        rm -rf .pytest_cache
        rm -rf build
        rm -rf dist
        rm -rf *.egg-info
        find . -name "*.pyc" -delete
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        print_status "Cleanup completed ✓"
        ;;
    "fix")
        print_status "Fixing common setup issues..."
        # Clean and recreate virtual environment
        rm -rf venv
        setup_virtual_env
        install_dependencies
        print_status "Fix completed ✓"
        ;;
    "minimal")
        print_status "Installing minimal dependencies only..."
        source venv/bin/activate 2>/dev/null || true
        pip install streamlit azure-search-documents azure-identity openai python-dotenv pydantic requests
        print_status "Minimal installation completed ✓"
        ;;
    "help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  setup     - Run full setup (default)"
        echo "  install   - Install dependencies only"
        echo "  test      - Run tests only"
        echo "  validate  - Validate environment only"
        echo "  clean     - Clean up generated files"
        echo "  fix       - Fix common setup issues"
        echo "  minimal   - Install minimal dependencies"
        echo "  help      - Show this help"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac