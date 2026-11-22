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
    return site


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

    # C22 inside the app workspace (UnderDoc ADR-31, 2026-11-21): the root's element defaults must not beat a utility or a
    # component. Before, td{text-align:left} of the root won over .text-right and the button reset took the padding of a
    # tab. The same tabs outside the root are the measure.
    aw = s.js("""(() => {
      const ex = document.querySelector('.c22-example:has(#c22-aw-sheets)');
      const a = e => getComputedStyle(e).textAlign;
      const tabs = ex.querySelector('.tabs'), kopie = tabs.cloneNode(true);
      kopie.removeAttribute('id'); kopie.querySelectorAll('[id]').forEach(e => e.removeAttribute('id'));
      document.body.appendChild(kopie);
      const masz = t => { const tab = getComputedStyle(t.querySelector('[role=tab]')), l = getComputedStyle(t.querySelector('[role=tablist]'));
                          return [tab.paddingLeft, tab.paddingTop, tab.backgroundColor, l.paddingLeft, getComputedStyle(t).gap]; };
      const out = { rechts: [...ex.querySelectorAll('.tw .text-right')].map(a), zahl: a(ex.querySelector('.table td[data-type="number"]')),
                    links: a(ex.querySelector('.tw td:not([class])')), innen: masz(tabs), aussen: masz(kopie) };
      kopie.remove();
      return out;
    })()""")
    r.check("App-Arbeitsbereich: .text-right und data-type=\"number\" richten Zellen aus wie überall",
            aw["rechts"] and set(aw["rechts"]) == {"right"} and aw["zahl"] == "end" and aw["links"] == "start", str(aw))
    r.check("App-Arbeitsbereich: .tabs sind gepolstert wie außerhalb",
            aw["innen"] == aw["aussen"] and aw["innen"][0] != "0px", str(aw))
    # The spreadsheet (data-sticky="sheet"): the box scrolls inside its bounded height, letters and row numbers stick to
    # it; a selected cell is tinted AND framed, the active one framed thicker, the selected letter and number are bold.
    sh = s.js("""(async () => {
      const t = document.querySelector('#c22-aw-sheets .table[data-sticky="sheet"]'), box = t.parentElement;
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
    ziehen("Arbeitsbereich", {"box": ".c22-app-workspace [data-drag-demo]", "row": ".row", "oben": "ul.t.top > li > .row",
                              "held": ".dropgap.held .row", "kinder": ":scope > ul > li > .row"})
    # The same module on the building block (T-19 step 3): rows are li > div of .workspace-tree.
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
    # The app workspace at phone width (UnderDoc, 2026-11-09): nav2 and nav3 over the window take their width from the
    # workspace (all of it but a strip at the left), not from the column of nav1 they sit in, where nav3 had none.
    app = h.js("""(() => {
      const w = document.querySelector('.c22-app-workspace'), m = w.querySelector('.main').getBoundingClientRect();
      const r = w.querySelector('.rail').getBoundingClientRect(), n3 = w.querySelector('.rail .nav3').getBoundingClientRect();
      return { leiste: Math.round(r.width), soll: Math.round(Math.min(320, m.width - 76)), nav3: n3.width > 0, rechts: r.right <= m.right + 1 };
    })()""")
    r.check("App-Arbeitsbereich: unter md nehmen nav2 und nav3 die Breite vom Arbeitsbereich, nav3 inklusive",
            abs(app["leiste"] - app["soll"]) <= 1 and app["nav3"] and app["rechts"], str(app))
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
