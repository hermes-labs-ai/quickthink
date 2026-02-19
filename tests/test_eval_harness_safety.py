import importlib.util
import sys
from pathlib import Path


def _load_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, Path(path))
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_append_run_offsets_detect_existing_rows(tmp_path: Path) -> None:
    run_suite = _load_module("scripts/eval_harness/run_suite.py", "run_suite_mod")
    out = tmp_path / "rows.jsonl"
    out.write_text(
        "\n".join(
            [
                '{"model":"qwen2.5:1.5b","mode":"lite","prompt_id":"R001","run_index":1}',
                '{"model":"qwen2.5:1.5b","mode":"lite","prompt_id":"R001","run_index":3}',
                '{"model":"qwen2.5:1.5b","mode":"direct","prompt_id":"R001","run_index":2}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    offsets = run_suite._load_existing_run_offsets(out)
    assert offsets[("qwen2.5:1.5b", "lite", "R001")] == 3
    assert offsets[("qwen2.5:1.5b", "direct", "R001")] == 2


def test_judge_constraint_binary_and_punctuation() -> None:
    judge_suite = _load_module("scripts/eval_harness/judge_suite.py", "judge_suite_mod")

    score_yes, notes_yes = judge_suite.score_constraint_adherence(
        "Output only YES or NO and respond without using punctuation.",
        ["Output is YES or NO only", "Contains no punctuation marks"],
        "YES",
    )
    assert score_yes == 2
    assert any("binary constraint met" in n for n in notes_yes)

    score_bad, notes_bad = judge_suite.score_constraint_adherence(
        "Output only YES or NO and respond without using punctuation.",
        ["Output is YES or NO only", "Contains no punctuation marks"],
        "Maybe.",
    )
    assert score_bad == 0
    assert any("violated" in n for n in notes_bad)
