"""Configuración de observabilidad con Arize Phoenix."""
import os
import logging

logger = logging.getLogger(__name__)


def setup_observability():
    """Inicializa Phoenix / OpenInference si está disponible."""
    try:
        from phoenix.otel import register
        from openinference.instrumentation.langchain import LangChainInstrumentor

        # HTTP endpoint (puerto 6006)
        endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces")
        project = os.getenv("PHOENIX_PROJECT_NAME", "intelligence-system")

        tracer_provider = register(
            project_name=project,
            endpoint=endpoint,
            protocol="http/protobuf",
            auto_instrument=True,
        )
        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
        logger.info(f"Observabilidad Phoenix configurada → {endpoint} (proyecto: {project})")
    except Exception as e:
        logger.warning(f"No se pudo configurar Phoenix: {e}. Continuando sin trazas.")
