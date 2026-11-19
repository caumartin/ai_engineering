"""
Observabilidad: inicialización de Arize Phoenix (OpenInference) o LangSmith.
"""
import os
import logging

logger = logging.getLogger(__name__)


def setup_observability():
    """
    Configura instrumentación de trazas.
    Prioridad: Phoenix (local/self-hosted) > LangSmith.
    """
    phoenix_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006")
    langsmith_key = os.getenv("LANGSMITH_API_KEY")

    if os.getenv("ENABLE_PHOENIX", "true").lower() == "true":
        try:
            from phoenix.otel import register
            from openinference.instrumentation.langchain import LangChainInstrumentor

            tracer_provider = register(
                project_name=os.getenv("PHOENIX_PROJECT", "multi-agent-api"),
                endpoint=f"{phoenix_endpoint}/v1/traces",
                auto_instrument=True,
            )
            LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
            logger.info(f"Phoenix observability enabled → {phoenix_endpoint}")
            return "phoenix"
        except Exception as e:
            logger.warning(f"Phoenix setup failed: {e}. Falling back to LangSmith if available.")

    if langsmith_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_API_KEY"] = langsmith_key
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "multi-agent-api")
        logger.info("LangSmith tracing enabled")
        return "langsmith"

    logger.warning("No observability backend configured. Traces will not be exported.")
    return None
