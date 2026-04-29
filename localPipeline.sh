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
rm -rf "${ROOT_DIR}/build" "${ROOT_DIR}/dist" "${ROOT_DIR}/my_lastfm_player.egg-info"
"${PYTHON}" -m build
WHEEL_PATH="$(find "${ROOT_DIR}/dist" -maxdepth 1 -name "my_lastfm_player-*.whl" -print -quit)"
"${PYTHON}" -m pip install --force-reinstall --no-deps "${WHEEL_PATH}"
"${PYTHON}" -c "import my_lastfm_player; print(f'Package import ok: {my_lastfm_player.__version__}')"

echo "Coverage report: ${ROOT_DIR}/htmlcov/index.html"
echo "localPipeline.sh completed successfully"
