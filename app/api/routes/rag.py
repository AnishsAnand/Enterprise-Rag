from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any
import json
from app.services.chroma_service import chroma_service
from app.services.ai_service import ai_service

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    max_results: int = 5
    include_context: bool = True

class DocumentUpload(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}

@router.post("/query")
async def query_rag(request: QueryRequest):
    """Query the RAG system"""
    try:
        search_results = await chroma_service.search_documents(
            request.query, 
            request.max_results
        )
        
        if not search_results:
            return {
                'query': request.query,
                'answer': 'No relevant documents found in the knowledge base.',
                'sources': [],
                'context_used': []
            }
        
        context = [result['content'] for result in search_results]
        answer = await ai_service.generate_response(request.query, context)
        sources = []
        for result in search_results:
            sources.append({
                'url': result['metadata'].get('url', ''),
                'distance': result['distance'],
                'content_preview': result['content'][:200] + '...' if len(result['content']) > 200 else result['content']
            })
        
        return {
            'query': request.query,
            'answer': answer,
            'sources': sources,
            'context_used': context if request.include_context else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-document")
async def add_document(request: DocumentUpload):
    """Add a document to the RAG system"""
    try:
        document = {
            'content': request.content,
            'url': request.metadata.get('url', ''),
            'format': request.metadata.get('format', 'text'),
            'timestamp': request.metadata.get('timestamp', ''),
            'source': request.metadata.get('source', 'manual_upload')
        }
        
        doc_ids = await chroma_service.add_documents([document])
        
        return {
            'status': 'success',
            'document_id': doc_ids[0],
            'message': 'Document added successfully'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a file for RAG"""
    try:
        content = await file.read()
        if file.content_type == 'text/plain':
            text_content = content.decode('utf-8')
        elif file.content_type == 'application/json':
            json_data = json.loads(content.decode('utf-8'))
            text_content = json.dumps(json_data, indent=2)
        elif file.content_type == 'text/csv':
            text_content = content.decode('utf-8')
        else:
            text_content = content.decode('utf-8', errors='ignore')
        
        document = {
            'content': text_content,
            'url': f'file://{file.filename}',
            'format': file.content_type,
            'timestamp': '',
            'source': 'file_upload'
        }
        
        doc_ids = await chroma_service.add_documents([document])
        
        return {
            'status': 'success',
            'filename': file.filename,
            'document_id': doc_ids[0],
            'content_length': len(text_content)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_documents(
    query: str,
    max_results: int = 10
):
    """Search documents without generating AI response"""
    try:
        search_results = await chroma_service.search_documents(query, max_results)
        
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                'content': result['content'],
                'metadata': result['metadata'],
                'relevance_score': 1 - result['distance'],  
                'content_preview': result['content'][:300] + '...' if len(result['content']) > 300 else result['content']
            })
        
        return {
            'query': query,
            'results_count': len(formatted_results),
            'results': formatted_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_rag_stats():
    """Get RAG system statistics"""
    try:
        stats = await chroma_service.get_collection_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear")
async def clear_rag_system():
    """Clear all documents from RAG system"""
    try:
        await chroma_service.delete_collection()
        await chroma_service.initialize()
        
        return {
            'status': 'success',
            'message': 'RAG system cleared successfully'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
