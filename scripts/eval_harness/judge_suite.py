#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

JSON_ONLY_HINT = re.compile(r"\bjson\b", re.IGNORECASE)
YAML_HINT = re.compile(r"\byaml\b", re.IGNORECASE)
XML_HINT = re.compile(r"\bxml\b", re.IGNORECASE)
CSV_HINT = re.compile(r"\bcsv\b", re.IGNORECASE)
MARKDOWN_TABLE_HINT = re.compile(r"markdown table", re.IGNORECASE)
WORD_EXACT_HINT = re.compile(r"exactly\s+(\d+)\s+words", re.IGNORECASE)
UNDER_WORD_HINT = re.compile(r"under\s+(\d+)\s+words", re.IGNORECASE)
LINE_EXACT_HINT = re.compile(r"exactly\s+(\d+)\s+lines", re.IGNORECASE)


@dataclass
class PromptCase:
    prompt_id: str
    group: str
    prompt: str
    expected_rubric: str
    pass_fail_checklist: list[str]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_prompt_cases(path: Path) -> dict[str, PromptCase]:
    out: dict[str, PromptCase] = {}
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            out[str(item["prompt_id"])] = PromptCase(
                prompt_id=str(item["prompt_id"]),
                group=str(item["group"]),
                prompt=str(item["prompt"]),
                expected_rubric=str(item["expected_rubric"]),
                pass_fail_checklist=list(item["pass_fail_checklist"]),
            )
    return out


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def contains_json(text: str) -> bool:
    text = text.strip()
    if not text:
        return False
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False


def contains_yaml_like(text: str) -> bool:
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    if not lines:
        return False
    # lightweight YAML signal, not strict parser requirement
    return any(":" in ln for ln in lines) and not any(ln.lstrip().startswith("{") for ln in lines)


def contains_xml_like(text: str) -> bool:
    t = text.strip()
    return t.startswith("<") and t.endswith(">") and "</" in t


def contains_markdown_table(text: str) -> bool:
    lines = [ln for ln in text.splitlines() if "|" in ln]
    return len(lines) >= 2


def line_count(text: str) -> int:
    return len([ln for ln in text.strip().splitlines() if ln.strip()])


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text.strip()))


def score_format_validity(prompt: str, answer: str) -> tuple[int, list[str]]:
    notes: list[str] = []
    ok = True

    if JSON_ONLY_HINT.search(prompt):
        if not contains_json(answer):
            ok = False
            notes.append("requested JSON, output not valid JSON")
    if YAML_HINT.search(prompt):
        if not contains_yaml_like(answer):
            ok = False
            notes.append("requested YAML, output not YAML-like")
    if XML_HINT.search(prompt):
        if not contains_xml_like(answer):
            ok = False
            notes.append("requested XML, output not XML-like")
    if CSV_HINT.search(prompt):
        if "," not in answer:
            ok = False
            notes.append("requested CSV, missing commas")
    if MARKDOWN_TABLE_HINT.search(prompt):
        if not contains_markdown_table(answer):
            ok = False
            notes.append("requested markdown table, table format missing")

    if not any((JSON_ONLY_HINT.search(prompt), YAML_HINT.search(prompt), XML_HINT.search(prompt), CSV_HINT.search(prompt), MARKDOWN_TABLE_HINT.search(prompt))):
        return (2, ["no strict format requested"])

    return (2 if ok else 0, notes or ["format requirement satisfied"])


def score_verbosity(prompt: str, answer: str) -> tuple[int, list[str]]:
    notes: list[str] = []
    wc = word_count(answer)

    match = WORD_EXACT_HINT.search(prompt)
    if match:
        target = int(match.group(1))
        if wc == target:
            return (2, [f"exact word count matched: {target}"])
        if abs(wc - target) <= 2:
            return (1, [f"near target words: {wc}/{target}"])
        return (0, [f"word count mismatch: {wc}/{target}"])

    match = UNDER_WORD_HINT.search(prompt)
    if match:
        cap = int(match.group(1))
        if wc < cap:
            return (2, [f"under word cap: {wc}<{cap}"])
        return (0, [f"word cap exceeded: {wc}>={cap}"])

    match = LINE_EXACT_HINT.search(prompt)
    if match:
        target_lines = int(match.group(1))
        lines = line_count(answer)
        if lines == target_lines:
            return (2, [f"exact line count matched: {target_lines}"])
        if abs(lines - target_lines) == 1:
            return (1, [f"near line target: {lines}/{target_lines}"])
        return (0, [f"line count mismatch: {lines}/{target_lines}"])

    if wc <= 120:
        return (2, ["default concise length acceptable"])
    if wc <= 200:
        return (1, ["slightly verbose"])
    return (0, ["overly verbose"])


