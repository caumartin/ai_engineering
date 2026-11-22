"""
API REST profesional - Sistema Intelligence (Entrega Final)
"""
import os
import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from app.observability import setup_observability
from app.worker import run_graph_task, resume_graph_task, get_job_status, update_job_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Consulta o tarea a resolver")
    is_critical: Optional[bool] = Field(False, description="Si es True, requiere aprobación humana (HITL)")


class ApprovalRequest(BaseModel):
    approved: bool = Field(..., description="True para aprobar, False para rechazar")


class TaskResponse(BaseModel):
    job_id: str
    status: str
    message: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_observability()
    logger.info("Sistema Intelligence iniciado.")
    yield
    logger.info("Sistema Intelligence detenido.")


app = FastAPI(
    title="Sistema Intelligence - Entrega Final",
    description="Sistema multi-agente con Supervisor + RAG + API asíncrona + Observabilidad",
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
    return {"status": "ok", "service": "intelligence-system"}


@app.post("/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """Encola una tarea y devuelve un job_id inmediatamente (no bloquea)."""
    job_id = str(uuid.uuid4())
    await update_job_status(job_id, "PENDING")
    background_tasks.add_task(run_graph_task, job_id, request.query, request.is_critical or False)
    return TaskResponse(
        job_id=job_id,
        status="PENDING",
        message="Tarea encolada. Usa GET /tasks/{job_id} para consultar el estado.",
    )


@app.get("/tasks/{job_id}")
async def get_task(job_id: str):
    """Consulta el estado de una tarea."""
    status = await get_job_status(job_id)
    if status.get("status") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, **status}


@app.post("/tasks/{job_id}/approve")
async def approve_task(job_id: str, approval: ApprovalRequest, background_tasks: BackgroundTasks):
    """Aprueba o rechaza una tarea en estado WAITING_APPROVAL (HITL)."""
    status = await get_job_status(job_id)
    if status.get("status") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="Job not found")
    if status.get("status") != "WAITING_APPROVAL":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not waiting for approval. Current status: {status.get('status')}",
        )
    background_tasks.add_task(resume_graph_task, job_id, approval.approved)
    return {
        "job_id": job_id,
        "status": "RUNNING",
        "message": f"Aprobación recibida ({'aprobado' if approval.approved else 'rechazado'}). Reanudando.",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
