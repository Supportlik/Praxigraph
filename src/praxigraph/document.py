"""Load a Markdown document with YAML front matter."""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .config import ConfigError

_FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass
class Document:
    path: Path
    slug: str
    doc_type: str          # e.g. "Protokoll", "Bericht", "Bescheinigung"
    title: str
    date: dt.date
    body_md: str
    number: str | None = None
    recipient: str | None = None
    meta: list[dict] = field(default_factory=list)  # extra {label, value} rows
    signature: bool = False
    lang: str | None = None


def _parse_date(value: object, path: Path) -> dt.date:
    """Front matter dates: a YAML date, or an ISO string YYYY-MM-DD."""
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value.strip())
        except ValueError:
            pass
    raise ConfigError(f"{path}: 'date' must be a date (YYYY-MM-DD), got {value!r}.")


def _parse_meta(value: object, path: Path) -> list[dict]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ConfigError(f"{path}: 'meta' must be a list of {{label, value}} entries.")
    meta = []
    for entry in value:
        if not isinstance(entry, dict) or "label" not in entry or "value" not in entry:
            raise ConfigError(f"{path}: every 'meta' entry needs 'label' and 'value'.")
        meta.append({"label": str(entry["label"]), "value": str(entry["value"])})
    return meta


def load_document(path: str | Path) -> Document:
    path = Path(path)
    if not path.is_file():
        raise ConfigError(f"Document not found: {path}")
    text = path.read_text(encoding="utf-8")
    match = _FRONT_MATTER.match(text)
    if not match:
        raise ConfigError(f"{path}: missing YAML front matter (--- block at the top).")
    try:
        front = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path}: invalid YAML front matter: {exc}") from exc
    if not isinstance(front, dict):
        raise ConfigError(f"{path}: front matter must be a YAML mapping.")

    for key in ("type", "title", "date"):
        if key not in front or front[key] in (None, ""):
            raise ConfigError(f"{path}: missing required front matter field '{key}'.")

    recipient = front.get("recipient")
    return Document(
        path=path,
        slug=str(front.get("slug") or path.stem),
        doc_type=str(front["type"]),
        title=str(front["title"]),
        date=_parse_date(front["date"], path),
        body_md=text[match.end():],
        number=str(front["number"]) if front.get("number") not in (None, "") else None,
        recipient=str(recipient).rstrip() if recipient not in (None, "") else None,
        meta=_parse_meta(front.get("meta"), path),
        signature=bool(front.get("signature", False)),
        lang=str(front["lang"]) if front.get("lang") else None,
    )
