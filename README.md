# Praxigraph

[![CI](https://github.com/Supportlik/Praxigraph/actions/workflows/ci.yml/badge.svg)](https://github.com/Supportlik/Praxigraph/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/praxigraph.svg)](https://pypi.org/project/praxigraph/)
[![Python versions](https://img.shields.io/pypi/pyversions/praxigraph.svg)](https://pypi.org/project/praxigraph/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/Supportlik/Praxigraph/blob/main/LICENSE)

**Praxigraph** (Greek *πρᾶξις* "act, transaction, proceeding" + *γράφειν* "to write": "the one that writes down your proceedings") is a Markdown-driven generator for business documents on your own letterhead: **meeting minutes, status reports, certificates, timesheets** — anything you issue on company paper that is not an invoice. It is the sibling project of [Ergograph](https://github.com/Supportlik/Ergograph), which does the same for CVs and dossiers.

The generator contains **no personal data**. Your letterhead (company name, address, contact, tax IDs, bank details, logo) lives in a `config.yaml` outside the repo; each document is one Markdown file with YAML front matter. The code only provides rendering, the theme and the PDF export.

## How it works

```
config.yaml + documents/*.md  ->  HTML (theme "letter")  ->  PDF (Chrome headless)
```

1. `config.yaml` holds the letterhead and steers the build: header logo and the multi-column footer (address, contact, tax IDs, bank) are printed on **every** page.
2. One Markdown file per document. The front matter carries the document type, title, date, an optional number, recipient and extra info-box rows; the Markdown body becomes the content — headings, lists and tables included.
3. Chrome (headless) renders the HTML to A4 PDFs, which then get page numbers (`i / n`, bottom right) and title/author metadata stamped in.

## Installation

Requirements: Python ≥ 3.10 and Google Chrome or Chromium. Chrome is only needed
for the PDF step (`praxigraph build --html-only` works without it) and is not
installed by pip — Praxigraph looks for an existing installation (see `chrome:` below).

```bash
# as an isolated tool (recommended)
uv tool install praxigraph

# or into the current environment
pip install praxigraph
```

All three dependencies (PyYAML, Markdown, pypdf) are pure Python.

## Quick start

```bash
cd examples/minimal/
praxigraph validate            # check config + documents
praxigraph build               # build everything (HTML + PDF)
praxigraph build --html-only   # HTML only, no Chrome
praxigraph build --doc kickoff-protokoll
```

The PDFs end up under `pdf/YYYY-MM-DD_<slug>.pdf` — the date comes from the
document's front matter, so rebuilding never shuffles your archive
(disable the prefix with `output.date_prefix: false`).

## Example output

The rendered example PDFs are committed under
[`examples/minimal/pdf/`](examples/minimal/pdf/): meeting minutes with a
recipient address, a status report, and a signed timesheet certificate — all
for a fictional company.

## The steering file `config.yaml`

```yaml
letterhead:
  name: Daniel Falkner                  # bold first line, also the PDF author
  tagline: IT-Beratung & Systemintegration
  street: Ahornweg 12
  zip: "93049"
  city: Regensburg
  # country: Deutschland                # optional, shown in the footer
  logo: assets/logo.svg                 # optional; SVG is inlined, PNG/JPEG embedded
  contact:                              # optional; each key is optional too
    phone: +49 941 000000
    email: mail@falkner-it.example
    website: falkner-it.example
  tax:                                  # optional: vat_id, tax_number
    vat_id: DE999999999
  bank:                                 # optional: name, iban, bic
    name: Musterbank
    iban: DE02 1203 0000 0000 2020 51
    bic: BYLADEM1001
  signature:                            # used by documents with `signature: true`
    name: Daniel Falkner
    place: Regensburg

theme: letter          # bundled theme, or path to your own .css
# color: "#1a3c6e"     # accent color (title, footer); default black
# lang: de             # HTML language attribute, default de
# date_format: "%d.%m.%Y"

documents: documents   # a directory with *.md, or an explicit list of files

labels:                # optional overrides of the German defaults, e.g. for English paper
  # date: Date
  # vat_id: VAT ID

output:
  html_dir: .build/html
  pdf_dir: pdf
  date_prefix: true    # date-stamped file names; false = stable names

# chrome: /path/to/chrome   # optional; otherwise auto-detected
```

The letterhead footer renders up to four columns, and empty ones simply
disappear: address · contact · tax IDs · bank details.

## A document

````markdown
---
type: Protokoll                  # document type, printed above the title
title: Kickoff Website-Relaunch
date: 2026-08-14                 # also the file-name prefix
number: P-2026-001               # optional, shown in the type line and info box
recipient: |                     # optional; adds a DIN-letter address block
  Muster GmbH
  Frau Erika Muster
  Musterallee 8
  93047 Regensburg
meta:                            # optional extra rows in the info box
  - label: Projekt
    value: Website-Relaunch
signature: true                  # optional signature block (place, date, line, name)
# slug: kickoff                  # optional, default: file name stem
# lang: de                       # optional, overrides config
---

## Teilnehmer

- Erika Muster (Muster GmbH)
...
````

The body is standard Markdown (Python-Markdown with the `tables`,
`fenced_code` and `sane_lists` extensions). Tables render in the letterhead
style: dark header row, thin rules. Front matter values are plain text and are
HTML-escaped; formatting belongs in the Markdown body.

## Development

```bash
uv run pytest                        # test suite, no Chrome and no network needed
cd examples/minimal && uv run praxigraph build
```

Design decisions and requirements live in [`docs/SPEC.md`](docs/SPEC.md).
Version history: [`CHANGELOG.md`](CHANGELOG.md).

## License

[MIT](LICENSE)
