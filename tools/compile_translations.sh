#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRANSLATIONS_DIR="${ROOT_DIR}/my_lastfm_player/translations"

if command -v lrelease >/dev/null 2>&1; then
    LRELEASE="lrelease"
else
    printf '[ERROR] lrelease was not found. Install Qt Linguist tools first.\n' >&2
    exit 1
fi

"${LRELEASE}" "${TRANSLATIONS_DIR}"/*.ts
printf '[INFO] Compiled Qt translation files in %s\n' "${TRANSLATIONS_DIR}"
