# Security Policy

<p align="left"><b>English</b> · <a href="i18n/SECURITY.de.md">Deutsch</a></p>

<p align="right"><img src="docs/logo.png" alt="C22" width="60" height="60"></p>

## Reporting a vulnerability

Please report privately through GitHub's
[private vulnerability reporting](https://github.com/Ollornog/C22/security/advisories/new)
rather than opening a public issue. Expect a first reply within a week.

## Scope and design decisions worth knowing

- **C22 ships static assets, not a running service.** It has no network access, no
  authentication and no state of its own; it provides CSS, a little JavaScript and
  optional Jinja templates.
- **Everything is self-contained.** The assets reference no external CDN, font host or
  tracker at runtime — a consuming app makes no third-party request because of C22. An
  asset that does is a bug worth reporting.
- **The Jinja macros escape by default.** A macro that emits caller-supplied HTML marks
  it as such deliberately; a macro that lets unescaped input through is a bug.

## Not in scope

How a consuming application authenticates, stores data or proxies requests — that belongs
to the app, not to this presentation layer.
