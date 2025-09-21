# Database Configuration
import os
import sqlite3
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for Future Self AI Career Advisor"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default to SQLite in the project root
            project_root = Path(__file__).resolve().parent.parent.parent
            db_path = project_root / 'future_self_advisor.db'
        
        self.db_path = db_path
        self.connection = None
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            
            # Create tables
            self.create_tables()
            logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def create_tables(self):
        """Create database tables"""
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                name TEXT NOT NULL,
                age INTEGER,
                photo_url TEXT,
                resume_data TEXT,  -- JSON string
                career_interests TEXT,  -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                conversations TEXT,  -- JSON string
                aged_avatars TEXT,  -- JSON string
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                career TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                messages TEXT,  -- JSON string
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Career matches table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS career_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                career TEXT,
                match_percentage REAL,
                matched_skills TEXT,  -- JSON string
                missing_skills TEXT,  -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Skills analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                career TEXT,
                analysis_data TEXT,  -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Timeline projections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS timeline_projections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                career TEXT,
                timeline_data TEXT,  -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        self.connection.commit()
        logger.info("Database tables created successfully")
    
    def get_connection(self):
        """Get database connection"""
        if self.connection is None:
            self.init_database()
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str, params: tuple = ()):
        """Execute a query and return results"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def execute_insert(self, query: str, params: tuple = ()):
        """Execute an insert query and return the last row ID"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor.lastrowid
    
    def execute_update(self, query: str, params: tuple = ()):
        """Execute an update query"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor.rowcount

# Global database instance
db_manager = None

def get_database():
    """Get the global database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def init_database():
    """Initialize the database"""
    global db_manager
    db_manager = DatabaseManager()
    return db_manager
