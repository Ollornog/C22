#!/usr/bin/env bash
# Build the C22 gallery: (1) generate the static HTML pages (Components/Blocks/
# Charts/Typeset), (2) compile one CSS per style pack so the gallery can switch
# packs live. Needs tools/tailwindcss (scripts/fetch-tailwind.sh) and the
# vendored Basecoat (scripts/vendor-basecoat.sh).
set -euo pipefail
cd "$(dirname "$0")/.."

python3 gallery/build.py

# Eigene Packs (c22/static/css/packs/<name>.css) sind reine TOKEN-Overrides über
# der vega-Form (Pack-Entmonolithisierung Phase B): sie laden vega als Vendor-
# Schicht und legen ihre Tokens als LETZTEN Import obendrauf (gewinnt im
# Gleichstand). Vendor-Packs laden ihre eigene styles/<name>.css.
PACKS=(vega spica nova maia lyra mira luma sera rhea)
for pack in "${PACKS[@]}"; do
  in="c22/static/css/_in-$pack.css"
  vendor_style="$pack"
  eigener_pack=""
  if [ -f "c22/static/css/packs/$pack.css" ]; then
    vendor_style="vega"
    eigener_pack="@import \"./packs/$pack.css\";"
  fi
  # Layer-Entmachtung (PO 2026-07-18): die Vendor-KOMPONENTEN-Regeln liegen in einer eigenen
  # Ebene UNTER components — jede C22-Regel gewinnt per Kaskaden-Layer, egal wie spezifisch
  # der Vendor-Selektor ist. Die @layer-Zeile MUSS vor dem Tailwind-Import stehen
  # (Deklarationsreihenfolge = Rang). base/base.css bleibt ungelayert importiert: sie enthält
  # @custom-variant/@theme, die Tailwind nicht in einem layer(…) verschachteln kann (Fehler
  # „@custom-variant cannot be nested") — ihre Regeln stecken ohnehin in @layer base/theme.
  {
    printf '@layer theme, base, vendor, components, utilities;\n'
    printf '@import "tailwindcss";\n'
    printf '@import "../../vendor/basecoat/dist/base/base.css";\n'
    printf '@import "../../vendor/basecoat/dist/basecoat-components.css" layer(vendor);\n'
    printf '@import "../../vendor/basecoat/dist/styles/%s.css" layer(vendor);\n' "$vendor_style"
    printf '@import "./tokens.css";\n'
    printf '@import "./components.css";\n'
    [ -n "$eigener_pack" ] && printf '%s\n' "$eigener_pack"
    printf '@source "../../components/**/*.html";\n'
    printf '@source "../../blocks/**/*.html";\n'
    printf '@source "../../charts/**/*.html";\n'
    printf '@source "../../typeset/**/*.html";\n'
    printf '@source "../../../gallery/**/*.html";\n'
  } > "$in"
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
echo "Galerie-Seiten + ${#PACKS[@]} Pack-CSS gebaut"
