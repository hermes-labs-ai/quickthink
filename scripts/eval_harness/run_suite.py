#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from quickthink import QuickThinkConfig, QuickThinkEngine

ALLOWED_MODES = ("direct", "lite", "two_pass", "direct_think")


@dataclass
class PromptCase:
    prompt_id: str
    group: str
    prompt: str
    expected_rubric: str
    pass_fail_checklist: list[str]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _acquire_lock(lock_path: Path) -> None:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise SystemExit(
            f"lock exists: {lock_path}. Another run may be active; use a different --out path or remove stale lock."
        ) from exc
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"pid": os.getpid(), "timestamp": now_iso()}) + "\n")


def _release_lock(lock_path: Path) -> None:
    try:
        lock_path.unlink()
    except FileNotFoundError:
        return


def load_prompt_set(path: Path, limit: int | None = None) -> list[PromptCase]:
    cases: list[PromptCase] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            cases.append(
                PromptCase(
                    prompt_id=str(item["prompt_id"]),
                    group=str(item["group"]),
                    prompt=str(item["prompt"]),
                    expected_rubric=str(item["expected_rubric"]),
                    pass_fail_checklist=list(item["pass_fail_checklist"]),
                )
            )
            if limit and len(cases) >= limit:
                break
    return cases


def _load_existing_run_offsets(path: Path) -> dict[tuple[str, str, str], int]:
    offsets: dict[tuple[str, str, str], int] = {}
    if not path.exists():
        return offsets
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = (str(row.get("model", "")), str(row.get("mode", "")), str(row.get("prompt_id", "")))
            run_index = int(row.get("run_index", 0) or 0)
            if run_index > offsets.get(key, 0):
                offsets[key] = run_index
    return offsets


def git_sha() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        return out
    except Exception:
        return "unknown"


def model_supports_thinking(model: str) -> bool:
    model_l = model.lower()
    return model_l.startswith(("qwen3", "deepseek-r1", "deepseek-v3", "gpt-oss"))


def make_config(model: str, ollama_url: str, mode: str, continuity_hint: str | None) -> QuickThinkConfig:
    cfg = QuickThinkConfig.with_model_profile(model=model, ollama_url=ollama_url)
    thinking_capable = model_supports_thinking(model)
    if thinking_capable:
        # Default policy: explicitly disable thinking unless mode requests it.
        cfg.think = False

    if mode == "direct":
        cfg.mode = "lite"
        cfg.bypass_short_prompts = True
        cfg.adaptive_routing = False
        cfg.bypass_char_threshold = 100_000
    elif mode == "direct_think":
        cfg.mode = "lite"
        cfg.bypass_short_prompts = True
        cfg.adaptive_routing = False
        cfg.bypass_char_threshold = 100_000
        cfg.think = True if thinking_capable else None
    else:
        cfg.mode = mode
    cfg.continuity_hint = continuity_hint
    return cfg


def run_case(engine: QuickThinkEngine, mode: str, case: PromptCase, run_index: int) -> dict[str, Any]:
    result = engine.run(case.prompt)
    return {
        "timestamp": now_iso(),
        "model": engine.config.model,
        "mode": mode,
        "prompt_id": case.prompt_id,
        "group": case.group,
        "run_index": run_index,
        "answer": result.answer,
        "plan": result.plan,
        "plan_repaired": result.plan_repaired,
        "bypassed": result.bypassed,
        "route_score": result.route_score,
        "selected_plan_budget": result.selected_plan_budget,
        "plan_latency_ms": round(float(result.plan_latency_ms), 2),
        "answer_latency_ms": round(float(result.answer_latency_ms), 2),
        "total_latency_ms": round(float(result.total_latency_ms), 2),
        "token_usage_prompt": None,
        "token_usage_completion": None,
    }


