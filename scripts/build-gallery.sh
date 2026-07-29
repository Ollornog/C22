#!/usr/bin/env bash
# Build the C22 gallery: (1) generate the static HTML pages (Components/Blocks/
# Charts/Typeset), (2) compile one CSS per style pack so the gallery can switch
# packs live. Needs tools/tailwindcss (scripts/fetch-tailwind.sh) and the
# vendored Basecoat (scripts/vendor-basecoat.sh).
set -euo pipefail
cd "$(dirname "$0")/.."

python3 gallery/build.py

# Jedes Pack hat eine C22-ACHSENSCHICHT (c22/static/css/packs/<name>.css): dort entscheidet
# es Radius, Dichte, Typo-Skala, Schatten, Bewegung und Strichstärke — die Achsen, die die
# vendorten Packs selbst NICHT als Token führen (sie tragen ihren Charakter in Klassenregeln,
# weshalb C22-eigene Flächen ihnen früher nicht folgten). Register: c22/axes.py.
#
# Die FORM (welche Vendor-Style-Datei) ist normalerweise das gleichnamige Pack. Ein FARB-Pack
# wie spica hat keine eigene Vendor-Datei und nennt seine Form im Kopf: `@c22-form: vega`.
PACKS=(vega spica nova maia lyra mira luma sera rhea)
for pack in "${PACKS[@]}"; do
  in="c22/static/css/_in-$pack.css"
  vendor_style="$pack"
  eigener_pack=""
  achsen="c22/static/css/packs/$pack.css"
  if [ -f "$achsen" ]; then
    eigener_pack="@import \"./packs/$pack.css\";"
    form="$(sed -n 's/.*@c22-form:[[:space:]]*\([a-z][a-z0-9-]*\).*/\1/p' "$achsen" | head -1)"
    [ -n "$form" ] && vendor_style="$form"
  else
    echo "Pack '$pack' hat keine Achsenschicht ($achsen) — jedes Pack muss seine Achsen angeben." >&2
    exit 1
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
