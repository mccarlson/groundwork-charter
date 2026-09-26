#!/usr/bin/env python3
"""Pull request checks for the charter repository.

Run by .github/workflows/charter-checks.yml. The pull request is read from
environment variables (HEAD_REF, PR_TITLE, PR_BODY) so titles and bodies are
never interpolated into a shell. Without HEAD_REF, only the repository checks
run, which is how to use it locally:

    python .github/scripts/charter_checks.py

Every failure is reported, not just the first. Exit 1 if any check fails.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]

BRANCH_RE = re.compile(r"^(spec|adr|charter)/([0-9]{3,})-[a-z0-9]+(-[a-z0-9]+)*$")

# Must stay project-agnostic (process/workflow.md, vocabulary rule).
VOCABULARY_PATHS = ["process", ".specify/extensions/issues", ".claude/hooks"]
DENYLIST = ROOT / "product" / "vocabulary-denylist.txt"

# Charter documents whose relative links must resolve.
LINK_PATHS = ["README.md", "CLAUDE.md", "product", "process", "specs", "adr"]
LINK_RE = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)

Failure = tuple[str | None, int | None, str]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def check_pull_request(head_ref: str, title: str, body: str) -> list[Failure]:
    match = BRANCH_RE.fullmatch(head_ref)
    if not match:
        return [(None, None,
                 f"branch '{head_ref}' must be <spec|adr|charter>/<NNN>-<slug>, where NNN is a "
                 f"charter issue number and slug is kebab-case (process/workflow.md §4)")]

    failures: list[Failure] = []
    prefix, number = match.group(1), match.group(2)

    expected = f"{prefix}({number}): "
    if not title.startswith(expected) or not title[len(expected):].strip():
        failures.append((None, None,
                         f"PR title must be '{expected}<summary>', matching the branch; "
                         f"got '{title}' (process/workflow.md §7)"))

    issue = int(number)
    if not re.search(rf"#{issue}(?![0-9])", body or ""):
        failures.append((None, None,
                         f"PR body must reference issue #{issue}, e.g. 'Closes #{issue}' "
                         f"(process/workflow.md §3)"))
    return failures


def load_denylist() -> list[str]:
    terms = []
    for line in DENYLIST.read_text(encoding="utf-8").splitlines():
        term = line.split("#", 1)[0].strip().lower()
        if term:
            terms.append(term)
    return terms


def text_files(base: Path):
    candidates = [base] if base.is_file() else sorted(base.rglob("*")) if base.is_dir() else []
    for path in candidates:
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        try:
            yield path, path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue


def check_vocabulary() -> list[Failure]:
    if not DENYLIST.exists():
        return [(None, None, f"{rel(DENYLIST)} is missing; the vocabulary rule has nothing to check against")]

    terms = load_denylist()
    failures: list[Failure] = []
    for base in VOCABULARY_PATHS:
        for path, text in text_files(ROOT / base):
            for lineno, line in enumerate(text.splitlines(), 1):
                lowered = line.lower()
                for term in terms:
                    if term in lowered:
                        failures.append((rel(path), lineno,
                                         f"'{term}' is project vocabulary; files under {base}/ must stay "
                                         f"project-agnostic (process/workflow.md, vocabulary rule)"))
    return failures


def check_links() -> list[Failure]:
    failures: list[Failure] = []
    for base in LINK_PATHS:
        for path, text in text_files(ROOT / base):
            if path.suffix != ".md":
                continue
            in_fence = False
            for lineno, line in enumerate(text.splitlines(), 1):
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                for target in LINK_RE.findall(line):
                    if SCHEME_RE.match(target) or target.startswith("#"):
                        continue
                    target_path = unquote(target.split("#", 1)[0])
                    if not target_path:
                        continue
                    resolved = (ROOT / target_path.lstrip("/")) if target_path.startswith("/") \
                        else (path.parent / target_path)
                    if not resolved.exists():
                        failures.append((rel(path), lineno, f"link target '{target}' does not exist"))
    return failures


def report(name: str, failures: list[Failure]) -> None:
    if not failures:
        print(f"ok    {name}")
        return
    print(f"FAIL  {name}")
    in_actions = os.environ.get("GITHUB_ACTIONS") == "true"
    for file, line, message in failures:
        location = f"{file}:{line}: " if file else ""
        print(f"      {location}{message}")
        if in_actions:
            where = f" file={file},line={line}" if file else ""
            print(f"::error{where}::{message}")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    results: list[tuple[str, list[Failure]]] = []

    head_ref = os.environ.get("HEAD_REF", "")
    if head_ref:
        results.append(("pull request: branch, title, issue reference",
                        check_pull_request(head_ref, os.environ.get("PR_TITLE", ""),
                                           os.environ.get("PR_BODY", ""))))
    else:
        print("skip  pull request checks (HEAD_REF not set)")

    results.append(("vocabulary rule", check_vocabulary()))
    results.append(("relative links", check_links()))

    for name, failures in results:
        report(name, failures)
    return 1 if any(failures for _, failures in results) else 0


if __name__ == "__main__":
    sys.exit(main())
