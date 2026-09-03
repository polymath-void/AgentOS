"""
main.py — FastAPI server with JWT auth, multi-tenancy, workflows, and scheduling.

Routes:
  Public:
    GET  /              → Landing page
    GET  /health        → Health check
    POST /auth/register → Create account
    POST /auth/login    → Get JWT token

  Protected (JWT required):
    POST /chat          → Chat with agent
    POST /workflow      → Execute self-healing workflow ⭐
    GET  /cards         → List user's cards
    POST /cards         → Create card from prompt
    GET  /cards/{id}    → Get card detail
    DELETE /cards/{id}  → Delete card
    GET  /auth/me       → Get user profile
    PUT  /auth/api-key  → Update Gemini API key
    GET  /auth/history  → Get chat history
    GET  /schedules     → List user's schedules ⏰
    POST /schedules     → Create a schedule ⏰
    DELETE /schedules/{id} → Delete a schedule
    PUT  /schedules/{id}/toggle → Enable/disable schedule

  App:
    GET  /app           → Chat PWA (requires login)
"""

from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager

import auth
import card_store
import database
import dependency_manager
import intent_router
import tool_executor
from fastapi import Depends, FastAPI, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from gemini_engine import GeminiEngine, GeminiEngineError
from models import AgentResponse, CardCreationRequest, TaskRequest

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

_engine: GeminiEngine | None = None
_workflow_engine = None
_tool_status: dict = {}

# Model fallback list (in order of preference)
MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-pro",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _engine, _workflow_engine, _tool_status
    logger.info("SaaS-Agent v2: startup…")

    # Initialize multi-tenant database
    database.get_conn()

    _tool_status = dependency_manager.check_and_install_dependencies()

    try:
        _engine = GeminiEngine()
    except GeminiEngineError as exc:
        logger.error(f"GeminiEngine init failed: {exc}")
        _engine = None

    # Initialize self-healing workflow engine
    if _engine:
        from workflow_engine import WorkflowEngine
        _workflow_engine = WorkflowEngine(_engine)
        logger.info("WorkflowEngine: ready ⚡")

        # Start scheduled autopilot background thread
        import scheduler
        scheduler.start_scheduler(_workflow_engine, _engine)
        logger.info("Scheduler: autopilot started ⏰")

    yield
    logger.info("SaaS-Agent v2: shutdown…")
    import scheduler
    scheduler.stop_scheduler()
    database.close()


app = FastAPI(
    title="SaaS-Agent v2",
    description="AI-powered personal agent platform with multi-tenant auth.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Public Routes
# ---------------------------------------------------------------------------


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "engine": "ready" if _engine else "unavailable",
        "workflow_engine": "ready" if _workflow_engine else "unavailable",
        "tools": _tool_status,
        "available_models": MODELS,
    }


# ---------------------------------------------------------------------------
# Auth Routes
# ---------------------------------------------------------------------------


@app.post("/auth/register", response_model=auth.TokenResponse)
async def register(request: auth.RegisterRequest):
    """Register a new user account."""
    user = auth.create_user(
        email=request.email,
        password=request.password,
        display_name=request.display_name,
    )

    # Seed default cards for this new user
    card_store.seed_cards_for_user(user["id"])

    token = auth.create_token(user["id"], user["email"])
    return auth.TokenResponse(
        access_token=token,
        user=auth.UserProfile(**user),
    )


@app.post("/auth/login", response_model=auth.TokenResponse)
async def login(request: auth.LoginRequest):
    """Login and receive a JWT token."""
    user = auth.authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = auth.create_token(user["id"], user["email"])
    return auth.TokenResponse(
        access_token=token,
        user=auth.UserProfile(**user),
    )


@app.get("/auth/me")
async def get_profile(current_user: dict = Depends(auth.get_current_user)):
    """Get current user's profile."""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "display_name": current_user["display_name"],
        "plan": current_user["plan"],
        "has_api_key": bool(current_user.get("gemini_api_key")),
        "preferred_model": current_user.get("preferred_model", "gemini-2.5-flash"),
        "messages_today": current_user.get("messages_today", 0),
        "created_at": current_user["created_at"],
    }


@app.put("/auth/api-key")
async def update_api_key(
    request: auth.ApiKeyUpdate,
    current_user: dict = Depends(auth.get_current_user),
):
    """Store Gemini API key server-side (no more client-side storage)."""
    auth.update_user_api_key(current_user["id"], request.api_key, request.model)
    return {"status": "ok", "message": "API key saved securely."}


@app.get("/auth/history")
async def get_history(
    limit: int = 50,
    current_user: dict = Depends(auth.get_current_user),
):
    """Get user's chat history."""
    history = auth.get_chat_history(current_user["id"], limit=limit)
    return {"history": history}


# ---------------------------------------------------------------------------
# Chat Route (Protected)
# ---------------------------------------------------------------------------


