import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel, Field

# Load environment variables from backend/.env
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)
load_dotenv(override=True)

api_key = os.getenv("GROQ_API_KEY")
MODEL = os.getenv(
    "GROQ_MODEL",
    "qwen/qwen3.8-27b"
)

if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is missing. Add it to backend/.env"
    )

client = Groq(api_key=api_key)

app = FastAPI(title="Conversation Memory Chatbot")

# Allow requests from the local React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory storage:
# Each session ID maps to its own list of messages.
chat_sessions: dict[str, list[dict[str, Any]]] = {}


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=10000)


class SessionResponse(BaseModel):
    session_id: str


def make_message(role: str, content: str) -> dict[str, str]:
    return {
        "role": role,
        "content": content,
    }


@app.get("/")
def home():
    return {
        "message": "Conversation Memory Chatbot API is running"
    }


# TASK 1: Generate a new, separate chat session.
@app.post("/api/sessions", response_model=SessionResponse)
def create_session():
    session_id = str(uuid.uuid4())
    chat_sessions[session_id] = []

    return {"session_id": session_id}


# Return the messages belonging to one session.
@app.get("/api/sessions/{session_id}/history")
def get_history(session_id: str):
    if session_id not in chat_sessions:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found"
        )

    return {
        "session_id": session_id,
        "messages": chat_sessions[session_id],
    }


# TASKS 2 and 3:
# Store messages and send the session's conversation to Groq.
@app.post("/api/chat")
def chat(request: ChatRequest):
    session_id = request.session_id
    question = request.message.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    if session_id not in chat_sessions:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found. Start a new chat."
        )

    history = chat_sessions[session_id]

    # Build the conversation sent to Groq.
    # Groq only accepts 'role' and 'content' keys; filter out extra fields like 'timestamp'.
    groq_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in history
    ]

    # The existing history provides context for follow-up questions.
    groq_messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant. "
                "Answer clearly and concisely. "
                "Use previous messages to understand "
                "follow-up questions. If context is missing, "
                "ask the user to clarify."
            ),
        },
        *groq_history,
        make_message("user", question),
    ]

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=groq_messages,
            temperature=0.7,
            max_tokens=1024,
        )

        answer = completion.choices[0].message.content

        if not answer:
            raise HTTPException(
                status_code=502,
                detail="The AI returned an empty response."
            )

    except HTTPException:
        raise
    except Exception:
        # Log detailed errors on the server, not to the user.
        import logging
        logging.exception("Groq API request failed")

        raise HTTPException(
            status_code=502,
            detail="Unable to get an AI response. Please try again."
        )

    # TASK 2: Save both messages after successful generation.
    timestamp = datetime.now(timezone.utc).isoformat()

    history.append({
        "role": "user",
        "content": question,
        "timestamp": timestamp,
    })

    history.append({
        "role": "assistant",
        "content": answer,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    return {
        "session_id": session_id,
        "question": question,
        "answer": answer,
        "messages": history,
    }
