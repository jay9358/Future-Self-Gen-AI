# RAG Pipeline for Enhanced Context and Faster Responses
import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import hashlib
import time
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

logger = logging.getLogger(__name__)

class DocumentChunk:
    """Represents a chunk of document with metadata"""
    def __init__(self, content: str, metadata: Dict[str, Any], chunk_id: str = None):
        self.content = content
        self.metadata = metadata
        self.chunk_id = chunk_id or hashlib.md5(content.encode()).hexdigest()[:12]
        self.embedding = None
        self.tfidf_vector = None

class RAGPipeline:
    """Retrieval-Augmented Generation pipeline with vector embeddings and semantic search"""
    
    def __init__(self, model_name: str = "paraphrase-albert-small-v2"):
        self.knowledge_base = {}
        self.document_chunks: List[DocumentChunk] = []
        self.embeddings_cache = {}
        self.context_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
        
        # Initialize TF-IDF vectorizer for hybrid search
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.tfidf_matrix = None
        
    def load_knowledge_base(self):
        """Load and index career-specific knowledge base"""
        try:
            # Load career database as knowledge base
            from model.career_database import career_database      
            
            # Process career data into document chunks
            for career_id, info in career_database.get_all_careers().items():
                self.knowledge_base[career_id] = info
                
                # Create document chunks for each career
                self._create_career_chunks(career_id, info)
            
            # Build embeddings and TF-IDF index
            self._build_indexes()
            
            logger.info(f"Loaded knowledge base for {len(self.knowledge_base)} careers with {len(self.document_chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
    
    def _create_career_chunks(self, career_id: str, career_info: Dict[str, Any]):
        """Create document chunks from career information"""
        chunks = []
        
        # Basic career info chunk
        basic_info = f"""
        Career: {career_info.get('title', career_id)}
        Description: {career_info.get('description', '')}
        Category: {career_info.get('category', '')}
        """
        chunks.append(DocumentChunk(
            content=basic_info.strip(),
            metadata={'type': 'basic_info', 'career_id': career_id, 'section': 'overview'}
        ))
        
        # Skills chunk
        if career_info.get('required_skills'):
            skills_text = f"Required skills for {career_info.get('title', career_id)}: {', '.join(career_info['required_skills'])}"
            chunks.append(DocumentChunk(
                content=skills_text,
                metadata={'type': 'skills', 'career_id': career_id, 'section': 'requirements'}
            ))
        
        # Preferred skills chunk
        if career_info.get('preferred_skills'):
            pref_skills_text = f"Preferred skills for {career_info.get('title', career_id)}: {', '.join(career_info['preferred_skills'])}"
            chunks.append(DocumentChunk(
                content=pref_skills_text,
                metadata={'type': 'preferred_skills', 'career_id': career_id, 'section': 'requirements'}
            ))
        
        # Salary information chunk
        if career_info.get('salary_range'):
            salary_text = f"Salary ranges for {career_info.get('title', career_id)}: "
            for level, salary in career_info['salary_range'].items():
                salary_text += f"{level} level: {salary}, "
            chunks.append(DocumentChunk(
                content=salary_text.rstrip(', '),
                metadata={'type': 'salary', 'career_id': career_id, 'section': 'compensation'}
            ))
        
        # Career progression chunk
        if career_info.get('growth_path'):
            progression_text = f"Career progression for {career_info.get('title', career_id)}: {' -> '.join(career_info['growth_path'])}"
            chunks.append(DocumentChunk(
                content=progression_text,
                metadata={'type': 'progression', 'career_id': career_id, 'section': 'growth'}
            ))
        
        # Tools and technologies chunk
        if career_info.get('tools'):
            tools_text = f"Tools and technologies for {career_info.get('title', career_id)}: {', '.join(career_info['tools'])}"
            chunks.append(DocumentChunk(
                content=tools_text,
                metadata={'type': 'tools', 'career_id': career_id, 'section': 'technology'}
            ))
        
        # Programming languages chunk
        if career_info.get('languages'):
            langs_text = f"Programming languages for {career_info.get('title', career_id)}: {', '.join(career_info['languages'])}"
            chunks.append(DocumentChunk(
                content=langs_text,
                metadata={'type': 'languages', 'career_id': career_id, 'section': 'technology'}
            ))
        
        self.document_chunks.extend(chunks)
    
    def _build_indexes(self):
        """Build embedding and TF-IDF indexes"""
        if not self.document_chunks:
            logger.warning("No document chunks to index")
            return
        
        try:
            # Build embeddings
            if self.embedding_model:
                texts = [chunk.content for chunk in self.document_chunks]
                embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
                
                for i, chunk in enumerate(self.document_chunks):
                    chunk.embedding = embeddings[i]
                
                logger.info(f"Built embeddings for {len(self.document_chunks)} chunks")
            
            # Build TF-IDF index
            texts = [chunk.content for chunk in self.document_chunks]
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            
            # Store TF-IDF vectors in chunks
            for i, chunk in enumerate(self.document_chunks):
                chunk.tfidf_vector = self.tfidf_matrix[i]
            
            logger.info(f"Built TF-IDF index for {len(self.document_chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error building indexes: {e}")
    
    def retrieve_relevant_documents(self, query: str, career: str = None, top_k: int = 5) -> List[DocumentChunk]:
        """Retrieve relevant document chunks using hybrid search"""
        if not self.document_chunks:
            logger.warning("No document chunks available for retrieval")
            return []
        
        try:
            # Filter chunks by career if specified
            candidate_chunks = self.document_chunks
            if career:
                candidate_chunks = [chunk for chunk in self.document_chunks 
                                 if chunk.metadata.get('career_id') == career]
            
            if not candidate_chunks:
                candidate_chunks = self.document_chunks
            
            # Hybrid search: combine semantic and keyword search
            semantic_scores = self._semantic_search(query, candidate_chunks)
            keyword_scores = self._keyword_search(query, candidate_chunks)
            
            # Combine scores (weighted average)
            combined_scores = {}
            for chunk in candidate_chunks:
                semantic_score = semantic_scores.get(chunk.chunk_id, 0)
                keyword_score = keyword_scores.get(chunk.chunk_id, 0)
                combined_scores[chunk.chunk_id] = 0.7 * semantic_score + 0.3 * keyword_score
            
            # Sort by combined score and return top_k
            sorted_chunks = sorted(candidate_chunks, 
                                 key=lambda x: combined_scores.get(x.chunk_id, 0), 
                                 reverse=True)
            
            return sorted_chunks[:top_k]
            
        except Exception as e:
            logger.error(f"Error in document retrieval: {e}")
            return []
    
    def _semantic_search(self, query: str, chunks: List[DocumentChunk]) -> Dict[str, float]:
        """Perform semantic search using embeddings"""
        if not self.embedding_model or not chunks:
            return {}
        
        try:
            # Get query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Calculate similarities
            similarities = {}
            for chunk in chunks:
                if chunk.embedding is not None:
                    similarity = cosine_similarity(
                        query_embedding.reshape(1, -1),
                        chunk.embedding.reshape(1, -1)
                    )[0][0]
                    similarities[chunk.chunk_id] = float(similarity)
            
            return similarities
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return {}
    
    def _keyword_search(self, query: str, chunks: List[DocumentChunk]) -> Dict[str, float]:
        """Perform keyword search using TF-IDF"""
        if not self.tfidf_vectorizer or not chunks:
            return {}
        
        try:
            # Transform query to TF-IDF vector
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calculate similarities
            similarities = {}
            for chunk in chunks:
                if chunk.tfidf_vector is not None:
                    similarity = cosine_similarity(
                        query_vector,
                        chunk.tfidf_vector
                    )[0][0]
                    similarities[chunk.chunk_id] = float(similarity)
            
            return similarities
            
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            return {}
    
    def get_relevant_context(self, career: str, question: str, session_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get relevant context using RAG retrieval"""
        cache_key = f"{career}_{hash(question)}"
        
        # Check cache first
        if cache_key in self.context_cache:
            cached_data = self.context_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['context']
        
        # Retrieve relevant documents using RAG
        retrieved_chunks = self.retrieve_relevant_documents(question, career, top_k=5)
        
        # Get career-specific knowledge
        career_info = self.knowledge_base.get(career, {})
        
        # Analyze question type and extract relevant information
        question_type = self._analyze_question_type(question)
        
        # Build context from retrieved documents
        retrieved_context = []
        for chunk in retrieved_chunks:
            retrieved_context.append({
                'content': chunk.content,
                'type': chunk.metadata.get('type', 'unknown'),
                'section': chunk.metadata.get('section', 'unknown'),
                'career_id': chunk.metadata.get('career_id', 'unknown')
            })
        
        context = {
            'career_info': career_info,
            'question_type': question_type,
            'retrieved_documents': retrieved_context,
            'relevant_skills': self._extract_relevant_skills(question, career_info),
            'career_stage': self._determine_career_stage(question, session_context),
            'topics': self._extract_topics(question),
            'session_history': session_context.get('messages', [])[-3:] if session_context else []
        }
        
        # Cache the context
        self.context_cache[cache_key] = {
            'context': context,
            'timestamp': time.time()
        }
        
        return context
    
    def _analyze_question_type(self, question: str) -> str:
        """Analyze the type of question being asked"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['salary', 'money', 'pay', 'income', 'earn']):
            return 'salary'
        elif any(word in question_lower for word in ['skill', 'learn', 'study', 'course', 'training']):
            return 'skills'
        elif any(word in question_lower for word in ['interview', 'apply', 'job', 'hiring']):
            return 'interview'
        elif any(word in question_lower for word in ['challenge', 'difficult', 'hard', 'struggle']):
            return 'challenges'
        elif any(word in question_lower for word in ['day', 'daily', 'work', 'routine']):
            return 'daily_life'
        elif any(word in question_lower for word in ['future', 'career', 'path', 'journey']):
            return 'career_path'
        else:
            return 'general'
    
    def _extract_relevant_skills(self, question: str, career_info: Dict[str, Any]) -> List[str]:
        """Extract relevant skills mentioned in the question"""
        question_lower = question.lower()
        relevant_skills = []
        
        for skill in career_info.get('skills', []):
            if skill.lower() in question_lower:
                relevant_skills.append(skill)
        
        return relevant_skills
    
    def _determine_career_stage(self, question: str, session_context: Dict[str, Any] = None) -> str:
        """Determine the career stage the user is asking about"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['start', 'begin', 'entry', 'junior', 'first']):
            return 'entry'
        elif any(word in question_lower for word in ['mid', 'middle', 'experienced', 'senior']):
            return 'mid'
        elif any(word in question_lower for word in ['lead', 'manager', 'director', 'executive']):
            return 'senior'
        else:
            return 'general'
    
    def _extract_topics(self, question: str) -> List[str]:
        """Extract key topics from the question"""
        # Simple keyword extraction
        topics = []
        question_lower = question.lower()
        
        topic_keywords = {
            'technology': ['tech', 'technology', 'programming', 'coding', 'software'],
            'leadership': ['lead', 'leadership', 'manage', 'team', 'direct'],
            'education': ['learn', 'study', 'education', 'degree', 'certification'],
            'work_life': ['work', 'life', 'balance', 'schedule', 'hours'],
            'growth': ['grow', 'growth', 'advance', 'progress', 'develop']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def generate_enhanced_prompt(self, career: str, question: str, context: Dict[str, Any]) -> str:
        """Generate enhanced prompt with RAG-retrieved context"""
        career_info = context.get('career_info', {})
        question_type = context.get('question_type', 'general')
        retrieved_documents = context.get('retrieved_documents', [])
        relevant_skills = context.get('relevant_skills', [])
        career_stage = context.get('career_stage', 'general')
        topics = context.get('topics', [])
        
        # Build context-aware prompt
        prompt_parts = [
            f"You are a {career_info.get('title', career)} 10 years in the future.",
            f"Career: {career}",
            f"Question: {question}",
        ]
        
        # Add retrieved document context (RAG)
        if retrieved_documents:
            prompt_parts.append("\nRelevant career information:")
            for doc in retrieved_documents[:3]:  # Use top 3 most relevant
                prompt_parts.append(f"- {doc['content']}")
        
        # Add specific context based on question type
        if question_type == 'salary':
            salary_range = career_info.get('salary_range', {})
            if salary_range:
                prompt_parts.append(f"\nSalary context: {salary_range}")
            else:
                # Try to extract from retrieved documents
                salary_docs = [doc for doc in retrieved_documents if doc['type'] == 'salary']
                if salary_docs:
                    prompt_parts.append(f"\nSalary information: {salary_docs[0]['content']}")
        
        if question_type == 'skills':
            skills_docs = [doc for doc in retrieved_documents if doc['type'] in ['skills', 'preferred_skills']]
            if skills_docs:
                prompt_parts.append(f"\nSkills information:")
                for doc in skills_docs:
                    prompt_parts.append(f"- {doc['content']}")
            
            if relevant_skills:
                prompt_parts.append(f"\nUser mentioned skills: {', '.join(relevant_skills)}")
        
        if question_type == 'interview':
            prompt_parts.append("\nFocus on interview preparation, common questions, and success strategies.")
        
        if career_stage != 'general':
            progression_docs = [doc for doc in retrieved_documents if doc['type'] == 'progression']
            if progression_docs:
                prompt_parts.append(f"\nCareer progression: {progression_docs[0]['content']}")
        
        if topics:
            prompt_parts.append(f"\nTopics to address: {', '.join(topics)}")
        
        # Add tools and technology context if relevant
        tools_docs = [doc for doc in retrieved_documents if doc['type'] in ['tools', 'languages']]
        if tools_docs and any(topic in ['technology', 'tools', 'programming'] for topic in topics):
            prompt_parts.append(f"\nTechnology stack:")
            for doc in tools_docs:
                prompt_parts.append(f"- {doc['content']}")
        
        # Add session history for context
        session_history = context.get('session_history', [])
        if session_history:
            prompt_parts.append(f"\nPrevious conversation context:")
            for msg in session_history[-2:]:  # Last 2 messages
                prompt_parts.append(f"- {msg.get('role', 'user')}: {msg.get('content', '')[:100]}...")
        
        prompt_parts.extend([
            "\nInstructions:",
            "Respond in first person as their future self.",
            "Be specific, encouraging, and realistic.",
            "Use the retrieved information to provide accurate, detailed answers.",
            "Keep response under 150 words.",
            "Include actionable advice based on the career information."
        ])
        
        return "\n".join(prompt_parts)
    
    def add_resume_data(self, resume_text: str, user_id: str, career_focus: str = None):
        """Add resume data to the knowledge base for personalized responses"""
        try:
            # Create chunks from resume text
            resume_chunks = self._chunk_resume_text(resume_text, user_id, career_focus)
            
            # Add to document chunks
            self.document_chunks.extend(resume_chunks)
            
            # Rebuild indexes to include new data
            self._build_indexes()
            
            logger.info(f"Added {len(resume_chunks)} resume chunks for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error adding resume data: {e}")
    
    def _chunk_resume_text(self, resume_text: str, user_id: str, career_focus: str = None) -> List[DocumentChunk]:
        """Chunk resume text into manageable pieces"""
        chunks = []
        
        # Split resume into sections (simple approach)
        sections = resume_text.split('\n\n')
        
        for i, section in enumerate(sections):
            if len(section.strip()) > 50:  # Only include substantial sections
                chunk = DocumentChunk(
                    content=f"User resume section: {section.strip()}",
                    metadata={
                        'type': 'resume',
                        'user_id': user_id,
                        'career_focus': career_focus,
                        'section_index': i,
                        'source': 'user_resume'
                    }
                )
                chunks.append(chunk)
        
        return chunks
    
    def search_across_careers(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search across all careers for relevant information"""
        try:
            # Retrieve documents without career filter
            retrieved_chunks = self.retrieve_relevant_documents(query, career=None, top_k=top_k)
            
            # Group by career and return results
            results = []
            for chunk in retrieved_chunks:
                career_id = chunk.metadata.get('career_id', 'unknown')
                results.append({
                    'career_id': career_id,
                    'content': chunk.content,
                    'type': chunk.metadata.get('type', 'unknown'),
                    'section': chunk.metadata.get('section', 'unknown'),
                    'relevance_score': getattr(chunk, 'relevance_score', 0)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in cross-career search: {e}")
            return []
    
    def get_career_insights(self, career: str) -> Dict[str, Any]:
        """Get comprehensive career insights"""
        career_info = self.knowledge_base.get(career, {})
        
        return {
            'title': career_info.get('title', career),
            'skills_roadmap': career_info.get('required_skills', []),
            'preferred_skills': career_info.get('preferred_skills', []),
            'salary_progression': career_info.get('salary_range', {}),
            'career_milestones': career_info.get('growth_path', []),
            'tools': career_info.get('tools', []),
            'languages': career_info.get('languages', []),
            'experience_levels': career_info.get('experience_levels', {}),
            'category': career_info.get('category', ''),
            'description': career_info.get('description', '')
        }
    
    def clear_cache(self):
        """Clear all caches"""
        self.embeddings_cache.clear()
        self.context_cache.clear()
        logger.info("RAG pipeline cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return {
            'knowledge_base_size': len(self.knowledge_base),
            'document_chunks': len(self.document_chunks),
            'context_cache_size': len(self.context_cache),
            'embeddings_cache_size': len(self.embeddings_cache),
            'cache_ttl': self.cache_ttl,
            'embedding_model_loaded': self.embedding_model is not None,
            'tfidf_index_built': self.tfidf_matrix is not None
        }
    
    def save_indexes(self, filepath: str):
        """Save indexes to disk for faster loading"""
        try:
            index_data = {
                'document_chunks': self.document_chunks,
                'tfidf_matrix': self.tfidf_matrix,
                'tfidf_vocabulary': self.tfidf_vectorizer.vocabulary_ if hasattr(self.tfidf_vectorizer, 'vocabulary_') else None
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(index_data, f)
            
            logger.info(f"Saved indexes to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving indexes: {e}")
    
    def load_indexes(self, filepath: str):
        """Load indexes from disk"""
        try:
            with open(filepath, 'rb') as f:
                index_data = pickle.load(f)
            
            self.document_chunks = index_data.get('document_chunks', [])
            self.tfidf_matrix = index_data.get('tfidf_matrix', None)
            
            # Rebuild TF-IDF vectorizer vocabulary if available
            if index_data.get('tfidf_vocabulary'):
                self.tfidf_vectorizer.vocabulary_ = index_data['tfidf_vocabulary']
            
            logger.info(f"Loaded indexes from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading indexes: {e}")

# Global instance
rag_pipeline = RAGPipeline()
rag_pipeline.load_knowledge_base()
