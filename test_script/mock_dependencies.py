"""
Simple fallback implementations for missing dependencies
This module provides basic functionality when external packages are not available
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class MockSearchResult:
    """Mock search result for testing without Azure SDK"""
    def __init__(self, content: str, title: str, score: float = 0.8):
        self.content = content
        self.title = title
        self.score = score
        self.highlights = [content[:100]]
        self.caption = content[:200]
        self.source = "mock_source"
        self.metadata = {}

class MockAzureSearchClient:
    """Mock Azure Search client for development/testing"""
    
    def __init__(self):
        logger.warning("Using mock Azure Search client - no real search functionality")
        self.mock_data = [
            MockSearchResult(
                "Passenger car national standards include safety regulations, emission standards, and performance requirements. These standards ensure vehicle safety and environmental compliance.",
                "Passenger Car National Standards Overview"
            ),
            MockSearchResult(
                "Electric vehicle range testing follows standardized procedures including WLTP (Worldwide Harmonized Light Vehicles Test Procedure) and EPA testing methods.",
                "Electric Vehicle Range Testing Standards"
            ),
            MockSearchResult(
                "Automotive product recall criteria include safety defects, non-compliance with regulations, and performance issues that could affect vehicle operation or passenger safety.",
                "Automotive Product Recall Criteria"
            ),
            MockSearchResult(
                "Audi uses ambient light sensors to automatically activate dipped headlights when lighting conditions require it, improving driver safety and visibility.",
                "Audi Light Sensor Technology"
            )
        ]
    
    def search_multiple_queries(self, queries: List[str], max_results_per_query: int = 20) -> Dict[str, List[MockSearchResult]]:
        """Mock search implementation"""
        results = {}
        for query in queries:
            # Return mock results based on query keywords
            query_results = []
            for mock_result in self.mock_data:
                if any(word.lower() in mock_result.content.lower() or word.lower() in mock_result.title.lower() 
                       for word in query.split()):
                    query_results.append(mock_result)
            
            # If no specific matches, return first few results
            if not query_results:
                query_results = self.mock_data[:2]
                
            results[query] = query_results[:max_results_per_query]
        
        return results
    
    def aggregate_and_rank_results(self, query_results: Dict[str, List[MockSearchResult]], top_k: int = 20) -> List[MockSearchResult]:
        """Mock aggregation"""
        all_results = []
        for results in query_results.values():
            all_results.extend(results)
        
        # Remove duplicates and sort by score
        unique_results = list({result.title: result for result in all_results}.values())
        return sorted(unique_results, key=lambda x: x.score, reverse=True)[:top_k]
    
    def format_context_for_llm(self, search_results: List[MockSearchResult]) -> str:
        """Format mock results for LLM"""
        if not search_results:
            return "No relevant information found in the knowledge base."
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            formatted_result = f"""
Document {i}:
Title: {result.title}
Content: {result.content}
Source: {result.source}
"""
            context_parts.append(formatted_result)
        
        return "\n" + "="*50 + "\n".join(context_parts)

class MockLLM:
    """Mock LLM for development/testing"""
    
    def __init__(self, **kwargs):
        logger.warning("Using mock LLM - no real AI functionality")
        self.config = kwargs
    
    def invoke(self, messages):
        """Mock LLM response"""
        # Extract the last message content
        if messages:
            last_message = messages[-1]
            content = getattr(last_message, 'content', str(last_message))
            
            # Generate mock response based on content
            if "search" in content.lower() or "query" in content.lower():
                # Mock query planning response
                response_content = """automotive safety standards
electric vehicle testing procedures
vehicle recall regulations"""
            else:
                # Mock answer generation response
                response_content = """Based on the provided context, I can help answer your question about automotive standards and regulations. 

The automotive industry follows comprehensive national and international standards that cover various aspects including safety, environmental compliance, and performance requirements. These standards ensure that vehicles meet specific criteria for road safety and environmental protection.

For electric vehicles specifically, testing standards like WLTP (Worldwide Harmonized Light Vehicles Test Procedure) provide standardized methods for measuring range and efficiency.

Please note: This is a mock response for development purposes. In the production system, this would be generated by Azure OpenAI GPT-4 based on your actual knowledge base."""
        
        # Create mock response object
        class MockResponse:
            def __init__(self, content):
                self.content = content
        
        return MockResponse(response_content)

class MockStateGraph:
    """Mock LangGraph StateGraph for development"""
    
    def __init__(self, state_schema):
        self.state_schema = state_schema
        self.nodes = {}
        self.edges = {}
        logger.warning("Using mock StateGraph - no real workflow functionality")
    
    def add_node(self, name: str, func):
        self.nodes[name] = func
        return self
    
    def add_edge(self, from_node: str, to_node: str):
        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append(to_node)
        return self
    
    def add_conditional_edges(self, from_node: str, condition_func, mapping: Dict[str, str]):
        # Simplified conditional edges
        self.edges[from_node] = list(mapping.values())
        return self
    
    def set_entry_point(self, node: str):
        self.entry_point = node
        return self
    
    def compile(self):
        return MockWorkflow(self.nodes, self.edges, getattr(self, 'entry_point', None))

class MockWorkflow:
    """Mock compiled workflow"""
    
    def __init__(self, nodes, edges, entry_point):
        self.nodes = nodes
        self.edges = edges
        self.entry_point = entry_point
    
    def invoke(self, initial_state):
        """Mock workflow execution"""
        state = initial_state.copy()
        
        # Simulate execution of workflow nodes
        if "query_planning" in self.nodes:
            state = self.nodes["query_planning"](state)
        
        if "document_retrieval" in self.nodes and not state.get("error_message"):
            state = self.nodes["document_retrieval"](state)
        
        if "answer_generation" in self.nodes and not state.get("error_message"):
            state = self.nodes["answer_generation"](state)
        
        return state

# Mock memory class
class MockConversationMemory:
    """Mock conversation memory"""
    
    def __init__(self, **kwargs):
        self.messages = []
        self.chat_memory = MockChatMemory()
    
    def clear(self):
        self.messages.clear()
        self.chat_memory.clear()

class MockChatMemory:
    """Mock chat memory"""
    
    def __init__(self):
        self.messages = []
    
    def add_user_message(self, message: str):
        self.messages.append({"type": "user", "content": message})
    
    def add_ai_message(self, message: str):
        self.messages.append({"type": "ai", "content": message})
    
    def clear(self):
        self.messages.clear()

# Mock message classes
class MockMessage:
    def __init__(self, content: str):
        self.content = content

class MockSystemMessage(MockMessage):
    pass

class MockHumanMessage(MockMessage):
    pass

class MockAIMessage(MockMessage):
    pass

# Constants for mock implementations
MOCK_END = "END"

def load_dotenv(path: str):
    """Simple .env file loader"""
    if not os.path.exists(path):
        return
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Export mock implementations
__all__ = [
    'MockSearchResult',
    'MockAzureSearchClient', 
    'MockLLM',
    'MockStateGraph',
    'MockWorkflow',
    'MockConversationMemory',
    'MockSystemMessage',
    'MockHumanMessage',
    'MockAIMessage',
    'MOCK_END',
    'load_dotenv'
]
