# Simple RAG (Retrieval-Augmented Generation) System - No External Dependencies
import os
import json
import logging
import hashlib
import re
from typing import List, Dict, Any, Optional
from collections import Counter

logger = logging.getLogger(__name__)

class SimpleDocument:
    """Simple document representation with basic text processing"""
    def __init__(self, content: str, metadata: Dict[str, Any] = None):
        self.content = content
        self.metadata = metadata or {}
        self.id = hashlib.md5(content.encode()).hexdigest()[:12]
        self.words = self._extract_words(content)
        self.word_freq = Counter(self.words)
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract words from text (simple tokenization)"""
        # Convert to lowercase and extract words
        words = re.findall(r'\b\w+\b', text.lower())
        return words

class SimpleRAG:
    """Simple RAG system using TF-IDF-like scoring without external dependencies"""
    
    def __init__(self):
        self.documents: List[SimpleDocument] = []
        self.vocabulary = set()
        self.document_frequencies = {}
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None):
        """Add a document to the knowledge base"""
        try:
            # Create document
            doc = SimpleDocument(content, metadata)
            
            # Update vocabulary
            self.vocabulary.update(doc.words)
            
            # Add to collection
            self.documents.append(doc)
            
            # Update document frequencies
            self._update_document_frequencies()
            
            logger.info(f"Added document with ID: {doc.id}")
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add multiple documents at once"""
        for doc_data in documents:
            content = doc_data.get('content', '')
            metadata = doc_data.get('metadata', {})
            self.add_document(content, metadata)
    
    def _update_document_frequencies(self):
        """Update document frequencies for TF-IDF calculation"""
        self.document_frequencies = {}
        total_docs = len(self.documents)
        
        for word in self.vocabulary:
            doc_count = sum(1 for doc in self.documents if word in doc.words)
            self.document_frequencies[word] = doc_count
    
    def _calculate_tf_idf_score(self, query_words: List[str], doc: SimpleDocument) -> float:
        """Calculate TF-IDF-like score for a document given query words"""
        if not query_words:
            return 0.0
        
        score = 0.0
        total_docs = len(self.documents)
        
        for word in query_words:
            if word in doc.word_freq:
                # Term frequency in document
                tf = doc.word_freq[word] / len(doc.words)
                
                # Inverse document frequency
                doc_freq = self.document_frequencies.get(word, 1)
                idf = 1.0 + (total_docs / (1.0 + doc_freq))
                
                # TF-IDF score
                score += tf * idf
        
        return score
    
    def _calculate_simple_similarity(self, query_words: List[str], doc: SimpleDocument) -> float:
        """Calculate simple word overlap similarity"""
        if not query_words:
            return 0.0
        
        # Count matching words
        matches = sum(1 for word in query_words if word in doc.words)
        
        # Calculate similarity as ratio of matches to query length
        similarity = matches / len(query_words)
        
        # Boost score if document contains more of the query words
        word_boost = sum(doc.word_freq.get(word, 0) for word in query_words)
        similarity += word_boost * 0.1
        
        return min(similarity, 1.0)  # Cap at 1.0
    
    def search(self, query: str, top_k: int = 5, method: str = "similarity") -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        if not self.documents:
            logger.warning("No documents available")
            return []
        
        try:
            # Extract words from query
            query_words = re.findall(r'\b\w+\b', query.lower())
            
            if not query_words:
                return []
            
            # Calculate scores for each document
            results = []
            for doc in self.documents:
                if method == "tfidf":
                    score = self._calculate_tf_idf_score(query_words, doc)
                else:  # default to similarity
                    score = self._calculate_simple_similarity(query_words, doc)
                
                results.append({
                    'document': doc,
                    'score': score,
                    'content': doc.content,
                    'metadata': doc.metadata,
                    'id': doc.id,
                    'matched_words': [word for word in query_words if word in doc.words]
                })
            
            # Sort by score and return top_k
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return []
    
    def retrieve_context(self, query: str, top_k: int = 3, method: str = "similarity") -> str:
        """Retrieve relevant context as a formatted string"""
        results = self.search(query, top_k, method)
        
        if not results:
            return "No relevant documents found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"Context {i} (score: {result['score']:.3f}):")
            context_parts.append(result['content'])
            if result['matched_words']:
                context_parts.append(f"Matched words: {', '.join(result['matched_words'])}")
            context_parts.append("")  # Empty line for readability
        
        return "\n".join(context_parts)
    
    def get_document_count(self) -> int:
        """Get total number of documents"""
        return len(self.documents)
    
    def clear_documents(self):
        """Clear all documents"""
        self.documents.clear()
        self.vocabulary.clear()
        self.document_frequencies.clear()
        logger.info("All documents cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get basic statistics"""
        return {
            'total_documents': len(self.documents),
            'vocabulary_size': len(self.vocabulary),
            'average_document_length': sum(len(doc.words) for doc in self.documents) / len(self.documents) if self.documents else 0
        }

# Example usage and testing
def create_sample_rag():
    """Create a sample RAG instance with some test data"""
    rag = SimpleRAG()
    
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
        },
        {
            'content': 'Artificial intelligence and machine learning are transforming industries by automating tasks and providing intelligent insights.',
            'metadata': {'topic': 'ai', 'impact': 'industry_transformation'}
        }
    ]
    
    rag.add_documents(sample_docs)
    return rag

# Global instance for easy import
simple_rag = SimpleRAG()

if __name__ == "__main__":
    # Test the simple RAG
    print("Testing Simple RAG System...")
    
    # Create sample RAG
    rag = create_sample_rag()
    
    # Test search
    queries = [
        "What is Python programming?",
        "Tell me about machine learning",
        "How to build websites?",
        "What is data science?",
        "artificial intelligence"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        results = rag.search(query, top_k=2)
        
        for i, result in enumerate(results, 1):
            print(f"Result {i}: {result['content'][:80]}... (score: {result['score']:.3f})")
            if result['matched_words']:
                print(f"  Matched: {', '.join(result['matched_words'])}")
    
    # Test context retrieval
    print(f"\nContext for 'Python programming':")
    context = rag.retrieve_context("Python programming", top_k=2)
    print(context)
    
    # Show stats
    print(f"\nRAG Stats: {rag.get_stats()}")
