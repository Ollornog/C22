# Icons — the name registry behind the icon-library axis

C22 ships **two** icon libraries (axis 8 in [`theming.md`](theming.md)):

- **lucide** (ISC) — inline `<svg>` stroke icons, the default in every component partial. Works
  without JS; stroke width rides on the `--icon-stroke` axis.
- **Phosphor** (MIT) — a vendored 21-icon subset in
  [`icons.js`](../c22/static/js/icons.js), rendered at runtime by `c22.js` from
  `<span data-icon-ph="name" data-weight="…">`. Its six weights are the icon-weight axis for
  fill icons.

Switching the library is an **install-/generation-time** decision (like shadcn's `iconLibrary`):
a tool replaces the inline markup based on the icon's *name*. That only works if every inline
icon **has** a machine-readable name — which is exactly what the annotation provides:

- Every lucide-like inline `<svg>` carries **`data-icon-lu="<lucide-name>"`**
  (written by [`tools/annotate-icons.py`](../tools/annotate-icons.py), enforced by rule 11 of
  `tests/test_conventions.py`).
- Phosphor spans carry **`data-icon-ph="<phosphor-name>"`** (pre-existing convention).

> **Why not `data-icon`?** That attribute is already taken: Basecoat uses
> `data-icon="inline-start|inline-end"` on the same `<svg>` elements to control icon padding
> inside `.btn` — a functional CSS selector, not a name. The library name therefore gets its own
> suffixed attribute, symmetrical to `data-icon-ph`.

## Name mapping — the 21 Phosphor icons

The two libraries name the same concepts differently. This table is the translation layer a
library-switching tool works from. The lucide column uses the **canonical** lucide-static 1.25.0
names (verified against `icon-nodes.json` of the pinned download — lucide keeps old names like
`x-circle`/`bar-chart-3` only as alias files).

| Semantic | lucide (`data-icon-lu`) | Phosphor (`data-icon-ph`) |
|----------|-------------------------|---------------------------|
| error / close-circle | `circle-x` | `x-circle` |
| warning | `triangle-alert` | `warning` |
| info | `info` | `info` |
| success / check-circle | `circle-check` | `check-circle` |
| activity | `activity` | `pulse` |
| dashboard / grid | `layout-grid` | `squares-four` |
| spinner | `loader-circle` | `circle-notch` |
| expand-all | `chevrons-down` | `caret-double-down` |
| chevron down | `chevron-down` | `caret-down` |
| chevron left | `chevron-left` | `caret-left` |
| chevron right | `chevron-right` | `caret-right` |
| clock | `clock` | `clock` |
| notification | `bell` | `bell` |
| home | `house` | `house` |
| settings | `settings` | `gear` |
| user | `user` | `user` |
| folder | `folder` | `folder` |
| bar chart | `chart-column` | `chart-bar` |
| search | `search` | `magnifying-glass` |
| list | `list` | `list` |
| sign out | `log-out` | `sign-out` |

## Custom icons (no lucide counterpart)

| Name | Where | Notes |
|------|-------|-------|
| `github` | `badge.html` (shields-style badge) | GitHub logo, not a lucide icon — carries the self-chosen name `data-icon-lu="github"`. A library switch must leave customs untouched. |

## How the table grows

- **New inline lucide icon in a partial** → run `python3 tools/annotate-icons.py`; it names the
  icon automatically (or reports it unmatched — then extend the tool's `OVERRIDES` or fix the
  icon). No entry needed here unless the icon also exists in the Phosphor subset.
- **New Phosphor icon in `icons.js`** → add its row to the mapping table above, with the
  *canonical* lucide name for the same concept (verify against the pinned lucide-static, don't
  guess).
- **New custom (non-lucide) glyph** → give it a self-chosen `data-icon-lu` name via the tool's
  `OVERRIDES` and list it under *Custom icons*.

Two annotations are **judgement calls**, kept honest here: the marker document icon
(`file-text` — a two-full-line variant no lucide version draws exactly) and the marker link arrow
(`arrow-up-right` — a coordinate variant of the same shape). Both are named after the closest
canonical lucide icon.
