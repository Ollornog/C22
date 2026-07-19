#!/usr/bin/env python3
"""C22 gallery generator — the Live-Container / SPOT.

Renders one static HTML page (`gallery/index.html`) showing every Stufe-1
component in its states. Engine-neutral: each component's *canonical HTML* lives
in `c22/components/<slug>.html`; this script only stitches them together.

Each entry is tagged by source — Basecoat (B), shadcn (S), custom (C) — and links
to the source doc pages as a button group. Interactive components are shown with
their real trigger (the JS in basecoat.all.min.js makes them work live).

    python3 gallery/build.py
    tools/tailwindcss -i c22/static/css/input.css -o c22/static/css/c22.css --minify
    webshot <url>/gallery/index.html out.png --net host
"""
from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = ROOT / "c22" / "components"
OUT = ROOT / "gallery" / os.environ.get("C22_OUT", "index.html")
GAP = os.environ.get("C22_GAP", "7rem")  # space before each section container

SHADCN = "https://ui.shadcn.com/docs/components/base/{slug}"
BASECOAT = "https://basecoatui.com/components/{slug}"

# (title, basecoat, shadcn, custom)
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
    ("Chart", True, True, False),
    ("Checkbox", True, True, False),
    ("Collapsible", True, True, False),
    ("Combobox", True, True, False),
    ("Command", True, True, False),
    ("Context Menu", False, True, True),
    ("Data Table", False, True, True),
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
    ("Typography", False, True, True),
    # Neue Einträge NUR ans Ende anhängen — die Nummern 1–69 sind extern referenziert (Review).
    ("Scrollbar", True, False, True),
    ("Close Button", False, False, True),
    ("Color Roles", False, False, True),
    ("Code Block", False, False, True),
    ("Editable Table", False, False, True),
]

