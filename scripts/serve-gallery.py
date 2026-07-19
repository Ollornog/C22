#!/usr/bin/env python3
"""Galerie-Server ohne Browser-Caching.

Pythons nackter http.server sendet keine Cache-Header — Browser cachen dann heuristisch
sogar die index.html und zeigen nach einem Rebuild alten Stand (samt alter ?v=-Asset-URLs),
bis man hart neu lädt. Dieser Wrapper sendet Cache-Control: no-store für alles; die Dateien
liegen lokal, der Mehraufwand ist unmessbar.

Aufruf (im Repo-Root):  python3 scripts/serve-gallery.py [port]   (Default 8232)
"""
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass  # still — der Server läuft dauerhaft im Hintergrund


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8232
    ThreadingHTTPServer(("127.0.0.1", port), NoCacheHandler).serve_forever()
