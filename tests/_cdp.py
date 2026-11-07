"""Headless Chrome over the DevTools protocol, standard library only.

The protocol runs over a pipe (`--remote-debugging-pipe`, fd 3 and 4, messages end in NUL), so
there is no port to collide with in parallel runs and no websocket package to install.
"""
from __future__ import annotations

import base64
import json
import os
import select
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

KANDIDATEN = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome")
FRIST = 60.0


class BrowserFehler(RuntimeError):
    pass


def finde_chrome() -> str:
    pfad = os.environ.get("CHROME") or next(filter(None, map(shutil.which, KANDIDATEN)), None)
    if not pfad:
        raise BrowserFehler(f"kein Chrome gefunden (gesucht: {', '.join(KANDIDATEN)}; oder CHROME setzen)")
    return pfad


class Browser:
    def __enter__(self) -> "Browser":
        self._profil = tempfile.mkdtemp(prefix="c22-chrome-")
        an_chrome_r, self._an_chrome = os.pipe()
        self._von_chrome, von_chrome_w = os.pipe()

        def fds() -> None:
            # Through a copy first: if the pipe already is fd 3, dup2 changes nothing and the
            # close-on-exec flag stays set, so Chrome would start without its pipe.
            lesen, schreiben = os.dup(an_chrome_r), os.dup(von_chrome_w)
            os.dup2(lesen, 3)
            os.dup2(schreiben, 4)

        self._proc = subprocess.Popen(
            [
                finde_chrome(),
                "--headless=new",
                "--remote-debugging-pipe",
                "--no-sandbox",
                "--no-first-run",
                "--disable-gpu",
                "--hide-scrollbars",
                # Same glyph positions on every machine: without these two, text widths differ
                # between hosts and a line break moves everything below it.
                "--font-render-hinting=none",
                "--disable-lcd-text",
                "--force-color-profile=srgb",
                f"--user-data-dir={self._profil}",
                "about:blank",
            ],
            preexec_fn=fds,
            close_fds=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        os.close(an_chrome_r)
        os.close(von_chrome_w)
        self._puffer = b""
        self._id = 0
        self.ereignisse: list[dict] = []
        return self

    def __exit__(self, *_: object) -> None:
        self._proc.terminate()
        try:
            self._proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self._proc.kill()
            self._proc.wait()
        os.close(self._an_chrome)
        os.close(self._von_chrome)
        # Chrome's helper processes outlive the main one by a moment and keep writing to the
        # profile: a single pass can fail on a file that has just appeared.
        for _ in range(50):
            shutil.rmtree(self._profil, ignore_errors=True)
            if not os.path.exists(self._profil):
                return
            time.sleep(0.1)
        raise BrowserFehler(f"Chrome-Profil bleibt liegen: {self._profil}")

    def _lies(self, frist: float) -> dict:
        ende = time.monotonic() + frist
        while b"\0" not in self._puffer:
            rest = ende - time.monotonic()
            if rest <= 0 or not select.select([self._von_chrome], [], [], rest)[0]:
                raise BrowserFehler(f"keine Antwort von Chrome innerhalb von {frist:.0f} s")
            teil = os.read(self._von_chrome, 1 << 20)
            if not teil:
                raise BrowserFehler("Chrome hat die Verbindung beendet")
            self._puffer += teil
        nachricht, self._puffer = self._puffer.split(b"\0", 1)
        return json.loads(nachricht)

    def sende(self, methode: str, sitzung: str | None = None, frist: float = FRIST, **params: object) -> dict:
        self._id += 1
        nachricht: dict = {"id": self._id, "method": methode, "params": params}
        if sitzung:
            nachricht["sessionId"] = sitzung
        os.write(self._an_chrome, json.dumps(nachricht).encode() + b"\0")
        while True:
            antwort = self._lies(frist)
            if antwort.get("id") == self._id:
                if "error" in antwort:
                    raise BrowserFehler(f"{methode}: {antwort['error'].get('message')}")
                return antwort.get("result", {})
            if "method" in antwort:
                self.ereignisse.append(antwort)

    def warte_auf(self, methode: str, sitzung: str, frist: float = FRIST) -> dict:
        for i, e in enumerate(self.ereignisse):
            if e["method"] == methode and e.get("sessionId") == sitzung:
                return self.ereignisse.pop(i)
        ende = time.monotonic() + frist
        while True:
            rest = ende - time.monotonic()
            if rest <= 0:
                raise BrowserFehler(f"{methode} kam nicht innerhalb von {frist:.0f} s")
            e = self._lies(rest)
            if e.get("method") == methode and e.get("sessionId") == sitzung:
                return e
            if "method" in e:
                self.ereignisse.append(e)

    def seite(self, breite: int = 1280, hoehe: int = 900, skript: str = "") -> "Seite":
        ziel = self.sende("Target.createTarget", url="about:blank")["targetId"]
        sitzung = self.sende("Target.attachToTarget", targetId=ziel, flatten=True)["sessionId"]
        return Seite(self, sitzung, breite, hoehe, skript)


class Seite:
    def __init__(self, browser: Browser, sitzung: str, breite: int, hoehe: int, skript: str) -> None:
        self.b, self.s = browser, sitzung
        self.sende("Page.enable")
        self.sende("Runtime.enable")
        self.sende("Network.enable")
        self.sende("Emulation.setDeviceMetricsOverride", width=breite, height=hoehe,
                   deviceScaleFactor=1, mobile=False)
        self.sende("Emulation.setTimezoneOverride", timezoneId="Europe/Berlin")
        self.sende("Emulation.setLocaleOverride", locale="de-DE")
        if skript:
            self.sende("Page.addScriptToEvaluateOnNewDocument", source=skript)

    def sende(self, methode: str, **params: object) -> dict:
        return self.b.sende(methode, self.s, **params)

    def geh(self, url: str) -> None:
        self.b.ereignisse[:] = [e for e in self.b.ereignisse if e.get("sessionId") != self.s]
        # A tab in the background gets no animation frames and no paint: rAF and screenshots hang.
        self.sende("Page.bringToFront")
        antwort = self.sende("Page.navigate", url=url)
        if antwort.get("errorText"):
            raise BrowserFehler(f"{url}: {antwort['errorText']}")
        self.b.warte_auf("Page.loadEventFired", self.s)
        self.js("document.fonts.ready.then(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))))")

    def js(self, ausdruck: str):
        """Evaluates an expression; promises are awaited, a thrown error is a test error."""
        antwort = self.sende("Runtime.evaluate", expression=ausdruck, awaitPromise=True, returnByValue=True)
        if "exceptionDetails" in antwort:
            d = antwort["exceptionDetails"]
            raise BrowserFehler(f"JS: {d.get('exception', {}).get('description') or d.get('text')}")
        return antwort["result"].get("value")

    def warte(self, bedingung: str, frist: float = 10.0) -> None:
        ende = time.monotonic() + frist
        while not self.js(bedingung):
            if time.monotonic() > ende:
                raise BrowserFehler(f"Bedingung nach {frist:.0f} s nicht erfüllt: {bedingung}")
            time.sleep(0.05)

    def foto(self, x: float, y: float, breite: float, hoehe: float, massstab: float) -> str:
        """PNG of a page region as base64, also beyond the viewport."""
        return self.sende("Page.captureScreenshot", format="png", captureBeyondViewport=True,
                          clip={"x": x, "y": y, "width": breite, "height": hoehe, "scale": massstab})["data"]

    def medium(self, medium: str) -> None:
        self.sende("Emulation.setEmulatedMedia", media=medium)

    def anfragen(self) -> tuple[list[str], list[str]]:
        """Everything the page asked for since the last navigation, and what failed."""
        alle: list[str] = []
        kaputt: list[str] = []
        bekannt: dict[str, str] = {}
        for e in self.b.ereignisse:
            if e.get("sessionId") != self.s:
                continue
            p = e.get("params", {})
            if e["method"] == "Network.requestWillBeSent":
                url = p["request"]["url"]
                bekannt[p["requestId"]] = url
                alle.append(url)
            elif e["method"] == "Network.responseReceived" and p["response"]["status"] >= 400:
                kaputt.append(f"{p['response']['status']} {p['response']['url']}")
            elif e["method"] == "Network.loadingFailed" and not p.get("canceled"):
                kaputt.append(f"{p.get('errorText')} {bekannt.get(p['requestId'], '?')}")
        return alle, kaputt


def schreibe_png(ziel: Path, daten: str) -> None:
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_bytes(base64.b64decode(daten))
