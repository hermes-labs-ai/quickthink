#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def latest_file(pattern: str) -> Path | None:
    files = sorted(Path().glob(pattern))
    return files[-1] if files else None


def read_text(path: Path | None) -> str:
    if not path or not path.exists():
        return "Unavailable"
    return path.read_text(encoding="utf-8")


def read_json(path: Path | None) -> dict:
    if not path or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Create release notes tied to benchmark artifacts")
    parser.add_argument("--version", required=True)
    parser.add_argument("--out", default="docs/release/RELEASE_NOTES_DRAFT.md")
    args = parser.parse_args()

    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    latest_report = latest_file("docs/evals/results/report-*.md")
    latest_compat = latest_file("docs/compatibility/snapshots/*.json")
    compat = read_json(latest_compat)

    lines = [
        f"# Release Notes v{args.version}",
        "",
        f"Date: {ts}",
        "",
        "## Summary",
        "- Describe the user-visible improvements in this release.",
        "",
        "## Evidence Links",
        f"- Eval report: `{latest_report}`" if latest_report else "- Eval report: unavailable",
        f"- Compatibility snapshot: `{latest_compat}`" if latest_compat else "- Compatibility snapshot: unavailable",
        "",
        "## Compatibility Snapshot",
    ]

    if compat:
        lines.append(f"- Generated: {compat.get('generated_at', 'unknown')}")
        lines.append(f"- Preset: {compat.get('preset', 'unknown')}")
        lines.append("- Models:")
        for row in compat.get("models", []):
            lines.append(
                "  - {}: status={}, lite_overhead_p50_ms={}".format(
                    row.get("model"), row.get("support_status"), row.get("lite_overhead_p50_ms")
                )
            )
    else:
        lines.append("- No compatibility snapshot found.")

    lines.extend(
        [
            "",
            "## Benchmark Notes",
            "Paste key metrics from the eval report here (win-rate, p50/p95 overhead, failure breakdown).",
            "",
            "## Breaking Changes",
            "- None (or list explicitly).",
            "",
            "## Upgrade Notes",
            "- Mention CLI/API changes and migration steps if any.",
        ]
    )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"status=OK out={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
