#!/usr/bin/env bash
# Vendor Basecoat into the repo ("own the code") — reproducibly, from the npm
# registry tarball, WITHOUT running `npm install` (no node_modules, no Node needed).
#
# Basecoat gives us the shadcn look as plain HTML + Tailwind. We do NOT track
# shadcn/ui directly (it is React code we don't use); shadcn look updates reach us
# THROUGH Basecoat (it is shadcn-theme-compatible). So Basecoat's version is the knob.
#
# UPDATE:
#   1. bump BASECOAT_VERSION below, run this script
#   2. review `git diff c22/vendor/basecoat` — see exactly what changed
#   3. rebuild the gallery + webshot-diff (visual regression) — nothing must break
#   4. mind SemVer: a MAJOR bump may change class names / tokens (breaking)
#   5. commit the vendored change together with the version bump
set -euo pipefail

BASECOAT_VERSION="1.0.2"

root="$(cd "$(dirname "$0")/.." && pwd)"
vendor="$root/c22/vendor/basecoat"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

curl -fsSL -o "$tmp/basecoat.tgz" \
  "https://registry.npmjs.org/basecoat-css/-/basecoat-css-${BASECOAT_VERSION}.tgz"
tar -xzf "$tmp/basecoat.tgz" -C "$tmp"   # -> $tmp/package

mkdir -p "$vendor"
rm -rf "$vendor/dist" "$vendor/templates"
cp -r "$tmp/package/dist" "$vendor/dist"
cp -r "$tmp/package/templates" "$vendor/templates"
printf '%s\n' "$BASECOAT_VERSION" > "$vendor/VERSION"

# Mirror the runtime JS bundle into the served static/ dir
cp "$tmp/package/dist/js/all.min.js" "$root/c22/static/js/basecoat.all.min.js"

echo "Basecoat ${BASECOAT_VERSION} vendored -> $vendor ($(find "$vendor" -type f | wc -l) files)"
