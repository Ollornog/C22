"""scripts/fetch-tailwind.sh: checksum and cache, offline against a fake curl.

Why: every push and every CI run fetched the Tailwind binary from github.com, and a 504 there turned the pre-push and
the CI red (2026-11-09, twice). The script now keeps one checked copy per version in a cache. This suite proves the
three promises without the network: a valid cache entry is used without any download, a broken entry is replaced, and a
download with the wrong checksum is refused (nothing lands in tools/ or in the cache).
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKRIPT = ROOT / "scripts" / "fetch-tailwind.sh"

fehler = 0


def pruef(ok: bool, text: str) -> None:
    global fehler
    print(f"  {'✓' if ok else '✗'} {text}")
    if not ok:
        fehler += 1


def main() -> int:
    quelle = SKRIPT.read_text(encoding="utf-8")
    version = re.search(r'^TAILWIND_VERSION="([^"]+)"', quelle, re.M).group(1)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        (tmp / "repo" / "scripts").mkdir(parents=True)
        # A fake binary that answers `--help`; its checksum replaces the pinned one in the copy of the script.
        echt = b"#!/bin/sh\nexit 0\n"
        summe = hashlib.sha256(echt).hexdigest()
        kopie = re.sub(r'^TAILWIND_SHA256="[0-9a-f]+"', f'TAILWIND_SHA256="{summe}"', quelle, flags=re.M)
        ziel_skript = tmp / "repo" / "scripts" / "fetch-tailwind.sh"
        ziel_skript.write_text(kopie, encoding="utf-8")
        # Fake curl: writes "$TW_INHALT" to the -o target and logs each call.
        bin_ = tmp / "bin"
        bin_.mkdir()
        curl = bin_ / "curl"
        curl.write_text('#!/bin/sh\necho call >> "$TW_LOG"\nwhile [ "$1" != "-o" ]; do shift; done\n'
                        'cp "$TW_INHALT" "$2"\n', encoding="utf-8")
        curl.chmod(curl.stat().st_mode | stat.S_IEXEC)
        inhalt = tmp / "inhalt"
        log = tmp / "log"
        cache = tmp / "cache"
        werkzeug = tmp / "repo" / "tools" / "tailwindcss"
        eintrag = cache / f"tailwindcss-{version}-linux-x64"

        def lauf(daten: bytes) -> int:
            inhalt.write_bytes(daten)
            log.write_text("")
            env = {**os.environ, "PATH": f"{bin_}:{os.environ['PATH']}", "TW_LOG": str(log),
                   "TW_INHALT": str(inhalt), "TAILWIND_CACHE": str(cache)}
            env.pop("XDG_CACHE_HOME", None)
            return subprocess.run(["bash", str(ziel_skript)], env=env, capture_output=True).returncode

        def downloads() -> int:
            return len(log.read_text().split())

        rc = lauf(echt)
        pruef(rc == 0 and downloads() == 1 and eintrag.read_bytes() == echt,
              "first run downloads, checks and stores the binary in the cache")
        werkzeug.unlink()
        rc = lauf(b"anything")
        pruef(rc == 0 and downloads() == 0 and werkzeug.read_bytes() == echt,
              "valid cache entry: used without any download (a 504 cannot hit)")
        eintrag.write_bytes(b"broken")
        rc = lauf(echt)
        pruef(rc == 0 and downloads() == 1 and eintrag.read_bytes() == echt,
              "broken cache entry: fetched again and replaced")
        shutil.rmtree(cache)
        werkzeug.unlink()
        rc = lauf(b"swapped binary")
        pruef(rc != 0 and not werkzeug.exists() and not eintrag.exists(),
              "download with the wrong checksum: refused, nothing in tools/ or in the cache")
    print(f"\n  {'ok' if not fehler else f'{fehler} failed'}")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
