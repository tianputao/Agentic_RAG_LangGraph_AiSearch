"""
Azure AI Search integration module for the Agentic RAG system
Handles all interactions with Azure Cognitive Search including:
- Hybrid search (semantic + keyword)
- Multi-threaded query execution
- Result ranking and formatting
"""

import os
import asyncio
import concurrent.futures
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass
# Azure SDK imports with fallbacks
try:
    from azure.search.documents import SearchClient
    from azure.search.documents.models import (
        VectorizedQuery,
        QueryType,
        QueryCaptionType,
        QueryAnswerType
    )
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import AzureError
    AZURE_SDK_AVAILABLE = True
except ImportError:
    # Mock imports for development without Azure dependencies
    from mock_dependencies import MockAzureSearchClient
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Data class for search results"""
    content: str
    title: str
    score: float
    highlights: List[str]
    caption: str
    source: str
    metadata: Dict[str, Any]

class AzureSearchClient:
    """
    Azure AI Search client with hybrid search capabilities
    Supports semantic search, keyword search, and multi-threaded operations
    """
    
    def __init__(self):
        """Initialize Azure Search client with environment variables"""
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.key = os.getenv("AZURE_SEARCH_KEY")
        self.index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        self.api_version = os.getenv("AZURE_SEARCH_API_VERSION", "2023-11-01")
        
        # Document URL configuration for generating clickable links
        self.doc_base_url = os.getenv("DOC_BASEURL")
        self.doc_sas_token = os.getenv("DOC_SAS")
        
        if not AZURE_SDK_AVAILABLE:
            logger.warning("Azure SDK not available, using mock search client")
            self.search_client = MockAzureSearchClient()
            return
        
        if not all([self.endpoint, self.key, self.index_name]):
            raise ValueError("Missing required Azure Search configuration. Check environment variables.")
        
        # Initialize search client
        try:
            credential = AzureKeyCredential(self.key)
            self.search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.index_name,
                credential=credential
            )
            logger.info(f"Azure Search client initialized for index: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Search client: {e}")
            # Fallback to mock client
            logger.warning("Falling back to mock search client")
            self.search_client = MockAzureSearchClient()
    
    def _generate_document_url(self, source_path: str) -> str:
        """
        Generate a complete URL for accessing a document in Azure Blob Storage
        
        Args:
            source_path: The source path/filename from the search result
            
        Returns:
            Complete URL with SAS token for document access
        """
        if not self.doc_base_url or not source_path:
            return source_path or ""
        
        # Clean source path - remove any leading slashes or blob container paths
        clean_path = source_path.strip('/')
        
        # If the source path already contains the base URL, return as is with SAS
        if clean_path.startswith(('http://', 'https://')):
            if self.doc_sas_token and '?' not in clean_path:
                return f"{clean_path}?{self.doc_sas_token}"
            return clean_path
        
        # Construct full URL
        base_url = self.doc_base_url.rstrip('/')
        full_url = f"{base_url}/{clean_path}"
        
        # Add SAS token if available
        if self.doc_sas_token:
            full_url = f"{full_url}?{self.doc_sas_token}"
        
        return full_url
    
    def _perform_hybrid_search(self, query: str, top_k: int = 20) -> List[SearchResult]:
        """
        Perform hybrid search combining semantic and keyword search
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            
        Returns:
            List of SearchResult objects
        """
        try:
            logger.info(f"Executing hybrid search for query: '{query[:50]}...'")
            
            # Configure hybrid search parameters
            search_params = {
                'search_text': query,
                'top': top_k,
                'query_type': QueryType.SEMANTIC,
                'semantic_configuration_name': 'default',  # Adjust based on your index configuration
                'query_caption': QueryCaptionType.EXTRACTIVE,
                'query_answer': QueryAnswerType.EXTRACTIVE,
                'include_total_count': True,
                'highlight_fields': 'content',
                'select': ['id','content','title', 'filepath', 'url', 'image_mapping', 'metadata', 'document_schema', 'publisher', 'document_code', 'document_category', 'doc_metadata', 'full_headers', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']  # Adjust field names based on your index
            }
            
            # Execute search
            start_time = time.time()
            results = self.search_client.search(**search_params)
            search_time = time.time() - start_time
            
            # Process results
            search_results = []
            for result in results:
                # Extract highlights with multiple field support
                highlights = []
                if hasattr(result, '@search.highlights') and result.get('@search.highlights'):
                    highlight_data = result['@search.highlights']
                    # Try multiple possible highlight fields
                    for field_name in ['content', 'title', 'text', 'body']:
                        if field_name in highlight_data and highlight_data[field_name]:
                            if isinstance(highlight_data[field_name], list):
                                highlights.extend(highlight_data[field_name])
                            else:
                                highlights.append(str(highlight_data[field_name]))
                
                # If no highlights found, try to create excerpt from content
                if not highlights and result.get('content'):
                    content = result.get('content', '')
                    # Create a simple excerpt as fallback
                    if len(content) > 100:
                        highlights.append(content[:100] + "...")
                
                # Extract caption with better handling
                caption = ""
                if hasattr(result, '@search.captions') and result.get('@search.captions'):
                    captions = result['@search.captions']
                    if captions and len(captions) > 0:
                        if hasattr(captions[0], 'text'):
                            caption = captions[0].text
                        elif isinstance(captions[0], dict) and 'text' in captions[0]:
                            caption = captions[0]['text']
                        else:
                            caption = str(captions[0])
                
                # Extract source path and generate complete URL
                source_path = result.get('filepath', '') or result.get('url', '') or result.get('source', '')
                complete_url = self._generate_document_url(source_path)
                
                # Create SearchResult object
                search_result = SearchResult(
                    content=result.get('content', ''),
                    title=result.get('title', ''),
                    score=result.get('@search.score', 0.0),
                    highlights=highlights,
                    caption=caption,
                    source=complete_url,  # Use the generated complete URL
                    metadata=result.get('metadata', {})
                )
                search_results.append(search_result)
            
            logger.info(f"Search completed in {search_time:.2f}s, found {len(search_results)} results")
            return search_results
            
        except AzureError as e:
            logger.error(f"Azure Search error for query '{query}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during search for query '{query}': {e}")
            return []
    
    def search_multiple_queries(self, queries: List[str], max_results_per_query: int = 20) -> Dict[str, List[SearchResult]]:
        """
        Execute multiple search queries concurrently using thread pool
        
        Args:
            queries: List of search query strings
            max_results_per_query: Maximum results per individual query
            
        Returns:
            Dictionary mapping queries to their search results
        """
        if not queries:
            logger.warning("No queries provided for search")
            return {}
        
        logger.info(f"Starting concurrent search for {len(queries)} queries")
        
        # Use ThreadPoolExecutor for concurrent search execution
        max_workers = min(len(queries), int(os.getenv("MAX_CONCURRENT_SEARCHES", 5)))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all search tasks
            future_to_query = {
                executor.submit(self._perform_hybrid_search, query, max_results_per_query): query 
                for query in queries
            }
            
            # Collect results
            results = {}
            for future in concurrent.futures.as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    search_results = future.result()
                    results[query] = search_results
                    logger.info(f"Completed search for query: '{query[:50]}...' - {len(search_results)} results")
                except Exception as e:
                    logger.error(f"Search failed for query '{query}': {e}")
                    results[query] = []
        
        return results
    
    def aggregate_and_rank_results(self, query_results: Dict[str, List[SearchResult]], 
                                 top_k: int = 20) -> List[SearchResult]:
        """
        Aggregate results from multiple queries and rank them
        
        Args:
            query_results: Dictionary of query results
            top_k: Number of top results to return after aggregation
            
        Returns:
            Ranked list of unique SearchResult objects
        """
        if not query_results:
            return []
        
        # Flatten all results
        all_results = []
        for query, results in query_results.items():
            for result in results:
                all_results.append(result)
        
        if not all_results:
            logger.warning("No search results found across all queries")
            return []
        
        # Remove duplicates based on content similarity
        unique_results = self._deduplicate_results(all_results)
        
        # Sort by search score (descending)
        ranked_results = sorted(unique_results, key=lambda x: x.score, reverse=True)
        
        # Return top K results
        final_results = ranked_results[:top_k]
        logger.info(f"Aggregated {len(all_results)} results into {len(final_results)} unique top results")
        
        return final_results
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Remove duplicate results based on content similarity
        
        Args:
            results: List of SearchResult objects
            
        Returns:
            List of unique SearchResult objects
        """
        if not results:
            return []
        
        unique_results = []
        seen_content = set()
        
        for result in results:
            # Create a simplified content hash for deduplication
            content_hash = hash(result.content[:500])  # Use first 500 chars for comparison
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_results.append(result)
        
        logger.info(f"Deduplicated {len(results)} results to {len(unique_results)} unique results")
        return unique_results
    
    def format_context_for_llm(self, search_results: List[SearchResult]) -> str:
        """
        Format search results into context string for LLM consumption
        
        Args:
            search_results: List of SearchResult objects
            
        Returns:
            Formatted context string
        """
        if not search_results:
            return "No relevant information found in the knowledge base."
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            # Format each result with title, content, and source
            formatted_result = f"""
Document {i}:
Title: {result.title}
Content: {result.content}
Source: {result.source}
"""
            # Add highlights if available
            if result.highlights:
                formatted_result += f"Key highlights: {' | '.join(result.highlights[:3])}\n"
            
            # Add caption if available
            if result.caption:
                formatted_result += f"Summary: {result.caption}\n"
            
            context_parts.append(formatted_result)
        
        formatted_context = "\n" + "="*50 + "\n".join(context_parts)
        
        logger.info(f"Formatted {len(search_results)} search results into context ({len(formatted_context)} characters)")
        return formatted_context
    
    async def async_search_multiple_queries(self, queries: List[str], 
                                          max_results_per_query: int = 20) -> Dict[str, List[SearchResult]]:
        """
        Asynchronous version of multiple query search (for future use)
        
        Args:
            queries: List of search query strings
            max_results_per_query: Maximum results per individual query
            
        Returns:
            Dictionary mapping queries to their search results
        """
        # Note: Azure Search Python SDK doesn't have native async support
        # This method uses asyncio with thread pool for concurrent execution
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            tasks = [
                loop.run_in_executor(executor, self._perform_hybrid_search, query, max_results_per_query)
                for query in queries
            ]
            
            results = await asyncio.gather(*tasks)
            
        # Combine results with queries
        return dict(zip(queries, results))

# Example usage and testing functions
def test_azure_search():
    """Test function for Azure Search integration"""
    try:
        client = AzureSearchClient()
        
        # Test single query
        test_query = "electric vehicle battery standards"
        results = client._perform_hybrid_search(test_query, top_k=5)
        print(f"Single query test: Found {len(results)} results")
        
        # Test multiple queries
        test_queries = [
            "automotive safety standards",
            "vehicle recall procedures",
            "headlight sensor technology"
        ]
        multi_results = client.search_multiple_queries(test_queries, max_results_per_query=10)
        print(f"Multi-query test: {len(multi_results)} queries processed")
        
        # Test aggregation
        aggregated = client.aggregate_and_rank_results(multi_results, top_k=15)
        print(f"Aggregation test: {len(aggregated)} final results")
        
        # Test context formatting
        context = client.format_context_for_llm(aggregated[:5])
        print(f"Context formatting test: {len(context)} characters generated")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    # Run tests if this module is executed directly
    test_azure_search()
