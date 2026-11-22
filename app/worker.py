"""Worker asíncrono para ejecución de tareas en background."""
import os
import json
import logging
import traceback
from typing import Optional
import redis.asyncio as redis
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from langgraph.errors import GraphInterrupt

from app.graph import build_graph

logger = logging.getLogger(__name__)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


async def get_redis():
    return redis.from_url(REDIS_URL, decode_responses=True)


async def update_job_status(
    job_id: str,
    status: str,
    result: Optional[dict] = None,
    error: Optional[str] = None,
    interrupt_payload: Optional[dict] = None,
):
    r = await get_redis()
    data = {
        "status": status,
        "result": json.dumps(result) if result else None,
        "error": error,
        "interrupt": json.dumps(interrupt_payload) if interrupt_payload else None,
    }
    await r.hset(f"job:{job_id}", mapping={k: v for k, v in data.items() if v is not None})
    await r.expire(f"job:{job_id}", 86400)
    await r.aclose()


async def get_job_status(job_id: str) -> dict:
    r = await get_redis()
    data = await r.hgetall(f"job:{job_id}")
    await r.aclose()
    if not data:
        return {"status": "NOT_FOUND"}
    result = {"status": data.get("status", "UNKNOWN"), "error": data.get("error")}
    if data.get("result"):
        try:
            result["result"] = json.loads(data["result"])
        except Exception:
            result["result"] = data["result"]
    if data.get("interrupt"):
        try:
            result["interrupt"] = json.loads(data["interrupt"])
        except Exception:
            result["interrupt"] = data["interrupt"]
    return result


async def run_graph_task(job_id: str, user_query: str, is_critical: bool = False):
    try:
        await update_job_status(job_id, "RUNNING")
        graph = await build_graph()
        config = {"configurable": {"thread_id": job_id}}

        initial_state = {
            "messages": [HumanMessage(content=user_query)],
            "user_query": user_query,
            "iteration_count": 0,
            "task_completed": False,
            "contributions": [],
            "research_data": None,
            "analysis_result": None,
            "rag_context": None,
            "is_critical": is_critical,
            "job_id": job_id,
        }

        try:
            final_state = None
            async for event in graph.astream(initial_state, config, stream_mode="values"):
                final_state = event

            state_snapshot = await graph.aget_state(config)
            if state_snapshot and state_snapshot.next:
                interrupt_info = None
                if hasattr(state_snapshot, "tasks") and state_snapshot.tasks:
                    for task in state_snapshot.tasks:
                        if hasattr(task, "interrupts") and task.interrupts:
                            interrupt_info = task.interrupts[0].value if task.interrupts else None
                            break
                await update_job_status(
                    job_id,
                    "WAITING_APPROVAL",
                    interrupt_payload=interrupt_info or {"message": "Human approval required"},
                )
                return

            result = {
                "research_data": final_state.get("research_data") if final_state else None,
                "analysis_result": final_state.get("analysis_result") if final_state else None,
                "rag_context": final_state.get("rag_context") if final_state else None,
                "contributions": final_state.get("contributions") if final_state else [],
                "iterations": final_state.get("iteration_count") if final_state else 0,
            }
            await update_job_status(job_id, "DONE", result=result)

        except GraphInterrupt as gi:
            payload = gi.args[0] if gi.args else {"message": "Interrupt triggered"}
            await update_job_status(job_id, "WAITING_APPROVAL", interrupt_payload=payload)

    except Exception as e:
        tb = traceback.format_exc()
        error_msg = f"{type(e).__name__}: {str(e) or repr(e)}\n{tb[-1500:]}"
        logger.exception(f"Task {job_id} failed")
        await update_job_status(job_id, "FAILED", error=error_msg)


async def resume_graph_task(job_id: str, approved: bool):
    try:
        await update_job_status(job_id, "RUNNING")
        graph = await build_graph()
        config = {"configurable": {"thread_id": job_id}}

        resume_value = {"approved": approved}
        final_state = None
        async for event in graph.astream(Command(resume=resume_value), config, stream_mode="values"):
            final_state = event

        result = {
            "research_data": final_state.get("research_data") if final_state else None,
            "analysis_result": final_state.get("analysis_result") if final_state else None,
            "rag_context": final_state.get("rag_context") if final_state else None,
            "contributions": final_state.get("contributions") if final_state else [],
            "iterations": final_state.get("iteration_count") if final_state else 0,
            "human_approved": approved,
        }
        await update_job_status(job_id, "DONE", result=result)

    except Exception as e:
        tb = traceback.format_exc()
        error_msg = f"{type(e).__name__}: {str(e) or repr(e)}\n{tb[-1500:]}"
        logger.exception(f"Resume task {job_id} failed")
        await update_job_status(job_id, "FAILED", error=error_msg)
