from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

@app.get("/api")
async def root():
    return {"status": "healthy"}

@app.post("/api/ask")
async def answer_question(request: QuestionRequest):
    return {
        "answer": "This is a test response. The system is working.",
        "similarity": 1.0,
        "source_url": "https://example.com",
        "source_title": "Test Source"
    } 