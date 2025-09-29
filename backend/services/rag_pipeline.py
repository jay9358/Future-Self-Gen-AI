# RAG Pipeline for Enhanced Context and Faster Responses
import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
import time

logger = logging.getLogger(__name__)

class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for enhanced AI responses"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.embeddings_cache = {}
        self.context_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
    def load_knowledge_base(self):
        """Load career-specific knowledge base"""
        try:
            # Load career database as knowledge base
            from model.career_database import career_database      
            
            for career, info in career_database.get_all_careers().items():
                self.knowledge_base[career] = {
                    'title': info.get('title', career),
                    'skills': info.get('required_skills', []),
                    'personality': info.get('personality', ''),
                    'salary_range': info.get('salary_range', {}),
                    'career_progression': info.get('career_progression', {}),
                    'education_path': info.get('education_path', []),
                    'certifications': info.get('certifications', [])
                }
            
            logger.info(f"Loaded knowledge base for {len(self.knowledge_base)} careers")
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
    
    def get_relevant_context(self, career: str, question: str, session_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get relevant context for the question"""
        cache_key = f"{career}_{hash(question)}"
        
        # Check cache first
        if cache_key in self.context_cache:
            cached_data = self.context_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['context']
        
        # Get career-specific knowledge
        career_info = self.knowledge_base.get(career, {})
        
        # Analyze question type and extract relevant information
        question_type = self._analyze_question_type(question)
        
        context = {
            'career_info': career_info,
            'question_type': question_type,
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
        """Generate enhanced prompt with RAG context"""
        career_info = context.get('career_info', {})
        question_type = context.get('question_type', 'general')
        relevant_skills = context.get('relevant_skills', [])
        career_stage = context.get('career_stage', 'general')
        topics = context.get('topics', [])
        
        # Build context-aware prompt
        prompt_parts = [
            f"You are a {career_info.get('title', career)} 10 years in the future.",
            f"Career: {career}",
            f"Question: {question}",
        ]
        
        # Add specific context based on question type
        if question_type == 'salary':
            salary_range = career_info.get('salary_range', {})
            prompt_parts.append(f"Salary context: Entry ${salary_range.get('entry', 0):,}, Mid ${salary_range.get('mid', 0):,}, Senior ${salary_range.get('senior', 0):,}")
        
        if question_type == 'skills':
            skills = career_info.get('skills', [])
            prompt_parts.append(f"Key skills: {', '.join(skills[:5])}")
            if relevant_skills:
                prompt_parts.append(f"User mentioned: {', '.join(relevant_skills)}")
        
        if question_type == 'interview':
            prompt_parts.append("Focus on interview preparation, common questions, and success strategies.")
        
        if career_stage != 'general':
            progression = career_info.get('career_progression', {})
            stage_info = progression.get(career_stage, {})
            if stage_info:
                prompt_parts.append(f"Career stage context: {stage_info}")
        
        if topics:
            prompt_parts.append(f"Topics to address: {', '.join(topics)}")
        
        # Add personality context
        personality = career_info.get('personality', '')
        if personality:
            prompt_parts.append(f"Personality traits: {personality}")
        
        prompt_parts.extend([
            "Respond in first person as their future self.",
            "Be specific, encouraging, and realistic.",
            "Keep response under 150 words.",
            "Include actionable advice."
        ])
        
        return "\n".join(prompt_parts)
    
    def get_career_insights(self, career: str) -> Dict[str, Any]:
        """Get comprehensive career insights"""
        career_info = self.knowledge_base.get(career, {})
        
        return {
            'title': career_info.get('title', career),
            'skills_roadmap': career_info.get('skills', []),
            'salary_progression': career_info.get('salary_range', {}),
            'career_milestones': career_info.get('career_progression', {}),
            'education_path': career_info.get('education_path', []),
            'certifications': career_info.get('certifications', [])
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
            'context_cache_size': len(self.context_cache),
            'embeddings_cache_size': len(self.embeddings_cache),
            'cache_ttl': self.cache_ttl
        }

# Global instance
rag_pipeline = RAGPipeline()
rag_pipeline.load_knowledge_base()
