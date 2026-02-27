from typer.testing import CliRunner

from quickthink.cli import app


def test_ask_invalid_lane_policy_rejected() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["ask", "hello", "--lane-policy", "bad_policy"],
    )
    assert result.exit_code != 0
    assert "lane-policy must be 'default' or 'strict_safe'" in result.stdout
