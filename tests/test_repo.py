"""Hygiene: was man beim Aufräumen vergisst, prüft eine Maschine besser.

Pflichtdateien, Versionsgleichstand, keine Artefakte, keine Geheimnisse — und
**keine persönlichen Namen**: kein eigener Host, keine eigene Domain, kein Kundenname.
Das Repo ist öffentlich; die Regel darf nicht am Vorsatz hängen.

Die allgemeinen Prüfungen und die Sperrlisten stehen in `tests/_kit/` — einer geteilten,
eingecheckten Basis, die `repokit sync` hierher schreibt. Sie ist stdlib-only und lädt zur
Testzeit nichts nach. Was hier steht, gilt nur für dieses Projekt.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _kit import hygiene  # noqa: E402
from _kit.report import Report  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
r = Report("Hygiene — Repo")

POLICY = hygiene.lade_policy()
PROJEKTE = ["TinySesam", "DashMyBoard", "C22"]
DATEIEN = hygiene.getrackte_dateien(str(ROOT))

# ---- Pflichtdateien (zweisprachig, wo es den Leser betrifft)
PFLICHT = [
    "README.md", "README.de.md", "LICENSE", "CHANGELOG.md",
    "CONTRIBUTING.md", "CONTRIBUTING.de.md", "SECURITY.md", "SECURITY.de.md",
    "CODE_OF_CONDUCT.md", "CODE_OF_CONDUCT.de.md",
    "pyproject.toml", ".ci-image",
    "scripts/check.sh", "scripts/_residue_check.sh", ".githooks/pre-push",
    ".github/workflows/ci.yml", ".github/dependabot.yml",
    "tests/_kit/hygiene.py", "tests/run_all.py", "tests/test_repo.py",
    "c22/__init__.py",
]
fehlend = hygiene.pruefe_pflichtdateien(str(ROOT), PFLICHT)
r.check(f"Pflichtdateien vorhanden ({len(PFLICHT)})", not fehlend, " | ".join(fehlend))

# ---- Keine private Infrastruktur (Muster + Namens-Hashes aus tests/_kit/hygiene_policy.json)
n_muster = len(POLICY.get("private_muster", []))
n_namen = len(POLICY.get("private_namen_sha256_16", []))
treffer = hygiene.pruefe_private_infrastruktur(str(ROOT), DATEIEN, POLICY, PROJEKTE)
r.check(f"keine private Infrastruktur ({n_muster} Muster + {n_namen} Namen)",
        not treffer, " | ".join(sorted(set(treffer))[:4]))

# ---- Nur neutrale Beispieladressen
adressen = hygiene.pruefe_adressen(str(ROOT), DATEIEN, POLICY)
r.check("nur neutrale Beispieladressen", not adressen, " | ".join(sorted(set(adressen))[:4]))

# ---- Version steht überall gleich
version = re.search(r'^version\s*=\s*"([^"]+)"',
                    (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.M).group(1)
versionsfehler = hygiene.pruefe_versionsgleichstand(str(ROOT))
r.check(f"Version {version}: pyproject, CHANGELOG und SemVer stimmen",
        not versionsfehler, " | ".join(versionsfehler))

# ---- Keine Artefakte, keine Geheimnisse
artefakte = hygiene.pruefe_artefakte(DATEIEN, POLICY)
r.check("keine generierten Artefakte versioniert", not artefakte, " | ".join(artefakte[:3]))
r.check("kein Datenverzeichnis oder .venv versioniert",
        not [f for f in DATEIEN if f.startswith("data/") or f.startswith(".venv/")])
lecks = hygiene.pruefe_geheimnisse(str(ROOT), DATEIEN, POLICY)
r.check("keine Geheimnisse im Klartext", not lecks, " | ".join(lecks[:3]))

# ---- Belegte Standards, maschinell erzwungen (context/repo-standards.md)
ungepinnt = hygiene.pruefe_actions_sha_gepinnt(str(ROOT), DATEIEN)
r.check("Actions per Commit-SHA gepinnt, nicht per Tag", not ungepinnt, " | ".join(ungepinnt[:3]))
ohne_rechte = hygiene.pruefe_workflow_permissions(str(ROOT), DATEIEN)
r.check("jeder Workflow setzt `permissions:`", not ohne_rechte, " | ".join(ohne_rechte[:3]))
selfhosted = hygiene.pruefe_kein_self_hosted_runner(str(ROOT), DATEIEN)
r.check("kein self-hosted Runner (öffentliches Repo)", not selfhosted, " | ".join(selfhosted[:3]))
kategorien = hygiene.pruefe_changelog_kategorien(str(ROOT), POLICY)
r.check("CHANGELOG nutzt gültige Kategorien", not kategorien, " | ".join(kategorien[:2]))

# GitHub wählt die README nach ORT aus, nicht nach Sprache — eine Übersetzung veraltet still.
uebersetzung = hygiene.pruefe_uebersetzungs_struktur(str(ROOT), [("README.md", "README.de.md")])
r.check("README.de.md folgt der Struktur von README.md", not uebersetzung, " | ".join(uebersetzung[:2]))

# ---- Sammellauf & Ausführbarkeit
r.check("run_all.py findet die Suiten automatisch",
        not hygiene.pruefe_run_all_sammelt_automatisch(str(ROOT)))
nicht_ausfuehrbar = hygiene.pruefe_ausfuehrbar(
    str(ROOT), ["scripts/check.sh", ".githooks/pre-push", "scripts/_residue_check.sh"])
r.check("Skripte sind ausführbar", not nicht_ausfuehrbar, " | ".join(nicht_ausfuehrbar))

sys.exit(r.done())
