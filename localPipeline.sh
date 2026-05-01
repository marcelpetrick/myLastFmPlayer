#!/usr/bin/env bash
set -u
set -o pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
PYTHON="${VENV_DIR}/bin/python"
APP="${VENV_DIR}/bin/my-lastfm-player"
RUN_APP=true

declare -a SUMMARY_LINES=()

VENV_OK=0
INSTALL_OK=0
LINT_OK=0
DOCS_OK=0
TESTS_OK=0
SPHINX_OK=0
CLEAN_OK=0
BUILD_OK=0
WHEEL_OK=0
PACKAGE_INSTALL_OK=0
IMPORT_OK=0
OPEN_COVERAGE_OK=0
OPEN_DOCS_OK=0
LAUNCH_OK=0
OPEN_REPORT_COMMAND=""

print_usage() {
    cat <<EOF
Usage: ./localPipeline.sh [--noRun]

Local project pipeline:
  1. Create or reuse .venv
  2. Install the project with development dependencies
  3. Run Ruff linting
  4. Check required documentation
  5. Build Sphinx documentation with warnings treated as errors
  6. Run pytest with coverage and generate htmlcov/index.html
  7. Open generated HTML reports when possible
  8. Remove stale package build artifacts
  9. Build source and wheel distributions
  10. Install the freshly built wheel
  11. Verify that the installed package imports and exposes its version
  12. Launch the installed application once by default
      Use --noRun to suppress application launch
  13. Print a final stage-by-stage summary

Generated HTML reports are opened with MY_LASTFM_PLAYER_REPORT_BROWSER when set,
then firefox, then xdg-open, then open.
EOF
}

log() {
    printf '[INFO] %s\n' "$*"
}

warn() {
    printf '[WARN] %s\n' "$*" >&2
}

error() {
    printf '[ERROR] %s\n' "$*" >&2
}

mark_result() {
    local label="$1"
    local status="$2"
    local details="$3"
    SUMMARY_LINES+=("$(printf '%-16s : %-4s %s' "${label}" "${status}" "${details}")")
}

print_summary() {
    printf '\n========== Local Pipeline Summary ==========\n'
    local line
    for line in "${SUMMARY_LINES[@]}"; do
        printf '%s\n' "${line}"
    done
    printf '============================================\n'
}

detect_open_command() {
    if [[ -n "${MY_LASTFM_PLAYER_REPORT_BROWSER:-}" ]]; then
        printf '%s\n' "${MY_LASTFM_PLAYER_REPORT_BROWSER}"
    fi

    printf '%s\n' "firefox"
    printf '%s\n' "xdg-open"
    printf '%s\n' "open"
}

open_html_report() {
    local report_label="$1"
    local report_path="$2"
    local open_command=""
    local opener_pid=0

    if [[ ! -f "${report_path}" ]]; then
        warn "${report_label} was not found: ${report_path}"
        return 1
    fi

    log "${report_label}: ${report_path}"
    while IFS= read -r open_command; do
        if [[ -z "${open_command}" ]]; then
            continue
        fi
        if ! command -v "${open_command}" >/dev/null 2>&1; then
            continue
        fi
        log "Opening ${report_label} with '${open_command}'."
        "${open_command}" "${report_path}" >/dev/null 2>&1 &
        opener_pid=$!

        sleep 1
        if kill -0 "${opener_pid}" >/dev/null 2>&1; then
            disown "${opener_pid}" >/dev/null 2>&1 || true
            OPEN_REPORT_COMMAND="${open_command}"
            return 0
        fi

        if wait "${opener_pid}"; then
            OPEN_REPORT_COMMAND="${open_command}"
            return 0
        fi
        warn "Could not open ${report_label} with '${open_command}'. Trying next opener."
    done < <(detect_open_command)

    warn "No supported opener could open ${report_label}. Open it manually at: ${report_path}"
    return 1
}

parse_arguments() {
    for argument in "$@"; do
        case "${argument}" in
            --noRun)
                RUN_APP=false
                ;;
            --help|-h)
                print_usage
                exit 0
                ;;
            *)
                error "Unknown argument: ${argument}"
                print_usage
                exit 2
                ;;
        esac
    done
}

prepare_virtual_environment() {
    if [[ -x "${PYTHON}" ]]; then
        log "Using existing virtual environment: ${VENV_DIR}"
        return 0
    fi

    log "Creating virtual environment: ${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
}

install_development_dependencies() {
    log "Installing project with development dependencies."
    "${PYTHON}" -m pip install -e ".[dev]"
}

run_lint() {
    log "Running Ruff lint check."
    "${PYTHON}" -m ruff check .
}

