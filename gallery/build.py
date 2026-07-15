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

# (title, basecoat, shadcn, custom, beta)
COMPONENTS: list[tuple[str, bool, bool, bool, bool]] = [
    ("Accordion", True, True, False, False),
    ("Alert", True, True, False, False),
    ("Alert Dialog", True, True, False, False),
    ("Aspect Ratio", False, True, True, False),
    ("Attachment", False, True, True, False),
    ("Avatar", True, True, False, False),
    ("Badge", True, True, False, False),
    ("Breadcrumb", True, True, False, False),
    ("Bubble", False, True, True, False),
    ("Button", True, True, False, False),
    ("Button Group", True, True, False, False),
    ("Calendar", False, True, True, False),
    ("Card", True, True, False, False),
    ("Carousel", False, True, True, False),
    ("Chart", True, True, False, True),
    ("Checkbox", True, True, False, False),
    ("Collapsible", True, True, False, False),
    ("Combobox", True, True, False, False),
    ("Command", True, True, False, False),
    ("Context Menu", False, True, True, False),
    ("Data Table", False, True, True, False),
    ("Date Picker", False, True, True, False),
    ("Dialog", True, True, False, False),
    ("Direction", False, True, True, False),
    ("Drawer", True, True, False, True),
    ("Dropdown Menu", True, True, False, False),
    ("Empty", True, True, False, False),
    ("Field", True, True, False, False),
    ("Hover Card", False, True, True, False),
    ("Input", True, True, False, False),
    ("Input Group", True, True, False, False),
    ("Input OTP", False, True, True, False),
    ("Item", True, True, False, False),
    ("Kbd", True, True, False, False),
    ("Label", True, True, False, False),
    ("Marker", False, True, True, False),
    ("Menubar", False, True, True, False),
    ("Message", False, True, True, False),
    ("Message Scroller", False, True, True, False),
    ("Native Select", True, True, False, False),
    ("Navigation Menu", False, True, True, False),
    ("Pagination", True, True, True, False),
    ("Popover", True, True, False, False),
    ("Progress", True, True, False, False),
    ("Radio Group", True, True, False, False),
    ("Resizable", False, True, True, False),
    ("Scroll Area", True, True, False, False),
    ("Select", True, True, False, False),
    ("Separator", False, True, True, False),
    ("Sheet", False, True, True, False),
    ("Sidebar", True, True, False, False),
    ("Skeleton", True, True, False, False),
    ("Slider", True, True, False, False),
    ("Sonner", False, True, True, False),
    ("Spinner", True, True, True, False),
    ("Switch", True, True, False, False),
    ("Table", True, True, False, False),
    ("Tabs", True, True, False, False),
    ("Textarea", True, True, False, False),
    ("Theme Switcher", True, False, False, False),
    ("Toast", True, True, False, False),
    ("Toggle", False, True, True, False),
    ("Toggle Group", False, True, True, False),
    ("Tooltip", True, True, False, False),
    ("Typography", False, True, True, False),
]

# Demo width per component (natural width like the source pages). Default below.
DEFAULT_WIDTH = "max-w-2xl"
WIDTHS = {
    "table": "max-w-3xl", "data-table": "max-w-4xl", "sidebar": "max-w-full",
    "chart": "max-w-3xl", "typography": "max-w-3xl", "calendar": "max-w-md",
    "navigation-menu": "max-w-3xl", "menubar": "max-w-3xl", "resizable": "max-w-3xl",
    "card": "max-w-4xl",
}

TAG_STYLE = {
    "B": "bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300",
    "S": "bg-neutral-900 text-white dark:bg-white dark:text-neutral-900",
    "C": "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
}


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
    "Aktion": "button button-group toggle toggle-group",
    "Formular": "input textarea label field checkbox radio-group switch select native-select combobox input-group input-otp slider",
    "Overlay": "dialog alert-dialog drawer sheet popover hover-card tooltip dropdown-menu context-menu menubar command",
    "Navigation": "breadcrumb pagination tabs navigation-menu sidebar",
    "Anzeige": "table data-table card avatar accordion collapsible item empty separator aspect-ratio carousel chart calendar date-picker badge kbd progress skeleton spinner scroll-area marker resizable typography",
    "Feedback": "alert toast sonner",
    "Chat": "bubble message message-scroller attachment",
    "Sonstiges": "direction theme-switcher",
}
CATEGORY = {s: cat for cat, lst in _CAT_GROUPS.items() for s in lst.split()}
INTERACTIVE = set(
    "accordion alert-dialog carousel collapsible combobox command context-menu date-picker "
    "dialog drawer dropdown-menu hover-card menubar navigation-menu popover resizable select "
    "sheet sidebar slider tabs theme-switcher toast toggle toggle-group tooltip".split())


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
    for idx, (title, bc, sh, custom, beta) in enumerate(COMPONENTS):
        slug = slug_of(title)
        num = idx + 1
        body = partial(title)
        done = body is not None
        built += done
        toc.append(
            f'<a href="#{slug}" class="flex items-baseline gap-2 truncate rounded-md px-2 py-1 '
            f'text-sm text-muted-foreground hover:bg-muted hover:text-foreground">'
            f'<span class="tabular-nums text-muted-foreground/50 w-6 shrink-0 text-right">{num}</span>'
            f'<span class="truncate">{html.escape(title)}</span></a>'
        )
        beta_badge = ('<span class="badge" data-variant="secondary">Beta</span>' if beta else "")
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
        sections.append(
            f'<section id="{slug}" class="scroll-mt-6" style="margin-top:{mt}">'
            f'<div class="mx-auto flex w-[820px] max-w-full items-center gap-6 pb-3">'
            f'<h2 class="flex items-center gap-3 text-xl font-semibold tracking-tight">{num_badge}{html.escape(title)}{beta_badge}</h2>'
            f'</div>'
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
    pack_links = "".join(
        f'<link rel="stylesheet" data-pack="{k}" href="../c22/static/css/c22-{k}.css"'
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
<script src="../c22/static/js/basecoat.all.min.js" defer></script>
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
  <main class="min-w-0 flex-1 overflow-y-auto px-6 py-8">
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
