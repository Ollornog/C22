#!/usr/bin/env python3
"""The browser level: what no string test can see.

    python3 tests/test_visual.py           # compare against tests/visual/, change nothing
    python3 tests/test_visual.py --renew   # write new reference images, on purpose and in the diff

Builds the website into a temp directory and looks at it in headless Chrome:

- every gallery section per view is compared to its reference image;
- every request a page makes goes to the page's own origin, none of them fails;
- every delivered page names a favicon;
- components that only show their behaviour when used are used: a scrolled table of contents,
  a carousel, a calendar, a chart, the text preview, the print block.

A missing Chrome is a failure, not a skip. `scripts/check.sh --fast` leaves this suite out.

What counts as a difference: reference and capture are compared in blocks of 8x8 pixels at a third
of the size. A pixel counts when a channel is off by more than 48 of 255, a block counts when more than
a quarter of its pixels do. Edge smoothing changes scattered pixels and stays below that, a moved
button fills whole blocks. The suite proves this on every run by moving a button itself.
"""
from __future__ import annotations

import base64
import functools
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from _cdp import Browser, BrowserFehler, Seite, schreibe_png  # noqa: E402
from _kit import hygiene  # noqa: E402
from _kit.report import Report  # noqa: E402

REFERENZ = HERE / "visual"
MASSSTAB = 1 / 3
BLOCK = 8
KANAL = 48
ANTEIL = 0.25
HOEHE_TOLERANZ = 2  # px of the reduced image: rounding differs between machines

ANSICHTEN = {
    "desktop": (1280, 900, "light"),
    "mobile": (390, 844, "light"),
    "dark": (1280, 900, "dark"),
}
SEITEN = ("components", "blocks", "charts", "typeset")
ALLE_SEITEN = ("index", *SEITEN, "generator", "legal")
PACKS = ("vega", "spica", "ankaa", "nova", "maia", "lyra", "mira", "luma", "sera", "rhea", "underdoc")
# Sections a layout pack reshapes (ADR-2) are compared in that pack as well, next to the vega images:
# reference <page>--<section>@<pack>.png. Without the pack the block must look like the rest of vega,
# with it like the app it was made for — both are pinned.
PACK_ABSCHNITTE = {"underdoc": {"blocks": ("navigation-document-workspace", "navigation-workspace-editing", "navigation-workspace-more", "navigation-workspace-views")}}

# Time and chance stand still, so a calendar or a clock looks the same on every run.
FEST = """
(() => {
  const T = Date.UTC(2026, 0, 15, 11, 0, 0), R = Date;
  window.Date = class extends R {
    constructor(...a) { if (a.length) super(...a); else super(T); }
    static now() { return T; }
  };
  let s = 22;
  Math.random = () => (s = (s * 16807) % 2147483647) / 2147483647;
})();
"""
# The page scrolls inside <main>; laid out in full, every section can be captured whole.
AUSGEROLLT = r"""
(() => {
  const st = document.createElement('style');
  st.textContent = `
    *, *::before, *::after { animation: none !important; transition: none !important; caret-color: transparent !important; }
    html, body, body > *, main { height: auto !important; max-height: none !important; overflow: visible !important; }
    /* Written by the browser in its own language: not C22's to answer for. */
    input[type=date]::-webkit-datetime-edit, input[type=file] { color: transparent !important; }
    input[type=file]::file-selector-button { color: transparent !important; width: 7rem !important; }
  `;
  document.head.appendChild(st);
  // Inter is the only font C22 brings. Emoji, Arabic and Hebrew come from whatever the machine has
  // installed, so they become plain letters here: the layout around them still counts.
  const fremd = /[\p{Extended_Pictographic}\u0590-\u08FF\uFB1D-\uFDFF\uFE70-\uFEFF\uFE00-\uFE0F]/gu;
  const gang = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (gang.nextNode()) {
    if (!['SCRIPT', 'STYLE'].includes(gang.currentNode.parentElement.tagName)) gang.currentNode.data = gang.currentNode.data.replace(fremd, 'x');
  }
  document.querySelectorAll('[placeholder]').forEach(e => { e.placeholder = e.placeholder.replace(fremd, 'x'); });
  // The tabs of the charts page are its navigation: each chart gets captured, not only the first tab.
  document.querySelectorAll('#charts > [role=tabpanel][hidden]').forEach(p => { p.hidden = false; });
})();
"""
VERGLEICH = """
async (a, b, block, kanal, anteil) => {
  const lade = d => new Promise((ok, no) => { const i = new Image(); i.onload = () => ok(i); i.onerror = no; i.src = 'data:image/png;base64,' + d; });
  const [ia, ib] = await Promise.all([lade(a), lade(b)]);
  const w = Math.min(ia.width, ib.width), h = Math.min(ia.height, ib.height);
  const pixel = i => { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d', { willReadFrequently: true }); x.drawImage(i, 0, 0); return x.getImageData(0, 0, w, h); };
  const pa = pixel(ia), pb = pixel(ib), da = pa.data, db = pb.data;
  let bloecke = 0;
  const out = document.createElement('canvas'); out.width = w; out.height = h;
  const ox = out.getContext('2d'); ox.drawImage(ib, 0, 0); ox.fillStyle = 'rgba(255,0,0,.45)';
  for (let by = 0; by < h; by += block) for (let bx = 0; bx < w; bx += block) {
    let n = 0, z = 0;
    for (let y = by; y < Math.min(by + block, h); y++) for (let x = bx; x < Math.min(bx + block, w); x++) {
      const i = (y * w + x) * 4; z++;
      if (Math.abs(da[i] - db[i]) > kanal || Math.abs(da[i + 1] - db[i + 1]) > kanal || Math.abs(da[i + 2] - db[i + 2]) > kanal) n++;
    }
    if (n > z * anteil) { bloecke++; ox.fillRect(bx, by, block, block); }
  }
  return { bloecke, hoeheA: ia.height, hoeheB: ib.height, breiteA: ia.width, breiteB: ib.width,
           diff: bloecke ? out.toDataURL('image/png').split(',')[1] : '' };
}
"""


def baue_site(arbeit: Path) -> Path:
    """Builds in a copy of the tree: the suite must leave the working tree as it found it."""
    quelle = arbeit / "src"
    weg = shutil.ignore_patterns(".git", "_site", ".venv", "__pycache__", "*.egg-info", "tailwindcss",
                                 ".claude", "visual")
    shutil.copytree(ROOT, quelle, ignore=weg)
    tailwind = ROOT / "tools" / "tailwindcss"
    if tailwind.exists():
        (quelle / "tools" / "tailwindcss").symlink_to(tailwind)
    else:
        subprocess.run(["bash", "scripts/fetch-tailwind.sh"], cwd=quelle, check=True)
    site = arbeit / "site"
    subprocess.run([sys.executable, "scripts/build-site.py", str(site)], cwd=quelle, check=True,
                   stdout=subprocess.DEVNULL)
    probeseite_combobox(site)
    return site


def probeseite_combobox(site: Path) -> None:
    """A page as an app with its own menus builds it: Basecoat's core and its combobox alone, not basecoat.all.min.js
    (the gallery loads the whole bundle, so it cannot show this). Not part of the website; only the suite opens it."""
    probe = site / "probe"
    probe.mkdir()
    for datei in ("basecoat.min.js", "combobox.min.js"):
        shutil.copy2(ROOT / "c22" / "vendor" / "basecoat" / "dist" / "js" / datei, probe / datei)
    (probe / "combobox-alone.html").write_text(
        '<!doctype html><html lang="de"><head><meta charset="utf-8"><link rel="icon" href="data:,">'
        '<link rel="stylesheet" href="../c22/static/css/c22-vega.css">'
        '<script src="basecoat.min.js" defer></script><script src="combobox.min.js" defer></script>'
        '<script src="../c22/static/js/c22.js" defer></script></head><body class="p-8">'
        '<div class="dropdown-menu" id="probe-dm"><button type="button" class="btn" id="probe-dm-t" aria-haspopup="menu" '
        'aria-controls="probe-dm-m" aria-expanded="false">Menü der App</button><div id="probe-dm-p" data-popover '
        'aria-hidden="true"><div role="menu" id="probe-dm-m"><button type="button" role="menuitem">Eins</button></div></div>'
        '</div><div id="probe-ort" class="mt-4"></div></body></html>', encoding="utf-8")


class StillerHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_: object) -> None:
        pass


def starte_server(site: Path) -> tuple[http.server.ThreadingHTTPServer, str]:
    handler = functools.partial(StillerHandler, directory=str(site))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


def lade_ausgerollt(s: Seite, url: str) -> None:
    s.geh(url)
    s.js(AUSGEROLLT)
    s.js("""Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })))
            .then(() => new Promise(r => setTimeout(r, 150)))""")


OBERSTE = "[...document.querySelectorAll('main section[id]')].filter(e => !e.parentElement.closest('section[id]'))"


def abschnitte(s: Seite) -> list[str]:
    return s.js(f"{OBERSTE}.filter(e => e.getBoundingClientRect().width > 0).map(e => e.id)")


def foto_abschnitt(s: Seite, kennung: str) -> str:
    """Only this section is laid out: painting a page of 60,000 px per capture takes half a second."""
    a = s.js(f"""(() => {{
      {OBERSTE}.forEach(e => {{ e.style.display = e.id === {kennung!r} ? '' : 'none'; }});
      return new Promise(ok => requestAnimationFrame(() => requestAnimationFrame(() => {{
        const r = document.getElementById({kennung!r}).getBoundingClientRect();
        ok({{ x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height }});
      }})));
    }})()""")
    return s.foto(a["x"], a["y"], a["w"], a["h"], MASSSTAB)


def vergleiche(hilfe: Seite, referenz: str, ist: str) -> dict:
    return hilfe.js(f"({VERGLEICH})({json.dumps(referenz)}, {json.dumps(ist)}, {BLOCK}, {KANAL}, {ANTEIL})")


def weicht_ab(e: dict) -> str:
    if abs(e["hoeheA"] - e["hoeheB"]) > HOEHE_TOLERANZ or abs(e["breiteA"] - e["breiteB"]) > HOEHE_TOLERANZ:
        return f"Größe {e['breiteA']}x{e['hoeheA']} -> {e['breiteB']}x{e['hoeheB']}"
    return f"{e['bloecke']} Blöcke" if e["bloecke"] else ""


def bilder(r: Report, b: Browser, basis: str, erneuern: bool, ablage: Path) -> None:
    hilfe = b.seite()
    hilfe.geh("about:blank")
    gefunden: set[Path] = set()
    for ansicht, (breite, hoehe, theme) in ANSICHTEN.items():
        s = b.seite(breite, hoehe, FEST)
        abweichend: list[str] = []
        fehlend: list[str] = []
        neu = 0
        anzahl = 0
        laeufe = [(seite, "vega", None) for seite in SEITEN] + [
            (seite, pack, kennungen) for pack, je_seite in PACK_ABSCHNITTE.items() for seite, kennungen in je_seite.items()]
        for seite, pack, nur in laeufe:
            lade_ausgerollt(s, f"{basis}/{seite}.html?pack={pack}&theme={theme}&lang=de")
            vorhanden = abschnitte(s)
            if nur is not None:
                fehlend += [f"{seite}--{k}@{pack} (Abschnitt fehlt)" for k in nur if k not in vorhanden]
            for kennung in (vorhanden if nur is None else [k for k in nur if k in vorhanden]):
                anzahl += 1
                zusatz = "" if pack == "vega" else f"@{pack}"
                datei = REFERENZ / ansicht / f"{seite}--{kennung}{zusatz}.png"
                gefunden.add(datei)
                ist = foto_abschnitt(s, kennung)
                if not datei.exists():
                    if erneuern:
                        schreibe_png(datei, ist)
                        neu += 1
                    else:
                        fehlend.append(datei.name)
                    continue
                vor = base64.b64encode(datei.read_bytes()).decode()
                e = vergleiche(hilfe, vor, ist)
                grund = weicht_ab(e)
                if not grund:
                    continue
                if erneuern:
                    # Below the threshold the file stays, so a renewal only touches what moved.
                    schreibe_png(datei, ist)
                    neu += 1
                    continue
                abweichend.append(f"{ansicht}/{datei.stem} ({grund})")
                schreibe_png(ablage / ansicht / f"{datei.stem}.ist.png", ist)
                if e["diff"]:
                    schreibe_png(ablage / ansicht / f"{datei.stem}.diff.png", e["diff"])
        s.sende("Page.close")
        if erneuern:
            print(f"  {ansicht}: {anzahl} Abschnitte, {neu} Referenzen geschrieben")
            continue
        r.check(f"{ansicht}: {anzahl} Abschnitte haben eine Referenz", anzahl > 0 and not fehlend,
                " | ".join(fehlend[:5]) + " -> python3 tests/test_visual.py --renew")
        r.check(f"{ansicht}: keine Abweichung (Bilder: {ablage})", not abweichend, " | ".join(abweichend[:8]))
    if erneuern:
        waisen = [d for d in REFERENZ.rglob("*.png") if d not in gefunden]
        for d in waisen:
            d.unlink()
        print(f"  {len(waisen)} verwaiste Referenzen entfernt")
    hilfe.sende("Page.close")


def schaerfe(r: Report, b: Browser, basis: str) -> None:
    """A comparison that never fires proves nothing, so each run moves a button on purpose."""
    hilfe = b.seite()
    hilfe.geh("about:blank")
    s = b.seite(1280, 900, FEST)
    lade_ausgerollt(s, f"{basis}/components.html?pack=vega&theme=light&lang=de")
    vorher = foto_abschnitt(s, "button")
    nochmal = foto_abschnitt(s, "button")
    r.check("Vergleich: dasselbe Bild zweimal ist gleich", not weicht_ab(vergleiche(hilfe, vorher, nochmal)))
    s.js("document.querySelector('#button .btn').style.transform = 'translateX(12px)'")
    verschoben = foto_abschnitt(s, "button")
    r.check("Vergleich: ein um 12 px verschobener Knopf wird rot", bool(weicht_ab(vergleiche(hilfe, vorher, verschoben))))
    s.sende("Page.close")
    hilfe.sende("Page.close")


def fremdressourcen(r: Report, b: Browser, basis: str) -> None:
    """The second view: the source does not see what JavaScript assembles at runtime."""
    eigen = urlsplit(basis).netloc
    s = b.seite()
    ziele = [f"{basis}/{p}.html?lang=de" for p in ALLE_SEITEN] + [f"{basis}/components.html?pack={p}" for p in PACKS]
    fremd: set[str] = set()
    kaputt: set[str] = set()
    anzahl = 0
    for url in ziele:
        s.geh(url)
        s.js("new Promise(r => setTimeout(r, 200))")
        alle, fehl = s.anfragen()
        anzahl += len(alle)
        kaputt.update(fehl)
        for u in alle:
            teile = urlsplit(u)
            if teile.scheme not in ("data", "blob") and teile.netloc != eigen:
                fremd.add(u)
    r.check(f"{len(ziele)} Seiten stellen Anfragen", anzahl > len(ziele), f"{anzahl} Anfragen")
    r.check("jede Anfrage bleibt beim eigenen Ursprung", not fremd, " | ".join(sorted(fremd)[:5]))
    r.check("keine Anfrage schlägt fehl", not kaputt, " | ".join(sorted(kaputt)[:5]))
    s.sende("Page.close")


def favicon(r: Report, basis: str) -> None:
    """On the raw response: Chrome wraps text in an HTML shell with a <head> of its own."""
    host = urlsplit(basis).netloc
    befunde: list[str] = []
    for p in ALLE_SEITEN:
        with urllib.request.urlopen(f"{basis}/{p}.html") as antwort:  # noqa: S310  own server
            befunde += [f"{p}: {b}" for b in hygiene.favicon_befunde_html(antwort.read().decode(), host)]
    r.check("jede ausgelieferte Seite nennt ihr Favicon", not befunde, " | ".join(befunde[:3]))
    # build-site.py only takes along what a page links to: the licence reaches the site through
    # the imprint, and the font is not served without it.
    try:
        with urllib.request.urlopen(f"{basis}/c22/static/fonts/OFL.txt") as antwort:  # noqa: S310  own server
            lizenz = antwort.read()
    except urllib.error.HTTPError as fehler:
        lizenz = str(fehler).encode()
    r.check("der Lizenztext der Schrift wird ausgeliefert", b"SIL OPEN FONT LICENSE" in lizenz.upper(), lizenz[:60].decode())
    with urllib.request.urlopen(f"{basis}/docs/logo.png") as antwort:  # noqa: S310  own server
        r.check("das Favicon wird ausgeliefert", antwort.status == 200 and antwort.read(4) == b"\x89PNG")


