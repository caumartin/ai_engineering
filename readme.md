# Orquestador Multi-Agente (Pre-entrega 6)

## Diagrama de Topología del Grafo

```mermaid
graph TD
    Start([Start]) --> Supervisor{Supervisor Node}
    
    Supervisor -->|researcher| Researcher[Agente de Búsqueda]
    Supervisor -->|analyst| Analyst[Agente de Análisis]
    Supervisor -->|FINISH| Validator[Nodo de Validación]
    
    Researcher --> Supervisor
    Analyst --> Supervisor
    
    Validator --> End([End])