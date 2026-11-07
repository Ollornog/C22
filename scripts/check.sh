#!/usr/bin/env bash
# The gate before every push: unit, hygiene and browser suites.
#
#   scripts/check.sh            # everything, needs Chrome and tools/tailwindcss (fetched if missing)
#   scripts/check.sh --fast     # without the browser suite (short loop)
#
# Der pre-push-Hook (.githooks/pre-push) ruft dieses Skript. Einmalig pro Klon:
#   git config core.hooksPath .githooks
set -euo pipefail

cd "$(dirname "$0")/.."
FAST=0
[[ "${1:-}" == "--fast" ]] && FAST=1

step() { printf '\n\033[1m▸ %s\033[0m\n' "$1"; }
fail() { printf '\n\033[31m✗ %s\033[0m\n' "$1" >&2; exit 1; }

# The tests import c22 from the source tree (the suites put the repo root on the path), so no
# installation is needed. Python alone is enough, the browser suite uses the standard library.
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
# Die Zeile ist der BELEG fuer `ci-local --matrix`: der Laeufer liest sie zurueck und
# vergleicht die Versionsnummer mit dem angeforderten Bein. Bis 2026-09-22 stand hier
# nur `sys.executable` — ein Pfad wie /opt/venvs/py313/bin/python nennt keine Version,
# und die Matrix lief deshalb in diesem Repo NIE durch ("unbelegt", Exit 1). Die
# Version gehoert also zuerst, der Pfad bleibt daneben stehen (er verraet das venv).
step "Interpreter: $("$PY" -c 'import sys; print(sys.version.split()[0], "@", sys.executable)')"

# Text-Schnellweg (repokit 0.35.0, PO 2026-10-15): Ändert der Stand gegenüber dem Standardzweig nur Text von der
# Erlaubnisliste des Kits (*.md in der Wurzel, docs/, backlog/, changelog.d/), fährt nur die eigene Prüfung des
# Texts — tests/test_repo.py: Hygiene, Links, Anker, Frontmatter — und endet. Die Pflicht-Checks laufen trotzdem und
# melden grün. Entscheidung und Liste: scripts/_nur_text.sh (aus dem Kit); verengen: scripts/nur-text-verengung.txt.
if grund="$(scripts/_nur_text.sh)"; then
    step "$grund"
    "$PY" tests/test_repo.py || fail "Repo-Hygiene"
    printf '\n\033[32m✓ Nur Text — Hygiene grün\033[0m\n'
    exit 0
fi
step "$grund"

if [[ $FAST -eq 1 ]]; then
    step "Suiten ohne visuellen Test (--fast)"
    "$PY" tests/run_all.py --no-browser || fail "Testsuite"
else
    step "Alle Suiten — Fach- und Hygiene-Test inklusive"
    "$PY" tests/run_all.py || fail "Testsuite"
fi

printf '\n\033[32m✓ Alles grün\033[0m\n'