def score_constraint_adherence(prompt: str, checklist: list[str], answer: str) -> tuple[int, list[str]]:
    notes: list[str] = []
    lower_prompt = prompt.lower()
    lower_answer = answer.lower().strip()
    checks = 0
    passes = 0

    # Hard, directly testable constraints first.
    if ("yes or no only" in lower_prompt) or ("only yes or no" in lower_prompt):
        checks += 1
        if lower_answer in {"yes", "no"}:
            passes += 1
            notes.append("binary constraint met")
        else:
            notes.append("binary constraint violated")

    if "lowercase only" in lower_prompt:
        checks += 1
        if answer == answer.lower():
            passes += 1
            notes.append("lowercase constraint met")
        else:
            notes.append("lowercase constraint violated")

    if "without using punctuation" in lower_prompt:
        checks += 1
        if not re.search(r"[^\w\s]", answer):
            passes += 1
            notes.append("punctuation constraint met")
        else:
            notes.append("punctuation constraint violated")

    if "json only" in lower_prompt:
        checks += 1
        if contains_json(answer):
            passes += 1
            notes.append("json-only constraint met")
        else:
            notes.append("json-only constraint violated")

    # Lightweight checklist semantic signal (conservative cap).
    checklist_hits = 0
    for item in checklist:
        item_l = item.lower()
        tokens = [t for t in re.findall(r"[a-z0-9_]+", item_l) if len(t) >= 5]
        if tokens and any(tok in lower_answer for tok in tokens):
            checklist_hits += 1
    if checklist:
        ratio = checklist_hits / len(checklist)
        notes.append(f"checklist signal: {checklist_hits}/{len(checklist)}")
        if ratio >= 0.7:
            passes += 1
            checks += 1

    if checks == 0:
        return (1, ["no directly testable constraints; neutral score"])
    ratio = passes / checks
    if ratio >= 0.85:
        return (2, notes)
    if ratio >= 0.5:
        return (1, notes)
    return (0, notes)


def score_correctness(case: PromptCase, answer: str) -> tuple[int, list[str]]:
    # For lightweight automation we infer by group + simple deterministic checks.
    lower = answer.lower()
    if case.group == "reasoning":
        # deterministic anchor map for selected arithmetic prompts
        anchors = {
            "R001": "9",
            "R002": "9",
            "R003": "0.313",
            "R005": "48",
            "R009": "42",
            "R013": "75.4",
            "R015": "85.0",
            "R017": "56.25",
            "R025": "60%",
            "R030": "1080",
        }
        val = anchors.get(case.prompt_id)
        if val:
            if val in lower:
                return (2, [f"anchor matched {val}"])
            return (0, [f"anchor not found {val}"])
        # non-arithmetic reasoning fallback: conservative by default
        if len(lower.strip()) == 0:
            return (0, ["empty answer"])
        if any(x in lower for x in ("it depends", "cannot", "not guaranteed", "tradeoff", "because")):
            return (1, ["reasoning signal present but not verifiable"])
        return (1, ["non-empty response but correctness not directly verifiable"])

    if case.group == "structured_output":
        fmt_score, fmt_notes = score_format_validity(case.prompt, answer)
        return (fmt_score, ["structured-output uses format score"] + fmt_notes)

    if case.group == "instruction_constraints":
        con_score, con_notes = score_constraint_adherence(case.prompt, case.pass_fail_checklist, answer)
        return (con_score, ["instruction-following uses constraint score"] + con_notes)

    if case.group == "multi_turn_continuity":
        if "context:" in case.prompt.lower() and len(answer.strip()) > 0:
            if any(k in lower for k in ("same", "keep", "continue", "maintain", "policy", "template", "json")):
                return (2, ["continuity language preserved"])
            return (1, ["answered but weak continuity signal"])

    return (1, ["default correctness fallback"])


