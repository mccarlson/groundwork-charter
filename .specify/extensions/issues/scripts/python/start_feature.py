#!/usr/bin/env python3
"""Start a feature from an assigned GitHub issue.

Refuses unless all of these hold:
  - the working tree is clean
  - the base branch is in sync with origin (fast-forwarded here when that is safe)
  - the issue exists, is open, carries the required label, and is assigned to
    exactly one person, who is the current GitHub user
  - no spec directory or branch already uses the issue number

Then creates <branch_prefix>/<NNN>-<slug> from the base branch and prints the
spec directory the feature must use, so the branch and the directory always
carry the same number.

Usage:
  start_feature.py --issue 42 --short-name job-capture [--json]

Exit codes: 0 success, 2 refused (message explains why).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+){0,3}$")
DEFAULTS = {"branch_prefix": "spec", "required_label": "type:feature", "base_branch": "main"}


class Refusal(Exception):
    pass


def run(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if check and proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise Refusal(f"`{' '.join(args)}` failed: {detail}")
    return proc


def git(root: Path, *args: str, check: bool = True) -> str:
    return run(["git", *args], root, check).stdout.strip()


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".specify").is_dir():
            return candidate
    raise Refusal("no .specify directory found; run from inside a Spec Kit project")


def read_config(root: Path) -> dict[str, str]:
    config = dict(DEFAULTS)
    path = root / ".specify" / "extensions" / "issues" / "issues-config.yml"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if ":" not in line:
                continue
            key, value = (part.strip() for part in line.split(":", 1))
            if key in config and value:
                config[key] = value.strip("\"'")
    return config


def github_repo(root: Path) -> str:
    url = git(root, "remote", "get-url", "origin")
    match = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if not match:
        raise Refusal(f"origin is not a GitHub repository: {url}")
    return f"{match.group(1)}/{match.group(2)}"


def sync_base(root: Path, base: str) -> str:
    """Fetch origin and bring the local base branch up to date. Returns a summary."""
    git(root, "fetch", "--prune", "origin")
    if not git(root, "rev-parse", "--verify", "--quiet", f"refs/remotes/origin/{base}", check=False):
        raise Refusal(f"origin/{base} does not exist yet; the repository needs its initial commit")
    if not git(root, "rev-parse", "--verify", "--quiet", f"refs/heads/{base}", check=False):
        raise Refusal(f"local branch '{base}' does not exist; check it out from origin first")

    ahead = int(git(root, "rev-list", "--count", f"origin/{base}..{base}"))
    behind = int(git(root, "rev-list", "--count", f"{base}..origin/{base}"))
    if ahead:
        raise Refusal(
            f"local {base} has {ahead} commit(s) that are not on origin/{base}. "
            f"Changes reach {base} only through pull requests: move those commits "
            f"to a branch, then reset {base} to origin/{base}"
        )
    if not behind:
        return f"{base} already matches origin/{base}"

    current = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    if current == base:
        git(root, "merge", "--ff-only", f"origin/{base}")
    else:
        git(root, "fetch", "origin", f"{base}:{base}")
    return f"fast-forwarded {base} by {behind} commit(s) from origin/{base}"


def verify_issue(root: Path, repo: str, number: int, required_label: str) -> dict:
    proc = run(
        ["gh", "issue", "view", str(number), "-R", repo,
         "--json", "number,state,title,url,assignees,labels"],
        root, check=False,
    )
    if proc.returncode != 0:
        raise Refusal(
            f"issue #{number} was not found in {repo}. Features start from an existing "
            f"issue (pull request numbers are not accepted): {proc.stderr.strip()}"
        )
    issue = json.loads(proc.stdout)

    if issue["state"] != "OPEN":
        raise Refusal(f"issue #{number} is {issue['state'].lower()}; only open issues can start a feature")

    labels = {label["name"] for label in issue["labels"]}
    if required_label and required_label not in labels:
        raise Refusal(f"issue #{number} is missing the '{required_label}' label")

    assignees = [a["login"] for a in issue["assignees"]]
    if len(assignees) != 1:
        who = ", ".join(assignees) if assignees else "nobody"
        raise Refusal(
            f"issue #{number} must have exactly one assignee (its owner); it has {who}. "
            f"Assign it on GitHub before starting"
        )

    me = run(["gh", "api", "user", "--jq", ".login"], root).stdout.strip()
    if assignees[0].lower() != me.lower():
        raise Refusal(
            f"issue #{number} is owned by {assignees[0]}, not {me}. Only the owner starts "
            f"work on an issue; to hand it off, reassign it on GitHub and comment why"
        )
    return issue


def verify_number_unused(root: Path, feature_num: str) -> None:
    existing = sorted((root / "specs").glob(f"{feature_num}-*"))
    if existing:
        raise Refusal(f"spec directory already exists for {feature_num}: {existing[0].relative_to(root).as_posix()}")

    refs = git(root, "for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes")
    pattern = re.compile(rf"(^|/){feature_num}-")
    taken = [ref for ref in refs.splitlines() if pattern.search(ref)]
    if taken:
        raise Refusal(f"a branch already uses {feature_num}: {taken[0]}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Start a feature from an assigned GitHub issue")
    parser.add_argument("--issue", required=True, help="issue number, e.g. 42 or #42")
    parser.add_argument("--short-name", required=True, help="kebab-case slug, at most 4 words")
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    args = parser.parse_args(argv)

    try:
        issue_arg = args.issue.lstrip("#")
        if not issue_arg.isdigit() or int(issue_arg) == 0:
            raise Refusal(f"--issue must be a positive issue number, got '{args.issue}'")
        number = int(issue_arg)

        slug = args.short_name.strip().lower()
        if not SLUG_RE.fullmatch(slug):
            raise Refusal(f"short name '{args.short_name}' must be kebab-case, 1-4 words (e.g. job-capture)")

        root = find_root(Path.cwd())
        config = read_config(root)
        base = config["base_branch"]

        if git(root, "status", "--porcelain"):
            raise Refusal("the working tree has uncommitted changes; commit or stash them first")

        repo = github_repo(root)
        sync = sync_base(root, base)
        issue = verify_issue(root, repo, number, config["required_label"])

        feature_num = f"{number:03d}"
        verify_number_unused(root, feature_num)

        branch = f"{config['branch_prefix']}/{feature_num}-{slug}"
        git(root, "switch", "-c", branch, base)
    except Refusal as refusal:
        if args.json:
            print(json.dumps({"REFUSED": str(refusal)}))
        print(f"REFUSED: {refusal}", file=sys.stderr)
        return 2

    result = {
        "BRANCH_NAME": branch,
        "FEATURE_NUM": feature_num,
        "SPECIFY_FEATURE_DIRECTORY": f"specs/{feature_num}-{slug}",
        "ISSUE_URL": issue["url"],
        "ISSUE_TITLE": issue["title"],
        "SYNC": sync,
    }
    if args.json:
        print(json.dumps(result))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