def verhalten(r: Report, b: Browser, basis: str) -> None:
    s = b.seite(1280, 900)
    k = f"{basis}/components.html?pack=vega&theme=light&lang=de"

    # Table of contents: scroll the container, read the reading mark.
    s.geh(k)
    s.js("""(() => { const c = document.querySelector('#toc-a-inhalt'); c.scrollTop = document.querySelector('#toc-a-3').offsetTop - c.offsetTop; })()""")
    s.warte("""document.querySelector('nav[data-toc="#toc-a-inhalt"] [aria-current]')?.getAttribute('href') === '#toc-a-3'""")
    r.check("Inhaltsverzeichnis: Scrollen setzt die Lesemarke", True)

    # Carousel: the next button moves the viewport.
    s.js("""(() => {
      const c = document.querySelector('[data-carousel]');
      window.__vp = c.querySelector('[data-carousel-viewport]');
      c.querySelector('[data-carousel-next]').click();
    })()""")
    s.warte("window.__vp.scrollLeft > 0")
    r.check("Karussell: der Weiter-Knopf bewegt die Bilder", True)

    # Calendar: the next month button changes the heading.
    titel = """document.querySelector('[data-calendar]').textContent"""
    vorher = s.js(titel)
    s.js("""document.querySelector('[data-calendar] [data-cal-next]').click()""")
    s.warte(f"{titel} !== {vorher!r}")
    r.check("Kalender: der Monatsknopf blättert", True)

    # Sidebar: bedienbar without onclick and without an inline style, a strict CSP allows both away.
    leiste = s.js("""(() => {
      const bl = document.getElementById('c22-sb-g');
      const zu = bl.getAttribute('aria-hidden');
      document.querySelector('[data-panel-toggle="#c22-sb-g"]').click();
      const halter = bl.closest('[data-sidebar-width]');
      return { vorher: zu, nachher: bl.getAttribute('aria-hidden'), breite: getComputedStyle(halter).getPropertyValue('--sidebar-width').trim(),
               inline: document.querySelectorAll('#sidebar .c22-examples [onclick], #sidebar .c22-examples [style*="--sidebar-width"]').length };
    })()""")
    r.check("Seitenleiste: der Umschalter wirkt ohne onclick", leiste["vorher"] != leiste["nachher"], str(leiste))
    r.check("Seitenleiste: Breite ohne Inline-Stil", leiste["breite"] == "15rem" and leiste["inline"] == 0, str(leiste))

    # Table: data-wrap wraps; without it the cell stays on one line.
    werte = s.js("""(() => {
      const t = [...document.querySelectorAll('#table table[data-wrap] td')][0];
      const n = document.querySelector('#table table:not([data-wrap]) td');
      const z = document.querySelector('#table td[data-wrap]');
      return [getComputedStyle(t).whiteSpace, getComputedStyle(n).whiteSpace, getComputedStyle(z).whiteSpace];
    })()""")
    r.check("Tabelle: data-wrap bricht um, ohne bleibt die Zeile", werte == ["normal", "nowrap", "normal"], str(werte))

    # Frame with a head: as wide as rail and panel on a wide screen; below md the menu button opens
    # rail and panel as a drawer, a followed link and Escape close it again.
    bloecke = f"{basis}/blocks.html?pack=vega&theme=light&lang=de"
    s.geh(bloecke)
    breit = s.js("""(() => {
      const f = document.querySelector('.app-frame[data-head]');
      const w = sel => f.querySelector(':scope > ' + sel).getBoundingClientRect();
      return { kopf: w('.app-frame-head').width, leiste: w('.sidebar[data-variant="rail"]').width,
               spalte: w('.sidebar[data-variant="panel"]').width, inhaltOben: w('main').top - f.getBoundingClientRect().top,
               menue: getComputedStyle(f.querySelector('[data-frame-menu]')).display };
    })()""")
    r.check("Rahmen mit Kopf: Kopf so breit wie Leiste und Spalte, Inhalt über die volle Höhe",
            abs(breit["kopf"] - breit["leiste"] - breit["spalte"]) < 1 and breit["inhaltOben"] < 1 and breit["menue"] == "none", str(breit))
    h = b.seite(390, 844)
    h.geh(bloecke)
    h.warte("document.querySelector('.app-frame[data-head] > .sidebar[data-variant=\"panel\"][data-sidebar-initialized]') !== null")
    schublade = h.js("""(() => {
      const f = document.querySelector('.app-frame[data-head]');
      const d = sel => getComputedStyle(f.querySelector(':scope > ' + sel)).display;
      const zu = { leiste: d('.sidebar[data-variant="rail"]'), spalte: d('.sidebar[data-variant="panel"]') };
      f.querySelector('[data-frame-menu]').click();
      const z = sel => Number(getComputedStyle(f.querySelector(':scope > ' + sel)).zIndex);
      const auf = { leiste: d('.sidebar[data-variant="rail"]'), spalte: d('.sidebar[data-variant="panel"]'),
                    leisteOben: z('.sidebar[data-variant="rail"]') > z('.sidebar[data-variant="panel"]'),
                    offen: f.querySelector(':scope > .sidebar[data-variant="panel"]').getAttribute('aria-hidden'),
                    expanded: f.querySelector('[data-frame-menu]').getAttribute('aria-expanded') };
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
      const esc = f.hasAttribute('data-menu-open');
      f.querySelector('[data-frame-menu]').click();
      const wieder = f.querySelector(':scope > .sidebar[data-variant="panel"]').getAttribute('aria-hidden');
      const link = f.querySelector(':scope > .sidebar[data-variant="panel"] a[href]');
      link.addEventListener('click', e => e.preventDefault(), { once: true });
      link.click();
      return { zu, auf, esc, wieder, nachLink: f.hasAttribute('data-menu-open') };
    })()""")
    # Below md every frame with a head is one column, with or without a panel: the main area is as wide as the frame.
    einspaltig = h.js("""(() => [...document.querySelectorAll('.app-frame[data-head]')].map(f => {
      const fr = f.getBoundingClientRect(), m = f.querySelector(':scope > main').getBoundingClientRect();
      return { cols: getComputedStyle(f).gridTemplateColumns.split(' ').length, main: Math.abs(m.width - fr.width) < 1, bar: f.dataset.head === 'bar' };
    }))()""")
    r.check("Rahmen mit Kopf: unter md eine Spalte, der Inhalt so breit wie der Rahmen (auch ohne Spalte, auch als Leiste)",
            len(einspaltig) >= 3 and any(x["cols"] == 1 for x in einspaltig) and all(x["cols"] == 1 and x["main"] for x in einspaltig) and any(x["bar"] for x in einspaltig), str(einspaltig))
    r.check("Rahmen mit Kopf: unter md zu, das Menü öffnet Leiste und Spalte, die Leiste liegt oben (ihre Menüs öffnen über der Spalte)",
            schublade["zu"] == {"leiste": "none", "spalte": "none"} and schublade["auf"] == {"leiste": "block", "spalte": "block", "leisteOben": True, "offen": "false", "expanded": "true"},
            str(schublade))
    r.check("Rahmen mit Kopf: Escape und ein Link schließen die Schublade, die Spalte bleibt dabei offen",
            not schublade["esc"] and not schublade["nachLink"] and schublade["wieder"] == "false", str(schublade))

    # Typeset: flow after the title and around a table.
    s.geh(f"{basis}/typeset.html?pack=vega&theme=light&lang=de")
    fluss = s.js("""(() => {
      const a = document.querySelector('article.typeset');
      const flow = parseFloat(getComputedStyle(a.querySelector(':scope > h1 + *')).fontSize);
      const m = e => parseFloat(getComputedStyle(e).marginTop);
      const c = a.querySelector(':scope > .table-container');
      return { h1: m(a.querySelector(':scope > h1 + *')), vorTabelle: m(c), nachTabelle: m(c.nextElementSibling), flow };
    })()""")
    r.check("Typeset: Abstand nach dem h1", fluss["h1"] > 0, str(fluss))
    r.check("Typeset: Abstand vor und nach dem Tabellen-Container",
            fluss["vorTabelle"] > 0 and fluss["nachTabelle"] > 0, str(fluss))

    # Text preview: three lines, a button only when something is hidden, the button opens it.
    s.geh(k)
    s.warte("document.querySelector('#text-clamp .text-clamp[data-ready]') !== null")
    v = s.js("""(() => {
      const [lang, kurz] = document.querySelectorAll('#text-clamp .text-clamp');
      const body = lang.querySelector('[data-clamp-body]');
      const btn = lang.querySelector('[data-clamp-toggle]');
      const zeilen = body.getBoundingClientRect().height / parseFloat(getComputedStyle(body).lineHeight);
      const zu = { zeilen, knopf: !btn.hidden, maske: getComputedStyle(body).maskImage !== 'none',
                   kurzKnopf: !kurz.querySelector('[data-clamp-toggle]').hidden,
                   kurzMaske: getComputedStyle(kurz.querySelector('[data-clamp-body]')).maskImage !== 'none' };
      btn.click();
      return { ...zu, auf: body.scrollHeight <= body.clientHeight + 1 && getComputedStyle(body).maskImage === 'none',
               label: btn.textContent, expanded: btn.getAttribute('aria-expanded') };
    })()""")
    r.check("Textvorschau: kürzt auf drei Zeilen und blendet aus", round(v["zeilen"]) == 3 and v["maske"], str(v))
    r.check("Textvorschau: Knopf nur bei Überhang", v["knopf"] and not v["kurzKnopf"] and not v["kurzMaske"], str(v))
    r.check("Textvorschau: der Knopf klappt auf und benennt sich um",
            v["auf"] and v["label"] == "Weniger anzeigen" and v["expanded"] == "true", str(v))

    # Flow: a node with a button is reachable by keyboard, its whole card is the target.
    knoten = s.js("""(() => {
      const b = document.querySelector('#flow [data-flow-open]');
      b.focus();
      const karte = b.closest('.card').getBoundingClientRect();
      b.closest('.card').scrollIntoView({ block: 'center' });
      const k = b.closest('.card').getBoundingClientRect();
      const unten = document.elementFromPoint(k.right - 24, k.bottom - 6);
      return { fokus: document.activeElement === b, trifft: unten === b, breite: karte.width };
    })()""")
    r.check("Ablauf: der Knoten-Knopf hat den Fokus und deckt die Karte", knoten["fokus"] and knoten["trifft"], str(knoten))

    # Print block: only the copy reaches the paper, black on white, from dark mode as well.
    s.geh(f"{basis}/components.html?pack=vega&theme=dark&lang=de")
    d = s.js("""(() => {
      window.__gedruckt = 0; window.print = () => { window.__gedruckt++; };
      document.querySelector('#print-block [data-print]').click();
      const kopie = document.querySelector('body > [data-print-copy]');
      return { gedruckt: window.__gedruckt, kopie: !!kopie, dunkel: document.documentElement.classList.contains('dark') };
    })()""")
    s.medium("print")
    p = s.js("""(() => {
      const kopie = document.querySelector('body > [data-print-copy]');
      const rest = [...document.body.children].filter(e => e !== kopie && !['SCRIPT', 'STYLE'].includes(e.tagName))
        .filter(e => getComputedStyle(e).display !== 'none').map(e => e.tagName);
      const titel = kopie.querySelector('.card-title');
      const farbe = e => { const c = document.createElement('canvas').getContext('2d'); c.fillStyle = getComputedStyle(e).color; c.fillRect(0, 0, 1, 1); return [...c.getImageData(0, 0, 1, 1).data].slice(0, 3); };
      const leise = kopie.querySelector('.card-description');
      return { sichtbar: getComputedStyle(kopie).display, rest, schrift: farbe(titel), leise: farbe(leise), knopf: getComputedStyle(kopie.querySelector('[data-print]')).display };
    })()""")
    s.medium("")
    aufraeumen = s.js("""window.dispatchEvent(new Event('afterprint')), { kopie: !!document.querySelector('[data-print-copy]'), dunkel: document.documentElement.classList.contains('dark') }""")
    r.check("Druckblock: Kopie unter body, dunkler Modus für den Druck aus", d == {"gedruckt": 1, "kopie": True, "dunkel": False}, str(d))
    r.check("Druckblock: auf dem Papier nur die Kopie, ohne Knopf",
            p["sichtbar"] == "block" and not p["rest"] and p["knopf"] == "none", str(p))
    r.check("Druckblock: schwarze Schrift, auch die leise", max(p["schrift"]) < 40 and max(p["leise"]) < 70, str(p))
    r.check("Druckblock: nach dem Druck ist alles wie vorher", aufraeumen == {"kopie": False, "dunkel": True}, str(aufraeumen))
    # A collapsed <details> that is the block itself opens on paper as well.
    zu = s.js("""(() => {
      const block = document.querySelector('#print-block details[data-printable]');
      block.open = false;
      block.querySelector('[data-print]').click();
      const kopie = document.querySelector('body > [data-print-copy]');
      const ergebnis = { offen: kopie.open, rahmen: block.open };
      window.dispatchEvent(new Event('afterprint'));
      return ergebnis;
    })()""")
    r.check("Druckblock: ein details-Block ist auf dem Papier offen", zu == {"offen": True, "rahmen": False}, str(zu))

    # Drop zone: a drag that carries files lights it up and leaving takes it off; a drag of text does nothing.
    z = s.js("""(() => {
      const zone = document.querySelector('#empty [data-dropzone]:not([data-over])');
      const mit = new DataTransfer(); mit.items.add(new File(['x'], 'a.txt', { type: 'text/plain' }));
      const ohne = new DataTransfer(); ohne.setData('text/plain', 'x');
      const ev = (t, dt, ziel) => (ziel || zone).dispatchEvent(new DragEvent(t, { bubbles: true, cancelable: true, dataTransfer: dt }));
      ev('dragenter', ohne); const text = zone.hasAttribute('data-over');
      ev('dragenter', mit); ev('dragenter', mit, zone.querySelector('h2')); ev('dragleave', mit);
      const drinnen = zone.hasAttribute('data-over');
      ev('dragleave', mit, zone.querySelector('h2')); const raus = zone.hasAttribute('data-over');
      ev('dragenter', mit); ev('drop', mit); const fallen = zone.hasAttribute('data-over');
      return { text, drinnen, raus, fallen };
    })()""")
    r.check("Ablagezone: Dateien darüber heben sie hervor, Verlassen und Ablegen nehmen es zurück",
            z == {"text": False, "drinnen": True, "raus": False, "fallen": False}, str(z))

    # Tab bar: the element that holds it gets room below where the bar shows (data-always at desktop width), and none
    # where the bar is gone (the plain bar from md on).
    t = s.js("""[...document.querySelectorAll('#tab-bar .tab-bar')].map(n => [n.hasAttribute('data-always'), parseFloat(getComputedStyle(n.parentElement).paddingBottom)])""")
    r.check("Tab-Leiste: schafft sich selbst Platz, nur wo sie steht",
            any(a and p >= 60 for a, p in t) and any(not a and p == 0 for a, p in t), str(t))

    # Weekly report on paper: the buttons stay off, the head of the table repeats, rows do not break.
    s.geh(f"{basis}/blocks.html?pack=vega&theme=light&lang=de")
    s.medium("print")
    w = s.js("""(() => {
      const blatt = document.querySelector('[id*="week-report"] .print-sheet');
      const knopf = blatt.querySelector('.print\\\\:hidden');
      return { knopf: getComputedStyle(knopf).display, kopf: getComputedStyle(blatt.querySelector('thead')).display,
               zeile: getComputedStyle(blatt.querySelector('tbody tr')).breakInside };
    })()""")
    s.medium("")
    r.check("Wochenbericht: auf Papier ohne Knöpfe, Tabellenkopf wiederholt, Zeilen ungeteilt",
            w == {"knopf": "none", "kopf": "table-header-group", "zeile": "avoid"}, str(w))

    # Sheet (EightPerDay M-6): the week row sticks right below the head, also after the head grew; today stays a word.
    k = s.js("""(async () => {
      const t = document.querySelector('#data-entry-time-sheet .table[data-sticky]');
      const box = t.parentElement, head = t.tHead, zeile = t.querySelector('tr[data-group-row]');
      const frame = () => new Promise(ok => requestAnimationFrame(() => requestAnimationFrame(ok)));
      box.scrollTop = 120; await frame();
      const oben = () => Math.round(zeile.cells[1].getBoundingClientRect().top - box.getBoundingClientRect().top - box.clientTop);
      const vorher = { kopf: Math.round(head.getBoundingClientRect().height), zeile: oben(),
                       tag: Math.round(t.querySelector('tbody th').getBoundingClientRect().left - box.getBoundingClientRect().left - box.clientLeft) };
      head.rows[0].cells[1].insertAdjacentHTML('beforeend', '<span class="block">zweite Zeile</span>');
      await frame(); await frame();
      const nachher = { kopf: Math.round(head.getBoundingClientRect().height), zeile: oben() };
      head.rows[0].cells[1].lastElementChild.remove(); box.scrollTop = 0;
      return { vorher, nachher };
    })()""")
    r.check("Stundenblatt: die Wochenzeile klebt unter dem Kopf, auch wenn er wächst",
            k["vorher"]["zeile"] == k["vorher"]["kopf"] and k["nachher"]["zeile"] == k["nachher"]["kopf"]
            and k["nachher"]["kopf"] > k["vorher"]["kopf"] and k["vorher"]["tag"] == 0, str(k))
    # Today and the running week in a sheet that sticks: the whole row is tinted, the sticky first cell too, and it stays
    # opaque (what scrolls under it must not shine through). Today as a column tints head and cells alike.
    h = s.js("""(() => {
      const b = e => getComputedStyle(e).backgroundColor;
      const t = document.querySelector('#data-entry-time-sheet .table[data-sticky]');
      const heute = t.querySelector('tbody tr[aria-current="date"]'), woche = t.querySelector('tr[data-group-row][aria-current="true"]');
      const normal = t.querySelector('tbody tr:not([aria-current]):not([data-group-row])');
      const raster = document.querySelector('#data-entry-time-sheet .table:not([data-sticky])');
      const sp = raster.querySelector('thead th[aria-current="date"]'), i = sp.cellIndex;
      const andere = raster.querySelector('thead th:not([aria-current])');
      const zellen = [...raster.tBodies[0].rows].map(r => r.cells[i]);
      return { zeile: [...heute.cells].map(c => b(c)), woche: [...woche.cells].map(c => b(c)), normal: b(normal.cells[0]),
               kopf: b(sp), andererKopf: b(andere), spalte: zellen.map(b), nachbar: b(raster.tBodies[0].rows[0].cells[i + 1]),
               kopfFett: getComputedStyle(sp).fontWeight, andererFett: getComputedStyle(andere).fontWeight,
               balken: getComputedStyle(sp).boxShadow !== 'none', ohneBalken: getComputedStyle(andere).boxShadow === 'none' };
    })()""")
    ein = lambda l: len(set(l)) == 1 and l[0] != "rgba(0, 0, 0, 0)" and "/" not in l[0]  # one colour, opaque
    r.check("Stundenblatt: heute und laufende Woche ganz getönt, auch die klebende erste Zelle, deckend",
            ein(h["zeile"]) and ein(h["woche"]) and h["zeile"][0] != h["normal"], str(h))
    r.check("Raster: heute als Spalte, Kopf und Zellen getönt, die anderen nicht",
            ein(h["spalte"] + [h["kopf"]]) and h["kopf"] == h["zeile"][0] and h["nachbar"] == "rgba(0, 0, 0, 0)"
            and h["balken"] and h["ohneBalken"], str(h))
    # A field that is the cell has no frame of its own; the chip line shows the field only with the focus.
    f = s.js("""(() => {
      const zelle = document.querySelector('#data-entry-time-sheet td[data-field] > .input');
      const feld = document.querySelector('#data-entry-time-sheet .chip-input > .input');
      const ohne = getComputedStyle(feld).opacity;
      feld.focus(); const mit = getComputedStyle(feld).opacity; feld.blur();
      return { rand: getComputedStyle(zelle).borderTopWidth, ohne, mit };
    })()""")
    r.check("Feld als Zelle ohne eigenen Rahmen, Chip-Zeile zeigt das Feld nur mit Fokus",
            f == {"rand": "0px", "ohne": "0", "mit": "1"}, str(f))
    # Popover without JavaScript: a click outside closes it, Escape closes it and gives the focus back to its button.
    p = s.js("""(async () => {
      const d = document.getElementById('c22-sheet-ansicht');
      const frame = () => new Promise(ok => requestAnimationFrame(() => requestAnimationFrame(ok)));
      d.open = true; document.body.click(); const aussen = d.open;
      // The body of a details that just opened takes the focus only once it is laid out: try until it does.
      d.open = true; const knopf = d.querySelector('button');
      for (let i = 0; i < 30 && document.activeElement !== knopf; i++) { await frame(); knopf.focus(); }
      const drin = document.activeElement === knopf;
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
      const esc = d.open, fokus = document.activeElement === d.querySelector('summary');
      d.open = true; d.querySelector('form p').click(); const innen = d.open;
      d.open = false;
      return { aussen, drin, esc, fokus, innen };
    })()""")
    r.check("Popover ohne JavaScript: Klick daneben und Escape schließen, Fokus zurück, Klick darin nicht",
            p == {"aussen": False, "drin": True, "esc": False, "fokus": True, "innen": True}, str(p))
    # Form in steps (UnderDoc's new collection): one step at a time, "next" checks the open step first, Enter goes on
    # instead of sending, "back" returns; the steps list follows.
    st = s.js("""(() => {
      const f = document.getElementById('c22-steps-new');
      const [eins, zwei] = f.querySelectorAll('[data-step]');
      const marke = [...f.querySelectorAll('ol.steps > li')];
      const knopf = (n) => f.querySelector('[data-step-' + n + ']');
      const zu_sehen = (el) => el.getClientRects().length > 0;
      const lage = () => ({ eins: zu_sehen(eins), zwei: zu_sehen(zwei), zurueck: zu_sehen(knopf('back')), weiter: zu_sehen(knopf('next')),
                            fertig: zu_sehen(knopf('done')), offen: marke.findIndex(m => m.getAttribute('aria-current') === 'step'),
                            erledigt: marke.filter(m => m.dataset.state === 'done').length });
      const start = lage();
      const name = f.querySelector('[name=title]'); name.value = '';
      knopf('next').click(); const leer = lage();
      name.value = 'Handbuch'; knopf('next').click(); const weiter = lage();
      const fokus = zwei.contains(document.activeElement);
      knopf('back').click(); const zurueck = lage();
      f.requestSubmit(); const enter = lage();
      knopf('back').click(); name.value = '';
      return { start, leer, weiter, fokus, zurueck, enter };
    })()""")
    erst = {"eins": True, "zwei": False, "zurueck": False, "weiter": True, "fertig": False, "offen": 0, "erledigt": 0}
    dann = {"eins": False, "zwei": True, "zurueck": True, "weiter": False, "fertig": True, "offen": 1, "erledigt": 1}
    r.check("Schritte: einer zur Zeit, Weiter prüft den Schritt, Enter geht weiter, Zurück kehrt um",
            st == {"start": erst, "leer": erst, "weiter": dann, "fokus": True, "zurueck": erst, "enter": dann}, str(st))

    # Number cells next to the spreadsheet (UnderDoc ADR-31): .text-right and data-type="number" align a cell to the end,
    # a plain cell to the start. Until T-20 this was checked inside the old app workspace, whose element defaults beat them.
    aw = s.js("""(() => {
      const ex = document.querySelector('.c22-example:has(#mo-sheets)');
      const a = e => getComputedStyle(e).textAlign;
      return { rechts: [...ex.querySelectorAll('.table td.text-right')].map(a), zahl: a(ex.querySelector('.table td[data-type="number"]')),
               links: a(ex.querySelector('.table td:not([class]):not([data-type])')) };
    })()""")
    r.check("Tabelle: .text-right und data-type=\"number\" richten Zellen aus wie überall",
            aw["rechts"] and set(aw["rechts"]) == {"right"} and aw["zahl"] == "end" and aw["links"] == "start", str(aw))
    # The spreadsheet (data-sticky="sheet"): the box scrolls inside its bounded height, letters and row numbers stick to
    # it; a selected cell is tinted AND framed, the active one framed thicker, the selected letter and number are bold.
    sh = s.js("""(async () => {
      const t = document.querySelector('#mo-sheets .table[data-sticky="sheet"]'), box = t.parentElement;
      const frame = () => new Promise(ok => requestAnimationFrame(() => requestAnimationFrame(ok)));
      // Narrower than the table's least width (row numbers and three dense columns are about 12rem), so it scrolls sideways.
      // The height comes from --table-max-height here, not from the example's max-h-* utility: that is the bounded box C22 gives.
      box.classList.remove('max-h-48'); box.style.setProperty('--table-max-height', '8rem');
      box.style.maxWidth = '6rem'; box.scrollTop = 60; box.scrollLeft = 40; await frame();
      const bb = box.getBoundingClientRect(), cs = getComputedStyle;
      const lage = { hoch: box.scrollHeight > box.clientHeight, kopf: Math.round(t.tHead.rows[0].cells[2].getBoundingClientRect().top - bb.top - box.clientTop),
                     nummer: Math.round(t.tBodies[0].rows[4].cells[0].getBoundingClientRect().left - bb.left - box.clientLeft),
                     gerollt: box.scrollTop > 0 && box.scrollLeft > 0 };
      const hoehe = Math.round(box.getBoundingClientRect().height);
      box.scrollTop = 0; box.scrollLeft = 0; box.style.maxWidth = ''; box.style.removeProperty('--table-max-height'); box.classList.add('max-h-48');
      const sel = t.querySelector('td[aria-selected="true"]:not([data-active])'), akt = t.querySelector('td[data-active]');
      const leer = t.querySelector('tbody td:not([aria-selected])');
      const bs = e => cs(e).boxShadow;
      return { lage, hoehe, getoent: cs(sel).backgroundColor !== cs(leer).backgroundColor, gerahmt: bs(sel) !== 'none' && bs(leer) === 'none',
               aktiv: /2px/.test(bs(akt)), buchstabe: +cs(t.querySelector('thead th[aria-selected="true"]')).fontWeight,
               nummerFett: +cs(t.querySelector('tbody th[aria-selected="true"]')).fontWeight,
               ruhig: +cs(t.querySelector('tbody th:not([aria-selected])')).fontWeight };
    })()""")
    r.check("Tabellenraster: der Kasten rollt in begrenzter Höhe, Buchstaben und Zeilennummern kleben",
            sh["lage"] == {"hoch": True, "kopf": 0, "nummer": 0, "gerollt": True} and sh["hoehe"] == 128, str(sh))
    r.check("Tabellenraster: Markierung getönt und gerahmt (nicht nur Farbe), aktive Zelle dicker, Kopf und Nummer fett",
            sh["getoent"] and sh["gerahmt"] and sh["aktiv"] and sh["buchstabe"] >= 600 and sh["nummerFett"] >= 600
            and sh["ruhig"] < 600, str(sh))

    # Chart: wide and flat stays flat, keeps its text size and reports a click.
    s.geh(f"{basis}/charts.html?pack=vega&theme=light&lang=de")
    s.js(AUSGEROLLT)
    s.warte("""[...document.querySelectorAll('[data-chart]')].some(e => JSON.parse(e.dataset.chart).height && e.querySelector('svg')?.getBoundingClientRect().height > 0)""")
    c = s.js("""(() => {
      const el = [...document.querySelectorAll('[data-chart]')].find(e => JSON.parse(e.dataset.chart).height);
      const asp = [...document.querySelectorAll('[data-chart]')].find(e => JSON.parse(e.dataset.chart).aspect);
      const svg = () => el.querySelector('svg');
      const text = () => { const t = svg().querySelector('text'); return t.getBoundingClientRect().height; };
      const m = { hoehe: svg().getBoundingClientRect().height, breite: svg().getBoundingClientRect().width, text: text(),
                  asp: asp.querySelector('svg').getBoundingClientRect().width / asp.querySelector('svg').getBoundingClientRect().height };
      let treffer = null;
      el.addEventListener('c22:chart-select', e => { treffer = e.detail; });
      svg().querySelectorAll('[data-hit]')[3].dispatchEvent(new MouseEvent('click', { bubbles: true }));
      const taste = new KeyboardEvent('keydown', { key: 'Enter', bubbles: true });
      const klick = treffer; treffer = null;
      svg().querySelectorAll('[data-hit]')[4].dispatchEvent(taste);
      const beschriftung = [...svg().querySelectorAll('text')].map(t => t.getBoundingClientRect());
      const ueberlappt = beschriftung.some((a, i) => beschriftung.slice(i + 1).some(b => a.right > b.left && b.right > a.left && Math.abs(a.top - b.top) < 2));
      return { ...m, klick, taste: treffer, ueberlappt };
    })()""")
    r.check("Diagramm: height ergibt genau diese Höhe", abs(c["hoehe"] - 160) < 1, str(c["hoehe"]))
    r.check("Diagramm: aspect ergibt das Seitenverhältnis", abs(c["asp"] - 4) < 0.05, str(c["asp"]))
    r.check("Diagramm: Klick meldet die Kategorie", bool(c["klick"]) and c["klick"]["index"] == 3, str(c["klick"]))
    r.check("Diagramm: Enter meldet die Kategorie", bool(c["taste"]) and c["taste"]["index"] == 4, str(c["taste"]))
    r.check("Diagramm: Beschriftungen überlappen nicht", not c["ueberlappt"])
    # Twice the width, same text: the box follows the element instead of scaling the text.
    schmal = s.js("""new Promise(ok => {
      const el = [...document.querySelectorAll('[data-chart]')].find(e => JSON.parse(e.dataset.chart).height);
      el.style.width = '400px';
      setTimeout(() => { const v = el.querySelector('svg'); ok({ b: v.getBoundingClientRect().width, h: v.getBoundingClientRect().height, t: v.querySelector('text').getBoundingClientRect().height }); }, 300);
    })""")
    r.check("Diagramm: schmaler gezogen bleiben Höhe und Schrift", abs(schmal["b"] - 400) < 1 and abs(schmal["h"] - 160) < 1
            and abs(schmal["t"] - c["text"]) < 1, str(schmal))
    s.sende("Page.close")


