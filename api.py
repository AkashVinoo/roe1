from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging
import uvicorn

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QuestionRequest(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str
    similarity: float
    source_url: str
    source_title: str

app = FastAPI()

# Add CORS middleware with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load pre-computed embeddings
embeddings = None
chunks = None
chunk_metadata = None

def load_data():
    """Load pre-computed data"""
    global embeddings, chunks, chunk_metadata
    try:
        with open('data/embeddings.npy', 'rb') as f:
            embeddings = np.load(f)
        with open('data/chunks.json', 'r') as f:
            chunks = json.load(f)
        with open('data/metadata.json', 'r') as f:
            chunk_metadata = json.load(f)
        logger.info("Data loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    load_data()

@app.post("/ask")
async def answer_question(request: QuestionRequest):
    """Answer a question about the TDS course"""
    if embeddings is None or chunks is None:
        raise HTTPException(
            status_code=503,
            detail="System is not initialized. Please ensure data is loaded."
        )
    
    try:
        # For now, return a test response
        return [Answer(
            answer="This is a test response. The system is working but needs to be configured with pre-computed embeddings.",
            similarity=1.0,
            source_url="https://example.com",
            source_title="Test Source"
        )]
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Check if the API is running and system is ready"""
    return {
        "status": "healthy",
        "system_ready": embeddings is not None and chunks is not None
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port) 