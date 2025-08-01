"""
Agentic RAG system using LangGraph for workflow orchestration
Implements multi-step agent flow with query planning, retrieval, and answer generation
"""

import os
import logging
from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass
import json
from datetime import datetime

# LangGraph and LangChain imports with fallbacks
try:
    from langgraph.graph import StateGraph, END
    from langchain_openai import AzureChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage, AIMessage
    from langchain.memory import ConversationBufferWindowMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback imports for development/testing
    from mock_dependencies import (
        MockStateGraph as StateGraph,
        MockLLM as AzureChatOpenAI,
        MockSystemMessage as SystemMessage,
        MockHumanMessage as HumanMessage,
        MockAIMessage as AIMessage,
        MockConversationMemory as ConversationBufferWindowMemory,
        MOCK_END as END
    )
    LANGCHAIN_AVAILABLE = False

# Local imports
from azure_search import AzureSearchClient, SearchResult
from prompts import (
    PLANNING_PROMPT, 
    ANSWER_PROMPT, 
    CONVERSATION_SUMMARY_PROMPT,
    FOLLOWUP_PLANNING_PROMPT
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State schema for the LangGraph agent"""
    user_question: str
    conversation_history: str
    planned_queries: List[str]
    search_results: Dict[str, List[SearchResult]]
    aggregated_results: List[SearchResult]
    context: str
    final_answer: str
    error_message: str
    metadata: Dict[str, Any]

@dataclass
class ConversationTurn:
    """Data class for conversation management"""
    timestamp: datetime
    user_input: str
    agent_response: str
    metadata: Dict[str, Any]

class AgenticRAGAgent:
    """
    Main Agentic RAG agent orchestrating the complete workflow
    Uses LangGraph for state management and flow control
    """
    
    def __init__(self):
        """Initialize the agent with Azure services and configuration"""
        self._setup_azure_clients()
        self._setup_conversation_memory()
        self._setup_langgraph_workflow()
        
        # Configuration
        self.max_search_results = int(os.getenv("MAX_SEARCH_RESULTS", 20))
        self.enable_memory = os.getenv("ENABLE_CONVERSATION_MEMORY", "true").lower() == "true"
        
        logger.info("Agentic RAG Agent initialized successfully")
    
    def _setup_azure_clients(self):
        """Initialize Azure OpenAI and Search clients"""
        try:
            if not LANGCHAIN_AVAILABLE:
                logger.warning("LangChain not available, using mock LLM")
                self.llm = AzureChatOpenAI()
            else:
                # Azure OpenAI client
                self.llm = AzureChatOpenAI(
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                    api_key=os.getenv("AZURE_OPENAI_KEY"),
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
                    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
                    temperature=0.1,  # Low temperature for factual responses
                    max_tokens=1500,
                    timeout=30
                )
            
            # Azure Search client
            self.search_client = AzureSearchClient()
            
            logger.info("Azure clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure clients: {e}")
            # Use fallback clients
            logger.warning("Using fallback mock clients")
            self.llm = AzureChatOpenAI()
            self.search_client = AzureSearchClient()
    
    def _setup_conversation_memory(self):
        """Setup conversation memory management"""
        self.conversation_memory = ConversationBufferWindowMemory(
            k=5,  # Keep last 5 conversation turns
            return_messages=True,
            memory_key="conversation_history"
        )
        self.conversation_turns: List[ConversationTurn] = []
    
    def _setup_langgraph_workflow(self):
        """Setup LangGraph workflow with defined states and transitions"""
        # Create state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes (states)
        workflow.add_node("query_planning", self._query_planning_node)
        workflow.add_node("document_retrieval", self._document_retrieval_node)
        workflow.add_node("answer_generation", self._answer_generation_node)
        workflow.add_node("error_handling", self._error_handling_node)
        
        # Define edges (transitions)
        workflow.set_entry_point("query_planning")
        
        # Add conditional edges for error handling
        workflow.add_conditional_edges(
            "query_planning",
            self._should_continue_to_retrieval,
            {
                "continue": "document_retrieval",
                "error": "error_handling"
            }
        )
        
        workflow.add_conditional_edges(
            "document_retrieval",
            self._should_continue_to_generation,
            {
                "continue": "answer_generation",
                "error": "error_handling"
            }
        )
        
        workflow.add_edge("answer_generation", END)
        workflow.add_edge("error_handling", END)
        
        # Compile the graph
        self.workflow = workflow.compile()
        logger.info("LangGraph workflow compiled successfully")
    
    def _query_planning_node(self, state: AgentState) -> AgentState:
        """
        Node 1: Query Planning and Analysis
        Analyzes user question and generates optimized search queries
        """
        try:
            logger.info("Executing query planning node")
            
            user_question = state["user_question"]
            conversation_history = state.get("conversation_history", "")
            
            # Prepare prompt with conversation context
            planning_prompt = PLANNING_PROMPT.format(
                question=user_question,
                conversation_history=conversation_history
            )
            
            # Call LLM for query planning
            messages = [SystemMessage(content=planning_prompt)]
            response = self.llm.invoke(messages)
            
            # Parse planned queries from response
            planned_queries = self._parse_planned_queries(response.content)
            
            # Update state
            state["planned_queries"] = planned_queries
            state["metadata"]["planning_completed"] = True
            state["metadata"]["num_planned_queries"] = len(planned_queries)
            
            logger.info(f"Query planning completed: {len(planned_queries)} queries generated")
            return state
            
        except Exception as e:
            logger.error(f"Error in query planning: {e}")
            state["error_message"] = f"Query planning failed: {str(e)}"
            return state
    
    def _document_retrieval_node(self, state: AgentState) -> AgentState:
        """
        Node 2: Document Retrieval using Azure AI Search
        Executes multi-threaded hybrid search and aggregates results
        """
        try:
            logger.info("Executing document retrieval node")
            
            planned_queries = state["planned_queries"]
            
            if not planned_queries:
                logger.warning("No planned queries available for retrieval")
                state["error_message"] = "No search queries generated"
                return state
            
            # Execute multi-threaded search
            search_results = self.search_client.search_multiple_queries(
                queries=planned_queries,
                max_results_per_query=self.max_search_results // len(planned_queries)
            )
            
            # Aggregate and rank results
            aggregated_results = self.search_client.aggregate_and_rank_results(
                query_results=search_results,
                top_k=self.max_search_results
            )
            
            # Format context for LLM
            context = self.search_client.format_context_for_llm(aggregated_results)
            
            # Update state
            state["search_results"] = search_results
            state["aggregated_results"] = aggregated_results
            state["context"] = context
            state["metadata"]["retrieval_completed"] = True
            state["metadata"]["num_documents_retrieved"] = len(aggregated_results)
            
            logger.info(f"Document retrieval completed: {len(aggregated_results)} documents retrieved")
            return state
            
        except Exception as e:
            logger.error(f"Error in document retrieval: {e}")
            state["error_message"] = f"Document retrieval failed: {str(e)}"
            return state
    
    def _answer_generation_node(self, state: AgentState) -> AgentState:
        """
        Node 3: Answer Generation using retrieved context
        Synthesizes final answer using LLM and retrieved documents
        """
        try:
            logger.info("Executing answer generation node")
            
            user_question = state["user_question"]
            context = state["context"]
            conversation_history = state.get("conversation_history", "")
            
            # Prepare answer generation prompt
            answer_prompt = ANSWER_PROMPT.format(
                question=user_question,
                context=context,
                conversation_history=conversation_history
            )
            
            # Call LLM for answer generation
            messages = [SystemMessage(content=answer_prompt)]
            response = self.llm.invoke(messages)
            
            final_answer = response.content
            
            # Update state
            state["final_answer"] = final_answer
            state["metadata"]["generation_completed"] = True
            state["metadata"]["answer_length"] = len(final_answer)
            
            logger.info(f"Answer generation completed: {len(final_answer)} characters generated")
            return state
            
        except Exception as e:
            logger.error(f"Error in answer generation: {e}")
            state["error_message"] = f"Answer generation failed: {str(e)}"
            return state
    
    def _error_handling_node(self, state: AgentState) -> AgentState:
        """
        Error handling node for graceful failure management
        """
        error_message = state.get("error_message", "Unknown error occurred")
        logger.error(f"Handling error: {error_message}")
        
        # Provide fallback response
        fallback_answer = (
            "I apologize, but I encountered an issue while processing your question. "
            "Please try rephrasing your question or contact support if the problem persists."
        )
        
        state["final_answer"] = fallback_answer
        state["metadata"]["error_handled"] = True
        
        return state
    
    def _should_continue_to_retrieval(self, state: AgentState) -> str:
        """Conditional edge: Check if query planning was successful"""
        if state.get("error_message"):
            return "error"
        if not state.get("planned_queries"):
            state["error_message"] = "No queries generated during planning"
            return "error"
        return "continue"
    
    def _should_continue_to_generation(self, state: AgentState) -> str:
        """Conditional edge: Check if document retrieval was successful"""
        if state.get("error_message"):
            return "error"
        if not state.get("context"):
            state["error_message"] = "No context retrieved from documents"
            return "error"
        return "continue"
    
    def _parse_planned_queries(self, planning_response: str) -> List[str]:
        """
        Parse planned queries from LLM response
        
        Args:
            planning_response: Raw response from query planning LLM
            
        Returns:
            List of cleaned query strings
        """
        # Split by lines and clean up
        lines = planning_response.strip().split('\n')
        queries = []
        
        for line in lines:
            line = line.strip()
            # Remove numbering, bullets, and other formatting
            line = line.lstrip('0123456789.-• ')
            if line and len(line) > 3:  # Filter out very short lines
                queries.append(line)
        
        # Ensure we have at least one query
        if not queries and planning_response.strip():
            queries = [planning_response.strip()]
        
        logger.info(f"Parsed {len(queries)} queries from planning response")
        return queries
    
    def _update_conversation_memory(self, user_input: str, agent_response: str):
        """Update conversation memory with new interaction"""
        if not self.enable_memory:
            return
        
        # Add to LangChain memory
        self.conversation_memory.chat_memory.add_user_message(user_input)
        self.conversation_memory.chat_memory.add_ai_message(agent_response)
        
        # Add to conversation turns
        turn = ConversationTurn(
            timestamp=datetime.now(),
            user_input=user_input,
            agent_response=agent_response,
            metadata={}
        )
        self.conversation_turns.append(turn)
        
        # Keep only recent turns (memory management)
        if len(self.conversation_turns) > 10:
            self.conversation_turns = self.conversation_turns[-10:]
    
    def _get_conversation_context(self) -> str:
        """Get formatted conversation context for prompts"""
        if not self.enable_memory or not self.conversation_turns:
            return ""
        
        # Format recent conversation turns
        context_parts = []
        for turn in self.conversation_turns[-3:]:  # Last 3 turns
            context_parts.append(f"User: {turn.user_input}")
            context_parts.append(f"Assistant: {turn.agent_response[:200]}...")  # Truncate for brevity
        
        return "\n".join(context_parts)
    
    def process_question(self, user_question: str) -> Dict[str, Any]:
        """
        Main entry point for processing user questions
        
        Args:
            user_question: User's input question
            
        Returns:
            Dictionary containing the final answer and metadata
        """
        logger.info(f"Processing question: '{user_question[:100]}...'")
        
        try:
            # Initialize state
            initial_state: AgentState = {
                "user_question": user_question,
                "conversation_history": self._get_conversation_context(),
                "planned_queries": [],
                "search_results": {},
                "aggregated_results": [],
                "context": "",
                "final_answer": "",
                "error_message": "",
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "user_question": user_question,
                    "planning_completed": False,
                    "retrieval_completed": False,
                    "generation_completed": False,
                    "error_handled": False
                }
            }
            
            # Execute workflow
            result_state = self.workflow.invoke(initial_state)
            
            # Extract final answer and metadata
            final_answer = result_state["final_answer"]
            metadata = result_state["metadata"]
            
            # Update conversation memory
            self._update_conversation_memory(user_question, final_answer)
            
            # Prepare response
            response = {
                "answer": final_answer,
                "metadata": metadata,
                "sources": self._extract_sources(result_state.get("aggregated_results", [])),
                "planned_queries": result_state.get("planned_queries", []),
                "error": result_state.get("error_message", "")
            }
            
            logger.info("Question processing completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process question: {e}")
            return {
                "answer": "I apologize, but I encountered an unexpected error while processing your question.",
                "metadata": {"error": str(e)},
                "sources": [],
                "planned_queries": [],
                "error": str(e)
            }
    
    def _extract_sources(self, search_results: List[SearchResult]) -> List[Dict[str, Any]]:
        """Extract source information from search results"""
        sources = []
        for result in search_results[:5]:  # Top 5 sources
            source_info = {
                "title": result.title,
                "source": result.source,
                "score": result.score,
                "highlights": result.highlights[:2] if result.highlights else []
            }
            sources.append(source_info)
        
        return sources
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get formatted conversation history for UI display"""
        history = []
        for turn in self.conversation_turns:
            history.append({
                "timestamp": turn.timestamp.isoformat(),
                "user_input": turn.user_input,
                "agent_response": turn.agent_response,
                "metadata": turn.metadata
            })
        
        return history
    
    def clear_conversation_memory(self):
        """Clear conversation memory and history"""
        self.conversation_memory.clear()
        self.conversation_turns.clear()
        logger.info("Conversation memory cleared")

# Example usage and testing
def test_agentic_rag():
    """Test function for the Agentic RAG system"""
    try:
        agent = AgenticRAGAgent()
        
        # Test questions
        test_questions = [
            "What are the main contents of passenger car national standards?",
            "What is the electric vehicle range testing standard?",
            "What are the recall criteria for defective automotive products?"
        ]
        
        for question in test_questions:
            print(f"\nTesting question: {question}")
            response = agent.process_question(question)
            print(f"Answer: {response['answer'][:200]}...")
            print(f"Sources: {len(response['sources'])} documents")
            print(f"Planned queries: {response['planned_queries']}")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    # Run tests if this module is executed directly
    test_agentic_rag()
