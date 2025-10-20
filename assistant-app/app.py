"""
Arizona Desert Plants RAG API
FastAPI application for querying the plant knowledge base
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os
from datetime import datetime

# Import your custom classes
from ArizonaPlantVectorStore import ArizonaPlantVectorStore
from ArizonaPlantRAG import ArizonaPlantRAG

# Initialize FastAPI app
app = FastAPI(
    title="Arizona Desert Plants Assistant API",
    description="RAG-powered API for Arizona desert plant information",
    version="1.0.0"
)

# Add CORS middleware (allows frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment variables
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "arizona_plants")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Global variables for vector store and RAG (initialized on startup)
vector_store = None
rag = None

# Request/Response Models
class QueryRequest(BaseModel):
    question: str = Field(..., description="User's question about desert plants", min_length=3)
    top_k: int = Field(5, description="Number of documents to retrieve", ge=1, le=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are some drought-tolerant plants for Phoenix?",
                "top_k": 5
            }
        }

class SearchResult(BaseModel):
    id: str
    title: str
    score: float
    content: str
    type: str
    source: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    retrieved_documents: List[SearchResult]
    timestamp: str
    model: str = "gpt-4o-mini"

class HealthResponse(BaseModel):
    status: str
    qdrant_connected: bool
    collection_exists: bool
    document_count: Optional[int] = None
    timestamp: str

# Startup event - initialize components
@app.on_event("startup")
async def startup_event():
    """Initialize vector store and RAG on startup"""
    global vector_store, rag
    
    print("Initializing Arizona Desert Plants RAG API...")
    
    try:
        # Initialize vector store
        vector_store = ArizonaPlantVectorStore(
            embedding_model_name=EMBEDDING_MODEL,
            collection_name=COLLECTION_NAME,
            qdrant_url=QDRANT_URL
        )
        print(f"✓ Connected to Qdrant at {QDRANT_URL}")

        # Initialize RAG
        rag = ArizonaPlantRAG(
            vector_store=vector_store
        )
        print("✓ RAG system initialized")
        
        # Verify collection exists
        # collection_info = vector_store.client.get_collection(COLLECTION_NAME)
        # print(f"✓ Collection '{COLLECTION_NAME}' has {collection_info.points_count} documents")
        
    except Exception as e:
        print(f"✗ Error during startup: {e}")
        raise

# API Endpoints

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Arizona Desert Plants Assistant API",
        "version": "1.0.0",
        "description": "RAG-powered API for desert plant information",
        "endpoints": {
            "health": "/health",
            "query": "/query",
            "search": "/search",
            "docs": "/docs"
        }
    }

@app.head("/health", tags=["Health"])
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API and Qdrant health"""
    try:
        # Check Qdrant connection
        collection_info = vector_store.client.get_collection(COLLECTION_NAME)
        
        return HealthResponse(
            status="healthy",
            qdrant_connected=True,
            collection_exists=True,
            document_count=collection_info.points_count,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            qdrant_connected=False,
            collection_exists=False,
            timestamp=datetime.now().isoformat()
        )

@app.post("/query", response_model=QueryResponse, tags=["RAG"])
async def query_rag(request: QueryRequest):
    """
    Query the RAG system with a question about desert plants
    
    This endpoint:
    1. Retrieves relevant documents from the vector store
    2. Generates a comprehensive answer using GPT-4
    3. Returns both the answer and source documents
    """
    try:
        if not rag or not vector_store:
            raise HTTPException(status_code=503, detail="RAG system not initialized")
        
        # Get answer from RAG
        answer = rag.rag(request.question)
        
        # Get retrieved documents for transparency
        retrieved_docs = vector_store.search(request.question, limit=request.top_k)
        
        # Format search results
        search_results = [
            SearchResult(
                id=doc['id'],
                title=doc['title'],
                score=doc['score'],
                content=doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content'],
                type=doc['type'],
                source=doc['source']
            )
            for doc in retrieved_docs
        ]
        
        return QueryResponse(
            question=request.question,
            answer=answer,
            retrieved_documents=search_results,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        import traceback
        print(f"ERROR in /query endpoint:")
        print(traceback.format_exc())  # Print full stack trace
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/search", tags=["Search"])
async def search_documents(request: QueryRequest):
    """
    Search for relevant documents without generating an answer
    
    Useful for:
    - Exploring the knowledge base
    - Testing retrieval quality
    - Building custom applications
    """
    try:
        if not vector_store:
            raise HTTPException(status_code=503, detail="Vector store not initialized")
        
        # Search documents
        results = vector_store.search(request.question, limit=request.top_k)
        
        # Format results
        search_results = [
            SearchResult(
                id=doc['id'],
                title=doc['title'],
                score=doc['score'],
                content=doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content'],
                type=doc['type'],
                source=doc['source']
            )
            for doc in results
        ]
        
        return {
            "query": request.question,
            "results": search_results,
            "count": len(search_results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

@app.get("/stats", tags=["Statistics"])
async def get_statistics():
    """Get statistics about the knowledge base"""
    try:
        collection_info = vector_store.client.get_collection(COLLECTION_NAME)
        
        return {
            "collection_name": COLLECTION_NAME,
            "total_documents": collection_info.points_count,
            "vector_dimension": collection_info.config.params.vectors.size,
            "embedding_model": EMBEDDING_MODEL,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")

# Run with: uv run uvicorn app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)