@app.post("/chat")
async def chat(
    request: TaskRequest,
    current_user: dict = Depends(auth.get_current_user),
):
    """Chat endpoint — uses server-side API key, supports model fallback."""
    if _engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GeminiEngine not ready.",
        )

    # Check rate limit
    auth.check_rate_limit(current_user)

    # Use server-side API key
    api_key = current_user.get("gemini_api_key", "")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Gemini API key configured. Go to Settings → API Key to add one.",
        )

    # Configure engine with user's key
    from google import genai
    _engine._api_key = api_key
    _engine._client = genai.Client(api_key=api_key)

    # Determine model (user preference → env → default)
    selected_model = current_user.get("preferred_model") or MODELS[0]

    # Resolve card (user-scoped)
    user_id = current_user["id"]
    if request.card_id:
        card = card_store.resolve_card(request.card_id, user_id=user_id)
    else:
        all_cards = card_store.get_all_cards_for_user(user_id)
        classification = intent_router.classify_with_recommendation(request.task, all_cards)
        card = card_store.resolve_card(classification.recommended_card_id, user_id=user_id)

    # Save user message to history
    auth.save_chat_message(
        user_id=user_id,
        role="user",
        content=request.task,
    )

    # Try LLM with fallback
    agent_response = None
    used_model = None
    fallback_used = False

    models_to_try = [selected_model] + [m for m in MODELS if m != selected_model]

    for model in models_to_try:
        try:
            logger.info(f"Trying model: {model}")
            _engine._model = model
            agent_response = _engine.execute(
                task=request.task,
                card=card,
                local_context=request.local_context,
            )
            used_model = model
            if model != selected_model:
                fallback_used = True
            break
        except GeminiEngineError as e:
            error_msg = str(e)
            if "503" in error_msg or "UNAVAILABLE" in error_msg or "429" in error_msg:
                logger.warning(f"Model {model} unavailable, trying fallback…")
                fallback_used = True
                continue
            else:
                logger.error(f"LLM error with {model}: {e}")
                raise HTTPException(status_code=502, detail=str(e))

    if not agent_response:
        raise HTTPException(
            status_code=503,
            detail="All models temporarily unavailable. Please try again.",
        )

    # Execute tools
    tool_results = []
    if agent_response.tool_calls:
        for tc in agent_response.tool_calls:
            result = tool_executor.execute_tool(tc)
            tool_results.append({"tool": tc.tool_name, "result": result})

    # Save assistant response to history
    auth.save_chat_message(
        user_id=user_id,
        role="assistant",
        content=agent_response.reply,
        card_id=card.id,
        model_used=used_model or "",
        tool_results=json.dumps(tool_results),
    )

    # Increment message counter
    auth.increment_message_count(user_id)

    return JSONResponse({
        "card_id": card.id,
        "card_name": card.name,
        "reply": agent_response.reply,
        "execution_mode": agent_response.execution_mode,
        "tool_results": tool_results,
        "json_data": agent_response.json_data,
        "summary_points": agent_response.summary_points,
        "model_used": used_model,
        "fallback_used": fallback_used,
    })


# ---------------------------------------------------------------------------
# Card Routes (Protected)
# ---------------------------------------------------------------------------


@app.get("/cards")
async def list_cards(current_user: dict = Depends(auth.get_current_user)):
    """List current user's cards."""
    cards = card_store.list_cards(user_id=current_user["id"])
    return {"cards": cards}


