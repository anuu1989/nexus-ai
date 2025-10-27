"""
RAG (Retrieval-Augmented Generation) System for NexusAI
Implements document ingestion, vector storage, and retrieval capabilities
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

# Core RAG dependencies
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.document_loaders import PyPDFLoader, TextLoader
    from langchain.schema import Document
    import chromadb
    from chromadb.config import Settings
except ImportError as e:
    print(f"RAG dependencies not installed: {e}")
    print("Install with: pip install sentence-transformers faiss-cpu langchain chromadb")

# Document processing
try:
    import PyPDF2
    from docx import Document as DocxDocument
    from bs4 import BeautifulSoup
    import markdown
except ImportError as e:
    print(f"Document processing dependencies not installed: {e}")

class RAGSystem:
    """Advanced RAG system with multiple vector stores and retrieval strategies"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.embedding_model = None
        self.vector_store = None
        self.chroma_client = None
        self.documents = []
        self.document_metadata = {}
        
        # Initialize components
        self._initialize_embedding_model()
        self._initialize_vector_store()
        self._initialize_chroma()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default RAG configuration"""
        return {
            'embedding_model': 'all-MiniLM-L6-v2',  # Fast and efficient
            'chunk_size': 1000,
            'chunk_overlap': 200,
            'max_chunks_per_query': 5,
            'similarity_threshold': 0.7,
            'vector_store_type': 'faiss',  # or 'chroma'
            'persist_directory': './rag_data',
            'collection_name': 'nexusai_knowledge'
        }
    
    def _initialize_embedding_model(self):
        """Initialize the sentence transformer model"""
        try:
            model_name = self.config['embedding_model']
            print(f"Loading embedding model: {model_name}")
            self.embedding_model = SentenceTransformer(model_name)
            print("✅ Embedding model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading embedding model: {e}")
            # Fallback to a smaller model
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Fallback embedding model loaded")
            except Exception as fallback_error:
                print(f"❌ Fallback embedding model failed: {fallback_error}")
    
    def _initialize_vector_store(self):
        """Initialize FAISS vector store"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.config['persist_directory'], exist_ok=True)
            
            # Initialize empty FAISS index
            embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
            self.vector_store = faiss.IndexFlatIP(embedding_dim)  # Inner product for cosine similarity
            
            # Try to load existing index
            index_path = os.path.join(self.config['persist_directory'], 'faiss_index.bin')
            metadata_path = os.path.join(self.config['persist_directory'], 'metadata.json')
            
            if os.path.exists(index_path) and os.path.exists(metadata_path):
                self.vector_store = faiss.read_index(index_path)
                with open(metadata_path, 'r') as f:
                    self.document_metadata = json.load(f)
                print(f"✅ Loaded existing FAISS index with {self.vector_store.ntotal} vectors")
            else:
                print("✅ Initialized new FAISS index")
                
        except Exception as e:
            print(f"❌ Error initializing vector store: {e}")
    
    def _initialize_chroma(self):
        """Initialize ChromaDB as alternative vector store"""
        try:
            chroma_path = os.path.join(self.config['persist_directory'], 'chroma')
            self.chroma_client = chromadb.PersistentClient(path=chroma_path)
            
            # Get or create collection
            self.chroma_collection = self.chroma_client.get_or_create_collection(
                name=self.config['collection_name'],
                metadata={"description": "NexusAI Knowledge Base"}
            )
            print("✅ ChromaDB initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing ChromaDB: {e}")
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add a document to the RAG system"""
        try:
            # Generate document ID
            doc_id = hashlib.md5(f"{content[:100]}{datetime.now()}".encode()).hexdigest()
            
            # Split document into chunks
            chunks = self._split_document(content)
            
            # Process metadata
            doc_metadata = metadata or {}
            doc_metadata.update({
                'doc_id': doc_id,
                'added_at': datetime.now().isoformat(),
                'chunk_count': len(chunks)
            })
            
            # Add to vector stores
            self._add_chunks_to_faiss(chunks, doc_metadata)
            self._add_chunks_to_chroma(chunks, doc_metadata)
            
            # Store document metadata
            self.document_metadata[doc_id] = doc_metadata
            self._save_metadata()
            
            print(f"✅ Added document {doc_id} with {len(chunks)} chunks")
            return doc_id
            
        except Exception as e:
            print(f"❌ Error adding document: {e}")
            return None
    
    def _split_document(self, content: str) -> List[str]:
        """Split document into chunks"""
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config['chunk_size'],
                chunk_overlap=self.config['chunk_overlap'],
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            chunks = splitter.split_text(content)
            return chunks
            
        except Exception as e:
            print(f"❌ Error splitting document: {e}")
            return [content]  # Return original content as single chunk
    
    def _add_chunks_to_faiss(self, chunks: List[str], metadata: Dict[str, Any]):
        """Add chunks to FAISS vector store"""
        try:
            if not self.embedding_model:
                return
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(chunks)
            
            # Normalize for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add to FAISS index
            self.vector_store.add(embeddings)
            
            # Store chunk metadata
            for i, chunk in enumerate(chunks):
                chunk_id = f"{metadata['doc_id']}_{i}"
                self.document_metadata[chunk_id] = {
                    **metadata,
                    'chunk_text': chunk,
                    'chunk_index': i
                }
            
            # Save index
            self._save_faiss_index()
            
        except Exception as e:
            print(f"❌ Error adding chunks to FAISS: {e}")
    
    def _add_chunks_to_chroma(self, chunks: List[str], metadata: Dict[str, Any]):
        """Add chunks to ChromaDB"""
        try:
            if not self.chroma_collection:
                return
            
            # Prepare data for ChromaDB
            chunk_ids = [f"{metadata['doc_id']}_{i}" for i in range(len(chunks))]
            chunk_metadata = [
                {**metadata, 'chunk_index': i} 
                for i in range(len(chunks))
            ]
            
            # Add to ChromaDB
            self.chroma_collection.add(
                documents=chunks,
                metadatas=chunk_metadata,
                ids=chunk_ids
            )
            
        except Exception as e:
            print(f"❌ Error adding chunks to ChromaDB: {e}")
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks for a query"""
        top_k = top_k or self.config['max_chunks_per_query']
        
        try:
            # Use FAISS for retrieval
            if self.embedding_model and self.vector_store.ntotal > 0:
                return self._retrieve_from_faiss(query, top_k)
            
            # Fallback to ChromaDB
            elif self.chroma_collection:
                return self._retrieve_from_chroma(query, top_k)
            
            else:
                print("No vector store available for retrieval")
                return []
                
        except Exception as e:
            print(f"❌ Error retrieving chunks: {e}")
            return []
    
    def _retrieve_from_faiss(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Retrieve from FAISS vector store"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.vector_store.search(query_embedding, top_k)
            
            # Format results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if score >= self.config['similarity_threshold']:
                    # Find chunk metadata by index
                    chunk_metadata = self._get_chunk_by_index(idx)
                    if chunk_metadata:
                        results.append({
                            'content': chunk_metadata.get('chunk_text', ''),
                            'score': float(score),
                            'metadata': chunk_metadata
                        })
            
            return results
            
        except Exception as e:
            print(f"❌ Error retrieving from FAISS: {e}")
            return []
    
    def _retrieve_from_chroma(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Retrieve from ChromaDB"""
        try:
            results = self.chroma_collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    score = 1.0 - results['distances'][0][i]  # Convert distance to similarity
                    if score >= self.config['similarity_threshold']:
                        formatted_results.append({
                            'content': doc,
                            'score': score,
                            'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                        })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error retrieving from ChromaDB: {e}")
            return []
    
    def _get_chunk_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Get chunk metadata by FAISS index"""
        # This is a simplified approach - in production, you'd want a more efficient mapping
        chunk_keys = [k for k in self.document_metadata.keys() if '_' in k and k.split('_')[-1].isdigit()]
        if index < len(chunk_keys):
            return self.document_metadata.get(chunk_keys[index])
        return None
    
    def _save_faiss_index(self):
        """Save FAISS index to disk"""
        try:
            index_path = os.path.join(self.config['persist_directory'], 'faiss_index.bin')
            faiss.write_index(self.vector_store, index_path)
        except Exception as e:
            print(f"❌ Error saving FAISS index: {e}")
    
    def _save_metadata(self):
        """Save metadata to disk"""
        try:
            metadata_path = os.path.join(self.config['persist_directory'], 'metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(self.document_metadata, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving metadata: {e}")
    
    def add_text_file(self, file_path: str, metadata: Dict[str, Any] = None) -> str:
        """Add a text file to the RAG system"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_metadata = metadata or {}
            file_metadata.update({
                'source': file_path,
                'type': 'text',
                'filename': os.path.basename(file_path)
            })
            
            return self.add_document(content, file_metadata)
            
        except Exception as e:
            print(f"❌ Error adding text file: {e}")
            return None
    
    def add_pdf_file(self, file_path: str, metadata: Dict[str, Any] = None) -> str:
        """Add a PDF file to the RAG system"""
        try:
            content = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
            
            file_metadata = metadata or {}
            file_metadata.update({
                'source': file_path,
                'type': 'pdf',
                'filename': os.path.basename(file_path),
                'pages': len(pdf_reader.pages)
            })
            
            return self.add_document(content, file_metadata)
            
        except Exception as e:
            print(f"❌ Error adding PDF file: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        try:
            faiss_count = self.vector_store.ntotal if self.vector_store else 0
            chroma_count = self.chroma_collection.count() if self.chroma_collection else 0
            
            doc_count = len([k for k in self.document_metadata.keys() if '_' not in k])
            chunk_count = len([k for k in self.document_metadata.keys() if '_' in k])
            
            return {
                'documents': doc_count,
                'chunks': chunk_count,
                'faiss_vectors': faiss_count,
                'chroma_vectors': chroma_count,
                'embedding_model': self.config['embedding_model'],
                'vector_store_type': self.config['vector_store_type']
            }
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}
    
    def search_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents and return results with metadata"""
        chunks = self.retrieve_relevant_chunks(query, limit)
        
        # Group by document and return document-level results
        doc_results = {}
        for chunk in chunks:
            doc_id = chunk['metadata'].get('doc_id')
            if doc_id and doc_id not in doc_results:
                doc_metadata = self.document_metadata.get(doc_id, {})
                doc_results[doc_id] = {
                    'doc_id': doc_id,
                    'score': chunk['score'],
                    'metadata': doc_metadata,
                    'relevant_chunks': []
                }
            
            if doc_id:
                doc_results[doc_id]['relevant_chunks'].append({
                    'content': chunk['content'],
                    'score': chunk['score']
                })
        
        return list(doc_results.values())

# Global RAG instance
rag_system = None

def get_rag_system() -> RAGSystem:
    """Get or create global RAG system instance"""
    global rag_system
    if rag_system is None:
        rag_system = RAGSystem()
    return rag_system

def initialize_rag():
    """Initialize RAG system"""
    try:
        global rag_system
        rag_system = RAGSystem()
        print("✅ RAG system initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        return False