def write_manifest(
    out_manifest: Path,
    prompt_set_path: Path,
    models: list[str],
    modes: list[str],
    runs: int,
    ollama_url: str,
    continuity_hint: str | None,
    prompt_count: int,
) -> None:
    payload = {
        "timestamp": now_iso(),
        "git_sha": git_sha(),
        "dataset_path": str(prompt_set_path),
        "dataset_sha256": file_sha256(prompt_set_path),
        "models": models,
        "modes": modes,
        "runs": runs,
        "ollama_url": ollama_url,
        "continuity_hint": continuity_hint,
        "prompt_count": prompt_count,
    }
    out_manifest.parent.mkdir(parents=True, exist_ok=True)
    out_manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run quickthink A/B/C eval suite")
    p.add_argument(
        "--prompt-set",
        default="docs/evals/prompt_set.jsonl",
        help="Path to JSONL prompt set",
    )
    p.add_argument(
        "--out",
        default="docs/evals/results/run_results.jsonl",
        help="Path for JSONL run output",
    )
    p.add_argument(
        "--manifest-out",
        default="docs/evals/results/run_manifest.json",
        help="Path for reproducibility manifest",
    )
    p.add_argument(
        "--models",
        nargs="*",
        default=["qwen2.5:1.5b", "mistral:7b", "gemma3:27b"],
    )
    p.add_argument("--modes", nargs="*", default=list(ALLOWED_MODES))
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--ollama-url", default="http://localhost:11434")
    p.add_argument("--continuity-hint", default=None)
    p.add_argument("--limit", type=int, default=0, help="Optional prompt limit for smoke tests")
    p.add_argument("--append", action="store_true", help="Append to output file instead of overwrite")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    prompt_set_path = Path(args.prompt_set)
    out_path = Path(args.out)
    manifest_path = Path(args.manifest_out)

    if not prompt_set_path.exists():
        raise SystemExit(f"prompt set not found: {prompt_set_path}")
    if args.runs < 1:
        raise SystemExit("--runs must be >= 1")

    for mode in args.modes:
        if mode not in ALLOWED_MODES:
            raise SystemExit(f"invalid mode '{mode}', expected one of {ALLOWED_MODES}")

    limit = args.limit if args.limit > 0 else None
    cases = load_prompt_set(prompt_set_path, limit=limit)
    if not cases:
        raise SystemExit("no prompts loaded")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_mode = "a" if args.append else "w"
    run_offsets = _load_existing_run_offsets(out_path) if args.append else {}
    lock_path = Path(f"{out_path}.lock")
    _acquire_lock(lock_path)

    try:
        engines: dict[tuple[str, str], QuickThinkEngine] = {}
        for model in args.models:
            for mode in args.modes:
                cfg = make_config(
                    model=model,
                    ollama_url=args.ollama_url,
                    mode=mode,
                    continuity_hint=args.continuity_hint,
                )
                engines[(model, mode)] = QuickThinkEngine(cfg)

        total = len(args.models) * len(args.modes) * len(cases) * args.runs
        done = 0
        with out_path.open(write_mode, encoding="utf-8") as fh:
            for model in args.models:
                for mode in args.modes:
                    engine = engines[(model, mode)]
                    for case in cases:
                        run_offset = run_offsets.get((model, mode, case.prompt_id), 0)
                        for run_index in range(1, args.runs + 1):
                            row = run_case(
                                engine=engine,
                                mode=mode,
                                case=case,
                                run_index=run_offset + run_index,
                            )
                            fh.write(json.dumps(row, ensure_ascii=True) + "\n")
                            done += 1
                            if done % 25 == 0 or done == total:
                                print(f"progress {done}/{total}")

        write_manifest(
            out_manifest=manifest_path,
            prompt_set_path=prompt_set_path,
            models=list(args.models),
            modes=list(args.modes),
            runs=int(args.runs),
            ollama_url=str(args.ollama_url),
            continuity_hint=args.continuity_hint,
            prompt_count=len(cases),
        )
        print(f"wrote results: {out_path}")
        print(f"wrote manifest: {manifest_path}")
        return 0
    finally:
        _release_lock(lock_path)


if __name__ == "__main__":
    raise SystemExit(main())
