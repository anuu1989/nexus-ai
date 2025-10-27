"""
NexusAI - Simplified RAG and LoRA Systems
=========================================

This file provides lightweight implementations of RAG (Retrieval-Augmented Generation)
and LoRA (Low-Rank Adaptation) systems that work without heavy ML dependencies.

Purpose:
- Provides demo functionality when full ML libraries aren't available
- Uses simple keyword matching for RAG instead of vector embeddings
- Simulates LoRA training without actual model fine-tuning
- Maintains the same API interface as full systems for seamless fallback

RAG System Features:
- Document storage and chunking
- Keyword-based search and retrieval
- JSON file persistence
- Statistics tracking

LoRA System Features:
- Adapter creation and management
- Training data storage
- Simulated training process
- Adapter metadata tracking

Author: Anurag Vaidhya
Powered by: KIRO AI
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

class SimpleRAGSystem:
    """
    Simplified RAG System
    ====================
    
    A lightweight implementation of Retrieval-Augmented Generation that works
    without heavy ML dependencies like transformers, faiss, or chromadb.
    
    Features:
    - Document storage with automatic chunking
    - Keyword-based search and retrieval
    - JSON file persistence for data storage
    - Statistics tracking and reporting
    
    How it works:
    1. Documents are split into chunks using simple word-based splitting
    2. Search uses keyword matching with scoring based on term frequency
    3. Results are ranked by relevance score
    4. All data is stored in JSON files for persistence
    """
    
    def __init__(self):
        # === DATA STORAGE ===
        # Dictionary to store document metadata and content
        self.documents = {}
        
        # Dictionary to store individual document chunks for search
        self.document_chunks = {}
        
        # === FILE SYSTEM SETUP ===
        # Directory to store RAG data files
        self.data_dir = './rag_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing data from disk
        self._load_data()
    
    def _load_data(self):
        """Load existing data"""
        try:
            docs_file = os.path.join(self.data_dir, 'documents.json')
            if os.path.exists(docs_file):
                with open(docs_file, 'r') as f:
                    self.documents = json.load(f)
            
            chunks_file = os.path.join(self.data_dir, 'chunks.json')
            if os.path.exists(chunks_file):
                with open(chunks_file, 'r') as f:
                    self.document_chunks = json.load(f)
        except Exception as e:
            print(f"Error loading RAG data: {e}")
    
    def _save_data(self):
        """Save data to disk"""
        try:
            with open(os.path.join(self.data_dir, 'documents.json'), 'w') as f:
                json.dump(self.documents, f, indent=2)
            
            with open(os.path.join(self.data_dir, 'chunks.json'), 'w') as f:
                json.dump(self.document_chunks, f, indent=2)
        except Exception as e:
            print(f"Error saving RAG data: {e}")
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Add a document to the RAG knowledge base
        
        Process:
        1. Generate unique document ID using content hash and timestamp
        2. Split document into searchable chunks
        3. Store document metadata and full content
        4. Store individual chunks with references to parent document
        5. Persist all data to JSON files
        
        Args:
            content (str): The document text content to add
            metadata (dict): Optional metadata (title, tags, source, etc.)
            
        Returns:
            str: Document ID if successful, None if failed
        """
        try:
            # === DOCUMENT ID GENERATION ===
            # Create unique ID using first 100 chars + timestamp to avoid collisions
            doc_id = hashlib.md5(f"{content[:100]}{datetime.now()}".encode()).hexdigest()
            
            # === DOCUMENT CHUNKING ===
            # Split document into smaller, searchable chunks for better retrieval
            chunks = self._split_text(content)
            
            # === DOCUMENT STORAGE ===
            # Store complete document with metadata for reference
            self.documents[doc_id] = {
                'id': doc_id,                           # Unique identifier
                'content': content,                     # Full document text
                'metadata': metadata or {},             # User-provided metadata
                'created_at': datetime.now().isoformat(), # Timestamp
                'chunk_count': len(chunks)              # Number of chunks created
            }
            
            # === CHUNK STORAGE ===
            # Store individual chunks for efficient search and retrieval
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_{i}"  # Unique chunk identifier
                self.document_chunks[chunk_id] = {
                    'doc_id': doc_id,           # Reference to parent document
                    'chunk_index': i,           # Position in document
                    'content': chunk,           # Chunk text content
                    'metadata': metadata or {}  # Inherited metadata
                }
            
            # === PERSISTENCE ===
            # Save all data to disk for persistence across sessions
            self._save_data()
            print(f"✅ Added document {doc_id} with {len(chunks)} chunks")
            return doc_id
            
        except Exception as e:
            print(f"❌ Error adding document: {e}")
            return None
    
    def _split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Simple text splitting"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks if chunks else [text]
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Simple keyword-based retrieval"""
        try:
            query_words = set(query.lower().split())
            results = []
            
            for chunk_id, chunk_data in self.document_chunks.items():
                content = chunk_data['content'].lower()
                
                # Simple scoring based on keyword matches
                score = 0
                for word in query_words:
                    if word in content:
                        score += content.count(word)
                
                if score > 0:
                    results.append({
                        'content': chunk_data['content'],
                        'score': score,
                        'metadata': chunk_data['metadata'],
                        'doc_id': chunk_data['doc_id']
                    })
            
            # Sort by score and return top_k
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            print(f"❌ Error retrieving chunks: {e}")
            return []
    
    def search_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents"""
        chunks = self.retrieve_relevant_chunks(query, limit)
        
        # Group by document
        doc_results = {}
        for chunk in chunks:
            doc_id = chunk['doc_id']
            if doc_id not in doc_results and doc_id in self.documents:
                doc_data = self.documents[doc_id]
                doc_results[doc_id] = {
                    'doc_id': doc_id,
                    'score': chunk['score'],
                    'metadata': doc_data['metadata'],
                    'relevant_chunks': []
                }
            
            if doc_id in doc_results:
                doc_results[doc_id]['relevant_chunks'].append({
                    'content': chunk['content'],
                    'score': chunk['score']
                })
        
        return list(doc_results.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            'documents': len(self.documents),
            'chunks': len(self.document_chunks),
            'embedding_model': 'simple_keyword_matching',
            'vector_store_type': 'in_memory'
        }

