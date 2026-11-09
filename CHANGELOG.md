# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2026-11-09

### Security

- pypdf raised to >= 6.21.4 (fixes GHSA-7mh2-4gg2-979f, GHSA-9mx8-4j7g-633p,
  GHSA-39mj-jf6j-2qj3, GHSA-qfv9-64jg-mh7p, GHSA-5hx5-vpf9-5wcv,
  GHSA-cgf9-327m-v77c, GHSA-f54x-cmq8-qg57, GHSA-gmh7-3g9r-mjh5,
  GHSA-jr96-gvgh-j3r4, GHSA-6c7f-9265-g8fw and CVE-2026-119203 to
  CVE-2026-119209).
- Release workflow: pypa/gh-action-pypi-publish 1.14.3 (GHSA-5xjx-3w67-w9x9).

### Changed

- CI: astral-sh/setup-uv 10.3.2; pytest 9.2.0 in the dev dependencies.

## [1.1.0] - 2026-10-07

### Added

- `letterhead.header_name: true` prints the name and tagline next to the
  header logo on every page (off by default).
- Security workflow (pip-audit, Trivy, CodeQL, dependency review) and
  Dependabot updates for Python dependencies and GitHub Actions.

### Security

- pypdf raised to >= 6.19.0 (fixes PYSEC-2026-4155 to PYSEC-2026-4159).
- Chrome now renders with its sandbox enabled; `--no-sandbox` is only used as
  root or with `PRAXIGRAPH_CHROME_NO_SANDBOX=1` (SPEC D9).

### Changed

- CI: least-privilege token, concurrency, locked dependencies, current action
  versions.

## [1.0.0] - 2026-09-01

### Added

- First release: Markdown documents with YAML front matter rendered onto an
  A4 letterhead (theme "letter") and exported to PDF via Chrome headless.
- Letterhead from `config.yaml`: logo (SVG inlined, PNG/JPEG embedded) in the
  header and a multi-column footer (address, contact, tax IDs, bank details)
  repeated on every page.
- Front matter fields: `type`, `title`, `date` (required), `number`,
  `recipient`, `meta`, `signature`, `slug`, `lang`.
- Page numbers (`i / n`, bottom right) and PDF title/author metadata via pypdf.
- The footer's e-mail and website are clickable links in the PDF.
- CLI: `praxigraph build` (with `--doc`, `--html-only`, `--date`) and
  `praxigraph validate`.
- Example under `examples/minimal/` with a fictional company; doubles as the
  test fixture.
