#!/usr/bin/env python3
"""Zweisprachigkeit der Galerie-Website (Deutsch · Englisch) und die zwei Pillen-Umschalter.

**Ein** Sprachsystem, nach dem Muster der TinySesam-Website: GitHub Pages hat keinen Server,
also trägt **jede Seite beide Sprachen** und blendet eine per CSS aus. `?lang=de` bzw. `?lang=en`
schaltet, die Wahl wird gespeichert und gilt über Seitenwechsel — keine Sprach-Dateinamen, keine
doppelten Seiten.

**Was zweisprachig ist:** alles, was die Website *sagt* — Kopfleiste, Landing, Impressum,
Beschriftungen der Galerie (Abhängigkeiten, Kategorien, „Code"). **Was deutsch bleibt:** die
Beispieltexte *in* den Components. Sie sind Demo-Inhalt, nicht Website-Text (Repo-Konvention:
„German example copy"), und eine Component in zwei Sprachen zu pflegen hieße, jedes Partial
zweimal zu führen.

Die **Browsersprache zählt bewusst nicht**: sonst bekäme ein englischer Browser eine englische
Seite, ohne dass jemand darum gebeten hat. Standard ist Deutsch, weil die Beispiele deutsch sind.
"""
from __future__ import annotations

import html
import json

LANGS = ("de", "en")
SPEICHER = "c22-lang"

# Beschriftungen der Website: (deutsch, englisch). Alles, was nicht aus einem Partial kommt.
TEXTE: dict[str, tuple[str, str]] = {
    "uses": ("nutzt:", "uses:"),
    "used_by": ("genutzt von:", "used by:"),
    "code": ("Code", "Code"),
    "pack": ("Pack", "Pack"),
    "not_built": ("— noch nicht gebaut —", "— not built yet —"),
    "empty": ("— noch keine Inhalte —", "— nothing here yet —"),
    "empty_cat": ("— noch keine Blocks in dieser Kategorie —", "— no blocks in this category yet —"),
    "nav_pages": ("Galerie-Seiten", "Gallery pages"),
    "nav_content": ("Inhalt dieser Seite", "Contents of this page"),
    "to_start": ("Zur Startseite", "To the start page"),
    "lang_choose": ("Sprache wählen", "Choose language"),
    "theme_choose": ("Erscheinungsbild wählen", "Choose appearance"),
    "light": ("Hell", "Light"),
    "dark": ("Dunkel", "Dark"),
    # Block-Kategorien
    "cat_navigation": ("Navigation", "Navigation"),
    "cat_full_page": ("Komplette Seite", "Full page"),
    "cat_login_signup": ("Login & Signup", "Login & signup"),
    "cat_tables": ("Tabellen", "Tables"),
    # Seiten-Titel (Reiter-Beschriftung ist der Eigenname, der Fenstertitel wird übersetzt)
    "title_start": ("C22 — Design-System im shadcn-Look", "C22 — a design system in the shadcn look"),
    "title_components": ("C22 — Components", "C22 — Components"),
    "title_blocks": ("C22 — Blocks", "C22 — Blocks"),
    "title_charts": ("C22 — Charts", "C22 — Charts"),
    "title_typeset": ("C22 — Typeset", "C22 — Typeset"),
    "title_generator": ("C22 — Generator (Design & Typografie)",
                        "C22 — Generator (design & typography)"),
    "title_legal": ("C22 — Impressum & Datenschutz", "C22 — Imprint & privacy"),
}


def zwei(de: str, en: str) -> str:
    """Beide Sprachen nebeneinander; das CSS zeigt genau eine. Für Textknoten, nicht Attribute."""
    return f'<span class="l-de">{de}</span><span class="l-en">{en}</span>'


def t(schluessel: str) -> str:
    """Beschriftung aus TEXTE, zweisprachig ausgegeben."""
    de, en = TEXTE[schluessel]
    return zwei(html.escape(de), html.escape(en))


def klartext(schluessel: str, lang: str = "de") -> str:
    """Dieselbe Beschriftung einsprachig — für Attribute (`aria-label`, `title`)."""
    return TEXTE[schluessel][LANGS.index(lang)]


# Attribute können nicht zwei Sprachen tragen. Beschriftungen für Bedienelemente stehen deshalb
# in der Standardsprache im `aria-label`; sichtbare Texte sind zweisprachig.
LANG_CSS = "".join(f'html[data-lang="{a}"] .l-{b}{{display:none}}'
                   for a in LANGS for b in LANGS if a != b)


def _segment(inhalt: str, wert: str, attribut: str, aktiv: bool, label: str) -> str:
    """Ein Segment einer Pille — kanonischer Radiogroup-Knopf, kein eigener Look."""
    return (f'<button type="button" class="btn" data-variant="outline" data-size="sm" role="radio" '
            f'aria-checked="{"true" if aktiv else "false"}" {attribut}="{wert}" '
            f'aria-label="{html.escape(label)}">{inhalt}</button>')


