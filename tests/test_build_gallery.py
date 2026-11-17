"""scripts/build-gallery.sh: a failed Tailwind build fails the script, offline against a fake binary.

Why: the script judged Tailwind only by the word "Error" in its output. A missing tools/tailwindcss left a shell
message without that word ("not found" in a German shell: "nicht gefunden"), the loop went on and the script ended with
"10 Pack-CSS gebaut" (2026-11-17). Now a missing or non-executable binary stops the script first with a clear message,
and the exit code of Tailwind decides; the word "Error" stays a second net. This suite runs a copy of the script in a
throw-away tree with a fake gallery/build.py and a fake binary, so it needs neither Tailwind nor the network.
"""
from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKRIPT = ROOT / "scripts" / "build-gallery.sh"
PACKS = ROOT / "c22" / "static" / "css" / "packs"

fehler = 0


def pruef(ok: bool, text: str) -> None:
    global fehler
    print(f"  {'✓' if ok else '✗'} {text}")
    if not ok:
        fehler += 1


def main() -> int:
    with tempfile.TemporaryDirectory() as t:
        repo = Path(t) / "repo"
        (repo / "scripts").mkdir(parents=True)
        shutil.copy(SKRIPT, repo / "scripts" / "build-gallery.sh")
        (repo / "gallery").mkdir()
        (repo / "gallery" / "build.py").write_text("print('pages')\n", encoding="utf-8")
        shutil.copytree(PACKS, repo / "c22" / "static" / "css" / "packs")
        (repo / "tools").mkdir()
        binary = repo / "tools" / "tailwindcss"
        css = repo / "c22" / "static" / "css"

        def fake(text: str, rc: int, executable: bool = True) -> None:
            # Writes the -o target, prints TEXT and ends with RC, as Tailwind would.
            binary.write_text('#!/bin/sh\nwhile [ "$1" != "-o" ]; do shift; done\n'
                              f'echo "/* built */" > "$2"\necho "{text}"\nexit {rc}\n', encoding="utf-8")
            mode = binary.stat().st_mode
            binary.chmod(mode | stat.S_IEXEC if executable else mode & ~(stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))

        def lauf() -> subprocess.CompletedProcess:
            for alt in css.glob("c22-*.css"):
                alt.unlink()
            env = {**os.environ, "LC_ALL": "C"}
            return subprocess.run(["bash", str(repo / "scripts" / "build-gallery.sh")], env=env,
                                  capture_output=True, text=True)

        r = lauf()
        pruef(r.returncode != 0 and "tools/tailwindcss" in r.stderr and "fetch-tailwind" in r.stderr
              and "gebaut" not in r.stdout,
              "binary missing: fails, names tools/tailwindcss and scripts/fetch-tailwind.sh, reports nothing built")
        fake("", 0, executable=False)
        r = lauf()
        pruef(r.returncode != 0 and "tools/tailwindcss" in r.stderr and "gebaut" not in r.stdout,
              "binary not executable: fails with the same message")
        fake("Can't resolve './missing.css'", 1)
        r = lauf()
        pruef(r.returncode != 0 and "Exit 1" in r.stderr and "gebaut" not in r.stdout,
              "Tailwind ends with 1 and prints no 'Error': the exit code fails the script")
        fake("Error: Cannot apply unknown utility class", 0)
        r = lauf()
        pruef(r.returncode != 0 and "gebaut" not in r.stdout,
              "Tailwind prints 'Error' but ends with 0 (older versions): still fails")
        fake("", 0)
        r = lauf()
        gebaut = sorted(p.name for p in css.glob("c22-*.css"))
        pruef(r.returncode == 0 and "Pack-CSS gebaut" in r.stdout and len(gebaut) == len(list(PACKS.glob("*.css"))),
              f"Tailwind ends with 0 and says nothing wrong: succeeds, one CSS per pack ({len(gebaut)})")
    print(f"\n  {'ok' if not fehler else f'{fehler} failed'}")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
