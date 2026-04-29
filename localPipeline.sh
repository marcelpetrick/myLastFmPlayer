#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
PYTHON="${VENV_DIR}/bin/python"

if [[ ! -x "${PYTHON}" ]]; then
    python3 -m venv "${VENV_DIR}"
fi

"${PYTHON}" -m pip install -e ".[dev]"

"${PYTHON}" -m ruff check .
"${PYTHON}" tools/check_docs.py
"${PYTHON}" -m pytest
"${PYTHON}" -m build
"${PYTHON}" -m pip install --force-reinstall --no-deps dist/my_lastfm_player-0.1.0-py3-none-any.whl
"${PYTHON}" -c "import my_lastfm_player; print(f'Package import ok: {my_lastfm_player.__version__}')"

echo "localPipeline.sh completed successfully"