# The first frame in which nav1 of the stored example exists: what it shows there is what the first
# paint shows, because a frame callback runs before the paint.
ERSTES_BILD = """
(() => {
  const look = () => {
    const n = document.querySelector('.workspace[data-workspace-store] > .workspace-nav[data-level="2"]');
    if (n && !window.__ersteStufe) window.__ersteStufe = { nav1: n.parentElement.querySelector(':scope > [data-level="1"]').dataset.step,
      nav2: n.dataset.step, nav3: n.parentElement.style.getPropertyValue('--workspace-nav3') };
    else requestAnimationFrame(look);
  };
  requestAnimationFrame(look);
})();
"""


# Dragging (app-workspace-drag.js) on an example to try it, for any list: the selectors name its rows.
ZIEHEN_JS = """(async () => {
      const box = document.querySelector(%(box)r);
      box.scrollIntoView({ block: 'center' });
      const pause = ms => new Promise(r => setTimeout(r, ms));
      const row = n => [...box.querySelectorAll(%(row)r)].find(x => !x.closest('.dropgap') && x.textContent.trim() === n);
      const oben = () => [...box.querySelectorAll(%(oben)r)].filter(n => n.closest('li').style.display !== 'none').map(n => n.textContent.trim()).join(' ');
      const zieh = async (von, nach, anteil, warten, abbrechen) => {
        const a = row(von).getBoundingClientRect(), x = a.left + a.width / 2, y = a.top + a.height / 2;
        row(von).dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, button: 0, clientX: x, clientY: y, pointerId: 1 }));
        window.dispatchEvent(new PointerEvent('pointermove', { bubbles: true, clientX: x, clientY: y + 8, pointerId: 1 }));
        await pause(60);
        const b = row(nach).getBoundingClientRect(), ty = b.top + b.height * anteil;
        window.dispatchEvent(new PointerEvent('pointermove', { bubbles: true, clientX: x, clientY: ty, pointerId: 1 }));
        await pause(warten);
        const gehalten = [...box.querySelectorAll(%(held)r)].map(n => n.textContent.trim()).join();
        const gerahmt = [...box.querySelectorAll('.drop-into')].map(n => n.textContent.trim()).join();
        if (abbrechen) document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
        else window.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, clientX: x, clientY: ty, pointerId: 1 }));
        await pause(20);
        return { gehalten, gerahmt, danach: oben() };
      };
      const start = oben();
      const hoch = await zieh('Kran', 'Turm', 0.1, 200, false);
      const esc = await zieh('Strom', 'Turm', 0.1, 100, true);
      const drauf = await zieh('Antennen', 'Turm', 0.5, 450, false);
      const unter = [...row('Turm').closest('li').querySelectorAll(%(kinder)r)].map(n => n.textContent.trim()).join();
      return { start, hoch, esc, drauf, unter, uebrig: box.querySelectorAll('.dropgap').length };
    })()"""


