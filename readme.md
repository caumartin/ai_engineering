# API de Producción - Sistema Multi-Agente (Pre-entrega 7)

API REST asíncrona (FastAPI) que expone el orquestador multi-agente del Módulo 6, con:

- Endpoints asíncronos (encola y devuelve `job_id`)
- Persistencia de estado y checkpoints con **Redis** (`RedisSaver`)
- Observabilidad con **Arize Phoenix** (OpenInference) o LangSmith
- Flujo **Human-in-the-Loop** (HITL) para tareas críticas
- Manejo de errores: estado `FAILED` en Redis ante excepciones


## Estructura

```
├── app/
│   ├── main.py          # FastAPI: POST /tasks, GET /tasks/{id}, POST /tasks/{id}/approve
│   ├── graph.py         # Orquestador multi-agente + RedisSaver + nodo HITL
│   ├── worker.py        # Ejecución en background + actualización de estado en Redis
│   ├── observability.py # Init de Phoenix / LangSmith
│   └── hitl.py          # Nodo de aprobación humana (interrupt)
├── agents/
│   ├── state.py
│   ├── research_agent.py
│   └── analyst_agent.py
├── requirements.txt
├── docker-compose.yml   # API + Redis + Phoenix
├── Dockerfile
├── .env.example
└── screenshots/         # Capturas del dashboard (trazas, costo, latencia p95)
```


## Requisitos

- Python 3.12+
- Docker & Docker Compose (recomendado)
- API key de Google AI Studio (`GOOGLE_API_KEY`)


## Cómo levantar (recomendado: API local + Redis/Phoenix en Docker)

1. Configura variables de entorno:

```bash
cp .env.example .env
# Edita .env y pon tu GOOGLE_API_KEY
```

2. Levanta solo Redis y Phoenix:

```bash
docker compose up -d
```

- Redis → `localhost:6379`
- Phoenix (dashboard) → `http://localhost:6006`

3. Instala dependencias y corre la API localmente:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

La API queda en `http://localhost:8000`.



## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/tasks` | Encola tarea. Devuelve `job_id` inmediatamente. |
| `GET` | `/tasks/{job_id}` | Consulta estado (`PENDING`, `RUNNING`, `WAITING_APPROVAL`, `DONE`, `FAILED`) |
| `POST` | `/tasks/{job_id}/approve` | Aprueba/rechaza tarea en HITL |
| `GET` | `/health` | Health check |


### Ejemplo de uso

```bash
# Crear tarea
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"query": "Analiza el mercado de IA y da sentimiento general", "is_critical": false}'

# Consultar estado
curl http://localhost:8000/tasks/<job_id>

# Tarea crítica (se detiene en HITL)
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"query": "Ejecutar análisis crítico del mercado y generar reporte de producción", "is_critical": true}'

# Aprobar
curl -X POST http://localhost:8000/tasks/<job_id>/approve \
  -H "Content-Type: application/json" \
  -d '{"approved": true}'
```


## Prueba de carga (5 peticiones concurrentes)

```bash
# Script de prueba concurrente
for i in {1..5}; do
  curl -X POST http://localhost:8000/tasks \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"Analiza el estado del mercado de IA $i\", \"is_critical\": false}" &
done
wait
```

## Observabilidad

1. Abrir Phoenix en `http://localhost:6006`
2. Ejecutar las 5 peticiones concurrentes
3. En el dashboard se verán:
   - Trazas de cada nodo del grafo (supervisor, research, analyst)
   - Costo por ejecución (calculado automáticamente a partir de tokens)
   - Latencia p95


## Estados de un job

| Estado | Significado |
|--------|-------------|
| `PENDING` | Encolado |
| `RUNNING` | Ejecutando el grafo |
| `WAITING_APPROVAL` | Pausado en HITL (esperando `POST /approve`) |
| `DONE` | Completado exitosamente |
| `FAILED` | Falló (excepción capturada y estado actualizado) |

