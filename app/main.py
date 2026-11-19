"""
FastAPI application: API REST asíncrona para el sistema multi-agente.
"""
import os
import uuid
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from app.observability import setup_observability
from app.worker import run_graph_task, resume_graph_task, get_job_status, update_job_status

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskRequest(BaseModel):
    query: str
    is_critical: Optional[bool] = False


class ApprovalRequest(BaseModel):
    approved: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_observability()
    logger.info("API started. Observability configured.")
    yield
    # Shutdown
    logger.info("API shutting down.")


app = FastAPI(
    title="Multi-Agent Production API",
    description="API asíncrona con Redis, observabilidad y HITL para el orquestador multi-agente",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/tasks")
async def create_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Recibe una tarea, la encola y devuelve un job_id inmediatamente.
    No bloquea el event loop.
    """
    job_id = str(uuid.uuid4())
    await update_job_status(job_id, "PENDING")

    # Encolar en background (no bloquea)
    background_tasks.add_task(run_graph_task, job_id, request.query, request.is_critical)

    return {
        "job_id": job_id,
        "status": "PENDING",
        "message": "Tarea encolada. Usa GET /tasks/{job_id} para consultar el estado.",
    }


@app.get("/tasks/{job_id}")
async def get_task(job_id: str):
    """Consulta el estado de una tarea (no bloquea)."""
    status = await get_job_status(job_id)
    if status.get("status") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, **status}


@app.post("/tasks/{job_id}/approve")
async def approve_task(job_id: str, approval: ApprovalRequest, background_tasks: BackgroundTasks):
    """
    Aprueba o rechaza una tarea que está esperando aprobación humana (HITL).
    Reanuda la ejecución del grafo.
    """
    status = await get_job_status(job_id)
    if status.get("status") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="Job not found")
    if status.get("status") != "WAITING_APPROVAL":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not waiting for approval. Current status: {status.get('status')}"
        )

    background_tasks.add_task(resume_graph_task, job_id, approval.approved)

    return {
        "job_id": job_id,
        "status": "RUNNING",
        "message": f"Aprobación recibida ({'aprobado' if approval.approved else 'rechazado'}). Reanudando ejecución.",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