def arbeitsbereich(r: Report, b: Browser, basis: str) -> None:
    """The workspace: columns snap and drag, the list toggles, menus, drawer, phone, paper, strict CSP."""
    url = f"{basis}/blocks.html?pack=vega&theme=light&lang=de"
    s = b.seite(1280, 900)
    s.geh(url)
    s.js("localStorage.removeItem('c22-beispiel-arbeitsbereich')")
    s.geh(url)
    roh = s.js("""(() => {
      const w = document.querySelector('.workspace[data-workspace-store]');
      return { inline: w.parentElement.querySelectorAll('[onclick], [onkeydown], [style]').length,
               greifer: [...w.querySelectorAll(':scope > .workspace-nav > [data-grip]')].map(g => [g.getAttribute('role'), g.tabIndex, g.getAttribute('aria-valuenow')]) };
    })()""")
    r.check("Arbeitsbereich: kein onclick, kein style-Attribut im Markup (strenge CSP)", roh["inline"] == 0, str(roh))
    r.check("Arbeitsbereich: jede Spaltenkante ist ein bedienbarer Trenner mit Wert",
            len(roh["greifer"]) == 3 and all(g[0] == "separator" and g[1] == 0 and g[2] for g in roh["greifer"]), str(roh))

    spalten = s.js("""(() => {
      const w = document.querySelector('.workspace[data-workspace-store]');
      w.scrollIntoView();
      const n = l => w.querySelector(':scope > [data-level="' + l + '"]');
      const breite = l => Math.round(n(l).getBoundingClientRect().width);
      const stufe = i => { const p = document.createElement('div'); p.style.width = 'var(--workspace-step-' + i + ')'; w.appendChild(p); const x = Math.round(p.getBoundingClientRect().width); p.remove(); return x; };
      const stufen = [0, 1, 2, 3].map(stufe);
      let gemeldet = null;
      w.addEventListener('c22:workspace-columns', e => { gemeldet = e.detail; });
      const taste = (l, key) => { const g = n(l).querySelector(':scope > [data-grip]'); g.focus(); g.dispatchEvent(new KeyboardEvent('keydown', { key, bubbles: true })); };
      const ziehe = (l, dx) => {
        const g = n(l).querySelector(':scope > [data-grip]'), q = g.getBoundingClientRect(), x = q.left + 2, y = q.top + 50;
        g.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, button: 0, clientX: x, clientY: y, pointerId: 1 }));
        window.dispatchEvent(new PointerEvent('pointermove', { bubbles: true, clientX: x + dx, clientY: y, pointerId: 1 }));
        const mitten = w.hasAttribute('data-resizing');
        window.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, clientX: x + dx, clientY: y, pointerId: 1 }));
        return mitten;
      };
      const vorher = { nav1: breite(1), nav2: breite(2), nav3: breite(3) };
      taste(1, 'ArrowRight');
      const pfeil = { stufe: n(1).dataset.step, breite: breite(1), wert: n(1).querySelector('[data-grip]').getAttribute('aria-valuenow') };
      const zieht = ziehe(2, -(stufen[3] - stufen[1]) + 6);
      const gezogen = { stufe: n(2).dataset.step, breite: breite(2), resizing: zieht, danach: w.hasAttribute('data-resizing') };
      ziehe(3, 50);
      const frei = breite(3);
      taste(3, 'End');
      const max = breite(3);
      taste(3, 'Home');
      const min = breite(3);
      ziehe(3, 40);
      return { stufen, vorher, pfeil, gezogen, frei, max, min, ende: breite(3), gemeldet,
               gespeichert: JSON.parse(localStorage.getItem('c22-beispiel-arbeitsbereich')) };
    })()""")
    st, v = spalten["stufen"], spalten["vorher"]
    r.check("Arbeitsbereich: Startbreiten folgen data-step (nav1 Symbol, nav2 Symbol mit Text daneben)",
            v["nav1"] == st[0] and v["nav2"] == st[3], str(spalten))
    r.check("Arbeitsbereich: Pfeiltaste rastet nav1 eine Stufe weiter",
            spalten["pfeil"] == {"stufe": "1", "breite": st[1], "wert": "1"}, str(spalten))
    r.check("Arbeitsbereich: Ziehen rastet nav2 auf die nächste Stufe",
            spalten["gezogen"] == {"stufe": "1", "breite": st[1], "resizing": True, "danach": False}, str(spalten))
    r.check("Arbeitsbereich: nav3 frei, Ende und Anfang begrenzen",
            spalten["frei"] == v["nav3"] + 50 and spalten["max"] > spalten["frei"] and spalten["min"] < v["nav3"], str(spalten))
    r.check("Arbeitsbereich: Änderung wird gemeldet und gespeichert",
            spalten["gemeldet"] == spalten["gespeichert"] == {"nav1": 1, "nav2": 1, "nav3": spalten["ende"]}, str(spalten))

    # Back after a reload, already in the first frame, and from workspace-boot.js alone: c22.js is
    # blocked for this load, so its later restore cannot be what puts them back.
    s.sende("Page.addScriptToEvaluateOnNewDocument", source=ERSTES_BILD)
    s.sende("Network.setBlockedURLs", urls=["*/c22.js*"])
    s.geh(url)
    erst = s.js("window.__ersteStufe")
    s.sende("Network.setBlockedURLs", urls=[])
    r.check("Arbeitsbereich: gespeicherte Breiten stehen schon im ersten Bild (workspace-boot.js)",
            erst == {"nav1": "1", "nav2": "1", "nav3": f"{spalten['ende']}px"}, str(erst))
    s.geh(url)
    s.js("localStorage.removeItem('c22-beispiel-arbeitsbereich')")

    liste = s.js("""(() => {
      const w = document.querySelector('.workspace[data-workspace-store]');
      const li = [...w.querySelectorAll('.workspace-tree li')].find(l => l.querySelector(':scope > div > button:not([data-toggle]) > span').textContent === 'Netzwerk');
      const pfeil = li.querySelector(':scope > div > [data-toggle]'), name = li.querySelector(':scope > div > button:not([data-toggle])');
      const zu = () => ({ hidden: li.querySelector(':scope > ul').hidden, expanded: pfeil.getAttribute('aria-expanded') });
      const a = zu();
      pfeil.click();
      const b = zu();
      name.dispatchEvent(new MouseEvent('click', { bubbles: true, detail: 1 }));
      name.dispatchEvent(new MouseEvent('click', { bubbles: true, detail: 2 }));
      const c = zu();
      const markiert = name.getAttribute('aria-current');
      const andere = w.querySelectorAll('.workspace-nav[data-level="3"] [aria-current]').length;
      return { a, b, c, markiert, andere };
    })()""")
    r.check("Arbeitsbereich: der Pfeil klappt zu, ein Doppelklick auf den Namen wieder auf",
            liste["a"] == {"hidden": False, "expanded": "true"} and liste["b"] == {"hidden": True, "expanded": "false"}
            and liste["c"] == {"hidden": False, "expanded": "true"}, str(liste))
    r.check("Arbeitsbereich: ein Klick auf den Namen macht ihn zum aktuellen Eintrag",
            liste["markiert"] == "true" and liste["andere"] == 1, str(liste))

    menue = s.js("""(() => {
      const w = document.querySelector('.workspace[data-workspace-store]');
      const zeile = [...w.querySelectorAll('.workspace-tree li > div')].find(d => d.textContent.trim() === 'Offene Tickets');
      zeile.scrollIntoView({ block: 'center' });
      const q = zeile.getBoundingClientRect();
      zeile.querySelector('span').dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: q.left + 30, clientY: q.top + 8 }));
      const p = w.querySelector('[data-cm-panel]'), pq = p.getBoundingClientRect();
      return { offen: !p.hidden, titel: p.querySelector('[role=heading]').textContent, zeile: zeile.hasAttribute('data-menu-row'),
               amZeiger: Math.abs(pq.left - (q.left + 30)) < 2 && Math.abs(pq.top - (q.top + 8)) < 2 };
    })()""")
    r.check("Arbeitsbereich: Rechtsklick öffnet das Menü am Zeiger und nennt die Zeile",
            menue == {"offen": True, "titel": "Offene Tickets", "zeile": True, "amZeiger": True}, str(menue))
    s.js("document.body.click()")

    lade = s.js("""(() => {
      const w = document.querySelector('.workspace[data-workspace-store]');
      const d = w.querySelector('aside[data-drawer]'), knopf = w.querySelector('[role=toolbar] [data-drawer-toggle]');
      const a = d.hidden;
      knopf.click();
      const b = { hidden: d.hidden, expanded: knopf.getAttribute('aria-expanded'), ueber: getComputedStyle(d).position };
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
      return { a, b, esc: d.hidden, expanded: knopf.getAttribute('aria-expanded') };
    })()""")
    r.check("Arbeitsbereich: Zahnrad öffnet die Schublade über dem Fenster, Escape schließt",
            lade == {"a": True, "b": {"hidden": False, "expanded": "true", "ueber": "absolute"}, "esc": True, "expanded": "false"}, str(lade))

    seite = s.js("""(() => {
      const w = document.querySelector('.workspace[data-workspace-store]');
      const aktiv = w.querySelector(':scope > [data-level="1"] [aria-current]');
      const d = l => getComputedStyle(w.querySelector(':scope > [data-level="' + l + '"]')).display;
      aktiv.click();
      const weg = { attr: w.hasAttribute('data-nav-hidden'), nav2: d(2), nav3: d(3) };
      aktiv.click();
      const aus = [...w.querySelectorAll('[aria-disabled="true"]')].map(e => getComputedStyle(e).opacity);
      return { weg, zurueck: { attr: w.hasAttribute('data-nav-hidden'), nav2: d(2), nav3: d(3) }, aus };
    })()""")
    r.check("Arbeitsbereich: zweiter Klick auf die aktive Ansicht blendet nav2 und nav3 aus und wieder ein",
            seite["weg"] == {"attr": True, "nav2": "none", "nav3": "none"} and seite["zurueck"] == {"attr": False, "nav2": "flex", "nav3": "flex"}, str(seite))
    r.check("Arbeitsbereich: Ausgegrautes ist sichtbar und blass",
            seite["aus"] and all(0 < float(o) < 1 for o in seite["aus"]), str(seite))

    s.medium("print")
    papier = s.js("""(() => {
      const w = document.querySelector('.workspace[data-workspace-store]');
      const d = sel => getComputedStyle(w.querySelector(sel)).display;
      return { top: d(':scope > .workspace-top'), tabs: d(':scope > .workspace-tabs'), nav: d(':scope > [data-level="2"]'),
               werkzeug: d('[role=toolbar]'), titel: d('.workspace-main > header > h1'), inhalt: d('.workspace-main > section') };
    })()""")
    s.medium("")
    r.check("Arbeitsbereich: auf Papier nur Titel und Inhalt",
            papier == {"top": "none", "tabs": "none", "nav": "none", "werkzeug": "none", "titel": "block", "inhalt": "block"}, str(papier))
    # Dragging (app-workspace-drag.js), on the example to try it: up and down between entries, waiting on the middle of
    # one puts it below that one, Escape gives up, and the entry is held in the list as it looks.
    def ziehen(was: str, sel: dict) -> None:
        zug = s.js(ZIEHEN_JS % sel)
        r.check(f"{was}: Ziehen trägt den Eintrag, wie er aussieht, und legt ihn zwischen die Einträge",
                zug["start"] == "Turm Antennen Strom Kran" and zug["hoch"] == {"gehalten": "Kran", "gerahmt": "", "danach": "Kran Turm Antennen Strom"}, str(zug))
        r.check(f"{was}: Escape bricht das Ziehen ab, nichts bleibt zurück",
                zug["esc"] == {"gehalten": "Strom", "gerahmt": "", "danach": "Kran Turm Antennen Strom"} and zug["uebrig"] == 0, str(zug))
        r.check(f"{was}: kurz auf der Mitte eines Eintrags warten legt darunter",
                zug["drauf"]["gerahmt"] == "Turm" and zug["unter"] == "Antennen" and zug["drauf"]["danach"] == "Kran Turm Strom", str(zug))
    # On the building block (T-19 step 3): rows are li > div of .workspace-tree.
    ziehen("Arbeitsbereich aus Bausteinen", {"box": ".workspace-nav[data-drag-demo]", "row": "li > div", "oben": "ul.workspace-tree > li > div",
                                              "held": ".dropgap.held > div", "kinder": ":scope > ul > li > div"})

    s.sende("Page.close")

    h = b.seite(390, 844)
    h.geh(url)
    handy = h.js("""(() => {
      const w = document.querySelector('.workspace[data-workspace-store]');
      const d = l => getComputedStyle(w.querySelector(':scope > [data-level="' + l + '"]')).display;
      const zu = { nav2: d(2), nav3: d(3), suche: getComputedStyle(w.querySelector('.workspace-top > form')).display };
      w.querySelector(':scope > [data-level="1"] [aria-current]').click();
      const n2 = w.querySelector(':scope > [data-level="2"]').getBoundingClientRect(), m = w.querySelector('.workspace-main').getBoundingClientRect();
      const auf = { nav2: d(2), nav3: d(3), ueber: n2.left < m.left + 1 && n2.right > m.left };
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
      return { zu, auf, esc: d(2) };
    })()""")
    r.check("Arbeitsbereich: unter md öffnen nav2 und nav3 über dem Fenster, Escape schließt",
            handy == {"zu": {"nav2": "none", "nav3": "none", "suche": "none"}, "auf": {"nav2": "flex", "nav3": "flex", "ueber": True}, "esc": "none"},
            str(handy))
    h.sende("Page.close")

    # Layout pack (ADR-2): the pack changes the form, vega keeps the block's defaults. The image comparison sees
    # geometry, not a faint tint or half a pixel of text, so the decisive values are read here as well.
    def form(pack: str) -> dict:
        f = b.seite(1280, 900)
        f.geh(f"{basis}/blocks.html?pack={pack}&theme=light&lang=de")
        werte = f.js("""(() => {
          const w = document.querySelector('#navigation-document-workspace .workspace'), c = e => getComputedStyle(w.querySelector(e));
          const kopf = c('.workspace-nav[data-level="3"] section > header'), muted = getComputedStyle(w).getPropertyValue('--muted');
          const probe = document.createElement('i'); probe.style.color = muted; w.append(probe);
          const band = getComputedStyle(probe).color;
          probe.style.color = getComputedStyle(w).getPropertyValue('--primary'); const primary = getComputedStyle(probe).color; probe.remove();
          const modus = getComputedStyle(document.querySelector('#navigation-workspace-editing [data-mode][aria-pressed="true"]')).backgroundColor === primary;
          return { band: kopf.backgroundColor === band, kopf: kopf.fontSize, kapitaelchen: c('.workspace-nav[data-level="2"] header').fontSize,
                   eintrag: c('.workspace-item').fontSize, dokument: c('.workspace-main > section > article').fontSize,
                   status: c('.workspace-main > footer').display, radius: c('.workspace-item').borderTopLeftRadius, modus };
        })()""")
        f.sende("Page.close")
        return werte
    ud, vega = form("underdoc"), form("vega")

    # Editing parts and windows (T-19 steps 2 and 3): what no picture shows.
    teile = b.seite(1280, 900)
    teile.geh(f"{basis}/blocks.html?pack=vega&theme=light&lang=de")
    werte = teile.js("""(() => {
      const griff = document.querySelector('#navigation-workspace-editing [data-block] > .editor-handle');
      const knopf = griff.querySelector(':scope > button'), sicht = () => getComputedStyle(griff).opacity;
      const offen = sicht(); knopf.setAttribute('aria-expanded', 'false'); const zu = sicht();
      knopf.focus(); const fokus = sicht(); knopf.blur(); knopf.setAttribute('aria-expanded', 'true');
      const leisten = [...document.querySelectorAll('#navigation-workspace-editing .editor-bar')];
      const zeilen = l => new Set([...l.querySelectorAll('.btn')].map(n => Math.round(n.getBoundingClientRect().top))).size;
      // The bar wraps between its groups; a group itself stays on one line (it only breaks when it alone is wider).
      const ganz = l => [...l.querySelectorAll(':scope > [role=group]')].every(g => zeilen(g) === 1);
      const fenster = [...document.querySelectorAll('#navigation-document-workspace .workspace-window')];
      const rahmen = getComputedStyle(fenster[0], '::after').borderTopWidth;
      const zurueck = getComputedStyle(fenster[1].querySelector('.workspace-tabs')).opacity;
      const vorne = getComputedStyle(fenster[0].querySelector('.workspace-tabs')).opacity;
      const toc = fenster[0].querySelector('nav.toc').getBoundingClientRect(), art = fenster[0].querySelector('article').getBoundingClientRect();
      return { offen, zu, fokus, schmal: Math.max(...leisten.map(zeilen)), gruppen: leisten.every(ganz), rahmen, zurueck, vorne, toc: toc.right <= art.left };
    })()""")
    teile.sende("Page.close")
    r.check("Griff eines Blocks: unsichtbar, bis man darüberfährt oder ihn fokussiert; offen, solange sein Menü offen ist",
            werte["offen"] == "1" and werte["zu"] == "0" and werte["fokus"] == "1", str(werte))
    r.check("Editor-Leiste: in einem schmalen Fenster bricht sie zwischen den Gruppen in eine zweite Zeile um",
            werte["schmal"] >= 2 and werte["gruppen"], str(werte))
    r.check("Zwei Fenster: das aktive gerahmt, das andere tritt zurück; das Inhaltsverzeichnis steht als Spalte vor dem Dokument",
            werte["rahmen"] == "2px" and werte["vorne"] == "1" and float(werte["zurueck"]) < 1 and werte["toc"], str(werte))
    handy = b.seite(390, 844)
    handy.geh(f"{basis}/blocks.html?pack=vega&theme=light&lang=de")
    sichtbar = handy.js("""[...document.querySelectorAll('#navigation-document-workspace .workspace-window')].map(f => getComputedStyle(f).display)""")
    handy.sende("Page.close")
    r.check("Zwei Fenster am Handy: nur das aktive Fenster", sichtbar == ["grid", "none"], str(sichtbar))
    # The head of a window with the read/edit toggle, narrow enough that the tools wrap: nothing runs over the title, and
    # the toggle keeps its size. A window without a tab row takes that row too (2026-11-22, found by UnderDoc).
    kopf = b.seite(1280, 900)
    kopf.geh(f"{basis}/blocks.html?pack=underdoc&theme=light&lang=de")
    werte = kopf.js("""(() => {
      const kopf = document.querySelector('#navigation-document-workspace .workspace-main > header');
      const knopf0 = document.createElement('button');
      knopf0.className = 'btn'; knopf0.setAttribute('data-mode', ''); knopf0.dataset.variant = 'outline';
      kopf.prepend(knopf0);
      const main = kopf.parentElement, alt = main.style.width;
      main.style.width = '420px';
      const r = s => kopf.querySelector(s).getBoundingClientRect();
      const werkzeug = r(':scope > div'), titel = r(':scope > h1'), knopf = r(':scope > [data-mode]');
      const zeilen = new Set([...kopf.querySelectorAll(':scope > div > *, :scope > div [role=toolbar] > *')].filter(n => n.getBoundingClientRect().height > 0).map(n => Math.round(n.getBoundingClientRect().top))).size;
      main.style.width = alt; knopf0.remove();
      const ws = document.querySelector('#navigation-document-workspace .workspace').cloneNode(true);
      ws.querySelector(':scope > .workspace-tabs').remove();
      document.querySelector('#navigation-document-workspace').append(ws);
      const oben = Math.round(ws.querySelector(':scope > .workspace-main').getBoundingClientRect().top - ws.getBoundingClientRect().top);
      ws.remove();
      return { zeilen, frei: titel.top >= werkzeug.bottom - 0.5, knopf: [Math.round(knopf.width), Math.round(knopf.height)], oben };
    })()""")
    kopf.sende("Page.close")
    r.check("Fensterkopf mit Lesen/Bearbeiten: umbrechende Werkzeuge laufen nicht über den Titel, der Knopf behält seine Größe (Pack underdoc 60px)",
            werte["zeilen"] >= 2 and werte["frei"] and werte["knopf"] == [60, 60], str(werte))
    r.check("Fenster ohne Reiterzeile: das Fenster nimmt auch deren Zeile (keine leere Zeile darüber)", werte["oben"] == 0, str(werte))
    r.check("Pack underdoc: Band hinter dem Kopf der Sammlung, kleinere Kapitälchen und Einträge, 15px-Dokument, engere Radien, Bearbeiten gefüllt",
            ud["band"] and ud["kopf"] == "13.5px" and ud["kapitaelchen"] == "10.5px" and ud["eintrag"] == "13.5px"
            and ud["dokument"] == "15px" and ud["radius"] != vega["radius"] and ud["modus"], str(ud))
    r.check("Pack vega: derselbe Baustein mit seinen Vorgaben (kein Band, Kapitälchen 12px, Einträge 14px), Statuszeile in beiden",
            not vega["band"] and vega["kopf"] == "12px" and vega["kapitaelchen"] == "12px" and vega["eintrag"] == "14px"
            and vega["status"] == ud["status"] == "flex" and not vega["modus"], str(vega))


