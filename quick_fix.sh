#!/bin/bash

# Quick Fix Script for Agentic RAG System
# This script addresses common setup issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

main() {
    print_status "Quick Fix for Agentic RAG System"
    print_status "================================="
    
    # Check if we're in the right directory
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found. Please run this script from the project root directory."
        exit 1
    fi
    
    # Step 1: Clean up any existing installation
    print_status "Step 1: Cleaning up existing installation..."
    rm -rf venv
    rm -rf __pycache__
    rm -rf .pytest_cache
    rm -rf build
    rm -rf dist
    rm -rf *.egg-info
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    print_success "Cleanup completed"
    
    # Step 2: Check Python version
    print_status "Step 2: Checking Python version..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.9 or later."
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    print_status "Found Python $python_version"
    
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
        print_success "Python version is compatible"
    else
        print_error "Python 3.9 or later is required. Current version: $python_version"
        exit 1
    fi
    
    # Step 3: Create virtual environment with latest tools
    print_status "Step 3: Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip and install build tools first
    print_status "Upgrading pip and installing build tools..."
    python -m pip install --upgrade pip
    python -m pip install --upgrade setuptools wheel build
    
    print_success "Virtual environment created and build tools installed"
    
    # Step 4: Install dependencies with retry
    print_status "Step 4: Installing dependencies..."
    
    # Install in order of importance
    critical_packages=(
        "streamlit>=1.28.0"
        "python-dotenv>=1.0.0"
        "pydantic>=2.0.0"
    )
    
    for package in "${critical_packages[@]}"; do
        print_status "Installing $package..."
        python -m pip install "$package" || {
            print_warning "Failed to install $package, trying with --no-deps"
            python -m pip install --no-deps "$package"
        }
    done
    
    # Install remaining packages
    print_status "Installing remaining packages from requirements.txt..."
    python -m pip install -r requirements.txt || {
        print_warning "Some packages failed to install. Installing individually..."
        while IFS= read -r line; do
            if [[ ! "$line" =~ ^[[:space:]]*# ]] && [[ -n "$line" ]]; then
                package=$(echo "$line" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1)
                print_status "Installing $package..."
                python -m pip install "$line" || print_warning "Failed to install $package"
            fi
        done < requirements.txt
    }
    
    print_success "Dependencies installation completed"
    
    # Step 5: Verify installation
    print_status "Step 5: Verifying installation..."
    
    # Test critical imports
    if python -c "import streamlit; print('Streamlit OK')" 2>/dev/null; then
        print_success "Streamlit import successful"
    else
        print_error "Streamlit import failed"
    fi
    
    if python -c "import pydantic; print('Pydantic OK')" 2>/dev/null; then
        print_success "Pydantic import successful"
    else
        print_error "Pydantic import failed"
    fi
    
    # Step 6: Create environment file if it doesn't exist
    print_status "Step 6: Setting up environment file..."
    if [ ! -f ".env" ]; then
        cat > .env << EOF
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
USE_MOCK=true
LOG_LEVEL=INFO
EOF
        print_success "Created .env file (please update with your Azure credentials)"
    else
        print_status ".env file already exists"
    fi
    
    # Step 7: Quick test
    print_status "Step 7: Running quick test..."
    export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
    if python -c "import sys; sys.path.insert(0, 'src'); from config import ConfigManager; print('Configuration OK')"; then
        print_success "Basic configuration test passed"
    else
        print_warning "Configuration test failed, but system may still work with mock data"
    fi
    
    print_success "Quick fix completed successfully!"
    print_status ""
    print_status "Next steps:"
    print_status "1. Update .env file with your Azure credentials"
    print_status "2. Run: source venv/bin/activate"
    print_status "3. Run: streamlit run src/app.py"
    print_status ""
    print_status "For troubleshooting, run: python src/test_system.py"
}

# Run main function
main "$@"
