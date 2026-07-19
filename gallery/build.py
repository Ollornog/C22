#!/usr/bin/env python3
"""C22 gallery generator — the Live-Container / SPOT, als Mehrseiten-Galerie.

Seiten (shadcn-artig, PO 2026-07-19):
  index.html    Components — jede Basis-Component in ihren Varianten
  blocks.html   Blocks — größere Kompositionen, gruppiert nach Themen
                (Navigation · Komplette Seite · Login & Signup · Tabellen)
  charts.html   Charts — Diagramm-Muster auf --chart-1…5-Tokens
  typeset.html  Typeset — Typografie im Zusammenhang (Basis für den späteren Generator)

Engine-neutral: kanonisches HTML liegt in `c22/components/`, `c22/blocks/<kategorie>/`,
`c22/charts/` und `c22/typeset/`; dieses Skript stitcht nur. Blocks/Charts/Typeset werden
per Verzeichnis-Scan entdeckt (kein zentrales Register) — Titel aus der ersten Zeile
`<!-- c22-title: … -->`, sonst aus dem Dateinamen.

    python3 gallery/build.py
    scripts/build-gallery.sh          # inkl. Pack-CSS
    webshot <url>/gallery/index.html out.png --net host
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = ROOT / "c22" / "components"
BLOCKS_DIR = ROOT / "c22" / "blocks"
CHARTS_DIR = ROOT / "c22" / "charts"
TYPESET_DIR = ROOT / "c22" / "typeset"
GALLERY = ROOT / "gallery"
GAP = "7rem"  # space before each section container

SHADCN = "https://ui.shadcn.com/docs/components/base/{slug}"
BASECOAT = "https://basecoatui.com/components/{slug}"

# Seiten der Galerie: (Dateiname, Reiter-Beschriftung)
PAGES = [
    ("index.html", "Components"),
    ("blocks.html", "Blocks"),
    ("charts.html", "Charts"),
    ("typeset.html", "Typeset"),
]

# Block-Kategorien in Anzeige-Reihenfolge: (Verzeichnis, deutscher Titel)
BLOCK_KATEGORIEN = [
    ("navigation", "Navigation"),
    ("full-page", "Komplette Seite"),
    ("login-signup", "Login & Signup"),
    ("tables", "Tabellen"),
]

# (title, basecoat, shadcn, custom) — alphabetisch sortiert (Neusortierung 2026-07-19;
# Chart/Typography/Data Table/Editable Table sind auf die eigenen Seiten umgezogen).
COMPONENTS: list[tuple[str, bool, bool, bool]] = [
    ("Accordion", True, True, False),
    ("Alert", True, True, False),
    ("Alert Dialog", True, True, False),
    ("Aspect Ratio", False, True, True),
    ("Attachment", False, True, True),
    ("Avatar", True, True, False),
    ("Badge", True, True, False),
    ("Breadcrumb", True, True, False),
    ("Bubble", False, True, True),
    ("Button", True, True, False),
    ("Button Group", True, True, False),
    ("Calendar", False, True, True),
    ("Card", True, True, False),
    ("Carousel", False, True, True),
    ("Checkbox", True, True, False),
    ("Close Button", False, False, True),
    ("Code Block", False, False, True),
    ("Collapsible", True, True, False),
    ("Color Roles", False, False, True),
    ("Combobox", True, True, False),
    ("Command", True, True, False),
    ("Context Menu", False, True, True),
    ("Date Picker", False, True, True),
    ("Dialog", True, True, False),
    ("Direction", False, True, True),
    ("Drawer", True, True, False),
    ("Dropdown Menu", True, True, False),
    ("Empty", True, True, False),
    ("Field", True, True, False),
    ("Hover Card", False, True, True),
    ("Icon", False, False, True),
    ("Input", True, True, False),
    ("Input Group", True, True, False),
    ("Input OTP", False, True, True),
    ("Item", True, True, False),
    ("Kbd", True, True, False),
    ("Label", True, True, False),
    ("Marker", False, True, True),
    ("Menubar", False, True, True),
    ("Message", False, True, True),
    ("Message Scroller", False, True, True),
    ("Native Select", True, True, False),
    ("Navigation Menu", False, True, True),
    ("Pagination", True, True, True),
    ("Popover", True, True, False),
    ("Progress", True, True, False),
    ("Radio Group", True, True, False),
    ("Resizable", False, True, True),
    ("Scroll Area", True, True, False),
    ("Scrollbar", True, False, True),
    ("Select", True, True, False),
    ("Separator", False, True, True),
    ("Sidebar", True, True, False),
    ("Skeleton", True, True, False),
    ("Slider", True, True, False),
    ("Spinner", True, True, True),
    ("Switch", True, True, False),
    ("Table", True, True, False),
    ("Tabs", True, True, False),
    ("Textarea", True, True, False),
    ("Theme Switcher", True, False, False),
    ("Toast", True, True, False),
    ("Toggle", False, True, True),
    ("Toggle Group", False, True, True),
    ("Tooltip", True, True, False),
]

# Demo width per component (natural width like the source pages). Default below.
DEFAULT_WIDTH = "max-w-2xl"
WIDTHS = {
    "table": "max-w-3xl", "sidebar": "max-w-full",
    "calendar": "max-w-md",
    "navigation-menu": "max-w-3xl", "menubar": "max-w-3xl", "resizable": "max-w-3xl",
    "card": "max-w-4xl",
}

TAG_STYLE = {
    "B": "bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300",
    "S": "bg-neutral-900 text-white dark:bg-white dark:text-neutral-900",
    "C": "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
}


# Abhängigkeits-Signaturen: eindeutige Markup-Marker je Component. Taucht ein Marker im
# Partial einer ANDEREN Component auf, gilt „nutzt diese Component" (Gegenrichtung =
# „genutzt von"). Bewusst kuratiert — nur Marker, die zuverlässig Verbau bedeuten;
# Icon fehlt absichtlich (data-icon-lu steckt in praktisch jedem Partial und wäre
# nur Rauschen), ebenso reine Utility-Muster (Aspect Ratio, Typography).
SIGNATURES: dict[str, list[str]] = {
    "accordion": [r'class="accordion'],
    "alert": [r'class="alert[" ]'],
    "alert-dialog": [r'class="alert-dialog'],
    "avatar": [r'class="avatar'],
    "badge": [r'class="badge'],
    "breadcrumb": [r'class="breadcrumb'],
    "bubble": [r'class="bubble[" ]', r'bubble-group'],
    "button": [r'class="btn[" ]'],
    "button-group": [r'class="button-group'],
    "calendar": [r'data-calendar'],
    "card": [r'class="card[" ]'],
    "carousel": [r'data-carousel\b'],
    "checkbox": [r'type="checkbox"(?![^>]*role="switch")'],
    "close-button": [r'btn-close'],
    "code-block": [r'class="code-block'],
    "collapsible": [r'class="collapsible'],
    "combobox": [r'class="combobox', r'combobox-trigger'],
    "command": [r'class="command[" ]'],
    "context-menu": [r'class="context-menu'],
    "date-picker": [r'data-date-input', r'data-clock', r'data-time-stepper'],
    "dialog": [r'class="dialog[" ]'],
    "drawer": [r'class="drawer[" ]'],
    "dropdown-menu": [r'class="dropdown-menu'],
    "field": [r'class="field[" ]', r'class="fieldset'],
    "hover-card": [r'hover-card'],
    "input": [r'<input class="input[^"]*"(?![^>]*type="(?:checkbox|radio|range|hidden)")'],
    "input-group": [r'class="input-group'],
    "input-otp": [r'input-otp'],
    "item": [r'class="item[" ]', r'item-group', r'item-media'],
    "kbd": [r'class="kbd'],
    "label": [r'class="label[" ]'],
    "marker": [r'class="marker[" ]'],
    "menubar": [r'class="menubar'],
    "message": [r'class="message[" ]'],
    "message-scroller": [r'message-scroller'],
    "native-select": [r'<select[^>]*class="select'],
    "navigation-menu": [r'navigation-menu'],
    "pagination": [r'data-pagination'],
    "popover": [r'data-popover'],
    "progress": [r'class="progress[" ]', r'progress-ring', r'progress-surface'],
    "radio-group": [r'type="radio"'],
    "resizable": [r'data-resize-handle'],
    "scrollbar": [r'class="scrollbar', r'data-scroll-fade', r'data-scrollbar-inset'],
    "select": [r'<div class="select', r'aria-haspopup="listbox"'],
    "separator": [r'class="separator', r'role="separator"', r'field-separator'],
    "sidebar": [r'class="sidebar'],
    "skeleton": [r'class="skeleton'],
    "slider": [r'type="range"'],
    "spinner": [r'data-icon-lu="loader-circle"'],
    "switch": [r'role="switch"'],
    "table": [r'class="table[" ]', r'table-container'],
    "tabs": [r'role="tablist"'],
    "textarea": [r'<textarea'],
    "toast": [r'class="toaster', r'c22Toast\('],
    "toggle": [r'class="toggle[" ]'],
    "toggle-group": [r'toggle-group'],
    "tooltip": [r'data-tooltip'],
}


def dependency_maps(bodies: dict[str, str | None]) -> tuple[dict, dict]:
    """nutzt/genutzt-von je Component aus den Signaturen im Partial-Markup ableiten."""
    deps: dict[str, list[str]] = {}
    used_by: dict[str, list[str]] = {}
    for slug, body in bodies.items():
        if not body:
            continue
        gefunden = []
        for anderer, muster in SIGNATURES.items():
            if anderer == slug or anderer not in bodies:
                continue
            if any(re.search(m, body) for m in muster):
                gefunden.append(anderer)
        if gefunden:
            deps[slug] = gefunden
            for anderer in gefunden:
                used_by.setdefault(anderer, []).append(slug)
    return deps, used_by


def slug_of(title: str) -> str:
    return title.lower().replace(" ", "-")


def partial(title: str) -> str | None:
    p = COMPONENTS_DIR / f"{slug_of(title)}.html"
    if p.exists() and p.read_text(encoding="utf-8").strip():
        return p.read_text(encoding="utf-8")
    return None


def letter_labels(body: str) -> str:
    """Prefix each variant label (c22-example-label) with a, b, c … in order."""
    counter = {"i": 0}

    def repl(m: re.Match) -> str:
        letter = chr(ord("a") + counter["i"])
        counter["i"] += 1
        return m.group(0) + f'<span class="c22-example-letter">{letter})</span> '

    return re.sub(r'<span class="c22-example-label">', repl, body)


def tags(bc: bool, sh: bool, custom: bool) -> str:
    names = {"B": "Basecoat", "S": "shadcn", "C": "custom"}
    out = []
    for key, on in (("B", bc), ("S", sh), ("C", custom)):
        cls = "bg-foreground text-background" if on else "bg-muted text-muted-foreground/40"
        out.append(f'<span class="rounded px-1 text-[10px] font-semibold leading-tight {cls}" '
                   f'title="{names[key]}">{key}</span>')
    return f'<span class="ml-auto flex shrink-0 gap-0.5">{"".join(out)}</span>'


def doclinks(slug: str, bc: bool, sh: bool) -> str:
    link = ('<a class="text-muted-foreground hover:text-foreground text-xs font-medium" '
            'target="_blank" rel="noreferrer" onclick="event.stopPropagation()" '
            'href="{href}">{label}</a>')
    lnks = []
    if bc:
        lnks.append(link.format(href=BASECOAT.format(slug=slug), label="Basecoat ↗"))
    if sh:
        lnks.append(link.format(href=SHADCN.format(slug=slug), label="shadcn ↗"))
    if not lnks:
        return ""
    return f'<div class="flex shrink-0 items-center gap-4">{"".join(lnks)}</div>'


_CAT_GROUPS = {
    "Aktion": "button button-group toggle toggle-group close-button",
    "Formular": "input textarea label field checkbox radio-group switch select native-select combobox input-group input-otp slider",
    "Overlay": "dialog alert-dialog drawer popover hover-card tooltip dropdown-menu context-menu menubar command",
    "Navigation": "breadcrumb pagination tabs navigation-menu sidebar",
    "Anzeige": "table card avatar accordion collapsible item empty separator aspect-ratio carousel calendar date-picker badge kbd icon progress skeleton spinner scroll-area scrollbar marker resizable color-roles code-block",
    "Feedback": "alert toast",
    "Chat": "bubble message message-scroller attachment",
    "Sonstiges": "direction theme-switcher",
}
CATEGORY = {s: cat for cat, lst in _CAT_GROUPS.items() for s in lst.split()}
INTERACTIVE = set(
    "accordion alert-dialog carousel collapsible combobox command context-menu date-picker "
    "dialog drawer dropdown-menu hover-card menubar navigation-menu popover resizable select "
    "sidebar slider tabs theme-switcher toast toggle toggle-group tooltip".split())


def descriptors(slug: str) -> str:
    badges = []
    cat = CATEGORY.get(slug)
    if cat:
        badges.append(cat)
    badges.append("interaktiv" if slug in INTERACTIVE else "statisch")
    return "".join(
        f'<span class="bg-muted text-muted-foreground rounded px-2 py-0.5 text-[11px] font-medium">{b}</span>'
        for b in badges)


# ── Generische Bausteine für alle Seiten ──────────────────────────────────────

def toc_link(anchor: str, label: str, num: int | None = None) -> str:
    nummer = (f'<span class="tabular-nums text-muted-foreground/50 w-6 shrink-0 text-right">{num}</span>'
              if num is not None else "")
    return (f'<a href="#{anchor}" class="flex items-baseline gap-2 truncate rounded-md px-2 py-1 '
            f'text-sm text-muted-foreground hover:bg-muted hover:text-foreground">'
            f'{nummer}<span class="truncate">{html.escape(label)}</span></a>')


def section(slug: str, num: int, title: str, body: str | None, *, first: bool,
            width: str, code_extra: str = "", pre_html: str = "") -> str:
    """Eine Galerie-Sektion: Kopf, optionale Zusatzzeile, Demo-Rahmen, Code-Klappe."""
    done = body is not None
    demo = (letter_labels(strip_title_comment(body)) if done
            else '<p class="text-muted-foreground text-sm italic">— noch nicht gebaut —</p>')
    code_block = (
        f'<details>'
        f'<summary class="flex cursor-pointer select-none list-none items-center justify-between gap-4 px-4 py-2 [&::-webkit-details-marker]:hidden">'
        f'<span class="text-muted-foreground hover:text-foreground text-xs font-medium">Code</span>'
        f'{code_extra}'
        f'</summary>'
        f'<pre class="bg-muted/40 overflow-x-auto rounded-b-xl p-4 text-xs leading-relaxed"><code>{html.escape(body.strip())}</code></pre>'
        f'</details>'
    ) if done else ""
    mt = "2rem" if first else GAP
    num_badge = f'<span class="tabular-nums text-muted-foreground">{num}.</span>'
    return (
        f'<section id="{slug}" class="scroll-mt-6" style="margin-top:{mt}">'
        f'<div class="mx-auto flex {width} max-w-full items-center gap-6 pb-3">'
        f'<h2 class="flex items-center gap-3 text-xl font-semibold tracking-tight">{num_badge}{html.escape(title)}</h2>'
        f'</div>'
        f'{pre_html}'
        f'<div class="mx-auto {width} max-w-full rounded-xl border">'
        f'<div class="flex min-h-64 flex-col items-center justify-center p-10">{demo}</div>'
        f'{code_block}'
        f'</div>'
        f'</section>'
    )


TITLE_RE = re.compile(r'^\s*<!--\s*c22-title:\s*(.+?)\s*-->\s*', re.S)


def strip_title_comment(body: str) -> str:
    return TITLE_RE.sub("", body, count=1)


def file_title(path: Path, body: str) -> str:
    m = TITLE_RE.match(body)
    if m:
        return m.group(1)
    return path.stem.replace("-", " ").title()


def discover(directory: Path) -> list[tuple[str, str, str]]:
    """(slug, titel, body) je HTML-Datei eines Seiten-Verzeichnisses."""
    eintraege = []
    if directory.exists():
        for p in sorted(directory.glob("*.html")):
            body = p.read_text(encoding="utf-8")
            if not body.strip():
                continue
            eintraege.append((p.stem, file_title(p, body), body))
    return eintraege


# ── Seiten-Hülle (Header mit Seiten-Nav + Pack-Umschalter) ────────────────────

PACKS = [
    ("vega", "Vega", ["neutral", "Standard"]),
    ("spica", "Spica", ["Marke", "blau"]),
    ("nova", "Nova", ["rund", "weich"]),
    ("maia", "Maia", ["sehr rund", "freundlich"]),
    ("lyra", "Lyra", ["eckig", "brutalist"]),
    ("mira", "Mira", ["kompakt", "dezent"]),
    ("luma", "Luma", ["luftig", "sehr rund"]),
    ("sera", "Sera", ["Großbuchstaben", "eckig"]),
    ("rhea", "Rhea", ["abgerundet", "ruhig"]),
]


def v(rel: str) -> int:
    """Cache-Buster: mtime als ?v= macht jede geänderte Datei zu einer neuen URL.
    Fehlt die Datei noch (erster Lauf: Seiten entstehen VOR den Pack-CSS), zählt 0 —
    der nächste Build stempelt dann die echte mtime."""
    p = ROOT / "c22" / "static" / rel
    return int(p.stat().st_mtime) if p.exists() else 0


def page_shell(active: str, subtitle: str, toc_html: str, main_html: str) -> str:
    pack_links = "".join(
        f'<link rel="stylesheet" data-pack="{k}" href="../c22/static/css/c22-{k}.css?v={v(f"css/c22-{k}.css")}"'
        f'{"" if i == 0 else " disabled"}>'
        for i, (k, _, _) in enumerate(PACKS))
    pack_options = "".join(f'<option value="{k}">{lbl}</option>' for k, lbl, _ in PACKS)
    pack_attrs_js = json.dumps({k: attrs for k, _, attrs in PACKS}, ensure_ascii=False)
    pack_badges_html = "".join(
        f'<span class="bg-muted text-muted-foreground rounded px-2 py-0.5 text-[11px] font-medium">{html.escape(a)}</span>'
        for a in PACKS[0][2])
    seiten_nav = "".join(
        (f'<a href="{datei}" aria-current="page" class="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-accent-foreground">{label}</a>'
         if datei == active else
         f'<a href="{datei}" class="rounded-md px-3 py-1.5 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground">{label}</a>')
        for datei, label in PAGES)
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>C22 — {html.escape(subtitle)}</title>
<link rel="icon" type="image/png" href="../docs/logo.png">
{pack_links}
<script src="../c22/static/js/basecoat.all.min.js?v={v("js/basecoat.all.min.js")}" defer></script>
<script src="../c22/static/js/icons.js?v={v("js/icons.js")}" defer></script>
<script src="../c22/static/js/c22.js?v={v("js/c22.js")}" defer></script>
</head>
<body class="bg-background text-foreground flex h-screen flex-col overflow-hidden">
<header class="flex shrink-0 flex-wrap items-center gap-x-6 gap-y-3 border-b px-6 py-3">
  <div class="flex items-center gap-3">
    <img src="../docs/logo.png" alt="C22" class="size-8">
    <div class="text-lg font-bold tracking-tight">C22
      <span class="text-muted-foreground text-sm font-normal">{html.escape(subtitle)}</span>
    </div>
  </div>
  <nav class="flex items-center gap-1" aria-label="Galerie-Seiten">{seiten_nav}</nav>
  <div class="ms-auto flex flex-wrap items-center gap-x-5 gap-y-2 text-sm">
    <label class="flex items-center gap-2"><span class="text-muted-foreground">Pack</span>
      <select class="select w-32" onchange="c22SetPack(this.value)">{pack_options}</select></label>
    <span id="c22-pack-attrs" class="flex flex-wrap items-center gap-1">{pack_badges_html}</span>
    <button type="button" class="btn" data-variant="outline" data-size="sm" onclick="document.documentElement.classList.toggle('dark')">Hell / Dunkel</button>
  </div>
</header>
<div class="flex min-h-0 flex-1">
  <aside class="hidden w-64 shrink-0 overflow-y-auto border-r px-3 py-4 lg:block">
    <nav class="flex flex-col gap-0.5">{toc_html}</nav>
  </aside>
  <main class="relative min-w-0 flex-1 overflow-y-auto px-6 py-8">
    {main_html}
  </main>
</div>
<script>
var C22_PACK_ATTRS = {pack_attrs_js};
function c22RenderPackAttrs(name) {{
  var el = document.getElementById('c22-pack-attrs');
  if (!el) return;
  el.innerHTML = '';
  (C22_PACK_ATTRS[name] || []).forEach(function (a) {{
    var s = document.createElement('span');
    s.className = 'bg-muted text-muted-foreground rounded px-2 py-0.5 text-[11px] font-medium';
    s.textContent = a;
    el.appendChild(s);
  }});
}}
function c22SetPack(name) {{
  document.querySelectorAll('link[data-pack]').forEach(function (l) {{
    l.disabled = (l.dataset.pack !== name);
  }});
  c22RenderPackAttrs(name);
  try {{ localStorage.setItem('c22-pack', name); }} catch (e) {{}}
}}
(function () {{
  var p = new URLSearchParams(location.search).get('pack');
  try {{ p = p || localStorage.getItem('c22-pack'); }} catch (e) {{}}
  p = p || 'vega';
  c22SetPack(p);
  var s = document.querySelector('select[onchange^="c22SetPack"]');
  if (s) s.value = p;
}})();
</script>
</body>
</html>
"""