SCHALTER = r"""(() => {
  // data-behaviour="app": c22.js leaves the workspace to the app. The same probe runs on a copy without the switch,
  // which proves that every probe would see the behaviour.
  const vorlage = document.querySelector('#navigation-document-workspace .workspace');
  const probe = app => {
    const huelle = document.createElement('div');
    const w = vorlage.cloneNode(true);
    w.removeAttribute('data-workspace-store'); w.removeAttribute('data-nav-hidden'); delete w.dataset.workspaceRestored;
    w.querySelectorAll('[data-grip]').forEach(g => ['aria-valuenow', 'aria-valuemin', 'aria-valuemax'].forEach(a => g.removeAttribute(a)));
    if (app) w.setAttribute('data-behaviour', 'app');
    const ok = document.createElement('button'); ok.type = 'button'; ok.setAttribute('data-confirm', 'Wirklich?');
    w.querySelector('.workspace-main > section').append(ok);
    huelle.append(w); document.body.append(huelle);
    window.C22.workspace.init(huelle);
    const out = { init: w.querySelector(':scope > .workspace-nav > [data-grip]').hasAttribute('aria-valuenow') };
    const nav1 = w.querySelector(':scope > .workspace-nav[data-level="1"]'), griff = nav1.querySelector(':scope > [data-grip]');
    const schritt = nav1.dataset.step;
    griff.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true, cancelable: true }));
    out.taste = nav1.dataset.step !== schritt;
    const r = griff.getBoundingClientRect();
    griff.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true, cancelable: true, button: 0, clientX: r.x, clientY: r.y + 5, pointerId: 1 }));
    out.zeiger = w.hasAttribute('data-resizing');
    window.dispatchEvent(new PointerEvent('pointerup', { bubbles: true, pointerId: 1 }));
    w.querySelector(':scope > .workspace-nav[data-level="1"] .workspace-item[aria-current]').click();
    out.klick = w.hasAttribute('data-nav-hidden');
    const pfeil = w.querySelector('.workspace-tree [data-toggle][aria-expanded]'), vorher = pfeil.getAttribute('aria-expanded');
    pfeil.click();
    out.liste = pfeil.getAttribute('aria-expanded') !== vorher;
    const name = [...w.querySelectorAll('.workspace-tree li > div > button:not([data-toggle])')].find(n => !n.hasAttribute('aria-current'));
    name.click();
    out.aktuell = name.hasAttribute('aria-current');
    const doppel = new MouseEvent('dblclick', { bubbles: true, cancelable: true });
    name.dispatchEvent(doppel);
    out.doppel = doppel.defaultPrevented;
    ok.click();
    const dialog = document.querySelector('dialog[data-confirm-dialog][open]');
    out.bestaetigen = !!dialog;
    if (dialog) dialog.close();
    huelle.remove();
    return out;
  };
  return { app: probe(true), normal: probe(false) };
})()"""

ANSICHTEN_WERTE = r"""(() => {
  const v = document.querySelector('#navigation-workspace-views'), c = (e, p) => getComputedStyle(e, p || null);
  const zone = v.querySelector('[data-drop-zone="start"]');
  const zoneSicht = c(zone).display; zone.hidden = true; const zoneWeg = c(zone).display; zone.hidden = false;
  const linie = c(v.querySelector('.workspace-tab[data-drop="before"]'), '::before');
  const platz = c(v.querySelector('.workspace-tab[data-drop="slot"]'));
  const ungelesen = c(v.querySelector('.item[data-state="unread"] h4')).fontWeight;
  const gelesen = c(v.querySelector('a.item:not([data-state]) h4')).fontWeight;
  const offen = c(v.querySelector('a.item[aria-current]')).boxShadow;
  const erledigt = c(v.querySelector('label.item:has(input:checked) h4')).textDecorationLine;
  const menue = Math.round(v.querySelector('.workspace .command [role=menuitem]').getBoundingClientRect().height * 10) / 10;
  const heute = v.querySelector('.month-sheet td[aria-current="date"]');
  const probe = document.createElement('i'); probe.style.color = 'var(--primary)'; heute.append(probe); const primary = c(probe).color; probe.remove();
  return { wort: zone.textContent.trim(), nachWort: c(zone, '::after').content, zeiger: c(zone).pointerEvents, zoneSicht, zoneWeg,
           linie: linie.width, linieInhalt: linie.content, platz: platz.outlineWidth + ' ' + platz.outlineStyle,
           ungelesen, gelesen, offen, erledigt, menue,
           heute: c(heute).borderTopColor === primary, heuteHoch: Math.round(heute.getBoundingClientRect().height) };
})()"""


def arbeitsbereich_ansichten(r: Report, b: Browser, basis: str) -> None:
    """The other views (T-19 step 4) and the switch that leaves the workspace to the app: what no picture shows."""
    s = b.seite(1280, 900)
    s.geh(f"{basis}/blocks.html?pack=vega&theme=light&lang=de")
    sw = s.js(SCHALTER)
    s.sende("Page.close")
    r.check("Schalter data-behaviour=\"app\": c22.js lässt den Arbeitsbereich in Ruhe (keine Taste, kein Zeiger, kein Klick, "
            "kein Doppelklick, keine Beschriftung beim Start)",
            not any(sw["app"][k] for k in ("init", "taste", "zeiger", "klick", "liste", "aktuell", "doppel")), str(sw["app"]))
    r.check("Schalter: ohne ihn greift dasselbe Verhalten (die Gegenprobe sieht jede Wirkung)",
            all(sw["normal"][k] for k in ("init", "taste", "zeiger", "klick", "liste", "aktuell", "doppel")), str(sw["normal"]))
    r.check("Schalter: die übrigen Bausteine von c22.js wirken im Arbeitsbereich der App weiter (Bestätigen)",
            sw["app"]["bestaetigen"] and sw["normal"]["bestaetigen"], str(sw))
    werte = {}
    for pack in ("vega", "underdoc"):
        f = b.seite(1280, 900)
        f.geh(f"{basis}/blocks.html?pack={pack}&theme=light&lang=de")
        werte[pack] = f.js(ANSICHTEN_WERTE)
        f.sende("Page.close")
    v, ud = werte["vega"], werte["underdoc"]
    r.check("Ablagezone: das Wort ist Inhalt (übersetzbar), kein CSS-content; sie fängt keinen Zeiger; hidden blendet sie aus",
            v["wort"] == "Neue Spalte" and v["nachWort"] == "none" and v["zeiger"] == "none"
            and v["zoneSicht"] == "grid" and v["zoneWeg"] == "none", str(v))
    r.check("Reiter ziehen: eine 3px-Linie vor dem Reiter, der Platzhalter gerahmt (Form, nicht nur Farbe)",
            v["linie"] == "3px" and v["linieInhalt"] == '""' and v["platz"] == "2px solid", str(v))
    r.check("Listen der Ansichten: ungelesen fetter, die offene mit Balken, erledigt durchgestrichen (in beiden Packs)",
            all(int(x["ungelesen"]) > int(x["gelesen"]) and "inset" in x["offen"] and x["erledigt"] == "line-through" for x in (v, ud)),
            f"vega {v} | underdoc {ud}")
    r.check("Pack underdoc: Menüs im Arbeitsbereich in der Zeilenhöhe des Entwurfs, flacher als in vega",
            ud["menue"] < v["menue"] and abs(ud["menue"] - 30.6) < 0.6, f"underdoc {ud['menue']} | vega {v['menue']}")
    r.check("Pack underdoc: der heutige Tag in der Primärrolle gerahmt und so hoch wie im Entwurf; vega ohne das",
            ud["heute"] and ud["heuteHoch"] == 62 and not v["heute"] and v["heuteHoch"] < 62, f"underdoc {ud} | vega {v}")


LUECKEN_WERTE = r"""(() => {
  // What UnderDoc's frame found missing (2026-11-22): a space between entries, open against kept open, the flow of a
  // document whose blocks sit in wrappers, room for the handles, an icon in the head of a collection, the avatar.
  const ex = [...document.querySelectorAll('#navigation-document-workspace .workspace')], hell = ex[0], dunkel = ex[1];
  const r = e => e.getBoundingClientRect(), c = e => getComputedStyle(e), h = e => Math.round(r(e).height * 10) / 10;
  const n2 = dunkel.querySelector('.workspace-nav[data-level="2"]'), n3 = dunkel.querySelector('.workspace-nav[data-level="3"]');
  const abstand2 = n2.querySelector('div > hr[data-variant="space"]'), linie3 = n3.querySelector('.workspace-tree li > div > hr:not([data-variant])');
  const abstand3 = n3.querySelector('.workspace-tree li > div > hr[data-variant="space"]');
  const eintraege = { abstand: [h(abstand2), h(abstand2.parentElement), c(abstand2).backgroundColor],
    linieListe: [h(linie3), h(linie3.parentElement), Math.round(r(linie3).width) > 100],
    abstandListe: [h(abstand3), h(abstand3.parentElement)], eintrag: h(n3.querySelector('.workspace-tree li > div:has(> button)')) };
  const balken = e => c(e).boxShadow.match(/(\d+(?:\.\d+)?)px 0px 0px 0px inset/)?.[1] + 'px';
  const offen = { gehalten: balken(n2.querySelector('.workspace-item[aria-current][data-pinned]')),
                  nurOffen: balken(n2.querySelector('.workspace-item[aria-current]:not([data-pinned])')) };
  // The flow: the same blocks bare and each in a wrapper with a handle stand at the same places.
  const art = hell.querySelector('.workspace-main > section > article');
  // Smaller text right after a heading (a code block, a small paragraph) shows whether the wrapper itself takes a gap.
  const folge = ['p', 'h2', 'p', 'p', 'h3', 'h2', 'pre.code-block', 'ul', 'h1', 'p.text-xs', 'blockquote', 'h3', 'p'];
  const baue = (mitHuelle, gemischt) => {
    const a = document.createElement('article'); a.className = 'typeset'; a.dataset.width = 'slim';
    folge.forEach((art_, i) => {
      const [tag, klasse] = art_.split('.'), e = document.createElement(tag); e.textContent = 'Block ' + i;
      if (klasse) e.className = klasse;
      if (tag === 'ul') e.innerHTML = '<li>Eins</li><li>Zwei</li>';
      if (!mitHuelle || (gemischt && i % 3 === 1)) { a.append(e); return; }
      const w = document.createElement('div'); w.setAttribute('data-block', '');
      w.append(art.querySelector('.editor-handle').cloneNode(true), e); a.append(w);
    });
    art.after(a); art.hidden = true;
    const oben = r(a).top, lagen = [...a.children].map(k => Math.round((r(k).top - oben) * 10) / 10);
    a.remove(); art.hidden = false;
    return lagen.join(' ');
  };
  const fluss = { nackt: baue(false), huelle: baue(true), gemischt: baue(true, true) };
  const kopf = n3.querySelector('section > header > a > svg'), av = hell.querySelector('.workspace-item > .avatar');
  return { eintraege, offen, fluss, schloss: [r(kopf).width, r(kopf).height], avatar: [r(av).width, c(av.firstElementChild).fontSize] };
})()"""

