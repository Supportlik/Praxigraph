from praxigraph.cli import main


def test_validate(example, capsys):
    assert main(["validate", "-c", str(example / "config.yaml")]) == 0
    assert "3 document(s)" in capsys.readouterr().out


def test_build_html_only(example):
    assert main(["build", "--html-only", "-c", str(example / "config.yaml")]) == 0
    assert (example / ".build" / "html" / "statusbericht-august.html").exists()


def test_error_exit_code(tmp_path, capsys):
    assert main(["validate", "-c", str(tmp_path / "missing.yaml")]) == 1
    assert "Error:" in capsys.readouterr().err


def test_version(capsys):
    try:
        main(["--version"])
    except SystemExit as exc:
        assert exc.code == 0
    assert "praxigraph" in capsys.readouterr().out
