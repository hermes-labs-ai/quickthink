from pathlib import Path

import pytest

from quickthink.ui_server import PROMPTS_DIR_DEFAULT, REPO_ROOT, RESULTS_DIR_DEFAULT, _resolve_repo_path


def test_resolve_repo_path_allows_eval_dirs() -> None:
    prompt_path = _resolve_repo_path("docs/evals/prompt_set.jsonl", allowed_root=PROMPTS_DIR_DEFAULT)
    result_path = _resolve_repo_path("docs/evals/results/smoke_run_results.jsonl", allowed_root=RESULTS_DIR_DEFAULT)
    assert prompt_path.is_absolute()
    assert result_path.is_absolute()
    assert str(prompt_path).startswith(str(REPO_ROOT))
    assert str(result_path).startswith(str(REPO_ROOT))


def test_resolve_repo_path_blocks_outside_repo() -> None:
    with pytest.raises(ValueError):
        _resolve_repo_path("/etc/hosts", allowed_root=PROMPTS_DIR_DEFAULT)


def test_resolve_repo_path_blocks_wrong_subdir() -> None:
    with pytest.raises(ValueError):
        _resolve_repo_path("README.md", allowed_root=RESULTS_DIR_DEFAULT)

