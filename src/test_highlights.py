#!/usr/bin/env python3
"""
Test script to verify highlights extraction from Azure Search
"""

import os
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
from azure_search import AzureSearchClient

def test_highlights():
    """Test the highlights extraction functionality"""
    
    # Load environment variables
    load_dotenv('../.env')
    
    print("🔍 Testing Highlights Extraction")
    print("=" * 40)
    
    # Initialize Azure Search client
    try:
        search_client = AzureSearchClient()
        print("✅ Azure Search client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Azure Search client: {e}")
        return
    
    # Test search with different queries
    test_queries = [
        "乘用车国家标准",
        "汽车安全规定", 
        "电动汽车测试"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 30)
        
        try:
            results = search_client._perform_hybrid_search(query, top_k=2)
            print(f"Found {len(results)} results")
            
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"  Title: {result.title}")
                print(f"  Score: {result.score:.3f}")
                print(f"  Source: {result.source[:80]}...")
                print(f"  Content: {result.content[:100]}...")
                print(f"  Caption: {result.caption[:100]}..." if result.caption else "  Caption: None")
                print(f"  Highlights ({len(result.highlights)}):")
                
                if result.highlights:
                    for j, highlight in enumerate(result.highlights[:3], 1):
                        print(f"    {j}. {highlight[:100]}...")
                else:
                    print("    No highlights found")
                
        except Exception as e:
            print(f"❌ Search failed for query '{query}': {e}")
    
    print("\n✅ Highlights Test Complete!")

if __name__ == "__main__":
    test_highlights()