class SimpleLoRASystem:
    """Simplified LoRA system for demo purposes"""
    
    def __init__(self):
        self.adapters = {}
        self.training_data = []
        self.data_dir = './lora_data'
        os.makedirs(self.data_dir, exist_ok=True)
        self._load_data()
    
    def _load_data(self):
        """Load existing data"""
        try:
            adapters_file = os.path.join(self.data_dir, 'adapters.json')
            if os.path.exists(adapters_file):
                with open(adapters_file, 'r') as f:
                    self.adapters = json.load(f)
        except Exception as e:
            print(f"Error loading LoRA data: {e}")
    
    def _save_data(self):
        """Save data to disk"""
        try:
            with open(os.path.join(self.data_dir, 'adapters.json'), 'w') as f:
                json.dump(self.adapters, f, indent=2)
        except Exception as e:
            print(f"Error saving LoRA data: {e}")
    
    def create_lora_adapter(self, adapter_name: str, custom_config: Dict[str, Any] = None) -> str:
        """Create a new LoRA adapter"""
        try:
            adapter_id = hashlib.md5(f"{adapter_name}{datetime.now()}".encode()).hexdigest()[:8]
            
            self.adapters[adapter_id] = {
                'id': adapter_id,
                'name': adapter_name,
                'config': custom_config or {},
                'created_at': datetime.now().isoformat(),
                'trained': False,
                'training_data_count': 0
            }
            
            self._save_data()
            print(f"✅ Created LoRA adapter '{adapter_name}' with ID: {adapter_id}")
            return adapter_id
            
        except Exception as e:
            print(f"❌ Error creating LoRA adapter: {e}")
            return None
    
    def add_training_data(self, data: List[Dict[str, str]], adapter_id: str = None):
        """Add training data"""
        try:
            for item in data:
                formatted_item = {
                    'input': item.get('input', ''),
                    'output': item.get('output', ''),
                    'adapter_id': adapter_id,
                    'added_at': datetime.now().isoformat()
                }
                self.training_data.append(formatted_item)
            
            if adapter_id and adapter_id in self.adapters:
                self.adapters[adapter_id]['training_data_count'] += len(data)
                self._save_data()
            
            print(f"✅ Added {len(data)} training examples")
            
        except Exception as e:
            print(f"❌ Error adding training data: {e}")
    
    def train_lora_adapter(self, adapter_id: str, training_args: Dict[str, Any] = None) -> bool:
        """Simulate training a LoRA adapter"""
        try:
            if adapter_id not in self.adapters:
                return False
            
            # Simulate training
            import time
            print(f"🚀 Training adapter '{self.adapters[adapter_id]['name']}'...")
            time.sleep(2)  # Simulate training time
            
            self.adapters[adapter_id]['trained'] = True
            self.adapters[adapter_id]['trained_at'] = datetime.now().isoformat()
            self._save_data()
            
            print(f"✅ Training completed for adapter '{self.adapters[adapter_id]['name']}'")
            return True
            
        except Exception as e:
            print(f"❌ Error training adapter: {e}")
            return False
    
    def list_adapters(self) -> List[Dict[str, Any]]:
        """List all adapters"""
        return [
            {
                'id': adapter_id,
                'name': adapter_data['name'],
                'trained': adapter_data['trained'],
                'created_at': adapter_data['created_at'],
                'training_data_count': adapter_data.get('training_data_count', 0),
                'config': adapter_data.get('config', {})
            }
            for adapter_id, adapter_data in self.adapters.items()
        ]
    
    def delete_adapter(self, adapter_id: str) -> bool:
        """Delete an adapter"""
        try:
            if adapter_id in self.adapters:
                del self.adapters[adapter_id]
                self._save_data()
                return True
            return False
        except Exception as e:
            print(f"❌ Error deleting adapter: {e}")
            return False
    
    def get_adapter_info(self, adapter_id: str) -> Optional[Dict[str, Any]]:
        """Get adapter information"""
        return self.adapters.get(adapter_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        trained_count = sum(1 for adapter in self.adapters.values() if adapter['trained'])
        
        return {
            'base_model': 'demo_model',
            'total_adapters': len(self.adapters),
            'trained_adapters': trained_count,
            'untrained_adapters': len(self.adapters) - trained_count,
            'total_training_examples': len(self.training_data),
            'device': 'cpu',
            'cuda_available': False
        }

# Global instances
simple_rag_system = None
simple_lora_system = None

def get_rag_system():
    """Get or create RAG system instance"""
    global simple_rag_system
    if simple_rag_system is None:
        simple_rag_system = SimpleRAGSystem()
    return simple_rag_system

def get_lora_system():
    """Get or create LoRA system instance"""
    global simple_lora_system
    if simple_lora_system is None:
        simple_lora_system = SimpleLoRASystem()
    return simple_lora_system

def initialize_rag():
    """Initialize RAG system"""
    try:
        global simple_rag_system
        simple_rag_system = SimpleRAGSystem()
        print("✅ Simple RAG system initialized")
        return True
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        return False

def initialize_lora():
    """Initialize LoRA system"""
    try:
        global simple_lora_system
        simple_lora_system = SimpleLoRASystem()
        print("✅ Simple LoRA system initialized")
        return True
    except Exception as e:
        print(f"❌ Error initializing LoRA system: {e}")
        return False