# Demo width per component (natural width like the source pages). Default below.
DEFAULT_WIDTH = "max-w-2xl"
WIDTHS = {
    "table": "max-w-3xl", "data-table": "max-w-4xl", "sidebar": "max-w-full",
    "editable-table": "max-w-3xl",
    "chart": "max-w-3xl", "typography": "max-w-3xl", "calendar": "max-w-md",
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
    "chart": [r'data-chart'],
    "checkbox": [r'type="checkbox"(?![^>]*role="switch")'],
    "close-button": [r'btn-close'],
    "code-block": [r'class="code-block'],
    "collapsible": [r'class="collapsible'],
    "combobox": [r'class="combobox', r'combobox-trigger'],
    "command": [r'class="command[" ]'],
    "context-menu": [r'class="context-menu'],
    "data-table": [r'data-datatable'],
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
    "Anzeige": "table data-table card avatar accordion collapsible item empty separator aspect-ratio carousel chart calendar date-picker badge kbd icon progress skeleton spinner scroll-area scrollbar marker resizable typography color-roles code-block",
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


def render() -> tuple[str, int]:
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
        done = body is not None
        built += done
        toc.append(
            f'<a href="#{slug}" class="flex items-baseline gap-2 truncate rounded-md px-2 py-1 '
            f'text-sm text-muted-foreground hover:bg-muted hover:text-foreground">'
            f'<span class="tabular-nums text-muted-foreground/50 w-6 shrink-0 text-right">{num}</span>'
            f'<span class="truncate">{html.escape(title)}</span></a>'
        )
        num_badge = f'<span class="tabular-nums text-muted-foreground">{num}.</span>'
        demo = (letter_labels(body) if done
                else '<p class="text-muted-foreground text-sm italic">— noch nicht gebaut —</p>')
        code_block = (
            f'<details>'
            f'<summary class="flex cursor-pointer select-none list-none items-center justify-between gap-4 px-4 py-2 [&::-webkit-details-marker]:hidden">'
            f'<span class="text-muted-foreground hover:text-foreground text-xs font-medium">Code</span>'
            f'{doclinks(slug, bc, sh)}'
            f'</summary>'
            f'<pre class="bg-muted/40 overflow-x-auto rounded-b-xl p-4 text-xs leading-relaxed"><code>{html.escape(body.strip())}</code></pre>'
            f'</details>'
        ) if done else ""
        mt = "2rem" if idx == 0 else GAP
        dep_teile = []
        if done and deps.get(slug):
            dep_teile.append(f'<span><span class="text-foreground/70 font-medium">nutzt:</span> {dep_chips(deps[slug])}</span>')
        if done and used_by.get(slug):
            dep_teile.append(f'<span><span class="text-foreground/70 font-medium">genutzt von:</span> {dep_chips(used_by[slug])}</span>')
        dep_html = (
            f'<div class="text-muted-foreground mx-auto flex w-[820px] max-w-full flex-wrap gap-x-6 gap-y-1 pb-3 text-xs">'
            + "".join(dep_teile) + '</div>'
        ) if dep_teile else ""
        sections.append(
            f'<section id="{slug}" class="scroll-mt-6" style="margin-top:{mt}">'
            f'<div class="mx-auto flex w-[820px] max-w-full items-center gap-6 pb-3">'
            f'<h2 class="flex items-center gap-3 text-xl font-semibold tracking-tight">{num_badge}{html.escape(title)}</h2>'
            f'</div>'
            f'{dep_html}'
            f'<div class="mx-auto w-[820px] max-w-full rounded-xl border">'
            f'<div class="flex min-h-64 flex-col items-center justify-center p-10">{demo}</div>'
            f'{code_block}'
            f'</div>'
            f'</section>'
        )
    total = len(COMPONENTS)
    packs = [
        ("vega", "Vega", ["neutral", "Standard"]),
        ("nova", "Nova", ["rund", "weich"]),
        ("maia", "Maia", ["sehr rund", "freundlich"]),
        ("lyra", "Lyra", ["eckig", "brutalist"]),
        ("mira", "Mira", ["kompakt", "dezent"]),
        ("luma", "Luma", ["luftig", "sehr rund"]),
        ("sera", "Sera", ["Großbuchstaben", "eckig"]),
        ("rhea", "Rhea", ["abgerundet", "ruhig"]),
    ]
    # Cache-Buster: Browser (auch Chrome an einem http.server ohne Cache-Header) cachen CSS/JS
    # heuristisch — nach einem Rebuild sah man sonst alte Optik/altes Verhalten, bis man hart
    # neu lud. Die mtime als ?v= macht jede geänderte Datei zu einer neuen URL.
    def v(rel: str) -> int:
        return int((ROOT / "c22" / "static" / rel).stat().st_mtime)

    pack_links = "".join(
        f'<link rel="stylesheet" data-pack="{k}" href="../c22/static/css/c22-{k}.css?v={v(f"css/c22-{k}.css")}"'
        f'{"" if i == 0 else " disabled"}>'
        for i, (k, _, _) in enumerate(packs))
    pack_options = "".join(f'<option value="{k}">{lbl}</option>' for k, lbl, _ in packs)
    pack_attrs_js = json.dumps({k: attrs for k, _, attrs in packs}, ensure_ascii=False)
    pack_badges_html = "".join(
        f'<span class="bg-muted text-muted-foreground rounded px-2 py-0.5 text-[11px] font-medium">{html.escape(a)}</span>'
        for a in packs[0][2])
    page = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>C22 — Component-Galerie ({built}/{total})</title>
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
      <span class="text-muted-foreground text-sm font-normal">Galerie · {built}/{total}</span>
    </div>
  </div>
  <div class="ms-auto flex flex-wrap items-center gap-x-5 gap-y-2 text-sm">
    <label class="flex items-center gap-2"><span class="text-muted-foreground">Pack</span>
      <select class="select w-28" onchange="c22SetPack(this.value)">{pack_options}</select></label>
    <span id="c22-pack-attrs" class="flex flex-wrap items-center gap-1">{pack_badges_html}</span>
    <button type="button" class="btn" data-variant="outline" data-size="sm" onclick="document.documentElement.classList.toggle('dark')">Hell / Dunkel</button>
  </div>
</header>
<div class="flex min-h-0 flex-1">
  <aside class="hidden w-64 shrink-0 overflow-y-auto border-r px-3 py-4 lg:block">
    <nav class="flex flex-col gap-0.5">{''.join(toc)}</nav>
  </aside>
  <main class="relative min-w-0 flex-1 overflow-y-auto px-6 py-8">
    {''.join(sections)}
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
}}
(function () {{
  var p = new URLSearchParams(location.search).get('pack') || 'vega';
  c22SetPack(p);
  var s = document.querySelector('select[onchange^="c22SetPack"]');
  if (s) s.value = p;
}})();
</script>
</body>
</html>
"""
    return page, built


def main() -> None:
    page, built = render()
    OUT.write_text(page, encoding="utf-8")
    print(f"Galerie geschrieben -> {OUT.relative_to(ROOT)}  ({built}/{len(COMPONENTS)} gebaut)")


if __name__ == "__main__":
    main()
