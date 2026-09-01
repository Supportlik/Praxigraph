import datetime as dt

import pytest

from praxigraph.config import ConfigError
from praxigraph.document import load_document


def test_loads_protokoll(example):
    doc = load_document(example / "documents" / "kickoff-protokoll.md")
    assert doc.slug == "kickoff-protokoll"
    assert doc.doc_type == "Protokoll"
    assert doc.title == "Kickoff Website-Relaunch"
    assert doc.date == dt.date(2026, 8, 14)
    assert doc.number == "P-2026-001"
    assert doc.recipient.startswith("Muster GmbH")
    assert doc.meta[0] == {"label": "Projekt", "value": "Website-Relaunch muster.example"}
    assert doc.signature is False
    assert "## Teilnehmer" in doc.body_md


def test_signature_flag(example):
    doc = load_document(example / "documents" / "leistungsnachweis-august.md")
    assert doc.signature is True


def _write(tmp_path, text):
    path = tmp_path / "doc.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_missing_front_matter(tmp_path):
    with pytest.raises(ConfigError, match="front matter"):
        load_document(_write(tmp_path, "# Just Markdown\n"))


def test_missing_required_field(tmp_path):
    with pytest.raises(ConfigError, match="'title'"):
        load_document(_write(tmp_path, "---\ntype: Bericht\ndate: 2026-01-01\n---\nx\n"))


def test_invalid_date(tmp_path):
    with pytest.raises(ConfigError, match="'date'"):
        load_document(_write(
            tmp_path, "---\ntype: B\ntitle: T\ndate: irgendwann\n---\nx\n"))


def test_invalid_meta(tmp_path):
    with pytest.raises(ConfigError, match="'meta'"):
        load_document(_write(
            tmp_path,
            "---\ntype: B\ntitle: T\ndate: 2026-01-01\nmeta: [nur-text]\n---\nx\n"))


def test_slug_override(tmp_path):
    doc = load_document(_write(
        tmp_path, "---\ntype: B\ntitle: T\ndate: 2026-01-01\nslug: eigener\n---\nx\n"))
    assert doc.slug == "eigener"
