#!/usr/bin/env python3
"""
Debug script to check URL generation and blob names
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from azure_search import AzureSearchClient

def debug_search_results():
    """Debug search results to identify URL and blob name issues"""
    
    print("🔍 Debugging URL Generation and Blob Names")
    print("=" * 50)
    
    # Check environment variables
    print("Environment Variables:")
    print(f"  DOC_BASEURL: {os.getenv('DOC_BASEURL', 'NOT SET')}")
    print(f"  DOC_SAS: {os.getenv('DOC_SAS', 'NOT SET')[:50]}..." if os.getenv('DOC_SAS') else "  DOC_SAS: NOT SET")
    print(f"  AZURE_SEARCH_ENDPOINT: {os.getenv('AZURE_SEARCH_ENDPOINT', 'NOT SET')}")
    print(f"  AZURE_SEARCH_INDEX_NAME: {os.getenv('AZURE_SEARCH_INDEX_NAME', 'NOT SET')}")
    print()
    
    # Initialize search client
    try:
        client = AzureSearchClient()
        print("✅ Azure Search client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Azure Search client: {e}")
        return
    
    # Test search query
    test_query = "乘用车国家标准"
    print(f"Testing query: '{test_query}'")
    print("-" * 30)
    
    try:
        # Perform search
        results = client._perform_hybrid_search(test_query, top_k=5)
        
        if not results:
            print("❌ No search results returned")
            return
        
        print(f"Found {len(results)} results")
        print()
        
        # Analyze each result
        for i, result in enumerate(results, 1):
            print(f"=== Result {i} ===")
            print(f"Title: {result.title}")
            print(f"Score: {result.score:.3f}")
            print(f"Source URL: {result.source}")
            
            # Parse the source URL to identify issues
            if result.source:
                if "blob.core.windows.net" in result.source:
                    print("✅ Valid blob storage URL format")
                    
                    # Extract blob name from URL
                    try:
                        # Split URL to get blob path
                        if '/docs-demo-knowledge-02-dev/' in result.source:
                            blob_part = result.source.split('/docs-demo-knowledge-02-dev/')[-1]
                            blob_name = blob_part.split('?')[0]  # Remove SAS token
                            print(f"Blob name: {blob_name}")
                            
                            # Check if blob name looks valid
                            if blob_name.endswith('.pdf'):
                                print("✅ Blob name has valid PDF extension")
                            else:
                                print("⚠️ Blob name doesn't end with .pdf")
                                
                            if len(blob_name) > 10:
                                print("✅ Blob name has reasonable length")
                            else:
                                print("⚠️ Blob name seems too short")
                                
                        else:
                            print("⚠️ URL doesn't contain expected container path")
                    except Exception as e:
                        print(f"⚠️ Error parsing blob name: {e}")
                else:
                    print("❌ Not a blob storage URL")
            else:
                print("❌ No source URL provided")
            
            # Check content preview
            content_preview = result.content[:200] if result.content else "No content"
            print(f"Content preview: {content_preview}...")
            
            # Check highlights
            if result.highlights:
                print(f"Highlights: {len(result.highlights)} found")
                for j, highlight in enumerate(result.highlights[:2], 1):
                    print(f"  Highlight {j}: {highlight[:100]}...")
            else:
                print("No highlights found")
            
            print()
        
    except Exception as e:
        print(f"❌ Error during search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_search_results()
