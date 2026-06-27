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
import secrets
import json
from fastapi.responses import StreamingResponse

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
    student_id = str(student["_id"])
    conversations = get_collection("conversations")

    session_id = data.session_id
    existing_state = None

    if session_id:
        existing_conv = await conversations.find_one({
            "session_id": session_id,
            "student_id": student_id
        })
        if existing_conv:
            existing_state = existing_conv.get("state")
    else:
        session_id = str(ObjectId())
        await conversations.insert_one({
            "session_id": session_id,
            "student_id": student_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "state": None
        })

    result = await run_naviiq_agent(
        student_id=student_id,
        session_id=session_id,
        user_message=data.message,
        existing_state=existing_state
    )

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
        "is_complete": result["is_complete"],
        "roadmap_complete": result.get("roadmap_complete", False),
        "share_token": result.get("share_token")
    }

# ─── GENERATE SHAREABLE LINK ───────────────────────────────

@router.post("/share/{session_id}")
async def generate_share_link(
    session_id: str,
    student=Depends(get_current_student)
):
    """
    Generates a unique shareable link for a completed roadmap.
    Only the student who owns the session can generate a link.
    """
    student_id = str(student["_id"])
    recommendations = get_collection("recommendations")

    # Find the recommendation for this session
    recommendation = await recommendations.find_one({
        "session_id": session_id,
        "student_id": student_id
    })

    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail="No completed roadmap found for this session"
        )

    # Check if share token already exists
    existing_token = recommendation.get("share_token")
    if existing_token:
        return {
            "share_token": existing_token,
            "share_url": f"/api/chat/roadmap/{existing_token}"
        }

    # Generate new unique token
    share_token = secrets.token_urlsafe(16)

    # Save token to recommendation
    await recommendations.update_one(
        {"session_id": session_id, "student_id": student_id},
        {"$set": {
            "share_token": share_token,
            "shared_at": datetime.utcnow()
        }}
    )

    return {
        "share_token": share_token,
        "share_url": f"/api/chat/roadmap/{share_token}"
    }

# ─── PUBLIC ROADMAP VIEW ───────────────────────────────────

@router.get("/roadmap/{share_token}")
async def view_shared_roadmap(share_token: str):
    """
    Public endpoint. No login required.
    Returns roadmap data for anyone with the share token.
    """
    recommendations = get_collection("recommendations")

    recommendation = await recommendations.find_one(
        {"share_token": share_token}
    )

    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail="Roadmap not found or link is invalid"
        )

    return {
        "matched_category": recommendation.get("matched_category"),
        "student_mode": recommendation.get("student_mode"),
        "roadmap_response": recommendation.get("roadmap_response"),
        "confidence_score": recommendation.get("confidence_score"),
        "infrastructure_adjusted": recommendation.get("infrastructure_adjusted"),
        "status": recommendation.get("status"),
        "shared_at": recommendation.get("shared_at")
    }

# ─── GET CONVERSATION HISTORY ──────────────────────────────

@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    student=Depends(get_current_student)
):
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

# --- STREAMING ENDPOINT ---

@router.post("/stream")
async def stream_message(
    data: ChatMessage,
    student=Depends(get_current_student)
):
    student_id = str(student["_id"])
    conversations = get_collection("conversations")

    session_id = data.session_id
    existing_state = None

    if session_id:
        existing_conv = await conversations.find_one({
            "session_id": session_id,
            "student_id": student_id
        })
        if existing_conv:
            existing_state = existing_conv.get("state")
    else:
        session_id = str(ObjectId())
        await conversations.insert_one({
            "session_id": session_id,
            "student_id": student_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "state": None
        })

    async def event_generator():
        result = await run_naviiq_agent(
            student_id=student_id,
            session_id=session_id,
            user_message=data.message,
            existing_state=existing_state
        )

        await conversations.update_one(
            {"session_id": session_id},
            {"$set": {
                "state": result["state"],
                "current_stage": result["current_stage"],
                "is_complete": result["is_complete"],
                "updated_at": datetime.utcnow()
            }}
        )

        response_text = result["response"]
        words = response_text.split(" ")

        for i, word in enumerate(words):
            chunk = word if i == len(words) - 1 else word + " "
            yield f"data: {json.dumps({'token': chunk})}\n\n"

        yield f"data: {json.dumps({'done': True, 'session_id': session_id, 'current_stage': result['current_stage'], 'is_complete': result['is_complete'], 'roadmap_complete': result.get('roadmap_complete', False), 'share_token': result.get('share_token')})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- TEST ENDPOINT ---

@router.get("/test")
async def chat_test():
    return {"message": "Chat route is working"}