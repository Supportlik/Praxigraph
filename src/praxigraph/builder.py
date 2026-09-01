"""Orchestrate the build: load documents, write HTML, render PDFs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import Config, ConfigError
from .document import Document, load_document
from .pdf import find_chrome, finalize_pdf, render_pdf
from .render import render_document


@dataclass
class BuildResult:
    document: Document
    html_path: Path
    pdf_path: Path | None
    ok: bool


def load_documents(cfg: Config) -> list[Document]:
    documents = [load_document(path) for path in cfg.documents]
    slugs = [doc.slug for doc in documents]
    for slug in slugs:
        if slugs.count(slug) > 1:
            raise ConfigError(f"Duplicate document slug '{slug}' "
                              f"(set a distinct 'slug' in the front matter).")
    return documents


def pdf_name(cfg: Config, doc: Document, datestamp: str | None = None) -> str:
    if not cfg.output.date_prefix:
        return f"{doc.slug}.pdf"
    return f"{datestamp or doc.date.isoformat()}_{doc.slug}.pdf"


def build(cfg: Config, slugs: list[str] | None = None, html_only: bool = False,
          datestamp: str | None = None) -> list[BuildResult]:
    documents = load_documents(cfg)
    if slugs:
        known = {doc.slug for doc in documents}
        for slug in slugs:
            if slug not in known:
                raise ConfigError(f"Unknown document '{slug}' "
                                  f"(available: {', '.join(sorted(known))})")
        documents = [doc for doc in documents if doc.slug in slugs]
    if not documents:
        raise ConfigError("No documents to build.")

    chrome = None if html_only else find_chrome(cfg.chrome)
    cfg.output.html_dir.mkdir(parents=True, exist_ok=True)
    if not html_only:
        cfg.output.pdf_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for doc in documents:
        html_path = cfg.output.html_dir / f"{doc.slug}.html"
        html_path.write_text(render_document(cfg, doc), encoding="utf-8")
        if html_only:
            print(f"  HTML {html_path}")
            results.append(BuildResult(doc, html_path, None, True))
            continue
        pdf_path = cfg.output.pdf_dir / pdf_name(cfg, doc, datestamp)
        ok = render_pdf(chrome, html_path, pdf_path)
        if ok:
            finalize_pdf(pdf_path, title=f"{doc.doc_type}: {doc.title}",
                         author=cfg.letterhead.name)
            print(f"  PDF  {pdf_path}")
        else:
            print(f"  FAILED {pdf_path}")
        results.append(BuildResult(doc, html_path, pdf_path, ok))
    return results
