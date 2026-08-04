from importlib.metadata import version as package_version

from typer.testing import CliRunner

from quickthink.cli import app


def test_version_reports_installed_package_version() -> None:
    result = CliRunner().invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip() == package_version("quickthink")
