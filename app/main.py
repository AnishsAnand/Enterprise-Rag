from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
from app.core.config import settings
from app.api.routes import scraper, rag, admin, support, rag_widget
from app.services.chroma_service import chroma_service
from app.services.ai_service import ai_service
from app.api.routes.auth import router as auth_router
from app.core.database import init_db
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from fastapi.responses import FileResponse

load_dotenv()

app = FastAPI(
    title="Enterprise RAG Bot",
    description="Advanced RAG system with web scraping and AI-powered knowledge retrieval",
    version="2.0.0"
)


@app.on_event("startup")
async def initialize_database():
    await init_db()

@app.on_event("startup")
async def startup_services():
    print("Starting Enterprise RAG Bot...")
    print("=" * 50)

    try:
        await chroma_service.initialize()
        print("ChromaDB initialized successfully")
    except Exception as e:
        print(f"ChromaDB initialization failed: {e}")
        print("Continuing without ChromaDB...")

    print("\nTesting AI Services:")
    print("-" * 30)

    try:
        test_embeddings = await ai_service.generate_embeddings(["test"])
        if test_embeddings and len(test_embeddings[0]) > 0:
            print("Embedding service working")
        else:
            print("Embedding service returned empty results")
    except Exception as e:
        print(f"Embedding service test failed: {e}")

    try:
        test_response = await ai_service.generate_response("Hello", ["Test context"])
        if test_response:
            print("Text generation service working")
        else:
            print("Text generation service returned empty response")
    except Exception as e:
        print(f"Text generation service test failed: {e}")

    print("\n" + "=" * 50)
    print("Enterprise RAG Bot started successfully!")
    print("Widget available at: http://localhost:4200")
    print("API docs at: http://localhost:8000/docs")
    print("=" * 50)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(scraper.router, prefix="/api/scraper", tags=["scraper"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
app.include_router(rag_widget.router, prefix="/api/rag-widget", tags=["rag-widget"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(support.router, prefix="/api/support", tags=["support"])
app.include_router(auth_router)


@app.get("/embed.js")
def serve_embed_script():
    return FileResponse("app/static/embed.js", media_type="application/javascript")

BASE_DIR = Path(__file__).resolve().parent.parent
frontend_path = BASE_DIR /"dist" /"enterprise-rag-frontend"
if not frontend_path.exists():
    raise RuntimeError(f"Static frontend directory not found at {frontend_path}")

app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

@app.get("/")
async def root():
    return {
        "message": "Enterprise RAG Bot API",
        "version": "2.0.0",
        "features": [
            "Advanced web scraping with anti-blocking",
            "AI-powered knowledge retrieval",
            "ChromaDB vector storage",
            "Multi-model AI support (Ollama, OpenRouter, Voyage)",
            "Popup widget interface"
        ]
    }

@app.get("/health")
async def health_check():
    chroma_status = "healthy"
    try:
        stats = await chroma_service.get_collection_stats()
        chroma_docs = stats['document_count']
    except:
        chroma_status = "unavailable"
        chroma_docs = 0

    ai_services = []
    if ai_service.ollama_client:
        ai_services.append("ollama")
    if ai_service.openrouter_client:
        ai_services.append("openrouter")
    if ai_service.voyage_client:
        ai_services.append("voyage")

    return {
        "status": "healthy",
        "services": {
            "chromadb": chroma_status,
            "ai_services": ai_services,
            "documents_stored": chroma_docs
        },
        "version": "2.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1
    )
