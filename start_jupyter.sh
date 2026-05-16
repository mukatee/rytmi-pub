#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$ROOT_DIR/.env"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  . "$ENV_FILE"
  set +a
fi

VENV_PYTHON="$ROOT_DIR/.venv/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Error: expected virtual environment Python at $VENV_PYTHON" >&2
  echo "Create or activate the project's .venv first." >&2
  exit 1
fi

cd "$ROOT_DIR"

MODE="lab"
if [[ "${1:-}" == "--notebook" ]]; then
  MODE="notebook"
  shift
elif [[ "${1:-}" == "--lab" ]]; then
  shift
fi

if ! "$VENV_PYTHON" -c "import jupyterlab" >/dev/null 2>&1 && [[ "$MODE" == "lab" ]]; then
  echo "jupyterlab is not installed in .venv." >&2
  echo "Install it with: source .venv/bin/activate && pip install jupyterlab notebook ipywidgets" >&2
  exit 1
fi

exec "$VENV_PYTHON" -m jupyter "$MODE" "$@"
