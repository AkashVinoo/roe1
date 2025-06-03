from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
from typing import Optional, List
import os
from project1 import QASystem
import uvicorn
import logging
from PIL import Image
import io
import signal
import sys

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
    allow_origins=[
        "https://akashvinoo.github.io",  # GitHub Pages domain
        "http://localhost:8000",         # Local development
        "http://127.0.0.1:8000",        # Local development
        "http://localhost:5500",         # Live Server extension
        "http://127.0.0.1:5500",        # Live Server extension
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global QA system instance
qa_system = None

def init_qa_system():
    """Initialize the QA system with error handling"""
    global qa_system
    try:
        if qa_system is None:
            qa_system = QASystem('tds_content.jsonl')
            logger.info("QA system initialized successfully")
    except FileNotFoundError:
        logger.error("Content file not found. Please run the crawler first.")
    except Exception as e:
        logger.error(f"Error initializing QA system: {str(e)}")

def cleanup(signum, frame):
    """Cleanup handler for graceful shutdown"""
    logger.info("Received shutdown signal, cleaning up...")
    sys.exit(0)

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    init_qa_system()

@app.post("/ask")
async def answer_question(request: QuestionRequest):
    """
    Answer a question about the TDS course
    """
    if qa_system is None:
        raise HTTPException(
            status_code=503,
            detail="QA system is not initialized. Please ensure content has been crawled."
        )
    
    try:
        # Get answers from QA system
        answers = qa_system.get_answer(request.question)
        
        if not answers:
            return [Answer(
                answer="I could not find a relevant answer to your question.",
                similarity=0.0,
                source_url="",
                source_title=""
            )]
        
        # Format all answers
        formatted_answers = [
            Answer(
                answer=ans['answer'],
                similarity=ans['similarity'],
                source_url=ans['source_url'],
                source_title=ans.get('source_title', ans['source_url'])
            )
            for ans in answers
            if ans['similarity'] > 0.2  # Only include relevant answers
        ]
        
        return formatted_answers
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Check if the API is running and QA system is ready"""
    return {
        "status": "healthy",
        "qa_system_ready": qa_system is not None
    }

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True  # Enable auto-reload for development
    ) 