@app.post("/cards")
async def create_card_from_prompt(
    request: CardCreationRequest,
    current_user: dict = Depends(auth.get_current_user),
):
    """Create card from user description (LLM generates system_prompt)."""
    if _engine is None:
        raise HTTPException(status_code=503, detail="GeminiEngine not ready.")

    # Check card limit
    user_cards = card_store.list_cards(user_id=current_user["id"])
    plan = current_user.get("plan", "free")
    max_cards = auth.PLAN_LIMITS.get(plan, auth.PLAN_LIMITS["free"])["max_cards"]
    if len(user_cards) >= max_cards:
        raise HTTPException(
            status_code=403,
            detail=f"Card limit reached ({max_cards} on {plan} plan). Upgrade to create more.",
        )

    try:
        from models import AgentCard

        # Ensure engine has a valid API key
        api_key = current_user.get("gemini_api_key", "")
        if not api_key:
            raise HTTPException(status_code=400, detail="Set your API key first.")

        from google import genai
        _engine._api_key = api_key
        _engine._client = genai.Client(api_key=api_key)

        # Generate system_prompt via LLM
        prompt = (
            f"User wants to create an AI agent:\n{request.user_description}\n\n"
            "Generate a specific system_prompt (2-3 paragraphs) for this agent."
        )

        system_card = card_store.get_system_agent(user_id=current_user["id"])
        gen_response = _engine.execute(
            task=prompt,
            card=system_card,
            local_context={},
        )
        system_prompt = gen_response.reply

        # Create card scoped to this user
        card = AgentCard(
            name=request.suggested_name or "Custom Card",
            description=request.user_description[:100],
            system_prompt=system_prompt,
            scope_tags=request.scope_tags,
            execution_mode="function_calling",
        )
        saved = card_store.save_card(card, user_id=current_user["id"])

        return {
            "status": "created",
            "card_id": saved.id,
            "card": saved.model_dump(),
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Card creation failed: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/cards/{card_id}")
async def get_card(
    card_id: str,
    current_user: dict = Depends(auth.get_current_user),
):
    """Get a specific card (user-scoped)."""
    card = card_store.get_card(card_id, user_id=current_user["id"])
    if not card:
        raise HTTPException(status_code=404, detail=f"Card {card_id} not found.")
    return card.model_dump()


@app.delete("/cards/{card_id}")
async def delete_card(
    card_id: str,
    current_user: dict = Depends(auth.get_current_user),
):
    """Delete a user-created card."""
    try:
        deleted = card_store.delete_card(card_id, user_id=current_user["id"])
    except card_store.CardStoreError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not deleted:
        raise HTTPException(status_code=404)
    return {"status": "deleted"}


# ---------------------------------------------------------------------------
# Workflow Route (Protected) — THE KILLER FEATURE
# ---------------------------------------------------------------------------


@app.post("/workflow")
async def execute_workflow(
    request: TaskRequest,
    current_user: dict = Depends(auth.get_current_user),
):
    """Execute a self-healing multi-step workflow."""
    if _workflow_engine is None:
        raise HTTPException(status_code=503, detail="WorkflowEngine not ready.")

    auth.check_rate_limit(current_user)

    api_key = current_user.get("gemini_api_key", "")
    if not api_key:
        raise HTTPException(status_code=400, detail="No API key. Go to Settings.")

    user_id = current_user["id"]
    card = card_store.resolve_card(request.card_id, user_id=user_id)

    # Save user message
    auth.save_chat_message(user_id=user_id, role="user", content=request.task)

    # Execute self-healing workflow
    result = _workflow_engine.execute_workflow(
        task=request.task,
        card=card,
        local_context=request.local_context or {},
        user_api_key=api_key,
        user_model=current_user.get("preferred_model", "gemini-2.5-flash"),
    )

    # Save result to history
    step_summary = []
    for s in result.step_results:
        icon = {"success": "✅", "healed": "🔧", "failed": "❌", "skipped": "⏭"}.get(s.status, "❓")
        step_summary.append(f"{icon} {s.title} ({s.status}, {s.duration_ms}ms)")

    auth.save_chat_message(
        user_id=user_id,
        role="assistant",
        content=f"{result.reply}\n\nWorkflow: {result.status} ({result.duration_ms}ms)\n" + "\n".join(step_summary),
        card_id=card.id,
    )
    auth.increment_message_count(user_id)

    return JSONResponse({
        "workflow_id": result.workflow_id,
        "card_name": result.card_name,
        "reply": result.reply,
        "status": result.status,
        "step_results": [s.model_dump() for s in result.step_results],
        "context_variables": result.context_variables,
        "duration_ms": result.duration_ms,
    })


# ---------------------------------------------------------------------------
# Schedule Routes (Protected) — AUTOPILOT
# ---------------------------------------------------------------------------


@app.get("/schedules")
async def list_schedules(current_user: dict = Depends(auth.get_current_user)):
    """List user's scheduled tasks."""
    import scheduler
    schedules = scheduler.list_schedules(current_user["id"])
    return {"schedules": schedules}


@app.post("/schedules")
async def create_schedule(
    request: dict,
    current_user: dict = Depends(auth.get_current_user),
):
    """Create a new scheduled task."""
    import scheduler
    try:
        sched = scheduler.ScheduleCreate(**request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    result = scheduler.create_schedule(current_user["id"], sched)
    return result.model_dump()


@app.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    current_user: dict = Depends(auth.get_current_user),
):
    """Delete a scheduled task."""
    import scheduler
    deleted = scheduler.delete_schedule(schedule_id, current_user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Schedule not found.")
    return {"status": "deleted"}


@app.put("/schedules/{schedule_id}/toggle")
async def toggle_schedule(
    schedule_id: str,
    current_user: dict = Depends(auth.get_current_user),
    enabled: bool = True,
):
    """Enable or disable a schedule."""
    import scheduler
    toggled = scheduler.toggle_schedule(schedule_id, current_user["id"], enabled)
    if not toggled:
        raise HTTPException(status_code=404, detail="Schedule not found.")
    return {"status": "enabled" if enabled else "disabled"}


# ---------------------------------------------------------------------------
# Static File Serving
# ---------------------------------------------------------------------------


@app.get("/")
async def serve_landing():
    """Serve the landing page."""
    landing = os.path.join("static", "index.html")
    if os.path.exists(landing):
        return FileResponse(landing, media_type="text/html")
    # Fallback to app if no landing page
    return FileResponse("static/app.html", media_type="text/html")


@app.get("/app")
async def serve_app():
    """Serve the chat app PWA."""
    return FileResponse("static/app.html", media_type="text/html")


@app.get("/{full_path:path}")
async def serve_static(full_path: str):
    """Serve static files (manifest, service worker, etc.)."""
    static_path = os.path.join("static", full_path)
    if os.path.exists(static_path):
        return FileResponse(static_path)
    return FileResponse("static/app.html")


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("SAAS_AGENT_HOST", "0.0.0.0")
    port = int(os.environ.get("SAAS_AGENT_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
