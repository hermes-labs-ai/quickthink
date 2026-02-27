from __future__ import annotations

import json
import subprocess
from pathlib import Path


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")


def test_gate_decision_marks_all_tie_lane_inconclusive(tmp_path: Path) -> None:
    runs_path = tmp_path / "runs.jsonl"
    judged_path = tmp_path / "judged.jsonl"
    out_path = tmp_path / "gate.json"

    # 2 prompt ids x 2 runs = 4 paired rows, all tied scores/latencies.
    run_rows: list[dict] = []
    judged_rows: list[dict] = []
    for prompt_id in ("E001", "E002"):
        for run_index in (1, 2):
            for mode in ("direct", "shared.concise_core"):
                run_rows.append(
                    {
                        "model": "qwen2.5:1.5b",
                        "mode": mode,
                        "group": "instruction_constraints",
                        "prompt_id": prompt_id,
                        "run_index": run_index,
                        "total_latency_ms": 100.0,
                    }
                )
                judged_rows.append(
                    {
                        "model": "qwen2.5:1.5b",
                        "mode": mode,
                        "group": "instruction_constraints",
                        "prompt_id": prompt_id,
                        "run_index": run_index,
                        "total_score": 6.0,
                    }
                )

    _write_jsonl(runs_path, run_rows)
    _write_jsonl(judged_path, judged_rows)

    cmd = [
        ".venv/bin/python",
        "scripts/eval_harness/make_gate_decision.py",
        "--runs-jsonl",
        str(runs_path),
        "--judged-jsonl",
        str(judged_path),
        "--out",
        str(out_path),
        "--backend-stable",
        "--min-pairs",
        "4",
    ]
    subprocess.run(cmd, check=True)

    payload = json.loads(out_path.read_text(encoding="utf-8"))
    lane = payload["lanes"][0]
    assert lane["decision"] == "INCONCLUSIVE"
    assert "no_non_tie_pairs" in lane["decision_reason"]
