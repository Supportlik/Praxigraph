import pytest
import yaml

from praxigraph.config import ConfigError, load_config


def test_loads_example(example):
    cfg = load_config(example / "config.yaml")
    assert cfg.letterhead.name == "Daniel Falkner"
    assert cfg.letterhead.tagline == "IT-Beratung & Systemintegration"
    assert cfg.letterhead.logo.name == "logo.svg"
    assert cfg.letterhead.contact["email"] == "mail@falkner-it.example"
    assert cfg.letterhead.bank["iban"].startswith("DE02")
    assert cfg.theme == "letter"
    assert cfg.lang == "de"
    assert [p.name for p in cfg.documents] == [
        "kickoff-protokoll.md", "leistungsnachweis-august.md",
        "statusbericht-august.md"]
    assert cfg.output.date_prefix is False


def _rewrite(example, mutate):
    path = example / "config.yaml"
    data = yaml.safe_load(path.read_text())
    mutate(data)
    path.write_text(yaml.safe_dump(data, allow_unicode=True))
    return path


def test_missing_file(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "config.yaml")


def test_missing_required_letterhead_field(example):
    path = _rewrite(example, lambda d: d["letterhead"].pop("name"))
    with pytest.raises(ConfigError, match="'name'"):
        load_config(path)


def test_unknown_label(example):
    path = _rewrite(example, lambda d: d.setdefault("labels", {}).update(nope="x"))
    with pytest.raises(ConfigError, match="Unknown label 'nope'"):
        load_config(path)


def test_label_override(example):
    path = _rewrite(example, lambda d: d.setdefault("labels", {}).update(date="Date"))
    assert load_config(path).labels["date"] == "Date"


def test_missing_logo(example):
    path = _rewrite(example, lambda d: d["letterhead"].update(logo="nope.svg"))
    with pytest.raises(ConfigError, match="Logo file not found"):
        load_config(path)


def test_missing_documents_dir(example):
    path = _rewrite(example, lambda d: d.update(documents="nope"))
    with pytest.raises(ConfigError, match="Documents directory"):
        load_config(path)


def test_documents_as_list(example):
    path = _rewrite(example,
                    lambda d: d.update(documents=["documents/kickoff-protokoll.md"]))
    cfg = load_config(path)
    assert [p.name for p in cfg.documents] == ["kickoff-protokoll.md"]
