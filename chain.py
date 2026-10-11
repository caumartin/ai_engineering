import logging
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from schemas import TechnicalEntitySchema, PipelineInput

import dotenv
dotenv.load_dotenv()


# Configuración de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("TechnicalExtractorPipeline")


# 1. Inicialización del modelo base y estructuración de salida
model = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)
structured_model = model.with_structured_output(TechnicalEntitySchema)
model_with_retry = structured_model.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)


# 2. Creación del Template de Prompt Modular
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """\
        Eres un experto en análisis de arquitectura de software, logs de error y \
        descripciones técnicas. Tu tarea es extraer entidades técnicas estructuradas \
        de textos no estructurados.

        Debes identificar:
        1. **tecnologias**: Todas las tecnologías, frameworks, lenguajes, bases de datos, \
        servicios cloud, herramientas de orquestación, cachés, colas, etc. que \
        aparezcan o se puedan inferir claramente del texto. Usa nombres canónicos \
        (ej. "PostgreSQL" en lugar de "postgres", "FastAPI" en lugar de "fastapi").
        2. **nivel_de_criticidad**: Evalúa el impacto:
        - "baja": información, mejoras cosméticas o situaciones sin riesgo inmediato.
        - "media": problemas de rendimiento, deuda técnica o riesgos moderados.
        - "alta": errores de producción, fallos críticos, pérdida de datos, \
            degradación severa o riesgos de seguridad/disponibilidad.
        3. **resumen_tecnico**: Un párrafo conciso (máx. ~80 palabras) que capture \
        el núcleo técnico del texto: qué ocurre, qué componentes intervienen y \
        cuál es el problema o característica principal.

        Responde ÚNICAMENTE con el objeto estructurado solicitado. No añadas \
        explicaciones fuera del esquema.
        """
    ),
    (
        "human",
        """\
        Analiza el siguiente texto y extrae las entidades técnicas:

        ---
        {input_text}
        ---

        Devuelve el resultado estructurado según el esquema definido.
        """
    )
])


# 3. Ensamblaje de la Cadena usando LCEL
chain = prompt | model_with_retry


# 4. Función asíncrona que valida la entrada usando PipelineInput y ejecuta la cadena
async def process_text(raw_data: dict) -> Optional[TechnicalEntitySchema]:
    logger.info("Validando datos de entrada con PipelineInput...")
    
    # Validamos y parseamos la entrada usando el esquema Pydantic de input
    validated_input = PipelineInput(**raw_data)
    
    logger.info("Iniciando pipeline de extracción con Gemini...")
    try:
        result = await chain.ainvoke({"input_text": validated_input.input_text})
        logger.info(f"Extracción y validación Pydantic completadas exitosamente: {result}")
        return result
    except Exception as e:
        logger.error(f"Fallo crítico en el pipeline tras agotar los reintentos automáticos: {e}")
        raise e
