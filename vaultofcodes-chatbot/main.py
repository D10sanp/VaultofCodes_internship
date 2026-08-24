"""
main.py

FastAPI backend for the VaultOfCodes AI Website Support Chatbot.

Endpoints:
    GET  /                          -> serves the chat widget demo page
    GET  /api/suggested-questions   -> quick-action questions for chat open
    POST /api/chat                  -> main chat endpoint
    GET  /api/health                -> simple health check

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from intent_classifier import classify_intent, needs_escalation
from knowledge_base import KB
from router import build_response, resolve_context

app = FastAPI(
    title="VaultOfCodes Support Chatbot",
    description="AI-powered first-level support & inquiry assistant for the VaultOfCodes website.",
    version="1.0.0",
)

# Allow the widget to be embedded from the VaultOfCodes website domain (and
# anywhere, for local testing). Tighten allow_origins in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# ----------------------------------------------------------------------
# In-memory conversation store.
# session_id -> {"last_topic": str | None, "history": [ {role, text, intent?} ]}
#
# NOTE: This is intentionally simple in-process memory suitable for a demo /
# single-instance deployment. For production with multiple server instances,
# swap this for Redis or a database keyed by session_id.
# ----------------------------------------------------------------------
SESSIONS: dict[str, dict] = {}

MAX_HISTORY_TURNS = 20  # cap stored history per session to avoid unbounded growth


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class LinkOut(BaseModel):
    label: str
    url: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    intent: str
    links: list[LinkOut] = []
    escalate: bool = False
    escalate_reason: str | None = None
    whatsapp_link: str | None = None
    quick_replies: list[str] = []


@app.get("/")
def serve_index():
    return FileResponse("static/index.html")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/suggested-questions")
def suggested_questions():
    return {"questions": KB["suggested_questions"]}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    session = SESSIONS.setdefault(session_id, {"last_topic": None, "history": []})

    user_msg = (req.message or "").strip()
    if not user_msg:
        return ChatResponse(
            session_id=session_id,
            reply="Could you type your question? I'm here to help with courses, internships, certificates, and more.",
            intent="unknown",
        )

    session["history"].append({"role": "user", "text": user_msg})

    # --- Conversation memory: resolve pronouns like "its duration" using last_topic ---
    resolved_msg = resolve_context(user_msg, session)

    # --- Escalation check runs independent of / prior to intent-specific answers ---
    escalate, escalate_reason = needs_escalation(resolved_msg)

    # --- Intent classification ---
    intent = classify_intent(resolved_msg)

    # Some intents are *always* handed to human support regardless of exact
    # phrasing (spec section 7: explicit human request, and unresolved
    # technical problems the bot has no fix for).
    if not escalate and intent in ("technical_support", "human_support"):
        escalate, escalate_reason = True, intent

    # --- Smart routing: decide the actual reply, links, and topic to remember ---
    reply, links, quick_replies, topic = build_response(intent, resolved_msg, escalate, escalate_reason)

    if topic:
        session["last_topic"] = topic

    session["history"].append({"role": "bot", "text": reply, "intent": intent})
    session["history"] = session["history"][-(MAX_HISTORY_TURNS * 2):]

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        intent=intent,
        links=[LinkOut(**l) for l in links],
        escalate=escalate,
        escalate_reason=escalate_reason,
        whatsapp_link=KB["support"]["whatsapp_link"] if escalate else None,
        quick_replies=quick_replies,
    )


@app.get("/api/session/{session_id}/history")
def get_history(session_id: str):
    """Debug/testing helper to inspect a session's conversation history."""
    session = SESSIONS.get(session_id)
    if not session:
        return {"session_id": session_id, "history": []}
    return {"session_id": session_id, "history": session["history"]}
