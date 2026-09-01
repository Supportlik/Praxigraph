import pytest

from praxigraph.config import ConfigError, load_config
from praxigraph.document import load_document
from praxigraph.render import load_theme, render_document


@pytest.fixture
def cfg(example):
    return load_config(example / "config.yaml")


def _render(cfg, example, name):
    return render_document(cfg, load_document(example / "documents" / name))


def test_letterhead_and_body(cfg, example):
    html = _render(cfg, example, "kickoff-protokoll.md")
    # letterhead: logo inlined as SVG, footer carries the company data
    assert "Falkner IT logo" in html
    assert "mail@falkner-it.example" in html
    assert "DE02 1203 0000 0000 2020 51" in html
    # first page: sender line, recipient, info box
    assert "Daniel Falkner – IT-Beratung &amp; Systemintegration" in html
    assert "Erika Muster" in html
    assert "P-2026-001" in html
    assert "14.08.2026" in html
    # document head and Markdown body
    assert "Kickoff Website-Relaunch" in html
    assert "<h2>Teilnehmer</h2>" in html
    assert "<th>Verantwortlich</th>" in html


def test_no_recipient_no_addressline(cfg, example):
    html = _render(cfg, example, "statusbericht-august.md")
    assert 'class="addressline"' not in html
    assert 'class="first-page-head with-recipient"' not in html


def test_signature_block(cfg, example):
    html = _render(cfg, example, "leistungsnachweis-august.md")
    assert 'class="signature"' in html
    assert "Regensburg, 31.08.2026" in html


def test_no_signature_block(cfg, example):
    assert 'class="signature"' not in _render(cfg, example, "kickoff-protokoll.md")


def test_color_override(cfg, example):
    cfg.color = "#1a3c6e"
    html = _render(cfg, example, "kickoff-protokoll.md")
    assert "--primary-color: #1a3c6e" in html


def test_logo_fallback_without_logo(cfg, example):
    cfg.letterhead.logo = None
    html = _render(cfg, example, "kickoff-protokoll.md")
    assert "logo-fallback" in html


def test_scalar_fields_are_escaped(cfg, example):
    cfg.letterhead.name = "A & B <GmbH>"
    html = _render(cfg, example, "kickoff-protokoll.md")
    assert "A &amp; B &lt;GmbH&gt;" in html


def test_unknown_theme(cfg):
    with pytest.raises(ConfigError, match="Theme 'nope'"):
        load_theme("nope", cfg.base)


def test_custom_theme_path(cfg, example):
    (example / "own.css").write_text("body { color: red; }")
    assert "color: red" in load_theme("own.css", example)