run_documentation_check() {
    log "Checking required documentation."
    "${PYTHON}" tools/check_docs.py
}

build_sphinx_documentation() {
    log "Building Sphinx documentation."
    "${PYTHON}" -m sphinx -W --keep-going -b html "${ROOT_DIR}/docs" "${ROOT_DIR}/build/sphinx/html"
}

run_tests_with_coverage() {
    log "Running pytest with coverage."
    "${PYTHON}" -m pytest
}

open_coverage_report() {
    local coverage_index="${ROOT_DIR}/htmlcov/index.html"
    open_html_report "Coverage report" "${coverage_index}"
}

open_sphinx_documentation() {
    local docs_index="${ROOT_DIR}/build/sphinx/html/index.html"
    open_html_report "Sphinx documentation" "${docs_index}"
}

clean_package_artifacts() {
    log "Removing stale package build artifacts."
    rm -rf "${ROOT_DIR}/build" "${ROOT_DIR}/dist" "${ROOT_DIR}/my_lastfm_player.egg-info"
}

build_package() {
    log "Building source and wheel distributions."
    "${PYTHON}" -m build
}

find_built_wheel() {
    find "${ROOT_DIR}/dist" -maxdepth 1 -name "my_lastfm_player-*.whl" -print -quit
}

install_built_wheel() {
    local wheel_path="$1"

    if [[ -z "${wheel_path}" || ! -f "${wheel_path}" ]]; then
        error "Built wheel was not found in ${ROOT_DIR}/dist."
        return 1
    fi

    log "Installing built wheel: ${wheel_path}"
    "${PYTHON}" -m pip install --force-reinstall --no-deps "${wheel_path}"
}

verify_package_import() {
    log "Verifying package import and version."
    "${PYTHON}" -c "import my_lastfm_player; print(f'Package import ok: {my_lastfm_player.__version__}')"
}

launch_application() {
    if [[ ! -x "${APP}" ]]; then
        warn "Installed application command was not found or is not executable: ${APP}"
        return 1
    fi

    local app_pid=0

    log "Starting my-lastfm-player once. The pipeline will not restart it after the app exits."
    "${APP}" >/dev/null 2>&1 &
    app_pid=$!

    sleep 1
    if kill -0 "${app_pid}" >/dev/null 2>&1; then
        disown "${app_pid}" >/dev/null 2>&1 || true
        return 0
    fi

    wait "${app_pid}"
}

