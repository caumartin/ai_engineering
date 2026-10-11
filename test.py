import asyncio
import logging
from chain import process_text

# Configuración de logs para el script de prueba
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("TestExecution")

async def main():

    # ---------------------------------------------------------------------------
    # Casos de prueba
    # ---------------------------------------------------------------------------
    CASOS_DE_PRUEBA = [
        {
            "nombre": "EJEMPLO_ARQUITECTURA",
            "texto": """
            Nuestra API está construida con FastAPI y utiliza Redis como capa de caché
            distribuida. La persistencia principal se realiza en PostgreSQL 15 con
            pgBouncer para el pool de conexiones. Últimamente estamos observando
            timeouts en las conexiones concurrentes cuando el tráfico supera los
            2000 RPS; el cuello de botella parece estar en el número máximo de
            conexiones del pool de pgBouncer.
            """,
        },
        {
            "nombre": "EJEMPLO_LOG_ERROR",
            "texto": """
                    [ERROR] 2025-03-12 14:22:01 - ConnectionPoolExhausted: Unable to acquire
                    connection from pool within 30s. Component: order-service (Spring Boot 3.2)
                    using HikariCP. Downstream: Kafka topic 'orders.created' and MongoDB
                    replica set. Circuit breaker opened after 5 consecutive failures.
                    """
        },
        {
            "nombre": "EJEMPLO_AMBIGUO",
            "texto": """
            El sistema a veces va lento. Usamos varias cosas en la nube y una base
            de datos. Hay que revisar los logs.
            """
        }
    ]

    logger.info("Ejecutando prueba unitaria del pipeline...")

    for caso in CASOS_DE_PRUEBA:
        logger.info(f"\n\nProcesando caso: {caso['nombre']}\n")
        try:
            resultado = await process_text({"input_text": caso["texto"]})
            print("\n" + "="*80)
            print(f"--- OBJETO VALIDADO OBTENIDO - {caso['nombre']} ---")
            print("="*80)
            print(resultado.model_dump_json(indent=2))
            print("="*80)
        except Exception as e:
            logger.error(f"La prueba falló debido a: {e}")

if __name__ == "__main__":
    asyncio.run(main())