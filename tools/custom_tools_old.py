from langchain_core.tools import tool
import json

@tool
def search_vector_db(query: str) -> str:
    """
    Consulta la base de datos vectorial interna o fuentes externas simuladas 
    para extraer información técnica o de infraestructura.
    """
    # Simulación de respuesta de una Base de Datos Vectorial / RAG o API externa
    mock_db = {
        "telecom_sites": "Sitio AMBA: Generador diesel operativo, consumo UPS normal. Sitio PBA: Alerta térmica menor en rack 3, temperatura actual 28.5°C.",
        "generadores": "El generador modelo Uniflair requiere revisión de nivel de aceite y prueba de transferencia automática (ATS)."
    }
    
    for key, value in mock_db.items():
        if key in query.lower() or "sitio" in query.lower() or "generador" in query.lower():
            return json.dumps({"status": "success", "source": key, "data": value})
            
    return json.dumps({"status": "success", "source": "general_search", "data": f"Información general recuperada para: {query}. Parámetros estables dentro del umbral operativo."})

@tool
def analyze_metrics_data(data_json: str) -> str:
    """
    Realiza análisis cuantitativo, cómputo estadístico o validación de esquemas sobre los datos.
    """
    try:
        # Procesamiento analítico simulado
        parsed = json.loads(data_json) if isinstance(data_json, str) else data_json
        analysis = {
            "risk_level": "MEDIO" if "alerta" in str(parsed).lower() else "BAJO",
            "computed_metrics": {
                "efficiency_score": 0.94,
                "anomaly_detected": "alerta térmica" in str(parsed).lower()
            },
            "recommendation": "Verificar sistemas de refrigeración in-row y programar mantenimiento preventivo."
        }
        return json.dumps(analysis, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "message": "Fallo al procesar métricas"})