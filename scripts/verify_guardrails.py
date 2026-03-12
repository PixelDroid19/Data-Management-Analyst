#!/usr/bin/env python3
"""Minimal verification harness for SDD markdown/contract guardrails."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from dataclasses import dataclass


ROOT = pathlib.Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Rule:
    file_path: str
    description: str
    pattern: str


RULES = [
    Rule(
        "agents/cells-services-flow.agent.md",
        "Requires mandatory factual-claim labeling invariant",
        r"Mandatory output invariant",
    ),
    Rule(
        "agents/cells-services-flow.agent.md",
        "Has pre-output quality gate that blocks delivery",
        r"## Pre-output Quality Gate \(Blocking\)",
    ),
    Rule(
        "agents/cells-services-flow.agent.md",
        "Preserves unresolved gaps as [NOT FOUND]",
        r"## Unresolved-Gap Policy \(Mandatory\)",
    ),
    Rule(
        "agents/sdd-orchestrator.agent.md",
        "Preserves worker evidence labels during synthesis",
        r"Preserve evidence states across the chain: `\[CONFIRMED\]`, `\[INFERRED\]`, and `\[NOT FOUND\]`",
    ),
    Rule(
        "agents/sdd-orchestrator.agent.md",
        "Forbids silent confidence promotion",
        r"Prohibited promotion without evidence",
    ),
    Rule(
        "skills/_shared/output-contract.md",
        "Defines no-unlabeled-facts invariant",
        r"Invariant: every factual statement in the report must be explicitly labeled with one evidence state",
    ),
    Rule(
        "skills/_shared/output-contract.md",
        "Defines unresolved-gap handling",
        r"Unresolved-gap handling:",
    ),
    Rule(
        "skills/_shared/open-spec.md",
        "Defines deterministic evidence order",
        r"### Deterministic evidence order \(mandatory\)",
    ),
    Rule(
        "skills/_shared/open-spec.md",
        "Defines the no-assumption golden rule",
        r"\*\*Do not assume\. Do not infer from names\. Do not close without evidence\.\*\*",
    ),
]


def _read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def run_test() -> int:
    failures: list[str] = []
    for rule in RULES:
        try:
            content = _read_text(rule.file_path)
        except FileNotFoundError as exc:
            failures.append(str(exc))
            continue

        if re.search(rule.pattern, content, flags=re.MULTILINE) is None:
            failures.append(
                f"[{rule.file_path}] {rule.description} -> pattern not found: {rule.pattern}"
            )

    if failures:
        print("Guardrail verification FAILED")
        for index, failure in enumerate(failures, start=1):
            print(f"{index}. {failure}")
        return 1

    print(f"Guardrail verification PASSED ({len(RULES)} checks)")
    return 0


def run_check() -> int:
    test_status = run_test()
    if test_status != 0:
        return test_status

    script_path = ROOT / "scripts/verify_guardrails.py"
    compiled = compile(
        script_path.read_text(encoding="utf-8"), str(script_path), "exec"
    )
    if compiled is None:
        print("Build/check FAILED: could not compile verification harness")
        return 1

    print("Build/check PASSED (harness compiles and guardrails validated)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Minimal executable verification harness for SDD guardrails"
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=("test", "check"),
        default="test",
        help="Command to run: test or check",
    )
    args = parser.parse_args()

    if args.command == "test":
        return run_test()
    return run_check()


if __name__ == "__main__":
    sys.exit(main())
