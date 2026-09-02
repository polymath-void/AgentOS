"""
main.py — SaaS-Agent FastAPI Server with Contextual Agentic Workflow Execution Engine
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import card_store
import tool_executor
from gemini_engine import GeminiEngine, GeminiEngineError
from models import AgentCard, TaskExecutionResult, TaskRequest, ToolCall
from workflow_engine import WorkflowEngine

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------

_engine: GeminiEngine | None = None
_workflow_engine: WorkflowEngine | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _engine, _workflow_engine
    logger.info("Unified Agent: starting up system control plane...")
    
    # Initialise card store (creates DB + tables + seeds System Agent)
    card_store.get_system_agent()

    # Initialise Gemini engine & Workflow engine
    try:
        _engine = GeminiEngine()
        _workflow_engine = WorkflowEngine(_engine)
        logger.info("Unified Agent: Contextual Workflow Engine online.")
    except GeminiEngineError as exc:
        logger.error("GeminiEngine init failed: %s", exc)

    yield
    logger.info("Unified Agent: shutting down...")
    card_store.close()


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Unified-Agent",
    description="Contextual Agentic Workflows Task Executor Agent Control Plane",
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
# Routes
# ---------------------------------------------------------------------------


@app.get("/health", tags=["meta"])
async def health():
    return {
        "status": "ok",
        "engine": "ready" if _engine is not None else "unavailable",
        "workflow_engine": "ready" if _workflow_engine is not None else "unavailable",
    }


@app.get("/state", tags=["meta"])
async def get_state():
    return {
        "engine_ready": _engine is not None,
        "workflow_engine_ready": _workflow_engine is not None,
        "cards_loaded": len(card_store.list_cards()),
        "total_tasks_executed": card_store.get_total_tasks_count(),
    }


@app.get("/tasks/history", tags=["meta"])
async def get_history(limit: int = 30):
    return {"history": card_store.get_task_history(limit=limit)}


@app.get("/cards", tags=["cards"])
async def list_cards():
    return {"cards": card_store.list_cards()}


@app.get("/cards/{card_id}", tags=["cards"])
async def get_card(card_id: str):
    card = card_store.get_card(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Card {card_id} not found.")
    return card.model_dump()


@app.delete("/cards/{card_id}", tags=["cards"])
async def delete_card(card_id: str):
    try:
        deleted = card_store.delete_card(card_id)
    except card_store.CardStoreError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Card {card_id} not found.")
    return {"status": "deleted", "card_id": card_id}


@app.post("/execute")
async def execute(request: TaskRequest):
    global _workflow_engine
    if _workflow_engine is None:
        raise HTTPException(status_code=503, detail="Workflow Engine is not ready (check GEMINI_API_KEY).")

    # Resolve active card or fall back to System Agent
    active_card = card_store.resolve_card(request.card_id)

    try:
        # Execute contextual workflow
        task_result: TaskExecutionResult = _workflow_engine.execute_workflow(
            task=request.task,
            card=active_card,
            local_context=request.local_context,
        )

        res_dict = task_result.model_dump()
        
        # Build backwards-compatible tool_results array for CLI clients
        tool_results = [
            {
                "command": step.target,
                "status": step.status,
                "output": step.output,
                "title": step.title,
            }
            for step in task_result.step_results
        ]
        res_dict["tool_results"] = tool_results

        return JSONResponse(content=jsonable_encoder(res_dict))

    except Exception as exc:
        logger.error("Workflow execution failure: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Workflow execution failure: {exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    host = os.environ.get("SAAS_AGENT_HOST", "127.0.0.1")
    port = int(os.environ.get("SAAS_AGENT_PORT", "8000"))
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level=os.environ.get("LOG_LEVEL", "info").lower(),
    )
