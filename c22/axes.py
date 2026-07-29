#!/usr/bin/env python3
"""The theming axes and the tokens each one is made of — **one source**.

`docs/theming.md` explains *why* the axes exist and what they are meant to control; this module
is the machine-readable half of the same statement: which CSS custom properties an axis consists
of, and whether a style pack must set them.

Three consumers, one truth:

* `tests/test_axes.py` checks both directions — **every pack sets every axis**, and **no component
  bypasses an axis** with a literal value.
* the gallery build can label a pack by its axis values.
* the future theme generator (phase C) writes exactly these tokens.

Why this matters: the vendored Basecoat packs carry their character almost entirely in *class
rules* (`lyra` makes things square by writing `rounded-none` into 66 of its own classes), not in
tokens. Anything C22 styles itself therefore did **not** follow the pack — a C22 surface stayed
round in `lyra` and stayed too angular in `maia`. Tokens per pack close that gap: the pack states
its character once, and every component follows because it only ever reads tokens.

Vocabulary: `PFLICHT` tokens must be present in a pack's compiled CSS — that is what makes the
axis effective. `ABGELEITET` tokens are computed from them (in `tokens.css`) and must not be set
per pack; they would break the single point of truth.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Achse:
    """One theming axis. `nummer` matches the table in docs/theming.md."""
    nummer: int
    name: str
    zweck: str
    pflicht: tuple[str, ...]
    abgeleitet: tuple[str, ...] = field(default=())


# Axis 1 (style) is the pack itself and the icon LIBRARY choice lives in the markup — neither is
# a token, so neither appears here. Axis 8 is C22's own: the three values a typesetting
# generator actually turns (line length, leading, paragraph flow). Everything else is a token.
ACHSEN: tuple[Achse, ...] = (
    Achse(2, "base-color", "the neutral surfaces everything sits on",
          ("--background", "--foreground", "--card", "--card-foreground",
           "--popover", "--popover-foreground", "--muted", "--muted-foreground",
           "--border", "--input")),
    Achse(3, "accent", "the named accent and the interaction roles derived from it",
          ("--primary", "--primary-foreground", "--secondary", "--secondary-foreground",
           "--accent", "--accent-foreground", "--ring")),
    Achse(4, "status", "the status role pairs (full pairs, like every other role)",
          ("--destructive", "--destructive-foreground", "--success", "--success-foreground",
           "--warning", "--warning-foreground", "--info", "--info-foreground")),
    Achse(5, "chart", "the chart series palette",
          ("--chart-1", "--chart-2", "--chart-3", "--chart-4", "--chart-5")),
    Achse(6, "font", "the type faces",
          ("--font-sans", "--font-mono", "--font-heading")),
    Achse(7, "type-scale", "how large text is, as ONE knob the sizes derive from",
          ("--text-scale", "--font-weight-heading", "--tracking-heading"),
          ("--text-xs", "--text-sm", "--text-base", "--text-lg", "--text-xl",
           "--text-2xl", "--text-3xl", "--text-4xl", "--text-5xl")),
    Achse(8, "typeset", "prose typography: line length, leading and the gap between paragraphs",
          ("--measure", "--leading-body", "--flow")),
    Achse(9, "radius", "how round everything is, as ONE knob",
          ("--radius",), ("--radius-sm", "--radius-md", "--radius-lg", "--radius-xl")),
    Achse(10, "menu", "the sidebar colour scheme (NOT the dropdown accent — see CLAUDE.md)",
          ("--sidebar", "--sidebar-foreground", "--sidebar-border",
           "--sidebar-primary", "--sidebar-primary-foreground", "--sidebar-ring")),
    Achse(11, "menu-accent", "how loud the sidebar's active row is",
          ("--sidebar-accent", "--sidebar-accent-foreground")),
    Achse(12, "density", "how much air the layout has (Tailwind's spacing base)",
          ("--spacing",)),
    Achse(13, "elevation", "how things lift off the surface",
          ("--shadow-2xs", "--shadow-xs", "--shadow-sm", "--shadow-md",
           "--shadow-lg", "--shadow-xl", "--shadow-2xl")),
    Achse(14, "motion", "how fast and with what curve things move",
          ("--default-transition-duration", "--default-transition-timing-function")),
    Achse(15, "icon-weight", "how heavy the icon strokes are",
          ("--icon-stroke",)),
)

# Every token an axis owns — a component may only ever read these, never hardcode their effect.
PFLICHT_TOKENS: tuple[str, ...] = tuple(t for a in ACHSEN for t in a.pflicht)
ABGELEITETE_TOKENS: tuple[str, ...] = tuple(t for a in ACHSEN for t in a.abgeleitet)
ALLE_TOKENS: tuple[str, ...] = PFLICHT_TOKENS + ABGELEITETE_TOKENS


def achse_von(token: str) -> Achse | None:
    """Which axis does this token belong to?"""
    for a in ACHSEN:
        if token in a.pflicht or token in a.abgeleitet:
            return a
    return None
