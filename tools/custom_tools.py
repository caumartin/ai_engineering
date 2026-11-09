# tools/custom_tools.py
from langchain_core.tools import tool
import json

@tool
def query_sales_and_products_db(query: str) -> str:
    """
    Consulta la base de datos de productos, clientes y transacciones de ventas 
    para extraer stock, historiales de compra o datos de clientes.
    """
    # Simulación de registros comerciales (puedes conectarlo a PostgreSQL/BigQuery)
    mock_commercial_db = {
        "cliente_acme": "Cliente: ACME S.A. | Segmento: Enterprise | Deuda actual: $1,200 USD | Historial: 15 compras anuales.",
        "producto_servidor": "Producto: Servidor Rack 2U Enterprise | SKU: SRV-2026-X | Stock disponible: 12 unidades | Precio unitario: $4,500 USD.",
        "ventas_q3": "Reporte de Ventas Q3: Total facturado: $145,000 USD. Top producto más vendido: Licencias de software Cloud. Margen promedio: 38%."
    }
    
    query_lower = query.lower()
    for key, value in mock_commercial_db.items():
        if any(term in query_lower for term in key.split("_")):
            return json.dumps({"status": "success", "source": key, "data": value})
            
    return json.dumps({
        "status": "success", 
        "source": "general_catalog", 
        "data": f"Consulta procesada para '{query}'. Stock y estado de cuenta dentro de parámetros normales."
    })

@tool
def analyze_sales_margins(financial_data: str) -> str:
    """
    Calcula márgenes de ganancia, proyecciones de descuento por volumen y 
    análisis de riesgo crediticio para clientes.
    """
    try:
        # Procesamiento analítico comercial simulado
        analysis = {
            "financial_metrics": {
                "gross_margin_percentage": 42.5,
                "credit_risk": "BAJO",
                "volume_discount_applicable": True,
                "recommended_max_discount": "10%"
            },
            "commercial_recommendation": "Aprobar orden de compra con condición de pago a 30 días y aplicar descuento por volumen del 5%."
        }
        return json.dumps(analysis, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "message": "Fallo al procesar métricas financieras"})