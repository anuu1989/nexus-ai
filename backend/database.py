"""
NexusAI Database System
======================

Simple SQLite database system for persistent storage of user data,
conversations, documents, and analytics.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib

class NexusAIDatabase:
    def __init__(self, db_path: str = 'nexusai.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    name TEXT,
                    email TEXT,
                    bio TEXT,
                    preferences TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT UNIQUE NOT NULL,
                    user_id TEXT,
                    title TEXT,
                    model_used TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE NOT NULL,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
                )
            ''')
            
            # Documents table (for RAG)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT UNIQUE NOT NULL,
                    user_id TEXT,
                    title TEXT,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    chunk_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Document chunks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chunk_id TEXT UNIQUE NOT NULL,
                    document_id TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (document_id)
                )
            ''')
            
            # Templates table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id TEXT UNIQUE NOT NULL,
                    user_id TEXT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    tags TEXT,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # LoRA adapters table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lora_adapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    adapter_id TEXT UNIQUE NOT NULL,
                    user_id TEXT,
                    name TEXT NOT NULL,
                    config TEXT,
                    model_path TEXT,
                    trained BOOLEAN DEFAULT FALSE,
                    training_data_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    trained_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    model_used TEXT,
                    response_time REAL,
                    tokens_used INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Search history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    query TEXT NOT NULL,
                    results_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            print("✅ Database initialized successfully")
    
    # User management methods
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        user_id = user_data.get('user_id') or hashlib.md5(f"{user_data.get('email', '')}{datetime.now()}".encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, name, email, bio, preferences)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                user_data.get('name'),
                user_data.get('email'),
                user_data.get('bio'),
                json.dumps(user_data.get('preferences', {}))
            ))
            conn.commit()
        
        return user_id
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'user_id': row[1],
                    'name': row[2],
                    'email': row[3],
                    'bio': row[4],
                    'preferences': json.loads(row[5] or '{}'),
                    'created_at': row[6],
                    'updated_at': row[7]
                }
        return None
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Update user data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET name = ?, email = ?, bio = ?, preferences = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (
                user_data.get('name'),
                user_data.get('email'),
                user_data.get('bio'),
                json.dumps(user_data.get('preferences', {})),
                user_id
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    # Conversation management methods
    def save_conversation(self, conversation_data: Dict[str, Any]) -> str:
        """Save or update a conversation"""
        conversation_id = conversation_data.get('id') or hashlib.md5(f"{conversation_data.get('title', '')}{datetime.now()}".encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Save conversation
            cursor.execute('''
                INSERT OR REPLACE INTO conversations (conversation_id, user_id, title, model_used, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                conversation_id,
                conversation_data.get('user_id'),
                conversation_data.get('title'),
                conversation_data.get('model')
            ))
            
            # Save messages
            messages = conversation_data.get('messages', [])
            for i, message in enumerate(messages):
                message_id = f"{conversation_id}_{i}"
                cursor.execute('''
                    INSERT OR REPLACE INTO messages (message_id, conversation_id, role, content, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    message_id,
                    conversation_id,
                    message.get('role'),
                    message.get('content'),
                    json.dumps(message.get('metadata', {}))
                ))
            
            conn.commit()
        
        return conversation_id
    
    def get_conversations(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get conversations for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT c.*, COUNT(m.id) as message_count
                    FROM conversations c
                    LEFT JOIN messages m ON c.conversation_id = m.conversation_id
                    WHERE c.user_id = ?
                    GROUP BY c.conversation_id
                    ORDER BY c.updated_at DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT c.*, COUNT(m.id) as message_count
                    FROM conversations c
                    LEFT JOIN messages m ON c.conversation_id = m.conversation_id
                    GROUP BY c.conversation_id
                    ORDER BY c.updated_at DESC
                ''')
            
            rows = cursor.fetchall()
            conversations = []
            
            for row in rows:
                conversations.append({
                    'id': row[1],
                    'title': row[3],
                    'model': row[4],
                    'created_at': row[5],
                    'updated_at': row[6],
                    'message_count': row[7]
                })
            
            return conversations
    
    def get_conversation_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get messages for a conversation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM messages 
                WHERE conversation_id = ? 
                ORDER BY created_at ASC
            ''', (conversation_id,))
            
            rows = cursor.fetchall()
            messages = []
            
            for row in rows:
                messages.append({
                    'role': row[3],
                    'content': row[4],
                    'metadata': json.loads(row[5] or '{}'),
                    'timestamp': row[6]
                })
            
            return messages
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and its messages"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete messages first
            cursor.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
            
            # Delete conversation
            cursor.execute('DELETE FROM conversations WHERE conversation_id = ?', (conversation_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    # Document management methods (for RAG)
    def save_document(self, document_data: Dict[str, Any]) -> str:
        """Save a document for RAG"""
        document_id = document_data.get('id') or hashlib.md5(f"{document_data.get('content', '')[:100]}{datetime.now()}".encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO documents (document_id, user_id, title, content, metadata, chunk_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                document_id,
                document_data.get('user_id'),
                document_data.get('title'),
                document_data.get('content'),
                json.dumps(document_data.get('metadata', {})),
                document_data.get('chunk_count', 0)
            ))
            conn.commit()
        
        return document_id
    
    def get_documents(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get documents"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
            else:
                cursor.execute('SELECT * FROM documents ORDER BY created_at DESC')
            
            rows = cursor.fetchall()
            documents = []
            
            for row in rows:
                documents.append({
                    'id': row[1],
                    'title': row[3],
                    'content': row[4],
                    'metadata': json.loads(row[5] or '{}'),
                    'chunk_count': row[6],
                    'created_at': row[7]
                })
            
            return documents
    
    # Analytics methods
    def log_analytics(self, event_data: Dict[str, Any]) -> None:
        """Log analytics event"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analytics (user_id, event_type, event_data, model_used, response_time, tokens_used)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                event_data.get('user_id'),
                event_data.get('event_type'),
                json.dumps(event_data.get('data', {})),
                event_data.get('model_used'),
                event_data.get('response_time'),
                event_data.get('tokens_used')
            ))
            conn.commit()
    
    def get_analytics(self, user_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get analytics data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Base query conditions
            where_clause = "WHERE created_at >= datetime('now', '-{} days')".format(days)
            params = []
            
            if user_id:
                where_clause += " AND user_id = ?"
                params.append(user_id)
            
            # Total events
            cursor.execute(f"SELECT COUNT(*) FROM analytics {where_clause}", params)
            total_events = cursor.fetchone()[0]
            
            # Events by type
            cursor.execute(f"SELECT event_type, COUNT(*) FROM analytics {where_clause} GROUP BY event_type", params)
            events_by_type = dict(cursor.fetchall())
            
            # Average response time
            cursor.execute(f"SELECT AVG(response_time) FROM analytics {where_clause} AND response_time IS NOT NULL", params)
            avg_response_time = cursor.fetchone()[0] or 0
            
            # Most used models
            cursor.execute(f"SELECT model_used, COUNT(*) FROM analytics {where_clause} AND model_used IS NOT NULL GROUP BY model_used ORDER BY COUNT(*) DESC LIMIT 5", params)
            popular_models = dict(cursor.fetchall())
            
            return {
                'total_events': total_events,
                'events_by_type': events_by_type,
                'avg_response_time': round(avg_response_time, 2),
                'popular_models': popular_models,
                'period_days': days
            }
    
    # Search methods
    def save_search(self, user_id: str, query: str, results_count: int) -> None:
        """Save search query"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO search_history (user_id, query, results_count)
                VALUES (?, ?, ?)
            ''', (user_id, query, results_count))
            conn.commit()
    
    def get_search_history(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get search history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT query, results_count, created_at 
                FROM search_history 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            rows = cursor.fetchall()
            return [
                {
                    'query': row[0],
                    'results_count': row[1],
                    'created_at': row[2]
                }
                for row in rows
            ]
    
    # Utility methods
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count records in each table
            tables = ['users', 'conversations', 'messages', 'documents', 'templates', 'lora_adapters', 'analytics']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f'{table}_count'] = cursor.fetchone()[0]
            
            # Database size
            stats['database_size'] = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            return stats
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False

# Global database instance
db = None

def get_database() -> NexusAIDatabase:
    """Get or create database instance"""
    global db
    if db is None:
        db = NexusAIDatabase()
    return db

def initialize_database():
    """Initialize database"""
    try:
        global db
        db = NexusAIDatabase()
        print("✅ Database system initialized")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False