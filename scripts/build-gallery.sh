#!/usr/bin/env bash
# Build the C22 gallery: (1) generate the static HTML, (2) compile one CSS per
# style pack so the gallery can switch packs live. Needs tools/tailwindcss
# (scripts/fetch-tailwind.sh) and the vendored Basecoat (scripts/vendor-basecoat.sh).
set -euo pipefail
cd "$(dirname "$0")/.."

python3 gallery/build.py

PACKS=(vega nova maia lyra mira luma sera rhea)
for pack in "${PACKS[@]}"; do
  in="c22/static/css/_in-$pack.css"
  # Layer-Entmachtung (PO 2026-07-18): die Vendor-KOMPONENTEN-Regeln liegen in einer eigenen
  # Ebene UNTER components — jede C22-Regel gewinnt per Kaskaden-Layer, egal wie spezifisch
  # der Vendor-Selektor ist. Die @layer-Zeile MUSS vor dem Tailwind-Import stehen
  # (Deklarationsreihenfolge = Rang). base/base.css bleibt ungelayert importiert: sie enthält
  # @custom-variant/@theme, die Tailwind nicht in einem layer(…) verschachteln kann (Fehler
  # „@custom-variant cannot be nested") — ihre Regeln stecken ohnehin in @layer base/theme.
  printf '@layer theme, base, vendor, components, utilities;\n@import "tailwindcss";\n@import "../../vendor/basecoat/dist/base/base.css";\n@import "../../vendor/basecoat/dist/basecoat-components.css" layer(vendor);\n@import "../../vendor/basecoat/dist/styles/%s.css" layer(vendor);\n@import "./tokens.css";\n@import "./components.css";\n@source "../../components/**/*.html";\n@source "../../../gallery/**/*.html";\n' "$pack" > "$in"
  # Tailwind meldet Fehler auf stdout, beendet sich aber mit Exit 0 — ein stilles >/dev/null
  # ließ kaputte Builds als Erfolg durchgehen (alte Pack-CSS blieben einfach liegen).
  ausgabe="$(./tools/tailwindcss -i "$in" -o "c22/static/css/c22-$pack.css" --minify 2>&1)" || true
  if printf '%s' "$ausgabe" | grep -q "Error"; then
    echo "Tailwind-Fehler beim Pack '$pack':" >&2
    printf '%s\n' "$ausgabe" >&2
    rm -f "$in"
    exit 1
  fi
  rm -f "$in"
done
echo "Galerie + ${#PACKS[@]} Pack-CSS gebaut"
