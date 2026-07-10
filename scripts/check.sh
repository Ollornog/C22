#!/usr/bin/env bash
# Das Tor vor jedem Push: Fach- + Hygiene-Tests (später zusätzlich der visuelle Test der Makros).
#
#   scripts/check.sh            # alles
#   scripts/check.sh --fast     # ohne visuellen Test (kurze Schleife)
#
# Der pre-push-Hook (.githooks/pre-push) ruft dieses Skript. Einmalig pro Klon:
#   git config core.hooksPath .githooks
set -euo pipefail

cd "$(dirname "$0")/.."
FAST=0
[[ "${1:-}" == "--fast" ]] && FAST=1

step() { printf '\n\033[1m▸ %s\033[0m\n' "$1"; }
fail() { printf '\n\033[31m✗ %s\033[0m\n' "$1" >&2; exit 1; }

# Die Tests importieren c22 aus dem Quellbaum (die Suiten legen den Repo-Root auf den Pfad)
# — eine Installation ist dafür nicht nötig. Gebraucht wird nur Python >= 3.10; die dev-Extras
# (websockets/httpx) erst der spätere visuelle Test, dann greift der uv-Zweig.
usable() { [[ -x "$1" ]] && "$1" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; }
PY=""
for cand in "${PYTHON:-}" .venv/bin/python "$(command -v python3 || true)"; do
    [[ -n "$cand" ]] && usable "$cand" && { PY="$cand"; break; }
done

if [[ -z "$PY" ]]; then
    command -v uv >/dev/null || fail "Kein Python mit c22 und kein uv. → pip install -e '.[dev]'"
    step "Lege .venv an (einmalig)"
    uv venv .venv >/dev/null || fail "uv venv"
    uv pip install -q --python .venv/bin/python -e ".[dev]" || fail "uv pip install"
    PY=".venv/bin/python"
fi
step "Interpreter: $("$PY" -c 'import sys; print(sys.executable)')"

if [[ $FAST -eq 1 ]]; then
    step "Suiten ohne visuellen Test (--fast)"
    "$PY" tests/run_all.py --no-browser || fail "Testsuite"
else
    step "Alle Suiten — Fach- und Hygiene-Test inklusive"
    "$PY" tests/run_all.py || fail "Testsuite"
fi

printf '\n\033[32m✓ Alles grün\033[0m\n'
