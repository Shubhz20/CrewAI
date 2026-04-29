"""CLI entry point for the personalized study plan generator.

Usage:
    python main.py --input examples/sample_input.json --output my_plan.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.crew import StudyPlanCrew


def _read_input(path: Path) -> str:
    """Read the input file. Accept either JSON or plain text."""
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        # Re-serialize to ensure clean formatting for the LLM
        return json.dumps(json.loads(raw), indent=2)
    return raw


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        required=True,
        help="Path to a student profile JSON or free-text intake file.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("study_plan.md"),
        help="Where to write the final Markdown plan.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Disable verbose CrewAI logs.",
    )
    args = parser.parse_args(argv)

    load_dotenv()

    if not args.input.exists():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 1

    raw_input = _read_input(args.input)

    crew = StudyPlanCrew(raw_input=raw_input, verbose=not args.quiet)
    result = crew.run()

    # CrewAI returns a CrewOutput; the final task's pydantic model lives on it.
    review = getattr(result, "pydantic", None)
    if review is not None and hasattr(review, "final_plan_markdown"):
        plan_md = review.final_plan_markdown
    else:
        # Fallback: take the raw final string.
        plan_md = str(result)

    args.output.write_text(plan_md, encoding="utf-8")
    print(f"\n[OK] Plan written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
