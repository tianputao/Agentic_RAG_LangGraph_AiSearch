"""
Streamlit web application for the Agentic RAG chatbot
Provides an interactive chat interface with conversation history and example questions
"""

# Import with fallbacks
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    print("Streamlit not available. Please install: pip install streamlit")
    STREAMLIT_AVAILABLE = False
    class MockStreamlit:
        def error(self, msg): print(f"ERROR: {msg}")
        def success(self, msg): print(f"SUCCESS: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
    st = MockStreamlit()

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any
import logging

# Configure page
st.set_page_config(
    page_title="Enterprise Agentic RAG Assistant",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import agent (with fallback for missing dependencies)
try:
    from rag_agent import AgenticRAGAgent
    AGENT_AVAILABLE = True
except ImportError as e:
    st.error(f"Failed to import RAG agent: {e}")
    st.error("Please install required dependencies: pip install -r requirements.txt")
    AGENT_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .example-question {
        background-color: #f0f2f6;
        border-left: 4px solid #1e3c72;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .example-question:hover {
        background-color: #e1e5f2;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #dcf8c6;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background-color: #f1f1f1;
        margin-right: 2rem;
    }
    
    .source-card {
        background-color: #2e2e2e;
        color: #ffffff;
        border: 1px solid #555;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .source-card h4 {
        color: #ffffff;
        margin-top: 0;
    }
    
    .source-card a {
        color: #4da6ff;
        text-decoration: none;
    }
    
    .source-card a:hover {
        color: #66b3ff;
        text-decoration: underline;
    }
    
    .metadata-info {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitRAGApp:
    """Main Streamlit application class for the RAG chatbot"""
    
    def __init__(self):
        """Initialize the Streamlit app"""
        self.example_questions = [
            "乘用车国家标准的主要内容是什么？",
            "金属氢化物镍相关标准有哪些？", 
            "What are the recall criteria for defective automotive products?",
            "What are the test methods for measuring fuel consumption ?"
        ]
        
        # Initialize session state
        self._initialize_session_state()
        
        # Load environment variables
        self._load_environment()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "agent" not in st.session_state:
            st.session_state.agent = None
        
        if "conversation_id" not in st.session_state:
            st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if "show_sources" not in st.session_state:
            st.session_state.show_sources = True
        
        if "show_metadata" not in st.session_state:
            st.session_state.show_metadata = False
    
    def _load_environment(self):
        """Load and validate environment variables"""
        # Load .env file if exists
        env_file = ".env"
        if os.path.exists(env_file):
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
            except ImportError:
                # Fallback manual loading
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test_script'))
                from mock_dependencies import load_dotenv
                load_dotenv(env_file)
        
        # Check required environment variables
        required_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_KEY", 
            "AZURE_OPENAI_CHAT_DEPLOYMENT",
            "AZURE_SEARCH_ENDPOINT",
            "AZURE_SEARCH_KEY",
            "AZURE_SEARCH_INDEX_NAME"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            st.info("Please check your .env file or environment configuration.")
            return False
        
        return True
    
    def _initialize_agent(self):
        """Initialize the RAG agent with error handling"""
        if not AGENT_AVAILABLE:
            return None
        
        try:
            if st.session_state.agent is None:
                with st.spinner("Initializing AI agent..."):
                    st.session_state.agent = AgenticRAGAgent()
            return st.session_state.agent
        except Exception as e:
            st.error(f"Failed to initialize agent: {e}")
            logger.error(f"Agent initialization failed: {e}")
            return None
    
    def render_header(self):
        """Render the application header"""
        st.markdown("""
        <div class="main-header">
            <h1>🚗 Enterprise Agentic RAG Assistant</h1>
            <p>AI-powered automotive knowledge retrieval and Q&A system</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar with configuration and controls"""
        with st.sidebar:
            st.header("Configuration")
            
            # Agent status
            agent = st.session_state.agent
            if agent:
                st.success("✅ Agent Ready")
            else:
                st.error("❌ Agent Not Available")
            
            # Settings
            st.header("Settings")
            st.session_state.show_sources = st.checkbox(
                "Show Sources", 
                value=st.session_state.show_sources,
                help="Display source documents used for answers"
            )
            
            st.session_state.show_metadata = st.checkbox(
                "Show Metadata",
                value=st.session_state.show_metadata, 
                help="Display technical metadata about the response"
            )
            
            # Conversation controls
            st.header("Conversation")
            
            if st.button("🗑️ Clear Chat History"):
                st.session_state.messages = []
                if agent:
                    agent.clear_conversation_memory()
                st.success("Chat history cleared!")
                st.rerun()
            
            # Export conversation
            if st.button("📥 Export Conversation"):
                self._export_conversation()
            
            # Statistics
            st.header("Statistics")
            st.metric("Messages", len(st.session_state.messages))
            st.metric("Conversation ID", st.session_state.conversation_id)
    
    def render_example_questions(self):
        """Render example questions banner"""
        st.subheader("💡 Example Questions")
        
        # Create columns for example questions
        cols = st.columns(2)
        
        for i, question in enumerate(self.example_questions):
            col = cols[i % 2]
            with col:
                if st.button(
                    question,
                    key=f"example_{i}",
                    help="Click to use this example question",
                    use_container_width=True
                ):
                    # Add question to chat
                    self._handle_user_input(question)
    
    def render_chat_interface(self):
        """Render the main chat interface"""
        st.subheader("💬 Chat Interface")
        
        # Display conversation history
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.messages:
                self._render_message(message)
        
        # Chat input
        if prompt := st.chat_input("Ask your question about automotive products and standards..."):
            self._handle_user_input(prompt)
    
    def _render_message(self, message: Dict[str, Any]):
        """Render a single chat message"""
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Render sources if available
            if (message["role"] == "assistant" and 
                st.session_state.show_sources and 
                "sources" in message):
                self._render_sources(message["sources"])
            
            # Render metadata if available
            if (message["role"] == "assistant" and 
                st.session_state.show_metadata and 
                "metadata" in message):
                self._render_metadata(message["metadata"])
    
    def _render_sources(self, sources: List[Dict[str, Any]]):
        """Render source documents"""
        if not sources:
            return
        
        with st.expander(f"📚 Sources ({len(sources)} documents)", expanded=False):
            for i, source in enumerate(sources, 1):
                # Generate clickable link if source is a valid URL
                source_url = source.get('source', 'Unknown')
                if source_url and source_url.startswith(('http://', 'https://')):
                    source_link = f'<a href="{source_url}" target="_blank">🔗 Open Document</a>'
                else:
                    source_link = source_url
                
                # Process highlights
                highlights = source.get('highlights', [])
                if highlights and len(highlights) > 0:
                    highlights_html = ''.join([f"<li>{highlight}</li>" for highlight in highlights[:3]])  # Limit to 3 highlights
                    highlights_section = f"""
                    <p><strong>Highlights:</strong></p>
                    <ul>
                        {highlights_html}
                    </ul>"""
                else:
                    # Fallback: show content excerpt if no highlights
                    content = source.get('content', '')
                    if content and len(content) > 100:
                        excerpt = content[:200] + "..."
                        highlights_section = f"""
                        <p><strong>Content Preview:</strong></p>
                        <p style="font-style: italic; opacity: 0.8;">{excerpt}</p>"""
                    else:
                        highlights_section = f"""
                        <p><strong>Content:</strong></p>
                        <p style="font-style: italic; opacity: 0.8;">Preview not available</p>"""
                
                st.markdown(f"""
                <div class="source-card">
                    <h4>📄 Source {i}: {source.get('title', 'Unknown')}</h4>
                    <p><strong>Relevance Score:</strong> {source.get('score', 0):.3f}</p>
                    <p><strong>Source:</strong> {source_link}</p>
                    {highlights_section}
                </div>
                """, unsafe_allow_html=True)
    
    def _render_metadata(self, metadata: Dict[str, Any]):
        """Render technical metadata"""
        with st.expander("🔧 Technical Metadata", expanded=False):
            # Format metadata nicely
            formatted_metadata = {
                "Timestamp": metadata.get("timestamp", "Unknown"),
                "Planning Completed": metadata.get("planning_completed", False),
                "Retrieval Completed": metadata.get("retrieval_completed", False), 
                "Generation Completed": metadata.get("generation_completed", False),
                "Documents Retrieved": metadata.get("num_documents_retrieved", 0),
                "Planned Queries": metadata.get("num_planned_queries", 0),
                "Answer Length": metadata.get("answer_length", 0)
            }
            
            st.json(formatted_metadata)
    
    def _handle_user_input(self, user_input: str):
        """Handle user input and generate response"""
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Initialize agent if needed
        agent = self._initialize_agent()
        
        if not agent:
            # Fallback response when agent is not available
            error_response = {
                "role": "assistant",
                "content": "I apologize, but the AI agent is currently unavailable. Please check the configuration and try again.",
                "timestamp": datetime.now().isoformat(),
                "sources": [],
                "metadata": {"error": "Agent not available"}
            }
            st.session_state.messages.append(error_response)
            st.rerun()
            return
        
        # Generate response
        with st.spinner("🤔 Thinking and searching for the best answer..."):
            try:
                # Process question through agent
                response = agent.process_question(user_input)
                
                # Create assistant message
                assistant_message = {
                    "role": "assistant",
                    "content": response["answer"],
                    "timestamp": datetime.now().isoformat(),
                    "sources": response.get("sources", []),
                    "metadata": response.get("metadata", {}),
                    "planned_queries": response.get("planned_queries", []),
                    "error": response.get("error", "")
                }
                
                # Add to conversation
                st.session_state.messages.append(assistant_message)
                
                # Log successful interaction
                logger.info(f"Successfully processed question: {user_input[:50]}...")
                
            except Exception as e:
                # Handle errors gracefully
                error_message = {
                    "role": "assistant", 
                    "content": f"I encountered an error while processing your question: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                    "sources": [],
                    "metadata": {"error": str(e)}
                }
                st.session_state.messages.append(error_message)
                logger.error(f"Error processing question: {e}")
        
        # Rerun to update the interface
        st.rerun()
    
    def _export_conversation(self):
        """Export conversation to JSON file"""
        try:
            conversation_data = {
                "conversation_id": st.session_state.conversation_id,
                "timestamp": datetime.now().isoformat(),
                "messages": st.session_state.messages,
                "settings": {
                    "show_sources": st.session_state.show_sources,
                    "show_metadata": st.session_state.show_metadata
                }
            }
            
            # Convert to JSON string
            json_str = json.dumps(conversation_data, indent=2, ensure_ascii=False)
            
            # Provide download button
            st.download_button(
                label="Download Conversation",
                data=json_str,
                file_name=f"conversation_{st.session_state.conversation_id}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"Failed to export conversation: {e}")
    
    def run(self):
        """Main application entry point"""
        # Render header
        self.render_header()
        
        # Render sidebar
        self.render_sidebar()
        
        # Main content area
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Chat interface
            self.render_chat_interface()
        
        with col2:
            # Example questions
            self.render_example_questions()
            
            # Help section
            with st.expander("ℹ️ Help & Instructions"):
                st.markdown("""
                **How to use this chatbot:**
                
                1. **Ask Questions**: Type your automotive-related questions in the chat input
                2. **Use Examples**: Click on example questions to get started
                3. **View Sources**: Toggle "Show Sources" to see supporting documents
                4. **Check Metadata**: Toggle "Show Metadata" for technical details
                5. **Clear History**: Use the sidebar button to start fresh
                
                **Supported Topics:**
                - Automotive standards and regulations
                - Vehicle safety and testing procedures
                - Electric vehicle specifications
                - Product recall information
                - Technical automotive documentation
                
                **Languages Supported:**
                - English
                - Chinese (Simplified)
                """)

def main():
    """Main function to run the Streamlit application"""
    try:
        app = StreamlitRAGApp()
        app.run()
    except Exception as e:
        st.error(f"Application failed to start: {e}")
        logger.error(f"Application startup failed: {e}")

if __name__ == "__main__":
    main()
