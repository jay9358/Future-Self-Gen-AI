# Basic RAG (Retrieval-Augmented Generation) System
import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class Document:
    """Simple document representation"""
    def __init__(self, content: str, metadata: Dict[str, Any] = None):
        self.content = content
        self.metadata = metadata or {}
        self.id = hashlib.md5(content.encode()).hexdigest()[:12]
        self.embedding = None

class BasicRAG:
    """Basic RAG system with document storage and retrieval"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.documents: List[Document] = []
        self.embedding_model = None
        
        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None):
        """Add a document to the knowledge base"""
        try:
            # Create document
            doc = Document(content, metadata)
            
            # Generate embedding
            if self.embedding_model:
                doc.embedding = self.embedding_model.encode([content])[0]
            
            # Add to collection
            self.documents.append(doc)
            logger.info(f"Added document with ID: {doc.id}")
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add multiple documents at once"""
        for doc_data in documents:
            content = doc_data.get('content', '')
            metadata = doc_data.get('metadata', {})
            self.add_document(content, metadata)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents using semantic similarity"""
        if not self.documents or not self.embedding_model:
            logger.warning("No documents or embedding model available")
            return []
        
        try:
            # Get query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Calculate similarities
            similarities = []
            for doc in self.documents:
                if doc.embedding is not None:
                    similarity = cosine_similarity(
                        query_embedding.reshape(1, -1),
                        doc.embedding.reshape(1, -1)
                    )[0][0]
                    
                    similarities.append({
                        'document': doc,
                        'similarity': float(similarity),
                        'content': doc.content,
                        'metadata': doc.metadata,
                        'id': doc.id
                    })
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return []
    
    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve relevant context as a formatted string"""
        results = self.search(query, top_k)
        
        if not results:
            return "No relevant documents found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"Context {i} (similarity: {result['similarity']:.3f}):")
            context_parts.append(result['content'])
            context_parts.append("")  # Empty line for readability
        
        return "\n".join(context_parts)
    
    def get_document_count(self) -> int:
        """Get total number of documents"""
        return len(self.documents)
    
    def clear_documents(self):
        """Clear all documents"""
        self.documents.clear()
        logger.info("All documents cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get basic statistics"""
        return {
            'total_documents': len(self.documents),
            'embedding_model_loaded': self.embedding_model is not None,
            'model_name': getattr(self.embedding_model, 'model_name', 'unknown') if self.embedding_model else None
        }

# Example usage and testing
def create_sample_rag():
    """Create a sample RAG instance with some test data"""
    rag = BasicRAG()
    
    # Add some sample documents
    sample_docs = [
        {
            'content': 'Python is a high-level programming language known for its simplicity and readability. It is widely used in web development, data science, and artificial intelligence.',
            'metadata': {'topic': 'programming', 'language': 'python'}
        },
        {
            'content': 'Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.',
            'metadata': {'topic': 'ai', 'field': 'machine_learning'}
        },
        {
            'content': 'Web development involves creating websites and web applications using technologies like HTML, CSS, JavaScript, and various frameworks.',
            'metadata': {'topic': 'web_dev', 'technologies': ['HTML', 'CSS', 'JavaScript']}
        },
        {
            'content': 'Data science combines statistics, programming, and domain expertise to extract insights from data and solve complex problems.',
            'metadata': {'topic': 'data_science', 'skills': ['statistics', 'programming', 'analysis']}
        }
    ]
    
    rag.add_documents(sample_docs)
    return rag

# Global instance for easy import
basic_rag = BasicRAG()

if __name__ == "__main__":
    # Test the basic RAG
    print("Testing Basic RAG System...")
    
    # Create sample RAG
    rag = create_sample_rag()
    
    # Test search
    queries = [
        "What is Python programming?",
        "Tell me about machine learning",
        "How to build websites?",
        "What is data science?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        results = rag.search(query, top_k=2)
        
        for i, result in enumerate(results, 1):
            print(f"Result {i}: {result['content'][:100]}... (similarity: {result['similarity']:.3f})")
    
    # Test context retrieval
    print(f"\nContext for 'Python programming':")
    context = rag.retrieve_context("Python programming", top_k=2)
    print(context)
    
    # Show stats
    print(f"\nRAG Stats: {rag.get_stats()}")
