#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYLUPDATE="${ROOT_DIR}/.venv/bin/pylupdate6"
TRANSLATIONS_DIR="${ROOT_DIR}/my_lastfm_player/translations"

if [[ ! -x "${PYLUPDATE}" ]]; then
    printf '[ERROR] pylupdate6 not found at %s\n' "${PYLUPDATE}" >&2
    printf '[ERROR] Run ./localPipeline.sh --noRun or install dev dependencies first.\n' >&2
    exit 1
fi

mkdir -p "${TRANSLATIONS_DIR}"

SOURCE_FILES=(
    "${ROOT_DIR}/my_lastfm_player/controller.py"
    "${ROOT_DIR}/my_lastfm_player/dependencies.py"
    "${ROOT_DIR}/my_lastfm_player/download.py"
    "${ROOT_DIR}/my_lastfm_player/i18n.py"
    "${ROOT_DIR}/my_lastfm_player/lastfm.py"
    "${ROOT_DIR}/my_lastfm_player/playback.py"
    "${ROOT_DIR}/my_lastfm_player/ui/main_window.py"
    "${ROOT_DIR}/my_lastfm_player/ui/preferences_dialog.py"
    "${ROOT_DIR}/my_lastfm_player/ui/track_table_model.py"
    "${ROOT_DIR}/my_lastfm_player/workers.py"
    "${ROOT_DIR}/my_lastfm_player/youtube.py"
)

for language in hr de zh uk; do
    "${PYLUPDATE}" "${SOURCE_FILES[@]}" \
        --ts "${TRANSLATIONS_DIR}/my_lastfm_player_${language}.ts"
done

printf '[INFO] Updated Qt translation source files in %s\n' "${TRANSLATIONS_DIR}"
