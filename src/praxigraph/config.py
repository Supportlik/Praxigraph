"""Load and validate the steering file config.yaml."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


class ConfigError(Exception):
    """Raised for any invalid or missing configuration value."""


#: German defaults; every label can be overridden under `labels:`.
DEFAULT_LABELS = {
    "number": "Nr.",
    "date": "Datum",
    "phone": "Tel.",
    "email": "E-Mail",
    "web": "Web",
    "vat_id": "USt-IdNr.",
    "tax_number": "Steuernr.",
    "bank": "Bank",
    "iban": "IBAN",
    "bic": "BIC",
}

_OPTIONAL_SECTIONS = ("contact", "tax", "bank", "signature")


@dataclass
class Letterhead:
    name: str
    street: str
    zip: str
    city: str
    tagline: str | None = None
    country: str | None = None
    logo: Path | None = None
    contact: dict = field(default_factory=dict)   # phone, email, website
    tax: dict = field(default_factory=dict)       # vat_id, tax_number
    bank: dict = field(default_factory=dict)      # name, iban, bic
    signature: dict = field(default_factory=dict)  # name, place


@dataclass
class OutputConfig:
    html_dir: Path
    pdf_dir: Path
    date_prefix: bool = True


@dataclass
class Config:
    base: Path
    letterhead: Letterhead
    documents: list[Path]
    theme: str = "letter"
    color: str | None = None
    lang: str = "de"
    date_format: str = "%d.%m.%Y"
    labels: dict = field(default_factory=lambda: dict(DEFAULT_LABELS))
    chrome: str | None = None
    output: OutputConfig | None = None


def _require(data: dict, key: str, where: str) -> object:
    if key not in data or data[key] in (None, ""):
        raise ConfigError(f"Missing required field '{key}' in {where}.")
    return data[key]


def _load_letterhead(data: dict, base: Path) -> Letterhead:
    if not isinstance(data, dict):
        raise ConfigError("'letterhead' must be a mapping.")
    head = Letterhead(
        name=str(_require(data, "name", "letterhead")),
        street=str(_require(data, "street", "letterhead")),
        zip=str(_require(data, "zip", "letterhead")),
        city=str(_require(data, "city", "letterhead")),
        tagline=data.get("tagline"),
        country=data.get("country"),
    )
    if data.get("logo"):
        logo = (base / str(data["logo"])).resolve()
        if not logo.exists():
            raise ConfigError(f"Logo file not found: {logo}")
        head.logo = logo
    for section in _OPTIONAL_SECTIONS:
        value = data.get(section) or {}
        if not isinstance(value, dict):
            raise ConfigError(f"'letterhead.{section}' must be a mapping.")
        setattr(head, section, {k: str(v) for k, v in value.items() if v not in (None, "")})
    return head


def _resolve_documents(value: object, base: Path) -> list[Path]:
    """`documents:` is either a directory containing *.md or a list of paths."""
    if value is None:
        value = "documents"
    if isinstance(value, str):
        directory = (base / value).resolve()
        if not directory.is_dir():
            raise ConfigError(f"Documents directory not found: {directory}")
        return sorted(directory.glob("*.md"))
    if isinstance(value, list):
        paths = []
        for item in value:
            path = (base / str(item)).resolve()
            if not path.is_file():
                raise ConfigError(f"Document not found: {path}")
            paths.append(path)
        return paths
    raise ConfigError("'documents' must be a directory name or a list of files.")


def load_config(path: str | Path) -> Config:
    path = Path(path)
    if not path.is_file():
        raise ConfigError(f"Config file not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"{path} must contain a YAML mapping.")

    base = path.parent.resolve()
    letterhead = _load_letterhead(_require(data, "letterhead", str(path)), base)

    labels = dict(DEFAULT_LABELS)
    overrides = data.get("labels") or {}
    if not isinstance(overrides, dict):
        raise ConfigError("'labels' must be a mapping.")
    for key, value in overrides.items():
        if key not in DEFAULT_LABELS:
            raise ConfigError(f"Unknown label '{key}' "
                              f"(known: {', '.join(sorted(DEFAULT_LABELS))})")
        labels[key] = str(value)

    out = data.get("output") or {}
    if not isinstance(out, dict):
        raise ConfigError("'output' must be a mapping.")
    output = OutputConfig(
        html_dir=(base / str(out.get("html_dir", ".build/html"))).resolve(),
        pdf_dir=(base / str(out.get("pdf_dir", "pdf"))).resolve(),
        date_prefix=bool(out.get("date_prefix", True)),
    )

    return Config(
        base=base,
        letterhead=letterhead,
        documents=_resolve_documents(data.get("documents"), base),
        theme=str(data.get("theme", "letter")),
        color=str(data["color"]) if data.get("color") else None,
        lang=str(data.get("lang", "de")),
        date_format=str(data.get("date_format", "%d.%m.%Y")),
        labels=labels,
        chrome=str(data["chrome"]) if data.get("chrome") else None,
        output=output,
    )
