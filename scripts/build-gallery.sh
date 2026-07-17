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
  printf '@import "tailwindcss";\n@import "../../vendor/basecoat/dist/basecoat-%s.css";\n@import "./tokens.css";\n@import "./components.css";\n@source "../../components/**/*.html";\n@source "../../../gallery/**/*.html";\n' "$pack" > "$in"
  ./tools/tailwindcss -i "$in" -o "c22/static/css/c22-$pack.css" --minify >/dev/null 2>&1
  rm -f "$in"
done
echo "Galerie + ${#PACKS[@]} Pack-CSS gebaut"
