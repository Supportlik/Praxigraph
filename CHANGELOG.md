# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-01

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
