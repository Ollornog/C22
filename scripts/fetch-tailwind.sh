#!/usr/bin/env bash
# Fetch the pinned Tailwind CSS standalone CLI (a single binary — no Node/npm).
#
# The binary is git-ignored (see .gitignore); CI and dev fetch it via this script.
#
# UPDATE: bump TAILWIND_VERSION, run this script, then `ci-local` must stay green.
#         Check the Tailwind release notes for breaking changes on a major bump.
set -euo pipefail

TAILWIND_VERSION="4.3.2"
ARCH="linux-x64"   # linux-arm64 / macos-x64 / macos-arm64 for other hosts

here="$(cd "$(dirname "$0")" && pwd)"
dest="$here/../tools/tailwindcss"
url="https://github.com/tailwindlabs/tailwindcss/releases/download/v${TAILWIND_VERSION}/tailwindcss-${ARCH}"

mkdir -p "$(dirname "$dest")"
curl -fsSL -o "$dest" "$url"
chmod +x "$dest"
"$dest" --help >/dev/null
echo "Tailwind ${TAILWIND_VERSION} (${ARCH}) -> $dest"
