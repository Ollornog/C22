# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed — unified layout of the documentation subpages

`CONTRIBUTING`, `SECURITY` and the German `i18n/` versions now carry the language switcher directly
below the heading and the logo bottom-right — the same pattern across all own repos. The English
`CODE_OF_CONDUCT.md` stays untouched and **pure** so GitHub recognises it as Contributor Covenant
rather than "Other".

## [0.1.0] - 2026-07-10

### Added
- Repository skeleton: package layout (`c22/static/{css,js}`, `c22/macros`),
  the `static_path()` and `macros_path()` helpers, a `Report`-based test harness,
  the shared hygiene kit via `repokit`, and a hardened CI workflow.
- Bilingual community files (README, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT).
- Project logo (`docs/logo.png`) in both README versions, with Flaticon attribution.

No design assets are included yet; they follow once the layout foundation is settled.
