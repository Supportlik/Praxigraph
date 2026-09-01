"""Assemble the HTML for one document: letterhead + Markdown body."""

from __future__ import annotations

import base64
import html
import re
from pathlib import Path

import markdown

from .config import Config, ConfigError, Letterhead
from .document import Document

THEMES_DIR = Path(__file__).parent / "themes"

_MD_EXTENSIONS = ["tables", "fenced_code", "sane_lists"]

_IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".webp": "image/webp"}


def _esc(value: str) -> str:
    return html.escape(str(value), quote=False)


def load_theme(theme: str, base: Path) -> str:
    """A bundled theme name, or a path to a custom .css file."""
    bundled = THEMES_DIR / f"{theme}.css"
    if bundled.is_file():
        return bundled.read_text(encoding="utf-8")
    custom = (base / theme).resolve()
    if custom.is_file():
        return custom.read_text(encoding="utf-8")
    names = ", ".join(sorted(p.stem for p in THEMES_DIR.glob("*.css")))
    raise ConfigError(f"Theme '{theme}' not found (bundled: {names}).")


def _logo_html(logo: Path) -> str:
    """SVG is inlined (keeps gradients crisp), raster images become data URIs."""
    suffix = logo.suffix.lower()
    if suffix == ".svg":
        svg = logo.read_text(encoding="utf-8")
        svg = re.sub(r"<\?xml[^>]*\?>", "", svg).strip()
        return f'<div class="logo">{svg}</div>'
    mime = _IMAGE_TYPES.get(suffix)
    if mime is None:
        raise ConfigError(f"Unsupported logo format '{suffix}' "
                          f"(supported: .svg, {', '.join(_IMAGE_TYPES)}).")
    data = base64.b64encode(logo.read_bytes()).decode("ascii")
    return f'<div class="logo"><img src="data:{mime};base64,{data}" alt=""></div>'


def _firm_line(head: Letterhead) -> str:
    return _esc(head.name) + (f" – {_esc(head.tagline)}" if head.tagline else "")


def _header_html(head: Letterhead) -> str:
    inner = _logo_html(head.logo) if head.logo else \
        f'<div class="logo-fallback">{_firm_line(head)}</div>'
    return f'<header class="letterhead-header">{inner}</header>'


def _footer_section(rows: list[tuple[str | None, str]]) -> str:
    parts = []
    for label, value in rows:
        prefix = f'<span class="footer-label">{_esc(label)}</span> ' if label else ""
        parts.append(f'<div class="footer-row">{prefix}'
                     f'<span class="footer-value">{value}</span></div>')
    return f'<div class="footer-section">{"".join(parts)}</div>'


def _footer_html(head: Letterhead, labels: dict) -> str:
    address = [(None, _esc(head.name)
                      + (f"<br>{_esc(head.tagline)}" if head.tagline else "")),
               (None, _esc(head.street)),
               (None, f"{_esc(head.zip)} {_esc(head.city)}")]
    if head.country:
        address.append((None, _esc(head.country)))
    sections = [_footer_section(address)]

    contact = [(labels[key], _esc(head.contact[field]))
               for key, field in (("phone", "phone"), ("email", "email"),
                                  ("web", "website"))
               if head.contact.get(field)]
    if contact:
        sections.append(_footer_section(contact))

    tax = [(labels[key], _esc(head.tax[key]))
           for key in ("vat_id", "tax_number") if head.tax.get(key)]
    if tax:
        sections.append(_footer_section(tax))

    bank = [(labels[key], _esc(head.bank[field]))
            for key, field in (("bank", "name"), ("iban", "iban"), ("bic", "bic"))
            if head.bank.get(field)]
    if bank:
        sections.append(_footer_section(bank))

    return ('<footer class="letterhead-footer"><div class="footer-grid">'
            + "".join(sections) + "</div></footer>")


def _infobox_html(doc: Document, cfg: Config) -> str:
    rows = []
    if doc.number:
        rows.append((cfg.labels["number"], doc.number))
    rows.append((cfg.labels["date"], doc.date.strftime(cfg.date_format)))
    rows.extend((entry["label"], entry["value"]) for entry in doc.meta)
    cells = "".join(
        f'<tr><td class="infobox-label">{_esc(label)}</td>'
        f'<td class="infobox-value">{_esc(value)}</td></tr>'
        for label, value in rows)
    return f'<div class="infobox"><table>{cells}</table></div>'


def _first_page_head(doc: Document, cfg: Config) -> str:
    head = cfg.letterhead
    recipient = ""
    modifier = ""
    if doc.recipient:
        modifier = " with-recipient"
        lines = "<br>".join(_esc(line) for line in doc.recipient.splitlines())
        recipient = (
            f'<div class="recipient-block">'
            f'<div class="addressline">{_firm_line(head)}<br>'
            f'{_esc(head.street)} – {_esc(head.zip)} {_esc(head.city)}</div>'
            f'<div class="recipient">{lines}</div></div>')
    return (f'<div class="first-page-head{modifier}">{recipient}'
            f'{_infobox_html(doc, cfg)}</div>')


def _signature_html(doc: Document, cfg: Config) -> str:
    if not doc.signature:
        return ""
    sig = cfg.letterhead.signature
    name = sig.get("name", cfg.letterhead.name)
    place = sig.get("place", cfg.letterhead.city)
    return (
        '<div class="signature">'
        f'<div class="signature-place-date">{_esc(place)}, '
        f'{doc.date.strftime(cfg.date_format)}</div>'
        '<div class="signature-line"></div>'
        f'<div class="signature-name">{_esc(name)}</div>'
        f'<div class="signature-firm">{_firm_line(cfg.letterhead)}</div>'
        '</div>')


def render_document(cfg: Config, doc: Document) -> str:
    theme = load_theme(cfg.theme, cfg.base)
    color = (f":root {{ --primary-color: {cfg.color}; }}" if cfg.color else "")
    body_html = markdown.markdown(doc.body_md, extensions=_MD_EXTENSIONS)
    number = f' <span class="doc-number">{_esc(doc.number)}</span>' if doc.number else ""
    return f"""<!DOCTYPE html>
<html lang="{_esc(doc.lang or cfg.lang)}">
<head>
<meta charset="utf-8">
<title>{_esc(doc.doc_type)}: {_esc(doc.title)}</title>
<style>{theme}</style>
<style>{color}</style>
</head>
<body>
{_header_html(cfg.letterhead)}
{_footer_html(cfg.letterhead, cfg.labels)}
<table class="page">
<thead><tr><td><div class="header-space"></div></td></tr></thead>
<tbody><tr><td class="content">
{_first_page_head(doc, cfg)}
<div class="doc-head">
<div class="doc-type">{_esc(doc.doc_type)}{number}</div>
<h1 class="doc-title">{_esc(doc.title)}</h1>
</div>
<div class="doc-body">
{body_html}
</div>
{_signature_html(doc, cfg)}
</td></tr></tbody>
<tfoot><tr><td><div class="footer-space"></div></td></tr></tfoot>
</table>
</body>
</html>
"""