# ── Seiten-Renderer ───────────────────────────────────────────────────────────

def render_components() -> tuple[str, int]:
    toc, sections, built = [], [], 0
    titles_by_slug = {slug_of(t): t for t, *_ in COMPONENTS}
    bodies = {slug_of(t): partial(t) for t, *_ in COMPONENTS}
    deps, used_by = dependency_maps(bodies)

    def dep_chips(slugs: list[str]) -> str:
        return " · ".join(
            f'<a href="#{s}" class="hover:text-foreground underline-offset-2 hover:underline">'
            f'{html.escape(titles_by_slug[s])}</a>'
            for s in sorted(slugs, key=lambda s: titles_by_slug[s]))

    for idx, (title, bc, sh, custom) in enumerate(COMPONENTS):
        slug = slug_of(title)
        num = idx + 1
        body = bodies[slug]
        built += body is not None
        toc.append(toc_link(slug, title, num))
        dep_teile = []
        if body and deps.get(slug):
            dep_teile.append(f'<span><span class="text-foreground/70 font-medium">nutzt:</span> {dep_chips(deps[slug])}</span>')
        if body and used_by.get(slug):
            dep_teile.append(f'<span><span class="text-foreground/70 font-medium">genutzt von:</span> {dep_chips(used_by[slug])}</span>')
        pre_html = (
            f'<div class="text-muted-foreground mx-auto flex w-[820px] max-w-full flex-wrap gap-x-6 gap-y-1 pb-3 text-xs">'
            + "".join(dep_teile) + '</div>'
        ) if dep_teile else ""
        sections.append(section(
            slug, num, title, body, first=idx == 0, width="w-[820px]",
            code_extra=doclinks(slug, bc, sh), pre_html=pre_html))
    page = page_shell("index.html", f"Components · {built}/{len(COMPONENTS)}",
                      "".join(toc), "".join(sections))
    (GALLERY / "index.html").write_text(page, encoding="utf-8")
    return "index.html", built


