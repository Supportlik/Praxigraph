# Praxigraph — Specification

Requirements are numbered R1…, design decisions D1…. Every substantive change
to formats or behavior updates this file.

## Purpose

Praxigraph renders business documents (meeting minutes, reports, certificates,
timesheets) from Markdown files onto a company letterhead and exports them as
A4 PDFs. It is the sibling of [Ergograph](https://github.com/Supportlik/Ergograph)
(CVs/dossiers) and follows the same philosophy: no personal data in the code,
everything steered from outside, Chrome headless for the PDF step, pypdf for
page numbers and metadata.

## Requirements

| # | Requirement | Implemented in |
|---|---|---|
| R1 | All letterhead data comes from `config.yaml`; the repo contains only a fictional example. | `config.py`, `examples/` |
| R2 | One document = one Markdown file with YAML front matter (`type`, `title`, `date` required). | `document.py` |
| R3 | The letterhead (logo header + company footer) is printed on **every** page. | theme `letter.css` (D2) |
| R4 | Page numbers `i / n` on every page, plus PDF title/author metadata. | `pdf.py` (D3) |
| R5 | An optional recipient renders as a letter address block with a small sender line above it. | `render.py` |
| R6 | An info box (number, date, free `meta` rows) sits top right on the first page. | `render.py` |
| R7 | `signature: true` appends a signature block (place, date, line, name, firm). | `render.py` |
| R8 | Labels default to German and are individually overridable (`labels:`). | `config.py` |
| R9 | Builds are reproducible: PDF names derive from the front matter date (`YYYY-MM-DD_<slug>.pdf`), or stable names with `date_prefix: false`. | `builder.py` |
| R10 | `praxigraph validate` checks config and all documents without Chrome. | `cli.py` |
| R11 | The test suite runs without Chrome and without network. | `tests/` |
| R12 | Front matter and config values are HTML-escaped; formatting belongs in the Markdown body. | `render.py` (D5) |

## Design decisions

- **D1 — Markdown, not YAML, for the body.** Ergograph's content is structured
  data (lists of stations, skills), so YAML fits. Minutes and reports are
  prose with headings and tables; Markdown is the natural format. Structured
  metadata stays in the YAML front matter.
- **D2 — Letterhead via `position: fixed` + thead/tfoot spacers.** Chrome's
  print engine supports neither CSS margin boxes nor `position: running`
  (both Paged-Media features used by commercial renderers). It does repeat
  `position: fixed` elements on every printed page, and a table's
  thead/tfoot repeat too and reserve the vertical space. The page skeleton
  therefore is one table with spacer rows; header and footer are fixed
  elements. `@page` margin is 0; horizontal margins come from content padding.
- **D3 — Page numbers stamped with pypdf.** Chrome does not support
  `counter(pages)`, so totals are unknowable in CSS. Like Ergograph, the
  numbers are stamped post-hoc in Helvetica (a PDF base-14 font, no
  embedding needed), bottom right just above the footer block.
- **D4 — The theme mirrors an invoice template.** The bundled theme "letter"
  replicates the metrics of a sevdesk "black invoice" letterhead (Roboto
  Condensed 9pt/11.5pt, content area 20/15 mm, ~46 mm header zone, ~30 mm
  four-column 7pt footer, black table header rows), so documents and invoices
  from the same company look like siblings. Custom themes: any `.css` path.
- **D5 — Scalar values are escaped, unlike Ergograph.** Ergograph treats
  content values as trusted HTML fragments (D2 there). Praxigraph documents
  have a real body channel for formatting — Markdown — so front matter and
  config scalars are plain text and get escaped. This keeps `&` in company
  names from breaking the page.
- **D6 — Webfont with graceful fallback.** The theme imports Roboto Condensed
  from Google Fonts; offline builds fall back to Helvetica/Arial. Chrome's
  `--virtual-time-budget` gives the font time to load.
- **D7 — No text-layer verification (yet).** Ergograph verifies ATS
  readability because CVs are machine-parsed. Reports and minutes are read by
  humans; the check adds little and is omitted in 0.1.0.
- **D8 — Fictional example doubles as the test fixture** (same as Ergograph):
  format changes must update examples, tests and this spec together.

## File name scheme

`pdf/<date>_<slug>.pdf` with `<date>` = front matter date (ISO) or the
`--date` override; `<slug>` = front matter `slug` or the Markdown file's stem.
`output.date_prefix: false` drops the prefix (used by the committed examples).
