#!/bin/bash
set -e

echo "=== Sistema Intelligence - Entrega Final ==="

if [ ! -f .env ]; then
  echo "Copiando .env.example → .env"
  cp .env.example .env
  echo "Edita .env y agrega tu GOOGLE_API_KEY antes de continuar."
  exit 1
fi

echo "Levantando Redis Stack + Phoenix..."
docker compose up -d

echo "Esperando a que los servicios estén listos..."
sleep 5

echo "Instalando dependencias..."
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo ""
echo "=== Listo ==="
echo "API:     http://localhost:8000"
echo "Phoenix: http://localhost:6006"
echo ""
echo "Inicia la API con:"
echo "  source .venv/bin/activate"
echo "  uvicorn app.main:app --reload --port 8000"
