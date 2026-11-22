---
type: Task
title: Pure token file per pack (c22-tokens-<pack>.css) for foreign pages
status: offen
id: T-21
milestone: M-2
created: '2026-11-22'
---
# T-21 — Pure token file per pack (c22-tokens-<pack>.css) for foreign pages

Finding from the TinySesam adapter (PR #251, TinySesam T-61): C22 has no pure token file. Apps load about 500 KB including global classes (.card, .tabs, reset) that collide on foreign pages. TinySesam fixed three collisions, but future classes can collide again. Proposal: one file per pack containing only the variables; then switch the TinySesam adapter to it. Migrated from the central todo list (auto-sprint 2026-11-20 tinysesam).
