# Naviiq Chat Routes
# Connects the FastAPI endpoints to the LangGraph agent
# Handles conversation sessions and state persistence

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from app.agents.naviiq_agent import run_naviiq_agent
from app.db.database import get_collection
from app.routes.auth import get_current_student
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# ─── REQUEST MODELS ────────────────────────────────────────

class ChatMessage(BaseModel):
    message: str
    session_id: str = None

# ─── CHAT ENDPOINT ─────────────────────────────────────────

@router.post("/message")
async def send_message(
    data: ChatMessage,
    student=Depends(get_current_student)
):
    """
    Main chat endpoint. Receives student message and returns agent response.
    Handles session creation and state persistence.
    """
    student_id = str(student["_id"])
    conversations = get_collection("conversations")

    # Get or create session
    session_id = data.session_id
    existing_state = None

    if session_id:
        # Load existing conversation state
        existing_conv = await conversations.find_one({
            "session_id": session_id,
            "student_id": student_id
        })
        if existing_conv:
            existing_state = existing_conv.get("state")

    else:
        # Create new session
        session_id = str(ObjectId())
        await conversations.insert_one({
            "session_id": session_id,
            "student_id": student_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "state": None
        })

    # Run the agent
    result = await run_naviiq_agent(
        student_id=student_id,
        session_id=session_id,
        user_message=data.message,
        existing_state=existing_state
    )

    # Save updated state to MongoDB
    await conversations.update_one(
        {"session_id": session_id},
        {"$set": {
            "state": result["state"],
            "current_stage": result["current_stage"],
            "is_complete": result["is_complete"],
            "updated_at": datetime.utcnow()
        }}
    )

    return {
        "session_id": session_id,
        "response": result["response"],
        "current_stage": result["current_stage"],
        "is_complete": result["is_complete"]
    }

# ─── GET CONVERSATION HISTORY ──────────────────────────────

@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    student=Depends(get_current_student)
):
    """
    Returns conversation history for a session.
    """
    student_id = str(student["_id"])
    conversations = get_collection("conversations")

    conversation = await conversations.find_one({
        "session_id": session_id,
        "student_id": student_id
    })

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    state = conversation.get("state", {})
    messages = state.get("messages", []) if state else []

    return {
        "session_id": session_id,
        "current_stage": conversation.get("current_stage", "identity"),
        "is_complete": conversation.get("is_complete", False),
        "messages": messages
    }

# ─── GET ALL SESSIONS ──────────────────────────────────────

@router.get("/sessions")
async def get_sessions(student=Depends(get_current_student)):
    """
    Returns all conversation sessions for the current student.
    """
    student_id = str(student["_id"])
    conversations = get_collection("conversations")

    cursor = conversations.find(
        {"student_id": student_id},
        {"session_id": 1, "current_stage": 1, "is_complete": 1, "created_at": 1}
    )

    sessions = []
    async for conv in cursor:
        conv["_id"] = str(conv["_id"])
        sessions.append(conv)

    return {"sessions": sessions}

# ─── TEST ENDPOINT ─────────────────────────────────────────

@router.get("/test")
async def chat_test():
    return {"message": "Chat route is working"}