def judge_with_rules(case: PromptCase, answer: str) -> dict[str, Any]:
    correctness, c_notes = score_correctness(case, answer)
    constraints, k_notes = score_constraint_adherence(case.prompt, case.pass_fail_checklist, answer)
    fmt, f_notes = score_format_validity(case.prompt, answer)
    verbosity, v_notes = score_verbosity(case.prompt, answer)

    total = correctness + constraints + fmt + verbosity
    passed = total >= 6 and min(correctness, constraints, fmt, verbosity) > 0

    return {
        "scores": {
            "correctness": correctness,
            "constraint_adherence": constraints,
            "format_validity": fmt,
            "verbosity_control": verbosity,
        },
        "total_score": total,
        "passed": passed,
        "judge_backend": "rule",
        "judge_confidence": 0.55,
        "judge_notes": {
            "correctness": c_notes,
            "constraint_adherence": k_notes,
            "format_validity": f_notes,
            "verbosity_control": v_notes,
        },
    }


def judge_with_ollama(case: PromptCase, answer: str, model: str, base_url: str) -> dict[str, Any]:
    prompt = (
        "You are a strict eval judge. Score the response on 4 dimensions from 0-2: "
        "correctness, constraint_adherence, format_validity, verbosity_control. "
        "Return JSON only with keys: scores, total_score, passed, judge_backend, judge_confidence, judge_notes.\n"
        "Scoring guidance:\n"
        "- correctness: task solved materially correctly\n"
        "- constraint_adherence: instruction/checklist compliance\n"
        "- format_validity: parseable requested format\n"
        "- verbosity_control: length/style compliance\n"
        "pass threshold: total>=6 and no zero dimension\n\n"
        f"Prompt ID: {case.prompt_id}\n"
        f"Prompt: {case.prompt}\n"
        f"Expected rubric: {case.expected_rubric}\n"
        f"Checklist: {case.pass_fail_checklist}\n"
        f"Model answer: {answer}\n"
    )
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0, "top_p": 0.7, "num_predict": 300},
    }
    with httpx.Client(timeout=90.0) as client:
        response = client.post(f"{base_url.rstrip('/')}/api/generate", json=payload)
        response.raise_for_status()
        raw = response.json().get("response", "").strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "scores": {
                "correctness": 1,
                "constraint_adherence": 1,
                "format_validity": 1,
                "verbosity_control": 1,
            },
            "total_score": 4,
            "passed": False,
            "judge_backend": "ollama_fallback",
            "judge_confidence": 0.2,
            "judge_notes": {"parse_error": ["judge output was not valid JSON"]},
        }

    data.setdefault("judge_backend", "ollama")
    data.setdefault("judge_confidence", 0.7)
    return data


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Judge quickthink eval run outputs")
    p.add_argument("--prompt-set", default="docs/evals/prompt_set.jsonl")
    p.add_argument("--results", default="docs/evals/results/run_results.jsonl")
    p.add_argument("--out", default="docs/evals/results/judged_results.jsonl")
    p.add_argument("--backend", choices=["rule", "ollama"], default="rule")
    p.add_argument("--judge-model", default="qwen2.5:1.5b")
    p.add_argument("--ollama-url", default="http://localhost:11434")
    p.add_argument("--limit", type=int, default=0)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    prompt_cases = load_prompt_cases(Path(args.prompt_set))
    results = load_jsonl(Path(args.results))
    if args.limit > 0:
        results = results[: args.limit]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as fh:
        for idx, row in enumerate(results, 1):
            prompt_id = str(row.get("prompt_id", ""))
            case = prompt_cases.get(prompt_id)
            if not case:
                continue
            answer = str(row.get("answer", ""))
            if args.backend == "ollama":
                judged = judge_with_ollama(case=case, answer=answer, model=args.judge_model, base_url=args.ollama_url)
            else:
                judged = judge_with_rules(case=case, answer=answer)

            out_row = {
                "timestamp": now_iso(),
                "model": row.get("model"),
                "mode": row.get("mode"),
                "prompt_id": prompt_id,
                "group": row.get("group"),
                "run_index": row.get("run_index"),
                "answer": answer,
                "scores": judged.get("scores", {}),
                "total_score": judged.get("total_score", 0),
                "passed": judged.get("passed", False),
                "judge_backend": judged.get("judge_backend", args.backend),
                "judge_confidence": judged.get("judge_confidence", 0.5),
                "judge_notes": judged.get("judge_notes", {}),
            }
            fh.write(json.dumps(out_row, ensure_ascii=True) + "\n")
            if idx % 50 == 0 or idx == len(results):
                print(f"judged {idx}/{len(results)}")

    print(f"wrote judged results: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