GRIFF_HANDY = r"""(() => {
  // Phone (and a narrow window): the handle of a block stays inside the window; without handles the old margin.
  const w = document.querySelector('#navigation-document-workspace .workspace'), sec = w.querySelector('.workspace-main > section');
  const r = e => e.getBoundingClientRect(), griff = sec.querySelector('[data-block] > .editor-handle');
  const sicht = r(griff).left >= r(sec).left, rand = getComputedStyle(sec).paddingLeft;
  const weg = [...sec.querySelectorAll('.editor-handle')].map(g => [g, g.parentElement]);
  weg.forEach(([g]) => g.remove()); const ohne = getComputedStyle(sec).paddingLeft; weg.forEach(([g, p]) => p.prepend(g));
  // With contents beside the document (hidden on the phone) the handles need the same room.
  const toc = document.createElement('nav'); toc.className = 'toc'; sec.prepend(toc); const mitToc = getComputedStyle(sec).paddingLeft; toc.remove();
  w.setAttribute('data-nav-open', '');
  const n = l => r(w.querySelector(':scope > .workspace-nav[data-level="' + l + '"]'));
  const spalten = [Math.round(n(1).width), Math.round(n(2).left - r(w).left), Math.round(n(3).left - r(w).left)];
  w.removeAttribute('data-nav-open');
  const wort = getComputedStyle(w.querySelector(':scope > .workspace-nav[data-level="1"] .workspace-item')).fontSize;
  return { sicht, rand, ohne, mitToc, spalten, wort };
})()"""

GRIFF_SCHMAL = r"""(() => {
  const main = document.querySelector('#navigation-document-workspace .workspace-main'), sec = main.querySelector(':scope > section');
  const r = e => e.getBoundingClientRect(), alt = main.style.width;
  main.style.width = '420px';
  const sicht = r(sec.querySelector('[data-block] > .editor-handle')).left >= r(sec).left;
  main.style.width = alt;
  return sicht;
})()"""


def arbeitsbereich_luecken(r: Report, b: Browser, basis: str) -> None:
    """What UnderDoc's frame on the building blocks found missing (2026-11-22): what no picture shows exactly."""
    werte, handy = {}, {}
    for pack in ("vega", "underdoc"):
        f = b.seite(1280, 900)
        f.geh(f"{basis}/blocks.html?pack={pack}&theme=light&lang=de")
        werte[pack] = f.js(LUECKEN_WERTE)
        werte[pack]["schmal"] = f.js(GRIFF_SCHMAL)
        f.sende("Page.close")
        f = b.seite(390, 844)
        f.geh(f"{basis}/blocks.html?pack={pack}&theme=light&lang=de")
        handy[pack] = f.js(GRIFF_HANDY)
        f.sende("Page.close")
    v, ud = werte["vega"], werte["underdoc"]
    r.check("Abstand und Linie als Einträge: der Abstand 14px ohne Strich, in der Liste so hoch wie Linie bzw. Abstand, "
            "nicht wie ein Eintrag; die Linie füllt ihre Zeile (in beiden Packs)",
            all(x["eintraege"]["abstand"][:2] == [14, 14] and x["eintraege"]["abstand"][2] == "rgba(0, 0, 0, 0)"
                and x["eintraege"]["linieListe"] == [1, 13, True] and x["eintraege"]["abstandListe"] == [14, 14]
                and x["eintraege"]["eintrag"] >= 28 for x in (v, ud)), f"vega {v['eintraege']} | underdoc {ud['eintraege']}")
    r.check("Offen gegenüber offen gehalten: im Pack underdoc dünne Linie (1px) gegen dicke (3px); vega beide 3px",
            ud["offen"] == {"gehalten": "3px", "nurOffen": "1px"} and v["offen"] == {"gehalten": "3px", "nurOffen": "3px"},
            f"vega {v['offen']} | underdoc {ud['offen']}")
    r.check("Typeset: Blöcke in Hüllen mit Griff stehen genau wie dieselben Blöcke ohne Hülle (auch gemischt, in beiden Packs)",
            all(x["fluss"]["nackt"] == x["fluss"]["huelle"] == x["fluss"]["gemischt"] for x in (v, ud)),
            f"vega {v['fluss']} | underdoc {ud['fluss']}")
    r.check("Symbol im Kopf einer offenen Sammlung 13px wie das einer Beschriftung",
            v["schloss"] == ud["schloss"] == [13, 13], f"vega {v['schloss']} | underdoc {ud['schloss']}")
    r.check("Avatar im Eintrag: im Pack underdoc 20px mit 9px-Kürzel wie im Entwurf, vega bleibt 24px",
            ud["avatar"] == [20, "9px"] and v["avatar"] == [24, "12px"], f"vega {v['avatar']} | underdoc {ud['avatar']}")
    r.check("Griffe: auf dem Handy (auch mit Inhaltsverzeichnis) und in einem schmalen Fenster bleibt der Griff im Fenster (36px Rand nur mit Griffen, sonst 16px)",
            all(x["sicht"] and x["rand"] == x["mitToc"] == "36px" and x["ohne"] == "16px" for x in handy.values()) and v["schmal"] and ud["schmal"],
            f"vega {handy['vega']} schmal {v['schmal']} | underdoc {handy['underdoc']} schmal {ud['schmal']}")
    r.check("Handy: nav1 im Pack underdoc 70px mit 10px-Wörtern (nav2 und nav3 schließen daran an), vega bleibt 84px",
            handy["underdoc"]["spalten"] == [70, 70, 154] and handy["underdoc"]["wort"] == "10px"
            and handy["vega"]["spalten"] == [84, 84, 168] and handy["vega"]["wort"] == "12px",
            f"vega {handy['vega']} | underdoc {handy['underdoc']}")


EDITOR_WERTE = r"""(() => {
  // What UnderDoc's editor found missing (2026-11-22, third round): the last two examples of workspace-editing.html.
  const ex = [...document.querySelectorAll('#navigation-workspace-editing .c22-example')], lesen = ex.at(-2), ed = ex.at(-1);
  const r = e => e.getBoundingClientRect(), c = (e, p) => getComputedStyle(e, p), z = v => Math.round(v * 10) / 10;
  const art = lesen.querySelector('article.typeset'), griff = art.querySelector('.editor-handle'), blase = art.querySelector('[data-comment]');
  // 1. Several elements in one wrapper (handle first, a comment bubble last): every element stands where it stands bare.
  const folge = ['p', 'h2', 'p', 'p', 'h3', 'h2', 'pre.code-block', 'ul', 'h1', 'p.text-xs', 'blockquote', 'h3', 'p', 'p', 'h2', 'p', 'ul'];
  const gruppen = [[0, 1, 2], [3], [4, 5, 6], [7, 8, 9, 10], [11], [12, 13], [14, 15, 16]];
  const baue = modus => {
    const a = document.createElement('article'); a.className = 'typeset'; a.dataset.width = 'slim';
    const els = folge.map((art_, i) => {
      const [tag, klasse] = art_.split('.'), e = document.createElement(tag); e.textContent = 'Block ' + i;
      if (klasse) e.className = klasse;
      if (tag === 'ul') e.innerHTML = '<li>Eins</li><li>Zwei</li>';
      return e;
    });
    gruppen.forEach((g, k) => {
      if (modus === 'nackt' || (modus === 'gemischt' && k % 3 === 1)) { g.forEach(i => a.append(els[i])); return; }
      const w = document.createElement('div'); w.setAttribute('data-block', '');
      w.append(griff.cloneNode(true), ...g.map(i => els[i]));
      if (k % 2) { w.classList.add('comment-anchor'); w.append(blase.cloneNode(true)); }
      a.append(w);
    });
    art.after(a); art.hidden = true;
    const oben = r(a).top, lagen = els.map(e => z(r(e).top - oben));
    a.remove(); art.hidden = false;
    return lagen.join(' ');
  };
  const fluss = { nackt: baue('nackt'), huellen: baue('huellen'), gemischt: baue('gemischt') };
  // 2. The active block shows its handle, in reading and in the editor (its wrapper there holds no lines).
  const deck = e => c(e).opacity;
  const aktiv = [deck(lesen.querySelector('[data-block][data-active] > .editor-handle')), deck(ed.querySelector('[data-block][data-active] > .editor-handle')),
                 deck(lesen.querySelector('[data-block]:not([data-active]) > .editor-handle'))];
  // 3. A block used elsewhere over sibling lines: one frame (first: top and sides, middle: sides, last: bottom and sides,
  //    no value: all round), drawn outside the text at the sides, and no line gets higher than without it.
  const zeilen = [...ed.querySelectorAll('[data-used]')];
  const rahmen = zeilen.map(l => { const b = c(l, '::before'); return [l.dataset.used || 'only', b.borderTopWidth, b.borderBottomWidth, b.borderLeftWidth, b.borderRightWidth].join(' '); });
  const links = zeilen.map(l => z(r(l).left - parseFloat(c(l, '::before').left)) - z(r(l).left));
  const hoch = () => zeilen.map(l => z(r(l).height)).join(' ');
  const mit = hoch(), werte = zeilen.map(l => l.getAttribute('data-used'));
  zeilen.forEach(l => l.removeAttribute('data-used')); const ohne = hoch();
  zeilen.forEach((l, i) => l.setAttribute('data-used', werte[i]));
  // 4. A task list: no bullet, the box hangs where the bullet was, a wrapped line starts under the text; done is struck through and muted.
  const aufgaben = [...lesen.querySelectorAll('li:has(> input[type=checkbox])')], erledigt = aufgaben.find(l => l.querySelector('input').checked),
        offen = aufgaben.find(l => !l.querySelector('input').checked), punkt = lesen.querySelector('figure li');
  const ul = offen.parentElement, kasten = offen.querySelector('input');
  const breit = offen.style.width; offen.style.width = '6em'; offen.textContent = ''; offen.append(kasten, ' Heizung im Gehäuse prüfen und reinigen');
  const bereich = document.createRange(); bereich.selectNodeContents(offen); const zeilenStart = [...bereich.getClientRects()].map(q => z(q.left));
  offen.style.width = breit;
  const aufgabe = { stil: [c(erledigt).listStyleType, c(offen).listStyleType, c(punkt).listStyleType],
    durch: [c(erledigt).textDecorationLine, c(offen).textDecorationLine], farbe: c(erledigt).color !== c(offen).color && c(erledigt).color === c(ed.querySelector('[data-used] > small')).color,
    haengt: z(r(kasten).left) < z(r(ul).left + parseFloat(c(ul).paddingLeft)), zeilen: zeilenStart };
  // 5. The content of an embedding takes the typeset flow: the same elements bare in a page stand at the same places.
  const fig = lesen.querySelector('figure.editor-embed'), kinder = [...fig.children].filter(k => k.tagName !== 'FIGCAPTION');
  const lage = els => { const o = r(els[0]).top; return els.map(e => z(r(e).top - o)).join(' '); };
  const imFig = lage(kinder);
  const a = document.createElement('article'); a.className = 'typeset'; a.dataset.width = 'slim';
  const kopien = kinder.map(k => k.cloneNode(true)); a.append(...kopien); art.after(a);
  const nackt = lage(kopien); a.remove();
  // 6. A held block in the page and in the editor: the dashed gap, cut to its first lines, the paragraph gap around it,
  //    nothing selectable while it is there; a handle that drags shows the open hand.
  const gaps = [lesen.querySelector('article > .dropgap.held'), ed.querySelector('.dropgap.held')];
  const halten = gaps.map(g => [c(g).outlineStyle + ' ' + c(g).outlineWidth, c(g).overflowY, z(r(g).height) <= z(parseFloat(c(g).fontSize) * 6.5) && g.scrollHeight > g.clientHeight + 10]);
  const abstand = [c(gaps[0]).marginTop, c(gaps[0]).marginBottom, c(art.querySelector(':scope > [data-block] > p + p')).marginTop];
  const waehlen = [c(art).userSelect, c(ed.querySelector('.editor')).userSelect, c(gaps[0].previousElementSibling).cursor];
  const weg = gaps.map(g => [g, g.parentElement, g.nextSibling]); weg.forEach(([g]) => g.remove());
  const danach = [c(art).userSelect, c(ed.querySelector('.editor')).userSelect];
  const ziehen = [c(art.querySelector('.editor-handle [data-drag]')).cursor, c(art.querySelector('.editor-handle [data-drag]')).touchAction];
  weg.forEach(([g, p, n]) => p.insertBefore(g, n));
  // 7. A part over two lines: the first piece says its name, the further one is framed without it.
  const [erst, weiter] = ed.querySelectorAll('[data-part][data-framed]');
  const teil = [c(erst, '::before').content.startsWith('"Teil'), c(weiter, '::before').content, c(weiter).outlineStyle, c(weiter).borderTopLeftRadius];
  // 9. The comment bubble stays inside the window's room at the end: a document at full width does not scroll sideways.
  const main = lesen.querySelector('.workspace-main'), sec = main.querySelector(':scope > section'), breiteAlt = main.style.width;
  main.style.width = '520px';
  const seitwaerts = sec.scrollWidth - sec.clientWidth, blasenRand = z(r(sec).right - r(art.querySelector('[data-comment]')).right);
  main.style.width = breiteAlt;
  // Optional: the handle's menu wraps as a menu, also inside an editor's pre-wrap text.
  const zeilenText = ed.querySelector('.editor > div'); zeilenText.style.whiteSpace = 'pre-wrap';
  const menue = c(ed.querySelector('.editor-handle [data-popover]')).whiteSpace; zeilenText.style.whiteSpace = '';
  return { fluss, aktiv, rahmen, links, mit, ohne, aufgabe, embed: { imFig, nackt }, halten, abstand, waehlen, danach, ziehen, teil,
           seitwaerts, blasenRand, menue };
})()"""

FINGER_WERTE = r"""(() => {
  // 10. Without a hovering pointer: a quiet handle and a bubble without count half visible, active and counted ones full.
  const ex = [...document.querySelectorAll('#navigation-workspace-editing .c22-example')], lesen = ex.at(-2);
  const c = e => getComputedStyle(e).opacity, blase = lesen.querySelector('[data-comment]');
  const ohneZahl = blase.cloneNode(true); ohneZahl.removeAttribute('data-count'); blase.after(ohneZahl);
  const aus = [c(lesen.querySelector('[data-block]:not([data-active]) > .editor-handle')), c(lesen.querySelector('[data-block][data-active] > .editor-handle')),
               c(ohneZahl), c(blase)];
  ohneZahl.remove();
  return aus;
})()"""


EDITOR_HANDY = r"""(() => {
  // The editor in a window on the phone: the handle of the active block stays inside the window.
  const ed = [...document.querySelectorAll('#navigation-workspace-editing .c22-example')].at(-1), sec = ed.querySelector('.workspace-main > section');
  return ed.querySelector('[data-block][data-active] > .editor-handle').getBoundingClientRect().left >= sec.getBoundingClientRect().left;
})()"""