def render_blocks() -> tuple[str, int]:
    toc, sections, num, first = [], [], 0, True
    for verzeichnis, kategorie in BLOCK_KATEGORIEN:
        eintraege = discover(BLOCKS_DIR / verzeichnis)
        anker = f"kategorie-{verzeichnis}"
        toc.append(f'<div class="mt-4 px-2 pb-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground first:mt-0">{html.escape(kategorie)}</div>')
        sections.append(
            f'<div id="{anker}" class="mx-auto w-[1240px] max-w-full scroll-mt-6" style="margin-top:{"0" if first else GAP}">'
            f'<h2 class="border-b pb-2 text-2xl font-bold tracking-tight">{html.escape(kategorie)}</h2></div>')
        if not eintraege:
            sections.append(
                f'<p class="text-muted-foreground mx-auto mt-6 w-[1240px] max-w-full text-sm italic">— noch keine Blocks in dieser Kategorie —</p>')
        for i, (slug, titel, body) in enumerate(eintraege):
            num += 1
            anchor = f"{verzeichnis}-{slug}"
            toc.append(toc_link(anchor, titel, num))
            # erster Block einer Kategorie rückt an die Überschrift heran
            sections.append(section(anchor, num, titel, body, first=i == 0, width="w-[1240px]"))
        first = False
    page = page_shell("blocks.html", f"Blocks · {num}", "".join(toc), "".join(sections))
    (GALLERY / "blocks.html").write_text(page, encoding="utf-8")
    return "blocks.html", num


def render_flat(datei: str, untertitel: str, directory: Path, width: str) -> tuple[str, int]:
    toc, sections = [], []
    eintraege = discover(directory)
    for idx, (slug, titel, body) in enumerate(eintraege):
        toc.append(toc_link(slug, titel, idx + 1))
        sections.append(section(slug, idx + 1, titel, body, first=idx == 0, width=width))
    if not eintraege:
        sections.append('<p class="text-muted-foreground text-sm italic">— noch keine Inhalte —</p>')
    page = page_shell(datei, f"{untertitel} · {len(eintraege)}", "".join(toc), "".join(sections))
    (GALLERY / datei).write_text(page, encoding="utf-8")
    return datei, len(eintraege)


def main() -> None:
    ergebnisse = [
        render_components(),
        render_blocks(),
        render_flat("charts.html", "Charts", CHARTS_DIR, "w-[900px]"),
        render_flat("typeset.html", "Typeset", TYPESET_DIR, "w-[820px]"),
    ]
    for datei, anzahl in ergebnisse:
        print(f"Galerie-Seite geschrieben -> gallery/{datei}  ({anzahl} Einträge)")


if __name__ == "__main__":
    main()
