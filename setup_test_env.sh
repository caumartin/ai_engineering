#!/usr/bin/env bash
set -euo pipefail

# Carpeta del entorno virtual (puedes sobreescribirla pasando VENV_DIR=.otro_venv ./setup_test_env.sh)
VENV_DIR="${VENV_DIR:-.venv-tests}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Si se ubica dentro de scripts/, subimos un nivel a la raíz del proyecto
if [[ "$(basename "$SCRIPT_DIR")" == "scripts" ]]; then
  PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

cd "$PROJECT_ROOT"

# Detectar intérprete de Python disponible en Linux o Git Bash (Windows)
PYTHON_BIN=""
for candidate in python3.12 python3 python; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c "import sys; assert sys.version_info >= (3, 10)" >/dev/null 2>&1; then
      PYTHON_BIN="$candidate"
      break
    fi
  fi
done

if [[ -z "$PYTHON_BIN" ]]; then
  echo "Error: No se encontró Python 3.10+ en el PATH (probado: python3.12, python3, python)." >&2
  exit 1
fi

echo "Usando intérprete: $($PYTHON_BIN --version) ($PYTHON_BIN)"

# Crear entorno virtual si no existe
if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creando entorno virtual en '$VENV_DIR'..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
else
  echo "El entorno virtual '$VENV_DIR' ya existe. Reutilizando..."
fi

# Detectar ruta de activación según SO (Linux/macOS vs Git Bash en Windows)
if [[ -f "$VENV_DIR/bin/activate" ]]; then
  ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
elif [[ -f "$VENV_DIR/Scripts/activate" ]]; then
  ACTIVATE_SCRIPT="$VENV_DIR/Scripts/activate"
else
  echo "Error: No se encontró el script de activación dentro de '$VENV_DIR'." >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$ACTIVATE_SCRIPT"

echo "Actualizando pip e instalando dependencias para test_concurrent.py..."
python -m pip install --upgrade pip --quiet
python -m pip install "httpx" --quiet

echo ""
echo "Entorno listo en: $PROJECT_ROOT/$VENV_DIR"
echo "Para activarlo manualmente:"
echo "  source $ACTIVATE_SCRIPT"
echo "Para ejecutar las pruebas:"
echo "  python test_concurrent.py"

# Si se pasa --run, ejecuta el test automáticamente al finalizar
if [[ "${1:-}" == "--run" ]]; then
  echo ""
  echo "Ejecutando test_concurrent.py..."
  python test_concurrent.py
fi