import shutil
from pathlib import Path

import pytest

EXAMPLE = Path(__file__).parent.parent / "examples" / "minimal"


@pytest.fixture
def example(tmp_path: Path) -> Path:
    """A writable copy of the minimal example (without generated output)."""
    target = tmp_path / "minimal"
    shutil.copytree(EXAMPLE, target,
                    ignore=shutil.ignore_patterns("pdf", ".build"))
    return target
