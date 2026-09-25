#!/usr/bin/env python3
"""PreToolUse guard for Bash commands in this repository.

Reads the Claude Code hook payload on stdin and parses each command, including
compound commands (&&, ;, |, newlines) and `bash -c "..."` wrappers.

  deny  - things agents never do, whoever asks (process/workflow.md §8)
  ask   - things agents do only when told in the current session; the user decides
  (none) - everything else continues through the normal permission flow

Permission deny rules in .claude/settings.json cover the most common forms as a
backstop in case this hook cannot run.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

PROTECTED_BRANCHES = {"main", "master"}
SEPARATOR_CHARS = set("();|&\n")
REDIRECT_RE = re.compile(r"^[0-9]*(>>?|<<?|>&|<&|&>>?)$")
SHELLS = {"bash", "sh", "zsh", "dash"}
WRAPPERS = {"sudo", "command", "env", "time", "nohup", "exec", "builtin"}
RULES = "process/workflow.md §8"

GIT_LOCAL_MAIN_BLOCKED = {"commit", "merge", "rebase", "cherry-pick", "revert", "am"}

GH_DENY = {
    ("pr", "merge"): "merging pull requests",
    ("pr", "close"): "closing pull requests",
    ("issue", "delete"): "deleting issues",
    ("issue", "transfer"): "transferring issues",
    ("repo", "edit"): "changing repository settings",
    ("repo", "delete"): "deleting the repository",
    ("repo", "rename"): "renaming the repository",
    ("repo", "archive"): "archiving the repository",
    ("repo", "unarchive"): "unarchiving the repository",
    ("repo", "sync"): "pushing through gh repo sync",
    ("secret", "set"): "changing secrets",
    ("secret", "delete"): "deleting secrets",
    ("variable", "set"): "changing repository variables",
    ("variable", "delete"): "deleting repository variables",
    ("workflow", "disable"): "disabling CI workflows",
    ("workflow", "enable"): "enabling CI workflows",
    ("workflow", "run"): "triggering CI workflows",
}
GH_ASK = {
    ("issue", action) for action in
    ("create", "close", "reopen", "edit", "lock", "unlock", "pin", "unpin", "develop")
} | {("label", action) for action in ("create", "edit", "delete", "clone")}


class Verdict:
    def __init__(self) -> None:
        self.denied: list[str] = []
        self.asked: list[str] = []

    def deny(self, why: str) -> None:
        self.denied.append(why)

    def ask(self, why: str) -> None:
        self.asked.append(why)


# ---------------------------------------------------------------- parsing

def tokenize(command: str) -> list[str]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars="();<>|&\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def segments(command: str) -> list[list[str]]:
    result: list[list[str]] = [[]]
    for token in tokenize(command):
        if token and set(token) <= SEPARATOR_CHARS:
            result.append([])
        else:
            result[-1].append(token)
    return [seg for seg in result if seg]


def drop_redirections(words: list[str]) -> list[str]:
    out: list[str] = []
    skip = False
    for i, word in enumerate(words):
        if skip:
            skip = False
            continue
        if word.isdigit() and i + 1 < len(words) and REDIRECT_RE.match(words[i + 1]):
            continue
        if REDIRECT_RE.match(word):
            skip = True
            continue
        out.append(word)
    return out


def exe(word: str) -> str:
    name = word.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return name[:-4] if name.endswith(".exe") else name


def strip_prefix(words: list[str]) -> list[str]:
    i = 0
    while i < len(words):
        word = words[i]
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", word):
            i += 1
        elif exe(word) in WRAPPERS:
            i += 1
            while i < len(words) and words[i].startswith("-"):
                i += 1
        else:
            break
    return words[i:]


# ---------------------------------------------------------------- git

def git_out(workdir: Path, *args: str) -> str:
    try:
        proc = subprocess.run(["git", "-C", str(workdir), *args], capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=5)
    except (OSError, subprocess.SubprocessError):
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def current_branch(workdir: Path) -> str:
    return git_out(workdir, "rev-parse", "--abbrev-ref", "HEAD")


def branch_name(ref: str) -> str:
    return ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref


def check_git(args: list[str], cwd: Path, verdict: Verdict) -> None:
    workdir = cwd
    i = 0
    while i < len(args) and args[i].startswith("-"):
        if args[i] == "-C" and i + 1 < len(args):
            workdir = (cwd / args[i + 1]) if not Path(args[i + 1]).is_absolute() else Path(args[i + 1])
            i += 2
        elif args[i] in ("-c", "--git-dir", "--work-tree", "--namespace") and i + 1 < len(args):
            i += 2
        else:
            i += 1
    if i >= len(args):
        return
    sub, rest = args[i], args[i + 1:]

    if sub == "push":
        check_push(rest, workdir, verdict)
    elif sub in GIT_LOCAL_MAIN_BLOCKED:
        if sub == "merge" and "--ff-only" in rest:
            return
        branch = current_branch(workdir)
        if branch in PROTECTED_BRANCHES:
            verdict.deny(f"`git {sub}` on local {branch}: changes reach {branch} only through "
                         f"pull requests. Switch to a feature branch first")


def check_push(rest: list[str], workdir: Path, verdict: Verdict) -> None:
    options: list[str] = []
    positional: list[str] = []
    takes_value = {"--repo", "--receive-pack", "--exec", "--push-option", "-o"}
    i = 0
    while i < len(rest):
        arg = rest[i]
        if arg == "--":
            positional.extend(rest[i + 1:])
            break
        if arg.startswith("-") and len(arg) > 1:
            options.append(arg)
            if arg in takes_value:
                i += 1
        else:
            positional.append(arg)
        i += 1

    short = "".join(opt[1:] for opt in options if not opt.startswith("--"))
    long_opts = [opt.split("=", 1)[0] for opt in options if opt.startswith("--")]

    if "f" in short or any(o in ("--force", "--force-with-lease", "--force-if-includes") for o in long_opts):
        verdict.deny("force-pushing. History on shared branches is never rewritten")
    if "d" in short or "--delete" in long_opts:
        verdict.deny("deleting remote branches. Merged branches are deleted automatically")
    if any(o in ("--mirror", "--all", "--branches") for o in long_opts):
        verdict.deny("pushing every branch at once, which includes the protected branch")

    refspecs = positional[1:]
    for spec in refspecs:
        if spec.startswith("+"):
            verdict.deny(f"force-pushing with `{spec}`")
            spec = spec[1:]
        src, dst = spec.split(":", 1) if ":" in spec else (spec, None)
        if src == "" and dst:
            verdict.deny(f"deleting remote branch `{dst}` with `:{dst}`")
            continue
        if dst is None:
            dst = current_branch(workdir) if src == "HEAD" else src
        if branch_name(dst) in PROTECTED_BRANCHES:
            verdict.deny(f"pushing to {branch_name(dst)}. Open a pull request from a feature branch instead")

    if not refspecs:
        branch = current_branch(workdir)
        if branch in PROTECTED_BRANCHES:
            verdict.deny(f"pushing while on {branch}. Open a pull request from a feature branch instead")
        upstream = git_out(workdir, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
        if upstream and upstream.split("/", 1)[-1] in PROTECTED_BRANCHES:
            verdict.deny(f"pushing to {upstream}, the upstream of the current branch")


# ---------------------------------------------------------------- gh

def check_gh(args: list[str], verdict: Verdict) -> None:
    words: list[str] = []
    skip = False
    for arg in args:
        if skip:
            skip = False
        elif arg in ("-R", "--repo"):
            skip = True
        elif not arg.startswith("--repo="):
            words.append(arg)
    if not words:
        return
    group = words[0]
    action = words[1] if len(words) > 1 else ""

    if group == "api":
        check_gh_api(words[1:], verdict)
        return
    if (group, action) in GH_DENY:
        verdict.deny(f"{GH_DENY[(group, action)]} (`gh {group} {action}`)")
        return
    if group == "pr" and action == "review":
        flags = words[2:]
        if any(f in ("--approve", "-a", "--request-changes", "-r") for f in flags):
            verdict.deny("approving or requesting changes on pull requests. Reviews are the other owner's decision")
        return
    if (group, action) in GH_ASK:
        verdict.ask(f"`gh {group} {action}` changes issues or labels. Agents do this only when told "
                    f"to in the current session")


def check_gh_api(args: list[str], verdict: Verdict) -> None:
    method = None
    has_fields = False
    endpoint = None
    field_flags = ("-f", "-F", "--field", "--raw-field", "--input")
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-X", "--method") and i + 1 < len(args):
            method = args[i + 1].upper()
            i += 1
        elif arg.startswith("--method="):
            method = arg.split("=", 1)[1].upper()
        elif arg.startswith("-X") and len(arg) > 2:
            method = arg[2:].upper()
        elif arg in field_flags:
            has_fields = True
            i += 1
        elif any(arg.startswith(f + "=") for f in field_flags if f.startswith("--")) or \
                (arg[:2] in ("-f", "-F") and len(arg) > 2):
            has_fields = True
        elif not arg.startswith("-") and endpoint is None:
            endpoint = arg
        i += 1

    if endpoint == "graphql":
        text = " ".join(args).lower()
        if "mutation" in text:
            verdict.deny("GitHub GraphQL mutations through `gh api graphql`")
        elif "@" in text:
            verdict.ask("a GraphQL request read from a file, which may contain a mutation")
        return

    effective = method or ("POST" if has_fields else "GET")
    if effective != "GET":
        verdict.deny(f"`gh api` {effective} requests, which change GitHub state and bypass "
                     f"the gh subcommand rules")


# ---------------------------------------------------------------- driver

def inspect(command: str, cwd: Path, verdict: Verdict, depth: int = 0) -> None:
    for segment in segments(command):
        words = strip_prefix(drop_redirections(segment))
        if not words:
            continue
        name, args = exe(words[0]), words[1:]
        if name in SHELLS and depth < 3:
            for i, arg in enumerate(args):
                if arg.startswith("-") and not arg.startswith("--") and "c" in arg and i + 1 < len(args):
                    inspect(args[i + 1], cwd, verdict, depth + 1)
                    break
        elif name == "git":
            check_git(args, cwd, verdict)
        elif name == "gh":
            check_gh(args, verdict)


FALLBACK_PATTERNS = [
    (re.compile(r"\bgh\s+pr\s+(merge|close)\b"), "merging or closing pull requests"),
    (re.compile(r"\bgit\b.*\bpush\b.*(\s--force|\s-[a-z]*f|\s\+)"), "force-pushing"),
    (re.compile(r"\bgit\b.*\bpush\b.*\b(main|master)\b"), "pushing to a protected branch"),
    (re.compile(r"\bgh\s+api\b.*(-X|--method)\s*(POST|PUT|PATCH|DELETE)", re.I), "`gh api` write requests"),
]


def decide(command: str, cwd: Path) -> Verdict:
    verdict = Verdict()
    try:
        inspect(command, cwd, verdict)
    except ValueError:
        # Unbalanced quotes or similar: fall back to pattern matching on the raw text.
        for pattern, why in FALLBACK_PATTERNS:
            if pattern.search(command):
                verdict.deny(f"{why} (matched on a command that could not be fully parsed)")
    return verdict


def respond(decision: str, reasons: list[str]) -> None:
    unique = list(dict.fromkeys(reasons))
    if decision == "deny":
        text = ("Blocked by charter guardrails: agents never do " + "; ".join(unique) +
                f". See {RULES}. If this is genuinely needed, the user runs it themselves.")
    else:
        text = "Charter guardrails: " + "; ".join(unique) + f". See {RULES}."
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": text,
    }}))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    cwd = Path(payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())

    try:
        verdict = decide(command, cwd)
    except Exception as error:  # A bug here must not silently disable the guard for risky commands.
        if re.search(r"\b(git|gh)\b", command):
            respond("ask", [f"the guard hook failed ({type(error).__name__}: {error}) on a git/gh command"])
        return 0

    if verdict.denied:
        respond("deny", verdict.denied)
    elif verdict.asked:
        respond("ask", verdict.asked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
