import pytest

from praxigraph.builder import build, load_documents, pdf_name
from praxigraph.config import ConfigError, load_config
from praxigraph.document import load_document


@pytest.fixture
def cfg(example):
    return load_config(example / "config.yaml")


def test_pdf_name_stable(cfg, example):
    doc = load_document(example / "documents" / "kickoff-protokoll.md")
    assert pdf_name(cfg, doc) == "kickoff-protokoll.pdf"


def test_pdf_name_with_date_prefix(cfg, example):
    cfg.output.date_prefix = True
    doc = load_document(example / "documents" / "kickoff-protokoll.md")
    assert pdf_name(cfg, doc) == "2026-08-14_kickoff-protokoll.pdf"
    assert pdf_name(cfg, doc, "2027-01-01") == "2027-01-01_kickoff-protokoll.pdf"


def test_duplicate_slug(cfg, example):
    duplicate = example / "documents" / "zweite-datei.md"
    duplicate.write_text(
        "---\ntype: B\ntitle: T\ndate: 2026-01-01\nslug: kickoff-protokoll\n---\nx\n")
    cfg.documents.append(duplicate)
    with pytest.raises(ConfigError, match="Duplicate document slug"):
        load_documents(cfg)


def test_build_html_only(cfg):
    results = build(cfg, html_only=True)
    assert len(results) == 3
    assert all(r.ok and r.pdf_path is None for r in results)
    assert (cfg.output.html_dir / "kickoff-protokoll.html").exists()


def test_build_slug_filter(cfg):
    results = build(cfg, slugs=["statusbericht-august"], html_only=True)
    assert [r.document.slug for r in results] == ["statusbericht-august"]


def test_build_unknown_slug(cfg):
    with pytest.raises(ConfigError, match="Unknown document 'nope'"):
        build(cfg, slugs=["nope"], html_only=True)
