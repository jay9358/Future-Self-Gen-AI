#!/usr/bin/env python3
"""
Test script for the RAG Pipeline
Demonstrates the proper RAG functionality with vector embeddings and semantic search
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.rag_pipeline import rag_pipeline
import json

def test_rag_pipeline():
    """Test the RAG pipeline functionality"""
    print("🚀 Testing RAG Pipeline")
    print("=" * 50)
    
    # Test 1: Check pipeline stats
    print("\n1. Pipeline Statistics:")
    stats = rag_pipeline.get_stats()
    print(json.dumps(stats, indent=2))
    
    # Test 2: Test document retrieval
    print("\n2. Testing Document Retrieval:")
    test_queries = [
        "What skills do I need for software engineering?",
        "What is the salary range for data scientists?",
        "What tools do frontend developers use?",
        "How do I become a DevOps engineer?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        retrieved_docs = rag_pipeline.retrieve_relevant_documents(query, top_k=3)
        print(f"Retrieved {len(retrieved_docs)} documents:")
        for i, doc in enumerate(retrieved_docs, 1):
            print(f"  {i}. [{doc.metadata.get('type', 'unknown')}] {doc.content[:100]}...")
    
    # Test 3: Test context generation
    print("\n3. Testing Context Generation:")
    career = "software_engineer"
    question = "What programming languages should I learn?"
    
    context = rag_pipeline.get_relevant_context(career, question)
    print(f"Career: {career}")
    print(f"Question: {question}")
    print(f"Retrieved {len(context.get('retrieved_documents', []))} relevant documents")
    print(f"Question type: {context.get('question_type', 'unknown')}")
    
    # Test 4: Test enhanced prompt generation
    print("\n4. Testing Enhanced Prompt Generation:")
    enhanced_prompt = rag_pipeline.generate_enhanced_prompt(career, question, context)
    print("Generated prompt:")
    print("-" * 30)
    print(enhanced_prompt)
    print("-" * 30)
    
    # Test 5: Test cross-career search
    print("\n5. Testing Cross-Career Search:")
    cross_results = rag_pipeline.search_across_careers("machine learning", top_k=3)
    print(f"Found {len(cross_results)} results across careers:")
    for result in cross_results:
        print(f"  - {result['career_id']}: {result['content'][:80]}...")
    
    # Test 6: Test career insights
    print("\n6. Testing Career Insights:")
    insights = rag_pipeline.get_career_insights("data_scientist")
    print("Data Scientist Insights:")
    print(json.dumps(insights, indent=2))
    
    print("\n✅ RAG Pipeline test completed successfully!")

if __name__ == "__main__":
    test_rag_pipeline()
