#!/usr/bin/env bash
# Fetch the pinned Tailwind CSS standalone CLI (a single binary — no Node/npm).
#
# The binary is git-ignored (see .gitignore); CI and dev fetch it via this script.
#
# UPDATE: bump TAILWIND_VERSION and TAILWIND_SHA256 (from the release's sha256sums.txt), run this script,
#         then `ci-local` must stay green. Check the Tailwind release notes for breaking changes on a major bump.
#
# CHECKSUM: release assets can be replaced under the same tag; without the check a swapped binary would run in the
# build right away.
#
# CACHE (2026-11-12): every push and every CI run fetched the binary from github.com, and a 504 there turned the
# pre-push and the CI red (2026-11-09, twice). With a cache directory one copy per version is kept there and checked
# against the checksum before each use; a mismatch fetches again. The directory is TAILWIND_CACHE, else
# $XDG_CACHE_HOME/c22-tailwind (ci-local mounts a persistent host cache there), else none. Without a writable cache
# the script fetches as before and says so. Same scheme as in our other repos.
set -euo pipefail

TAILWIND_VERSION="4.3.2"
ARCH="linux-x64"   # linux-arm64 / macos-x64 / macos-arm64 for other hosts (and their checksum)
TAILWIND_SHA256="5036c4fb4328e0bcdbb6065c70d8ac9452e0d4c947113a788a8f94fd390425c1"   # linux-x64

here="$(cd "$(dirname "$0")" && pwd)"
dest="$here/../tools/tailwindcss"
url="https://github.com/tailwindlabs/tailwindcss/releases/download/v${TAILWIND_VERSION}/tailwindcss-${ARCH}"

checksum_ok() { echo "${TAILWIND_SHA256}  $1" | sha256sum -c - >/dev/null 2>&1; }

mkdir -p "$(dirname "$dest")"
tmp="$(mktemp)"; trap 'rm -f "$tmp"' EXIT

cache="${TAILWIND_CACHE:-${XDG_CACHE_HOME:+$XDG_CACHE_HOME/c22-tailwind}}"
hit="${cache:+$cache/tailwindcss-${TAILWIND_VERSION}-${ARCH}}"
source_note="fetched"
if [[ -n "$hit" && -f "$hit" ]] && checksum_ok "$hit"; then
  cp "$hit" "$tmp"
  source_note="from cache $cache"
else
  curl -fsSL -o "$tmp" "$url"
  checksum_ok "$tmp" || {
    echo "ERROR: SHA256 mismatch for $url — download discarded." >&2
    exit 1
  }
  if [[ -n "$cache" ]]; then
    # Write under an own name first, then rename: parallel runs share the cache.
    if mkdir -p "$cache" 2>/dev/null && [[ -w "$cache" ]]; then
      cp "$tmp" "$hit.$$" && chmod 0644 "$hit.$$" && mv -f "$hit.$$" "$hit"
      source_note="fetched, stored in cache $cache"
    else
      echo "Note: cache $cache not writable — Tailwind fetched without cache." >&2
    fi
  fi
fi
mv "$tmp" "$dest"
trap - EXIT
chmod +x "$dest"
"$dest" --help >/dev/null
echo "Tailwind ${TAILWIND_VERSION} (${ARCH}, SHA256 checked, ${source_note}) -> $dest"
