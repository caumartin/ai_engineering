# Sistema Intelligence - Entrega Final

Sistema de IA de grado de producción que integra:

- **RAG** (recuperación de conocimiento)
- **Agentes multi-agente con Supervisor**
- **API REST profesional** (FastAPI, async)
- **Trazabilidad completa** (Arize Phoenix)
- **Persistencia de estado** (Redis + LangGraph Checkpointer)
- **Human-in-the-Loop** para tareas críticas

## Diagrama del Grafo de Agentes

```
                    ┌─────────────┐
                    │  SUPERVISOR │
                    └──────┬──────┘
                           │
         ┌─────────┬───────┼───────┬─────────┐
         ▼         ▼       ▼       ▼         ▼
      ┌─────┐  ┌────────┐ ┌──────┐ ┌──────┐  END
      │ RAG │  │Research│ │Analyst│ │ HITL │
      └──┬──┘  └───┬────┘ └───┬──┘ └───┬──┘
         │         │          │        │
         └─────────┴──────────┴────────┘
                           │
                    (vuelve a Supervisor)
```

El Supervisor decide dinámicamente el siguiente agente según el estado.  
Si la tarea es crítica, el flujo se pausa en HITL hasta recibir aprobación externa.

## Estructura

```
├── app/
│   ├── main.py           # FastAPI (endpoints async)
│   ├── graph.py          # Orquestador + AsyncRedisSaver
│   ├── worker.py         # Background tasks
│   ├── observability.py  # Phoenix / OpenInference
│   └── hitl.py           # Nodo Human-in-the-Loop
├── agents/
│   ├── state.py
│   ├── rag_agent.py
│   ├── research_agent.py
│   └── analyst_agent.py
├── rag/
│   └── retriever.py      # Chroma + embeddings
├── docker-compose.yml    # Redis Stack + Phoenix
├── requirements.txt
├── run.sh
└── screenshots/          # Trazas de Phoenix
```

## Cómo levantar (todo en Docker)

```bash
# 1. Configura el .env
cp .env.example .env
# Edita .env y pon tu GOOGLE_API_KEY

# 2. Levanta Redis + Phoenix + API
docker compose up -d --build
```

- API → `http://localhost:8000`
- Phoenix → `http://localhost:6006`
- Docs → `http://localhost:8000/docs`

Para ver logs de la API:
```bash
docker compose logs -f api
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/tasks` | Encola tarea. Devuelve `job_id` inmediatamente. |
| `GET` | `/tasks/{job_id}` | Consulta estado |
| `POST` | `/tasks/{job_id}/approve` | Aprueba/rechaza HITL |
| `GET` | `/health` | Health check |

### Ejemplo

```bash
# Tarea normal
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"query": "Explica RAG y agentes multi-agente", "is_critical": false}'


# Consultar estado:
curl -X GET http://localhost:8000/tasks/<job_id>


# Tarea crítica (se detiene en HITL)
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"query": "Generar reporte critico de produccion", "is_critical": true}'

# Aprobar
curl -X POST http://localhost:8000/tasks/<job_id>/approve \
  -H "Content-Type: application/json" \
  -d '{"approved": true}'
```

## Pruebas de observabilidad (mínimo 5)

```bash
for i in {1..5}; do
  curl -X POST http://localhost:8000/tasks \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"Analiza el estado actual de la IA $i\", \"is_critical\": false}" &
done
wait
```

Luego abre Phoenix y captura las trazas en `/screenshots`.

## Estados de un job

| Estado | Significado |
|--------|-------------|
| `PENDING` | Encolado |
| `RUNNING` | Ejecutando |
| `WAITING_APPROVAL` | Pausado en HITL |
| `DONE` | Completado |
| `FAILED` | Error capturado |

## Notas técnicas

- Todo el flujo es **async** (`astream`, `AsyncRedisSaver`, `BackgroundTasks`).
- Validación de entradas/salidas con **Pydantic**.
- Checkpointer de LangGraph en **Redis** (persistencia entre reinicios).
- Observabilidad con **Arize Phoenix** (trazas de cada nodo).
- RAG con **Chroma** + embeddings de Google.
- Sin hard-coding de secretos (todo en variables de entorno).
