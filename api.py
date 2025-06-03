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

class Link(BaseModel):
    url: str
    text: str

class QuestionRequest(BaseModel):
    question: str
    image: Optional[str] = None  # base64 encoded image

class QuestionResponse(BaseModel):
    answer: str
    links: List[Link] = []

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

def save_and_analyze_image(base64_str: str) -> str:
    """Save and analyze the image, returning any relevant text/context"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        
        # Decode base64 image
        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data))
        
        # Save image for reference
        os.makedirs('uploads', exist_ok=True)
        image_path = os.path.join('uploads', f'question_image_{hash(str(image_data))}.png')
        image.save(image_path)
        
        # TODO: Add OCR or image analysis here if needed
        # For now, just return confirmation
        return f"Image saved to {image_path}"
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return None

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    init_qa_system()

@app.post("/api/", response_model=QuestionResponse)
async def answer_question(request: QuestionRequest):
    """
    Answer a question about the TDS course, optionally with an image
    """
    if qa_system is None:
        raise HTTPException(
            status_code=503,
            detail="QA system is not initialized. Please ensure content has been crawled."
        )
    
    try:
        # Process image if provided
        image_context = None
        if request.image:
            image_context = save_and_analyze_image(request.image)
            logger.info(f"Image analysis result: {image_context}")
        
        # Get answers from QA system
        answers = qa_system.get_answer(request.question)
        
        if not answers:
            return QuestionResponse(
                answer="I could not find a relevant answer to your question.",
                links=[]
            )
        
        # Format the best answer
        best_answer = answers[0]  # Assuming answers are sorted by relevance
        
        # Create response with main answer and relevant links
        response = QuestionResponse(
            answer=best_answer['answer'],
            links=[
                Link(
                    url=ans['source_url'],
                    text=ans['content'][:100] + "..."  # First 100 chars as preview
                )
                for ans in answers
                if ans['similarity'] > 0.2  # Only include relevant links
            ]
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@app.get("/api/health")
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
        reload=False  # Disable auto-reload in production
    ) 