"""
main.py - FastAPI Backend Entry Point
======================================
This is the main backend file. FastAPI is a modern Python web framework.
It handles HTTP requests, validates inputs, and returns JSON responses.

Compatible with:
- Local development (uvicorn)
- AWS Lambda (via Mangum adapter)
"""

import time
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from dotenv import load_dotenv

# Import our custom modules
from chat_handler import get_bot_response
from database import save_chat_log, get_chat_history
from logger import log_request, log_error
from monitor import track_response_time, track_error

# Load environment variables from .env file
load_dotenv()

# ─────────────────────────────────────────────
# FastAPI App Initialization
# ─────────────────────────────────────────────
app = FastAPI(
    title="Serverless Chatbot API",
    description="A simple chatbot backend with MLOps features",
    version="1.0.0"
)

# Allow frontend (React) to call this API
# CORS = Cross-Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Request / Response Data Models
# ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Defines what the frontend must send"""
    message: str
    session_id: str = "default"

    @validator("message")
    def message_must_not_be_empty(cls, v):
        """Security: reject empty or too-long messages"""
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")
        if len(v) > 500:
            raise ValueError("Message too long (max 500 characters)")
        return v


class ChatResponse(BaseModel):
    """Defines what we send back to the frontend"""
    response: str
    session_id: str
    timestamp: str
    model_version: str
    response_time_ms: float


# ─────────────────────────────────────────────
# API Endpoints
# ─────────────────────────────────────────────

@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Chatbot API is running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Receives a message, returns a bot response.
    Also logs everything for MLOps monitoring.
    """
    start_time = time.time()

    try:
        # Step 1: Log the incoming request
        log_request(request.session_id, request.message)

        # Step 2: Get bot response from our chat handler
        bot_reply = get_bot_response(request.message)

        # Step 3: Calculate response time (for monitoring)
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        # Step 4: Get current model version from version.txt
        model_version = get_model_version()

        # Step 5: Get current timestamp
        from datetime import datetime
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Step 6: Save to database (SQLite locally, DynamoDB on AWS)
        save_chat_log(
            session_id=request.session_id,
            user_message=request.message,
            bot_response=bot_reply,
            timestamp=timestamp,
            model_version=model_version
        )

        # Step 7: Track monitoring metrics
        track_response_time(elapsed_ms)

        # Step 8: Return the response
        return ChatResponse(
            response=bot_reply,
            session_id=request.session_id,
            timestamp=timestamp,
            model_version=model_version,
            response_time_ms=elapsed_ms
        )

    except ValueError as e:
        # Input validation error
        track_error("validation_error")
        log_error(str(e))
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Unexpected error
        track_error("server_error")
        log_error(str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/history/{session_id}")
def history(session_id: str):
    """
    Get chat history for a session.
    Useful for restoring conversation context.
    """
    try:
        logs = get_chat_history(session_id)
        return {"session_id": session_id, "history": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """
    Detailed health check.
    AWS API Gateway can ping this to verify the function is alive.
    """
    model_version = get_model_version()
    return {
        "status": "healthy",
        "model_version": model_version,
        "environment": os.getenv("ENVIRONMENT", "local")
    }


# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────

def get_model_version() -> str:
    """Read the current model version from version.txt"""
    try:
        version_path = os.path.join(os.path.dirname(__file__), "../ml/version.txt")
        with open(version_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "1.0.0"  # Default version


# ─────────────────────────────────────────────
# Local Development Entry Point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
