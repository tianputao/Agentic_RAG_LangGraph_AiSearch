#!/usr/bin/env python3
"""
Test script to verify URL generation functionality
"""

import os
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
from azure_search import AzureSearchClient

def test_url_generation():
    """Test the URL generation functionality"""
    
    # Load environment variables
    load_dotenv('../.env')
    
    print("🔍 Testing URL Generation Functionality")
    print("=" * 50)
    
    # Check environment variables
    doc_base_url = os.getenv("DOC_BASEURL")
    doc_sas = os.getenv("DOC_SAS") 
    
    print(f"DOC_BASEURL: {doc_base_url[:50]}..." if doc_base_url else "DOC_BASEURL: Not set")
    print(f"DOC_SAS: {'Set' if doc_sas else 'Not set'}")
    print()
    
    if not doc_base_url or not doc_sas:
        print("❌ DOC_BASEURL or DOC_SAS not configured properly")
        return
    
    # Initialize Azure Search client
    try:
        search_client = AzureSearchClient()
        print("✅ Azure Search client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Azure Search client: {e}")
        return
    
    # Test URL generation with different source path formats
    test_cases = [
        "document.pdf",
        "/document.pdf", 
        "folder/document.pdf",
        "/folder/document.pdf",
        "deep/folder/structure/document.pdf"
    ]
    
    print("\n🧪 Testing URL Generation:")
    print("-" * 30)
    
    for test_path in test_cases:
        generated_url = search_client._generate_document_url(test_path)
        print(f"Input:  {test_path}")
        print(f"Output: {generated_url}")
        print()
    
    # Test actual search
    print("🔍 Testing Live Search:")
    print("-" * 20)
    
    try:
        results = search_client._perform_hybrid_search("汽车", top_k=3)
        print(f"Found {len(results)} results")
        
        for i, result in enumerate(results[:2], 1):
            print(f"\nResult {i}:")
            print(f"  Title: {result.title}")
            print(f"  Score: {result.score:.3f}")
            print(f"  Source URL: {result.source}")
            print(f"  Content: {result.content[:100]}...")
            
    except Exception as e:
        print(f"❌ Search test failed: {e}")
    
    print("\n✅ URL Generation Test Complete!")

if __name__ == "__main__":
    test_url_generation()
