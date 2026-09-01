"""Command line: `praxigraph build` and `praxigraph validate`."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .builder import build, load_documents
from .config import ConfigError, load_config


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="praxigraph",
        description="Markdown-driven business documents on your own letterhead "
                    "(HTML -> PDF via Chrome).")
    parser.add_argument("--version", action="version",
                        version=f"praxigraph {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    b = sub.add_parser("build", help="generate HTML and PDFs")
    b.add_argument("-c", "--config", default="config.yaml", help="path to the config.yaml")
    b.add_argument("--doc", action="append",
                   help="build only this document slug (repeatable)")
    b.add_argument("--html-only", action="store_true",
                   help="generate HTML only, no Chrome/PDF")
    b.add_argument("--date", default=None,
                   help="override the date prefix of the PDF file names (YYYY-MM-DD)")

    v = sub.add_parser("validate", help="check config and documents")
    v.add_argument("-c", "--config", default="config.yaml", help="path to the config.yaml")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        cfg = load_config(args.config)
        if args.command == "validate":
            documents = load_documents(cfg)
            print(f"OK: configuration and {len(documents)} document(s) are valid.")
            return 0

        results = build(cfg, slugs=args.doc, html_only=args.html_only,
                        datestamp=args.date)
        failed = [r for r in results if not r.ok]
        if failed:
            print(f"Error: {len(failed)} document(s) could not be rendered.",
                  file=sys.stderr)
            return 1
        print("done.")
        return 0
    except (ConfigError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