def pille_sprache() -> str:
    """DE · EN. Das aktive Segment setzt das Skript beim Laden (es kennt die gespeicherte Wahl)."""
    segmente = "".join(
        _segment(l.upper(), l, "data-c22-lang", i == 0, "Deutsch" if l == "de" else "English")
        for i, l in enumerate(LANGS))
    return (f'<span class="button-group" role="radiogroup" data-c22-lang-pill '
            f'aria-label="{html.escape(klartext("lang_choose"))}">{segmente}</span>')


ICON_SONNE = ('<svg data-icon-lu="sun" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
              'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
              'stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/>'
              '<path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/>'
              '<path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/>'
              '<path d="m19.07 4.93-1.41 1.41"/></svg>')
ICON_MOND = ('<svg data-icon-lu="moon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
             'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
             'stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>')


def pille_theme() -> str:
    """Hell · Dunkel über Basecoats dokumentierte Theme-API (persistiert `localStorage.themeMode`)."""
    segmente = (_segment(ICON_SONNE, "light", "data-c22-theme", True, klartext("light"))
                + _segment(ICON_MOND, "dark", "data-c22-theme", False, klartext("dark")))
    return (f'<span class="button-group" role="radiogroup" data-c22-theme-pill '
            f'aria-label="{html.escape(klartext("theme_choose"))}">{segmente}</span>')


def kopf_skript(titel_je_sprache: dict[str, str]) -> str:
    """Setzt Sprache und Erscheinungsbild, BEVOR gezeichnet wird — sonst blitzt die falsche auf.

    Reihenfolge der Sprachwahl: `?lang=` schlägt gespeicherte Wahl schlägt Standard (Deutsch).
    Das Erscheinungsbild verwaltet Basecoat selbst; hier wird nur das aktive Pillen-Segment
    nachgezogen und auf `basecoat:themechange` gehört, damit beide Pillen nie lügen.
    """
    return f"""<script>
(function () {{
  var LANGS = {json.dumps(list(LANGS))}, TITEL = {json.dumps(titel_je_sprache, ensure_ascii=False)};
  var wurzel = document.documentElement;

  function speichere(k, v) {{ try {{ localStorage.setItem(k, v); }} catch (e) {{}} }}
  function gelesen(k) {{ try {{ return localStorage.getItem(k); }} catch (e) {{ return null; }} }}

  function setzeSprache(l) {{
    if (LANGS.indexOf(l) < 0) l = LANGS[0];
    wurzel.lang = l;
    wurzel.setAttribute('data-lang', l);
    if (TITEL[l]) document.title = TITEL[l];
    speichere('{SPEICHER}', l);
    markiere('[data-c22-lang]', 'c22Lang', l);
  }}

  function markiere(auswahl, feld, wert) {{
    document.querySelectorAll(auswahl).forEach(function (b) {{
      b.setAttribute('aria-checked', b.dataset[feld] === wert ? 'true' : 'false');
    }});
  }}

  function themaJetzt() {{
    if (window.basecoat && window.basecoat.theme) return window.basecoat.theme.get();
    return wurzel.classList.contains('dark') ? 'dark' : 'light';
  }}

  // Erscheinungsbild, BEVOR gezeichnet wird. Basecoat 1.0.2 SCHREIBT `themeMode` beim
  // Umschalten, liest den Wert aber nie zurück (`getItem` kommt in seinem Bundle nicht vor) —
  // ohne diese Zeilen wäre die Wahl beim nächsten Aufruf wieder weg. Ist nichts gespeichert,
  // gilt die Systemeinstellung; ein Klick auf die Pille schlägt sie ab dann dauerhaft.
  var parameter = new URLSearchParams(location.search);
  var gewuenscht = parameter.get('theme');          // ?theme=dark — deep-linkbar und prüfbar
  var gemerkt = gewuenscht || gelesen('themeMode');
  wurzel.classList.toggle('dark', gemerkt
      ? gemerkt === 'dark'
      : window.matchMedia('(prefers-color-scheme: dark)').matches);

  var sprache = parameter.get('lang') || gelesen('{SPEICHER}') || LANGS[0];
  setzeSprache(sprache);
  // Dieses Skript läuft im `head` — die Pillen stehen noch nicht im DOM, `markiere` fand
  // eben also nichts. Sobald das Markup da ist, wird die Markierung nachgezogen.
  document.addEventListener('DOMContentLoaded', function () {{
    markiere('[data-c22-lang]', 'c22Lang', document.documentElement.getAttribute('data-lang'));
  }});

  document.addEventListener('click', function (e) {{
    var l = e.target.closest('[data-c22-lang]');
    if (l) {{ setzeSprache(l.dataset.c22Lang); return; }}
    var t = e.target.closest('[data-c22-theme]');
    if (t && window.basecoat && window.basecoat.theme) window.basecoat.theme.set(t.dataset.c22Theme);
  }});

  // Basecoat lädt später (defer) und setzt das Thema aus `localStorage.themeMode`; erst dann
  // steht fest, welches Segment aktiv ist.
  function themaMarkieren() {{ markiere('[data-c22-theme]', 'c22Theme', themaJetzt()); }}
  document.addEventListener('basecoat:themechange', themaMarkieren);
  document.addEventListener('DOMContentLoaded', themaMarkieren);
  themaMarkieren();
}})();
</script>"""