main() {
    local wheel_path=""
    local exit_code=1

    parse_arguments "$@"

    if [[ "${RUN_APP}" == false ]]; then
        log "Application launch is suppressed because --noRun was provided."
    fi

    if prepare_virtual_environment; then
        VENV_OK=1
        mark_result "Virtualenv" "PASS" ".venv is available"
    else
        mark_result "Virtualenv" "FAIL" "Could not create or reuse .venv"
    fi

    if [[ "${VENV_OK}" -eq 1 ]]; then
        if install_development_dependencies; then
            INSTALL_OK=1
            mark_result "Dependencies" "PASS" "Editable install with dev dependencies completed"
        else
            mark_result "Dependencies" "FAIL" "Dependency installation failed"
        fi
    else
        mark_result "Dependencies" "SKIP" "Skipped because .venv is unavailable"
    fi

    if [[ "${INSTALL_OK}" -eq 1 ]]; then
        if run_lint; then
            LINT_OK=1
            mark_result "Ruff" "PASS" "Lint check completed"
        else
            mark_result "Ruff" "FAIL" "Lint check failed"
        fi

        if run_documentation_check; then
            DOCS_OK=1
            mark_result "Docs" "PASS" "Required documentation checks completed"
        else
            mark_result "Docs" "FAIL" "Documentation checks failed"
        fi

        if build_sphinx_documentation; then
            SPHINX_OK=1
            mark_result "Sphinx" "PASS" "HTML documentation built with warnings as errors"
        else
            mark_result "Sphinx" "FAIL" "Sphinx documentation build failed"
        fi

        if run_tests_with_coverage; then
            TESTS_OK=1
            mark_result "Tests+Coverage" "PASS" "pytest completed and generated htmlcov"
        else
            mark_result "Tests+Coverage" "FAIL" "pytest or coverage failed"
        fi
    else
        mark_result "Ruff" "SKIP" "Skipped because dependencies are unavailable"
        mark_result "Docs" "SKIP" "Skipped because dependencies are unavailable"
        mark_result "Sphinx" "SKIP" "Skipped because dependencies are unavailable"
        mark_result "Tests+Coverage" "SKIP" "Skipped because dependencies are unavailable"
    fi

    if [[ "${SPHINX_OK}" -eq 1 ]]; then
        OPEN_REPORT_COMMAND=""
        if open_sphinx_documentation; then
            OPEN_DOCS_OK=1
            mark_result "Open Docs" "PASS" "Sphinx index.html was handed to ${OPEN_REPORT_COMMAND}"
        else
            mark_result "Open Docs" "WARN" "Sphinx path was printed but auto-open was unavailable or failed"
        fi
    else
        mark_result "Open Docs" "SKIP" "Skipped because Sphinx documentation was not generated"
    fi

    if [[ -f "${ROOT_DIR}/htmlcov/index.html" ]]; then
        OPEN_REPORT_COMMAND=""
        if open_coverage_report; then
            OPEN_COVERAGE_OK=1
            mark_result "Open Coverage" "PASS" "htmlcov/index.html was handed to ${OPEN_REPORT_COMMAND}"
        else
            mark_result "Open Coverage" "WARN" "Coverage path was printed but auto-open was unavailable or failed"
        fi
    else
        mark_result "Open Coverage" "SKIP" "Skipped because coverage was not generated"
    fi

    if [[ "${LINT_OK}" -eq 1 && "${DOCS_OK}" -eq 1 && "${SPHINX_OK}" -eq 1 && "${TESTS_OK}" -eq 1 ]]; then
        if clean_package_artifacts; then
            CLEAN_OK=1
            mark_result "Clean Build" "PASS" "Stale package artifacts removed"
        else
            mark_result "Clean Build" "FAIL" "Could not remove stale package artifacts"
        fi
    else
        mark_result "Clean Build" "SKIP" "Skipped because a quality gate failed"
    fi

    if [[ "${CLEAN_OK}" -eq 1 ]]; then
        if build_package; then
            BUILD_OK=1
            mark_result "Package Build" "PASS" "Source and wheel distributions built"
        else
            mark_result "Package Build" "FAIL" "Package build failed"
        fi
    else
        mark_result "Package Build" "SKIP" "Skipped because clean step failed"
    fi

    if [[ "${BUILD_OK}" -eq 1 ]]; then
        wheel_path="$(find_built_wheel)"
        if [[ -n "${wheel_path}" ]]; then
            WHEEL_OK=1
            mark_result "Wheel" "PASS" "Found built wheel in dist/"
        else
            mark_result "Wheel" "FAIL" "No wheel was found in dist/"
        fi
    else
        mark_result "Wheel" "SKIP" "Skipped because package build failed"
    fi

    if [[ "${WHEEL_OK}" -eq 1 ]]; then
        if install_built_wheel "${wheel_path}"; then
            PACKAGE_INSTALL_OK=1
            mark_result "Wheel Install" "PASS" "Built wheel installed into .venv"
        else
            mark_result "Wheel Install" "FAIL" "Built wheel installation failed"
        fi
    else
        mark_result "Wheel Install" "SKIP" "Skipped because no wheel is available"
    fi

    if [[ "${PACKAGE_INSTALL_OK}" -eq 1 ]]; then
        if verify_package_import; then
            IMPORT_OK=1
            mark_result "Import Check" "PASS" "Installed package imports successfully"
        else
            mark_result "Import Check" "FAIL" "Installed package import failed"
        fi
    else
        mark_result "Import Check" "SKIP" "Skipped because wheel install failed"
    fi

    if [[ "${VENV_OK}" -eq 1 && "${INSTALL_OK}" -eq 1 && "${LINT_OK}" -eq 1 && "${DOCS_OK}" -eq 1 && "${SPHINX_OK}" -eq 1 && "${TESTS_OK}" -eq 1 && "${CLEAN_OK}" -eq 1 && "${BUILD_OK}" -eq 1 && "${WHEEL_OK}" -eq 1 && "${PACKAGE_INSTALL_OK}" -eq 1 && "${IMPORT_OK}" -eq 1 ]]; then
        exit_code=0
    fi

    if [[ "${IMPORT_OK}" -eq 1 ]]; then
        if [[ "${RUN_APP}" == true ]]; then
            if launch_application; then
                LAUNCH_OK=1
                mark_result "Launch App" "PASS" "my-lastfm-player was started once"
            else
                mark_result "Launch App" "WARN" "Launching the app failed; this does not affect the pipeline result"
            fi
        else
            mark_result "Launch App" "SKIP" "Suppressed by --noRun"
        fi
    else
        mark_result "Launch App" "SKIP" "Skipped because install verification failed"
    fi

    if [[ "${exit_code}" -eq 0 ]]; then
        log "localPipeline.sh completed successfully"
    else
        error "localPipeline.sh completed with failing mandatory stage(s)"
    fi
    print_summary
    exit "${exit_code}"
}

main "$@"