def arbeitsbereich_editor(r: Report, b: Browser, basis: str) -> None:
    """What UnderDoc's editor on the building blocks found missing (2026-11-22, third round)."""
    werte = {}
    for pack in ("vega", "underdoc"):
        f = b.seite(1280, 900)
        f.geh(f"{basis}/blocks.html?pack={pack}&theme=light&lang=de")
        werte[pack] = f.js(EDITOR_WERTE)
        f.sende("Page.close")
        f = b.seite(1280, 900)
        # A finger: touch emulation gives pointer: coarse (the media emulation of pointer does not take in headless Chrome).
        f.sende("Emulation.setTouchEmulationEnabled", enabled=True, maxTouchPoints=5)
        f.sende("Emulation.setEmulatedMedia", features=[{"name": "hover", "value": "none"}])
        f.geh(f"{basis}/blocks.html?pack={pack}&theme=light&lang=de")
        werte[pack]["finger"] = f.js(FINGER_WERTE)
        f.sende("Page.close")
        f = b.seite(1280, 900)
        f.sende("Emulation.setEmulatedMedia", features=[{"name": "hover", "value": "hover"}, {"name": "pointer", "value": "fine"}])
        f.geh(f"{basis}/blocks.html?pack={pack}&theme=light&lang=de")
        werte[pack]["maus"] = f.js(FINGER_WERTE)
        f.sende("Page.close")
        f = b.seite(390, 844)
        f.geh(f"{basis}/blocks.html?pack={pack}&theme=light&lang=de")
        werte[pack]["handy"] = f.js(EDITOR_HANDY)
        f.sende("Page.close")
    v, ud = werte["vega"], werte["underdoc"]
    beide = (v, ud)
    zeige = lambda k: f"vega {v[k]} | underdoc {ud[k]}"  # noqa: E731
    r.check("Typeset: mehrere Elemente in einer Hülle (Griff vorn, Kommentarblase hinten) stehen wie ohne Hülle (auch gemischt, in beiden Packs)",
            all(x["fluss"]["nackt"] == x["fluss"]["huellen"] == x["fluss"]["gemischt"] for x in beide), zeige("fluss"))
    r.check("Griff des aktiven Blocks ([data-active]) sichtbar, beim Lesen und im Editor; ein anderer Block nicht",
            all(x["aktiv"] == ["1", "1", "0"] for x in beide), zeige("aktiv"))
    r.check("[data-used] über Geschwisterzeilen: ein Rahmen (first/middle/last, ohne Wert rundum), 6px neben dem Text, keine Zeile höher als ohne",
            all(x["rahmen"] == ["first 1px 0px 1px 1px", "middle 0px 0px 1px 1px", "middle 0px 0px 1px 1px", "last 0px 1px 1px 1px",
                                "only 1px 1px 1px 1px"] and set(x["links"]) == {6} and x["mit"] == x["ohne"] for x in beide),
            f"vega {v['rahmen']} {v['links']} {v['mit']}/{v['ohne']} | underdoc {ud['rahmen']} {ud['links']} {ud['mit']}/{ud['ohne']}")
    r.check("Aufgabenliste: Kästchen statt Punkt, es hängt vor dem Text, eine umbrochene Zeile beginnt unter dem Text; erledigt gedämpft und durchgestrichen",
            all(x["aufgabe"]["stil"] == ["none", "none", "disc"] and x["aufgabe"]["durch"] == ["line-through", "none"] and x["aufgabe"]["farbe"]
                and x["aufgabe"]["haengt"] and len(x["aufgabe"]["zeilen"]) >= 3
                and abs(x["aufgabe"]["zeilen"][2] - x["aufgabe"]["zeilen"][1]) <= 5 for x in beide), zeige("aufgabe"))
    r.check("Einbettung: ihr Inhalt (Überschrift, Absätze, Liste, Tabelle) steht wie derselbe Inhalt in der Seite",
            all(x["embed"]["imFig"] == x["embed"]["nackt"] for x in beide), zeige("embed"))
    r.check("Gehaltener Block (.dropgap.held) in Seite und Editor: gestrichelt, auf die ersten Zeilen gekürzt, Absatzabstand drumherum, "
            "solange er da ist nichts wählbar; ein ziehender Griff zeigt die offene Hand",
            all(all(h[0] == "dashed 1px" and h[1] == "hidden" and h[2] for h in x["halten"]) and x["abstand"][0] == x["abstand"][1] == x["abstand"][2]
                and x["waehlen"] == ["none", "none", "grabbing"] and "none" not in x["danach"] and x["ziehen"] == ["grab", "none"] for x in beide),
            f"vega {v['halten']} {v['abstand']} {v['waehlen']} {v['danach']} {v['ziehen']} | underdoc {ud['halten']} {ud['abstand']} {ud['waehlen']} {ud['danach']} {ud['ziehen']}")
    r.check("Teil über zwei Zeilen: das erste Stück mit Namen, das weitere (data-framed=\"continued\") gerahmt ohne Namen, oben eckig",
            all(x["teil"] == [True, "none", "solid", "0px"] for x in beide), zeige("teil"))
    r.check("Kommentarblase: bleibt im Raum am Ende des Fensters, das Dokument scrollt bei voller Breite nicht seitwärts (in beiden Packs)",
            all(x["seitwaerts"] <= 0 and x["blasenRand"] >= 0 for x in beide),
            f"vega {v['seitwaerts']} {v['blasenRand']} | underdoc {ud['seitwaerts']} {ud['blasenRand']}")
    r.check("Ohne Hover (Finger): Griff und Blase halb sichtbar, aktiver Griff und Blase mit Zahl voll; mit Maus bleiben die ruhigen unsichtbar",
            all(x["finger"] == ["0.45", "1", "0.45", "1"] and x["maus"] == ["0", "1", "0", "1"] for x in beide),
            f"vega {v['finger']} {v['maus']} | underdoc {ud['finger']} {ud['maus']}")
    r.check("Handy: der Griff des aktiven Blocks im Editor bleibt im Fenster (Raum für Griffe auch vor den Zeilen eines Editors)",
            v["handy"] is True and ud["handy"] is True, f"vega {v['handy']} | underdoc {ud['handy']}")
    r.check("Das Menü des Griffs bricht um wie ein Menü, auch im pre-wrap-Text eines Editors",
            v["menue"] == ud["menue"] == "normal", f"vega {v['menue']} | underdoc {ud['menue']}")


MENUE_WERTE = r"""(() => {
  // What UnderDoc's menus and views found missing (2026-11-22, fourth round), read in workspace-views.html.
  const ex = [...document.querySelectorAll('#navigation-workspace-views .c22-example')];
  const finde = t => ex.find(e => e.querySelector('.c22-example-label').textContent.replace(/^[a-z]+\) /, '').startsWith(t));
  const c = (e, p) => getComputedStyle(e, p), r = e => e.getBoundingClientRect();
  const farbe = (w, name) => { const i = document.createElement('i'); i.style.color = c(w).getPropertyValue(name); w.append(i); const v = c(i).color; i.remove(); return v; };
  // 1. A context menu inside the workspace: its rows (and a description in them) take the pack's menu size.
  const menue = finde('Menü im Arbeitsbereich'), panel = menue.querySelector('.context-menu > [data-cm-panel]');
  const zeile = panel.querySelector('[role=menuitem]'), klein = panel.querySelector('[role=menuitem] > div > small');
  // 2.-5. Searching on the page and the comments of one element.
  const kom = finde('Kommentare'), w = kom.querySelector('.workspace'), main = w.querySelector('.workspace-main');
  const kopf = main.querySelector(':scope > header'), lade = main.querySelector(':scope > aside[data-drawer]');
  const symbol = lade.querySelector(':scope > header > svg'), wort = document.createRange();
  wort.selectNodeContents([...symbol.parentElement.childNodes].find(n => n.nodeType === 3 && n.data.trim()));
  const marks = [...main.querySelectorAll('article mark')], jetzt = marks.find(m => m.hasAttribute('aria-current')), anderer = marks.find(m => !m.hasAttribute('aria-current'));
  const fokus = main.querySelector('.comment-anchor[data-comment-focus]'), ohne = main.querySelector('.comment-anchor:not([data-comment-focus])');
  const rahmen = e => [c(e).outlineStyle, c(e).outlineWidth];
  // 7. Rows that are controls: a toggle row off and on.
  const mod = finde('Module'), aus = mod.querySelector('button.item[aria-pressed="false"]'), an = mod.querySelector('button.item[aria-pressed="true"]');
  return {
    menue: [c(zeile).fontSize, c(klein).fontSize, panel.closest('.workspace') !== null, c(klein.parentElement).flexDirection, c(klein).color === farbe(w, '--muted-foreground')],
    symbol: [Math.round(r(symbol).width), Math.round(r(symbol).height), symbol.getAttribute('class'), Math.round(wort.getBoundingClientRect().left - r(symbol).right)],
    treffer: { jetzt: [...rahmen(jetzt), c(jetzt).fontWeight], anderer: [c(anderer).outlineStyle, c(anderer).fontWeight], grund: c(jetzt).backgroundColor === c(anderer).backgroundColor },
    fokus: { grund: c(fokus).backgroundColor === farbe(w, '--accent'), rahmen: rahmen(fokus), ohne: [c(ohne).backgroundColor, c(ohne).outlineStyle] },
    lade: { oben: Math.round(r(lade).top - r(main).top), kopf: Math.round(r(kopf).height) },
    schalter: { aus: [c(aus).borderTopStyle, c(aus).color === farbe(w, '--muted-foreground')], an: [c(an).borderTopStyle, c(an.querySelector(':scope > aside')).fontWeight] },
  };
})()"""

# Where the pointer goes to hover a row (the row scrolled into view first); then what the row looks like.
SCHWEBE_ZIEL = r"""((vor, sel) => {
  const ex = [...document.querySelectorAll('#navigation-workspace-views .c22-example')].find(e => e.querySelector('.c22-example-label').textContent.replace(/^[a-z]+\) /, '').startsWith(vor));
  const e = ex.querySelector(sel); e.scrollIntoView({ block: 'center' }); const b = e.getBoundingClientRect();
  return [b.left + b.width / 2, b.top + b.height / 2];
})"""
SCHWEBE_WERT = r"""((vor, sel) => {
  const ex = [...document.querySelectorAll('#navigation-workspace-views .c22-example')].find(e => e.querySelector('.c22-example-label').textContent.replace(/^[a-z]+\) /, '').startsWith(vor));
  const e = ex.querySelector(sel), w = ex.querySelector('.workspace'), s = getComputedStyle(e);
  const i = document.createElement('i'); i.style.color = getComputedStyle(w).getPropertyValue('--accent'); w.append(i); const akzent = getComputedStyle(i).color; i.remove();
  return [e.matches(':hover'), s.backgroundImage !== 'none' || s.backgroundColor === akzent, s.backgroundColor === akzent];
})"""


