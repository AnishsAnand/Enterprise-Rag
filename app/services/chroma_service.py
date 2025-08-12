import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any
import uuid
import os
from app.core.config import settings
from app.services.ai_service import ai_service


class ChromaService:
    def __init__(self):
        self.client = None
        self.collection = None

    async def initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)

            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            try:
                self.collection = self.client.get_collection("enterprise_rag_knowledge")
                print("Connected to existing ChromaDB collection")
            except Exception:
                self.collection = self.client.create_collection(
                    name="enterprise_rag_knowledge",
                    metadata={"description": "Enterprise RAG Bot Knowledge Base"}
                )
                print("Created new ChromaDB collection")

        except Exception as e:
            print(f"ChromaDB initialization error: {e}")
            print("Continuing without ChromaDB...")

    async def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add documents to ChromaDB with embeddings"""
        if not self.collection:
            await self.initialize()

        if not self.collection:
            print("ChromaDB not available, skipping document addition")
            return []

        try:
            ids, texts, metadatas = [], [], []

            for doc in documents:
                doc_id = str(uuid.uuid4())
                ids.append(doc_id)

                
                content = doc['content']
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='replace')
                else:
                    content = str(content).encode('utf-8', errors='replace').decode('utf-8')

                
                if len(content) > 8000:
                    content = content[:8000] + "..."

                texts.append(content)
                metadatas.append({
                    'url': doc.get('url', ''),
                    'format': doc.get('format', 'text'),
                    'timestamp': doc.get('timestamp', ''),
                    'source': doc.get('source', 'web_scraping'),
                    'title': doc.get('title', ''),
                    'content_length': len(doc.get('content', ''))
                })

            embeddings = await ai_service.generate_embeddings(texts)
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )

            print(f"Added {len(documents)} documents to ChromaDB")
            return ids
        except Exception as e:
            print(f"Error adding documents to ChromaDB: {e}")
            return []

    async def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search documents in ChromaDB"""
        if not self.collection:
            await self.initialize()

        if not self.collection:
            print("ChromaDB not available, returning empty results")
            return []

        try:
            if isinstance(query, bytes):
                query = query.decode('utf-8', errors='replace')
            else:
                query = str(query).encode('utf-8', errors='replace').decode('utf-8')

            query_embeddings = await ai_service.generate_embeddings([query])

            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )

            search_results = []
            for i in range(len(results['documents'][0])):
                search_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'relevance_score': 1 - results['distances'][0][i]
                })

            print(f"Found {len(search_results)} relevant documents")
            return search_results
        except Exception as e:
            print(f"Error searching documents in ChromaDB: {e}")
            return []

    async def delete_collection(self):
        """Delete the collection"""
        try:
            if self.client and self.collection:
                self.client.delete_collection("enterprise_rag_knowledge")
                self.collection = None
                print("ChromaDB collection deleted")
        except Exception as e:
            print(f"Error deleting ChromaDB collection: {e}")

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        if not self.collection:
            await self.initialize()

        if not self.collection:
            return {
                'document_count': 0,
                'collection_name': 'enterprise_rag_knowledge (not available)'
            }

        try:
            count = self.collection.count()
            return {
                'document_count': count,
                'collection_name': 'enterprise_rag_knowledge',
                'status': 'active'
            }
        except Exception as e:
            print(f"Error getting ChromaDB stats: {e}")
            return {
                'document_count': 0,
                'collection_name': 'enterprise_rag_knowledge (error)',
                'status': 'error'
            }


chroma_service = ChromaService()
