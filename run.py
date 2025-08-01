#!/usr/bin/env python3
"""
Simple runner script for the Agentic RAG system
Allows running the system with or without full dependencies
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check which dependencies are available"""
    deps = {
        'streamlit': False,
        'azure-search': False,
        'langchain': False,
        'python-dotenv': False
    }
    
    try:
        import streamlit
        deps['streamlit'] = True
    except ImportError:
        pass
    
    try:
        import azure.search.documents
        deps['azure-search'] = True
    except ImportError:
        pass
    
    try:
        import langchain
        deps['langchain'] = True
    except ImportError:
        pass
    
    try:
        import dotenv
        deps['python-dotenv'] = True
    except ImportError:
        pass
    
    return deps

def install_dependencies():
    """Install missing dependencies"""
    logger.info("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False

def run_streamlit():
    """Run the Streamlit application"""
    try:
        # Add src directory to Python path
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        logger.info("Starting Streamlit application...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            os.path.join('src', 'app.py'), 
            "--server.headless", "true"
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Streamlit: {e}")
        return False
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        return True
    return True

def run_cli_demo():
    """Run a simple CLI demo without Streamlit"""
    logger.info("Running CLI demo (Streamlit not available)")
    
    try:
        # Add src directory to Python path
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
            
        from rag_agent import AgenticRAGAgent
        
        # Initialize agent
        agent = AgenticRAGAgent()
        
        print("\n🚗 Agentic RAG CLI Demo")
        print("=" * 40)
        print("Ask questions about automotive standards and regulations")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                question = input("Question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not question:
                    continue
                
                print("\n🤔 Processing question...")
                response = agent.process_question(question)
                
                print(f"\n✅ Answer:")
                print(response['answer'])
                
                if response.get('sources'):
                    print(f"\n📚 Sources ({len(response['sources'])} documents):")
                    for i, source in enumerate(response['sources'][:3], 1):
                        print(f"  {i}. {source.get('title', 'Unknown')}")
                
                print("\n" + "-" * 40 + "\n")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("Goodbye! 👋")
        
    except Exception as e:
        logger.error(f"Failed to run CLI demo: {e}")
        return False

def main():
    """Main entry point"""
    print("🚀 Agentic RAG System Launcher")
    print("=" * 40)
    
    # Check environment
    if not os.path.exists('.env'):
        logger.warning("No .env file found. Using .env.example...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("Created .env file from .env.example")
            print("Please edit .env with your Azure credentials")
    
    # Check dependencies
    deps = check_dependencies()
    missing_deps = [name for name, available in deps.items() if not available]
    
    if missing_deps:
        print(f"\nMissing dependencies: {', '.join(missing_deps)}")
        
        if '--install' in sys.argv or '--auto' in sys.argv:
            if install_dependencies():
                deps = check_dependencies()
                missing_deps = [name for name, available in deps.items() if not available]
        else:
            print("Run with --install to automatically install dependencies")
            print("Or install manually: pip install -r requirements.txt")
    
    # Determine run mode
    if '--cli' in sys.argv or not deps['streamlit']:
        if not deps['streamlit']:
            print("\nStreamlit not available, running CLI demo...")
        run_cli_demo()
    else:
        print("\nStarting Streamlit web application...")
        run_streamlit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)