def arbeitsbereich_menues(r: Report, b: Browser, basis: str) -> None:
    """What UnderDoc's menus and views on the building blocks found missing (2026-11-22, fourth round)."""
    werte = {}
    for pack in ("vega", "underdoc"):
        f = b.seite(1280, 900)
        f.geh(f"{basis}/blocks.html?pack={pack}&theme=light&lang=de")
        werte[pack] = f.js(MENUE_WERTE)
        schweben = {}
        for vor, sel in (("Aufgaben", "main label.item"), ("Module", "button.item[aria-pressed]")):
            x, y = f.js(f"{SCHWEBE_ZIEL}({json.dumps(vor)}, {json.dumps(sel)})")
            f.sende("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y)
            f.warte("!document.getAnimations().some(a => a instanceof CSSTransition && a.playState === 'running')")
            schweben[sel] = f.js(f"{SCHWEBE_WERT}({json.dumps(vor)}, {json.dumps(sel)})")
        werte[pack]["schweben"] = schweben
        f.sende("Page.close")
    v, ud = werte["vega"], werte["underdoc"]
    beide = (v, ud)
    zeige = lambda k: f"vega {v[k]} | underdoc {ud[k]}"  # noqa: E731
    r.check("Kontextmenü im Arbeitsbereich: im Pack underdoc 13px-Zeilen und 11.5px-Beschreibung wie die anderen Menüs, vega bleibt 14px; "
            "die Beschreibung steht gedämpft als zweite Zeile (beide Packs)",
            ud["menue"][:3] == ["13px", "11.5px", True] and v["menue"][0] == "14px" and all(x["menue"][3:] == ["column", True] for x in beide),
            zeige("menue"))
    r.check("Symbol im Kopf einer Schublade: 16px vom Baustein, ohne eigene Größenklasse; der Name folgt ihm mit 8px (in beiden Packs)",
            all(x["symbol"] == [16, 16, None, 8] for x in beide), zeige("symbol"))
    r.check("Seitensuche: der aktuelle Treffer (mark[aria-current]) umrandet und fett, die anderen nicht; der Grund bleibt derselbe (Form, nicht nur Farbe)",
            all(x["treffer"]["jetzt"] == ["solid", "2px", "600"] and x["treffer"]["anderer"] == ["none", "400"] and x["treffer"]["grund"] for x in beide),
            zeige("treffer"))
    r.check("Kommentare eines Elements offen (.comment-anchor[data-comment-focus]): Akzentgrund und Rahmen; ein anderes Element ohne beides",
            all(x["fokus"]["grund"] and x["fokus"]["rahmen"] == ["solid", "1px"] and x["fokus"]["ohne"] == ["rgba(0, 0, 0, 0)", "none"] for x in beide),
            zeige("fokus"))
    r.check("Schublade: im Pack underdoc beginnt sie unter dem Fensterkopf (±1px), vega bedeckt den Kopf",
            abs(ud["lade"]["oben"] - ud["lade"]["kopf"]) <= 1 and v["lade"]["oben"] == 0, zeige("lade"))
    r.check("Zeilen als Schalter: aus gestrichelt und gedämpft, an durchgezogen mit fettem Wort; Aufgabe und Schalter reagieren auf die Maus "
            "(underdoc mit Akzentgrund wie im Entwurf)",
            all(x["schalter"] == {"aus": ["dashed", True], "an": ["solid", "600"]} for x in beide)
            and all(all(s[0] and s[1] for s in x["schweben"].values()) for x in beide)
            and all(s[2] for s in ud["schweben"].values()),
            f"vega {v['schalter']} {v['schweben']} | underdoc {ud['schalter']} {ud['schweben']}")


LUECKEN5_HILFE = r"""
  const c = (e, p) => getComputedStyle(e, p || null), r = e => e.getBoundingClientRect();
  const token = (w, wert, eig = 'color') => { const i = document.createElement('i'); i.style[eig] = wert; w.append(i); const v = c(i)[eig]; i.remove(); return v; };
  const beispiel = (abschnitt, vor) => [...document.querySelectorAll(`#${abschnitt} .c22-example`)]
    .find(e => e.querySelector('.c22-example-label').textContent.replace(/^[a-z]+\) /, '').startsWith(vor));
"""

LUECKEN5_WERTE = r"""(() => {""" + LUECKEN5_HILFE + r"""
  // 2. The current row of a sheet: its number filled (a block, not a tint with a bar), a line above and below its cells;
  //    a selected number stays tint and bar, a selected or active cell keeps its frame.
  const blatt = document.querySelector('table[aria-label="Umsatz 2026"]'), w = blatt.closest('section');
  const primary = token(w, 'var(--primary)'), primaryFg = token(w, 'var(--primary-foreground)');
  const jetzt = blatt.querySelector('tr[aria-current] > th'), gewaehlt = blatt.querySelector('th[scope=row][aria-selected="true"]');
  const zelle = blatt.querySelector('tr[aria-current] > td'), andere = blatt.querySelector('tr:not([aria-current]) > td:not([aria-selected])');
  const zeile = { nummer: [c(jetzt).backgroundColor === primary, c(jetzt).color === primaryFg, c(jetzt).fontWeight, c(jetzt).boxShadow],
                  gewaehlt: [c(gewaehlt).backgroundColor === primary, c(gewaehlt).boxShadow !== 'none'],
                  linien: [(c(zelle).boxShadow.match(/inset/g) || []).length, c(andere).boxShadow],
                  aktiv: c(blatt.querySelector('td[data-active]')).boxShadow.includes('2px') };
  return { zeile };
})()"""

LUECKEN5_BLOECKE = r"""(() => {""" + LUECKEN5_HILFE + r"""
  // 2. The number of a hit's row in the window's sheet (th[scope=row][aria-current] alone, as UnderDoc writes it).
  const bsp = beispiel('navigation-workspace-views', 'Protokoll in nav3'), w = bsp.querySelector('.workspace');
  const nr = bsp.querySelector('th[scope=row][aria-current]');
  const nummer = [c(nr).backgroundColor === token(w, 'var(--primary)'), c(nr).fontWeight];
  // 3. A log in nav3: the head of an entry is no column heading (no capitals, no wide letters; who and when on one line),
  //    a column heading elsewhere still is.
  const kopf = bsp.querySelector('.workspace-nav[data-level="3"] .timeline > li > header');
  const wer = kopf.querySelector('strong'), wann = kopf.querySelector('time');
  const spalte = document.querySelector('#navigation-workspace .workspace-nav[data-level="2"] > header, #navigation-workspace .workspace-nav header:not(.item > header)');
  const protokoll = [c(kopf).textTransform, c(kopf).letterSpacing, Math.abs(r(wer).top - r(wann).top) < 4, c(wer).textTransform];
  const ueberschrift = c(spalte).textTransform;
  // 5. The live preview of a Markdown editor.
  const ed = beispiel('navigation-workspace-editing', 'Editor: Markdown als Vorschau').querySelector('.editor');
  const md = (t, i = 0) => ed.querySelectorAll(`[data-md~="${t}"]`)[i];
  const muted = token(ed, 'var(--muted-foreground)'), mutedBg = token(ed, 'var(--muted)', 'backgroundColor');
  const mono = token(ed, 'var(--font-mono)', 'fontFamily'), px = v => parseFloat(v);
  const text = ed.querySelector(':scope > div > div:not([data-md])');
  const groesse = ['h1', 'h2', 'h3'].map(t => c(md(t)).fontSize).concat([c(text).fontSize]);
  const soll = ['--editor-h1', '--editor-h2', '--editor-h3'].map(t => token(ed, `var(${t})`, 'fontSize'));
  const textStart = e => { const g = document.createRange(); g.selectNodeContents(e); return g.getClientRects()[0].left; };
  const zitatLage = () => { const q = md('quote'); return Math.round(textStart(q) - (r(q).left + px(c(q, '::after').left))); };
  const codeLage = () => { const z = md('codeblock', 1); return Math.round(textStart(z) - r(z).left); };
  const flussHoehe = () => { const d = document.createElement('div'); d.style.height = 'var(--flow)'; md('blank').after(d); const h = Math.round(r(d).height); d.remove(); return h; };
  const kanten = ['first', null, 'last'].map((k, i) => { const z = md('codeblock', [0, 1, 3][i]); return [px(c(z).borderTopLeftRadius) > 0, px(c(z).borderBottomLeftRadius) > 0]; });
  const vorschau = {
    groesse, soll, gewicht: c(md('h1')).fontWeight,
    lauf: [c(md('strong')).fontWeight, c(md('em')).fontStyle, c(md('del')).textDecorationLine,
           c(md('code')).fontFamily === mono && c(md('code')).backgroundColor === mutedBg,
           c(md('link')).textDecorationLine + ' ' + c(md('link')).textDecorationStyle, c(md('wiki')).textDecorationStyle,
           c(md('url')).color === muted, c(md('mark')).color === muted, c(md('info')).color === muted,
           c(md('done')).textDecorationLine, c(md('done')).color === muted],
    zitat: [c(md('quote')).fontStyle, c(md('quote')).color === muted, c(md('quote'), '::after').width],
    code: [c(md('codeblock')).fontFamily === mono, c(md('codeblock', 1)).backgroundColor === mutedBg, kanten],
    teile: [c(md('table-source')).fontFamily === mono, c(md('table').querySelector('th[align=right]')).textAlign,
            c(md('directive')).borderTopStyle, c(md('image-alt')).borderTopStyle, c(md('rule')).borderTopStyle + ' ' + c(md('rule')).borderTopWidth,
            Math.round(r(md('task')).width) === Math.round(px(c(md('task').parentElement).fontSize)), c(md('image')).maxWidth,
            Math.round(r(md('blank')).height) === flussHoehe()],
    lagen: [zitatLage(), codeLage()],
  };
  // Against an editor's unlayered CSS: CodeMirror pads every line, an app resets it; both outrank C22's layer. The quote
  // and the code block must stand in all the same.
  const stil = document.createElement('style'); document.head.append(stil);
  stil.textContent = '.editor > div > div { padding: 0 2px 0 6px; }'; const mitCm = [zitatLage(), codeLage()];
  stil.textContent = '.editor > div > div { padding: 0; }'; const ohnePolster = [zitatLage(), codeLage()];
  stil.remove();
  vorschau.cm = { mitCm, ohnePolster };
  return { nummer, protokoll, ueberschrift, vorschau };
})()"""

LUECKEN5_HANDY = r"""(() => {""" + LUECKEN5_HILFE + r"""
  // 4. The phone: nav2 and nav3 open over the window cover what sticks in the window's sheet.
  const bsp = beispiel('navigation-workspace-views', 'Protokoll in nav3'), w = bsp.querySelector('.workspace');
  w.setAttribute('data-nav-open', ''); bsp.scrollIntoView({ block: 'start' });
  const ecke = bsp.querySelector('thead th:first-child'), kopf = bsp.querySelectorAll('thead th')[1], nr = bsp.querySelector('tbody th[scope=row]');
  const navs = [...bsp.querySelectorAll('.workspace-nav[data-level="2"], .workspace-nav[data-level="3"]')];
  const oben = e => { const b = r(e), x = b.left + b.width / 2, y = b.top + b.height / 2, t = document.elementFromPoint(x, y);
    return [navs.some(n => n.contains(t)), navs.some(n => { const q = r(n); return x >= q.left && x <= q.right; })]; };
  const aus = { ecke: oben(ecke), kopf: oben(kopf), nummer: oben(nr) };
  w.removeAttribute('data-nav-open');
  aus.zu = document.elementFromPoint(r(ecke).left + 4, r(ecke).top + 4) === ecke || ecke.contains(document.elementFromPoint(r(ecke).left + 4, r(ecke).top + 4));
  return aus;
})()"""

COMBOBOX_RECHTE = r"""((markup) => {
  document.getElementById('probe-ort').innerHTML = markup;
})"""
COMBOBOX_WERTE = r"""(() => {
  const cb = document.querySelector('#probe-ort .combobox'), pop = cb.querySelector('[data-popover]');
  const sicht = v => [...cb.querySelectorAll('[role=option]')].filter(o => o.getAttribute('aria-hidden') !== 'true').map(o => o.dataset.value);
  return { offen: pop.getAttribute('aria-hidden'), sicht: sicht(), wert: cb.querySelector('input[type=hidden]').value,
           feld: cb.querySelector('input[role=combobox]').value,
           menue: [document.getElementById('probe-dm').hasAttribute('data-dropdown-menu-initialized'),
                   document.getElementById('probe-dm-t').getAttribute('aria-expanded')] };
})()"""


def luecken_fuenf(r: Report, b: Browser, basis: str) -> None:
    """What UnderDoc's last switch found missing (2026-11-22, fifth round): a grouped combobox without Basecoat's global
    observer, the current row of a sheet, a log in nav3, a sheet under the open columns on the phone, the live preview of a
    Markdown editor."""
    # 1. Combobox alone: Basecoat's core and its combobox, rendered after load as an app does.
    quelle = (ROOT / "c22" / "blocks" / "data-entry" / "rights.html").read_text(encoding="utf-8")
    anfang = quelle.index('<div class="combobox')
    ende = quelle.index('<input type="hidden" name="who" value="">', anfang)
    ende = quelle.index("</div>", ende) + len("</div>")
    f = b.seite(1280, 900)
    f.geh(f"{basis}/probe/combobox-alone.html")
    f.js(f"{COMBOBOX_RECHTE}({json.dumps(quelle[anfang:ende])})")
    f.warte("document.querySelector('#probe-ort .combobox[data-combobox-initialized]') !== null")
    f.js("document.getElementById('probe-dm-t').click()")
    f.js("(() => { const i = document.querySelector('#probe-ort input[role=combobox]'); i.focus(); i.click(); })()")
    f.sende("Input.insertText", text="Bü")
    f.warte("document.querySelector('#probe-ort [data-popover]').getAttribute('aria-hidden') === 'false'")
    gefiltert = f.js(COMBOBOX_WERTE)
    f.js("document.querySelector('#probe-ort [role=option][data-value=\"group:buero\"]').click()")
    gewaehlt = f.js(COMBOBOX_WERTE)
    f.sende("Page.close")
    r.check("Combobox allein (Basecoats Kern + combobox.min.js, ohne basecoat.all.min.js): eine später eingesetzte gruppierte "
            "Combobox filtert über ihre Gruppen und wählt; ein .dropdown-menu der App bleibt unberührt",
            gefiltert["offen"] == "false" and gefiltert["sicht"] == ["group:buero"]
            and gewaehlt["wert"] == "group:buero" and gewaehlt["feld"] == "Gruppe Büro" and gewaehlt["offen"] == "true"
            and gefiltert["menue"] == [False, "false"], f"gefiltert {gefiltert} | gewählt {gewaehlt}")

    werte, bloecke, handy = {}, {}, {}
    for pack in ("vega", "underdoc"):
        f = b.seite(1280, 900)
        f.geh(f"{basis}/components.html?pack={pack}&theme=light&lang=de")
        werte[pack] = f.js(LUECKEN5_WERTE)
        f.sende("Page.close")
        f = b.seite(1280, 900)
        f.geh(f"{basis}/blocks.html?pack={pack}&theme=light&lang=de")
        bloecke[pack] = f.js(LUECKEN5_BLOECKE)
        f.sende("Page.close")
        f = b.seite(390, 844)
        f.geh(f"{basis}/blocks.html?pack={pack}&theme=light&lang=de")
        handy[pack] = f.js(LUECKEN5_HANDY)
        f.sende("Page.close")
    beide = ("vega", "underdoc")
    zeige = lambda d, k: " | ".join(f"{p} {d[p][k]}" for p in beide)  # noqa: E731
    r.check("Tabellenraster: die aktuelle Zeile (aria-current) mit gefüllter Nummer (fett, ohne Balken) und einer Linie über und unter "
            "ihren Zellen; eine gewählte Nummer bleibt getönt mit Balken, die aktive Zelle behält ihren Rahmen",
            all(werte[p]["zeile"] == {"nummer": [True, True, "600", "none"], "gewaehlt": [False, True], "linien": [2, "none"], "aktiv": True}
                for p in beide), zeige(werte, "zeile"))
    r.check("Tabellenraster im Fenster: th[scope=row][aria-current] allein füllt die Nummer",
            all(bloecke[p]["nummer"] == [True, "600"] for p in beide), zeige(bloecke, "nummer"))
    r.check("Protokoll in nav3: der Kopf eines Eintrags ist keine Spaltenüberschrift (keine Versalien, kein Sperrsatz, wer und wann "
            "auf einer Zeile); Spaltenüberschriften bleiben in Versalien",
            all(bloecke[p]["protokoll"] == ["none", "normal", True, "none"] and bloecke[p]["ueberschrift"] == "uppercase" for p in beide),
            " | ".join(f"{p} {bloecke[p]['protokoll']} {bloecke[p]['ueberschrift']}" for p in beide))
    r.check("Handy: offenes nav2/nav3 deckt die klebenden Zellen des Blatts im Fenster (Ecke, Kopf, Zeilennummer); geschlossen ist die Ecke oben",
            all(all(v == [True, True] for k, v in handy[p].items() if k != "zu") and handy[p]["zu"] for p in beide),
            zeige(handy, "ecke") + " / " + " | ".join(f"{p} {handy[p]}" for p in beide))
    v, ud = bloecke["vega"]["vorschau"], bloecke["underdoc"]["vorschau"]
    r.check("Editor-Vorschau: Überschriften in den Größen von --editor-h1…h3 (vega 24/20/18px, underdoc wie die gelesene Seite 20/18/16px), "
            "fett wie Überschriften, größer als der Text",
            all(x["groesse"][:3] == x["soll"] and x["gewicht"] == "600" for x in (v, ud))
            and v["groesse"][:3] == ["24px", "20px", "18px"] and ud["groesse"][:3] == ["20px", "18px", "16px"],
            f"vega {v['groesse']} {v['soll']} | underdoc {ud['groesse']} {ud['soll']}")
    r.check("Editor-Vorschau: fett, kursiv, durchgestrichen, Code (mono auf muted), Link unterstrichen, Wiki-Link gepunktet, Adresse, "
            "Markdown-Zeichen und Sprache gedämpft, erledigte Aufgabe durchgestrichen und gedämpft",
            all(x["lauf"] == ["700", "italic", "line-through", True, "underline solid", "dotted", True, True, True, "line-through", True]
                for x in (v, ud)), f"vega {v['lauf']} | underdoc {ud['lauf']}")
    r.check("Editor-Vorschau: Zitat kursiv und gedämpft mit 2px-Balken, 24px eingerückt; Codeblock mono auf muted, oben und unten "
            "gerundet, 12px eingerückt",
            all(x["zitat"] == ["italic", True, "2px"] and x["code"] == [True, True, [[True, False], [False, False], [False, True]]]
                and x["lagen"] == [24, 12] for x in (v, ud)),
            f"vega {v['zitat']} {v['code']} {v['lagen']} | underdoc {ud['zitat']} {ud['code']} {ud['lagen']}")
    r.check("Editor-Vorschau: Tabellenquelle mono, Spalte rechts (th[align]), Direktive und Bildtext gestrichelt, Linie, Kästchen 1em, "
            "Bild höchstens so breit wie die Zeile, Leerzeile so hoch wie der Absatzabstand",
            all(x["teile"] == [True, "right", "dashed", "dashed", "solid 1px", True, "100%", True] for x in (v, ud)),
            f"vega {v['teile']} | underdoc {ud['teile']}")
    r.check("Editor-Vorschau gegen ungelayertes Editor-CSS (CodeMirrors Polster je Zeile, die Rücksetzung der App): Zitat und Codeblock "
            "bleiben eingerückt",
            all(min(x["cm"]["mitCm"][0], x["cm"]["ohnePolster"][0]) >= 24 and min(x["cm"]["mitCm"][1], x["cm"]["ohnePolster"][1]) >= 12
                for x in (v, ud)), f"vega {v['cm']} | underdoc {ud['cm']}")


def main() -> int:
    erneuern = "--renew" in sys.argv
    r = Report("Browser — Galerie in Chrome")
    vorgegeben = os.environ.get("C22_VISUAL_OUT")
    ablage = Path(vorgegeben or tempfile.mkdtemp(prefix="c22-visual-"))
    with tempfile.TemporaryDirectory(prefix="c22-site-") as arbeit:
        site = baue_site(Path(arbeit))
        server, basis = starte_server(site)
        try:
            with Browser() as b:
                bilder(r, b, basis, erneuern, ablage)
                if not erneuern:
                    schaerfe(r, b, basis)
                    fremdressourcen(r, b, basis)
                    favicon(r, basis)
                    verhalten(r, b, basis)
                    arbeitsbereich(r, b, basis)
                    arbeitsbereich_ansichten(r, b, basis)
                    arbeitsbereich_luecken(r, b, basis)
                    arbeitsbereich_editor(r, b, basis)
                    arbeitsbereich_menues(r, b, basis)
                    luecken_fuenf(r, b, basis)
        except BrowserFehler as fehler:
            r.check("Browser läuft durch", False, str(fehler))
        finally:
            server.shutdown()
    # Nothing to look at after a green run, so no empty directory stays behind.
    if not vorgegeben and not any(ablage.iterdir()):
        ablage.rmdir()
    return 0 if erneuern else r.done()


if __name__ == "__main__":
    sys.exit(main())
