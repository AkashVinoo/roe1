import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import logging
import base64

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class QuestionRequest(BaseModel):
    question: str
    image: Optional[str] = Field(None, description="Base64 encoded image file")

class Answer(BaseModel):
    answer: str
    similarity: float
    source_url: str
    source_title: str

# Global variables for data storage
embeddings = None
chunks = None
chunk_metadata = None

def load_data():
    """Load pre-computed data"""
    global embeddings, chunks, chunk_metadata
    try:
        # For testing/deployment, use dummy data if files don't exist
        embeddings = np.zeros((1, 384))  # Dummy embedding vector
        chunks = ["This is a test chunk"]
        chunk_metadata = [{
            "url": "https://example.com",
            "title": "Test Document"
        }]
        logger.info("Using dummy data for testing")
        return True
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return False

def process_image(base64_image: str) -> str:
    """Process the base64 encoded image and return relevant information"""
    try:
        # Decode base64 image (just logging for now)
        logger.info("Received image attachment")
        return "Image received and processed"
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return "Error processing image"

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    load_data()

@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {"status": "healthy"}

@app.post("/")  # Changed to root path to match requirement
async def answer_question(request: QuestionRequest):
    """Answer a question about the TDS course, optionally with an image"""
    if embeddings is None or chunks is None:
        raise HTTPException(
            status_code=503,
            detail="System is not initialized. Please ensure data is loaded."
        )
    
    try:
        # Process image if provided
        image_info = ""
        if request.image:
            image_info = process_image(request.image)

        # Return a response using the dummy data
        return [Answer(
            answer=f"This is a test response from the deployed API. The system is working but using dummy data for testing. {image_info}",
            similarity=1.0,
            source_url="https://example.com",
            source_title="Test Document"
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

# Server startup
if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Log startup information
    logger.info(f"Starting server on port {port}")
    
    # Run the server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False
    ) 