# Groundwork Charter

This repository defines **what Groundwork is**: its vision, constitution, feature specs, decisions, and mockups. It contains no application code. Implementation repositories build against it.

**Runtime invariant:** nothing here is needed to run Groundwork. If deleting this repository would break a running system, something is in the wrong place.

## Read first

1. [`product/vision.md`](product/vision.md): what Groundwork is, the two bets, and how we'll know they hold.
2. [`.specify/memory/constitution.md`](.specify/memory/constitution.md): the non-negotiable principles. They win over any spec.
3. [`process/workflow.md`](process/workflow.md): how work moves from issue to merged PR, and what enforces each rule.

Current status, ownership, and open questions live in [Issues](https://github.com/mccarlson/groundwork-charter/issues), not in this file.

## Layout

| Path | Holds |
|---|---|
| `product/` | Groundwork-specific: vision, mockup requirements, domain notes |
| `process/` | How we work. Project-agnostic by rule, so it can be reused elsewhere |
| `.specify/` | Spec Kit: constitution, templates, scripts, extensions |
| `.claude/skills/` | Spec Kit commands for Claude Code (`/speckit-*`) |
| `specs/NNN-slug/` | One directory per feature: spec, plan, tasks |
| `adr/NNN-slug.md` | Architecture decision records |

`NNN` is always a GitHub issue number from this repository.

## Setup

Both owners need the same toolchain, on Windows or macOS:

| Tool | Check | Notes |
|---|---|---|
| git | `git --version` | |
| GitHub CLI | `gh auth status` | Must be signed in as you. The `issues` extension uses it to check issue ownership. |
| uv | `uv --version` | Runs the Spec Kit CLI (`specify`) |
| Python 3.11+ | `python --version` | Must answer to **`python`**, not only `python3`. Spec Kit's skills call `python`. On macOS, put a `python` symlink to `python3` in a directory on your `PATH`. A shell alias is not enough, because agents run non-interactive shells. |
| Claude Code | `claude --version` | |

Clone every Groundwork repository as a sibling under one parent directory:

```
<parent>/
  groundwork-charter/
  <implementation repos>/
```

This repository is public. Set your git identity for it with your GitHub no-reply address so your personal email stays out of the history:

```
git config user.name "<github-username>"
git config user.email "<id>+<github-username>@users.noreply.github.com"
```

Your no-reply address is shown under GitHub **Settings → Emails**.

## How work starts

Every unit of work begins as an issue in this repository, labeled with its type and assigned to exactly one owner.

**A feature** (`type:feature`):

1. Open the issue, label it `type:feature`, and assign it to yourself.
2. In Claude Code, from this repository: `/speckit-specify #<issue> <feature description>`. The `issues` extension syncs `main`, confirms the issue is open, labeled, and yours, then creates `spec/NNN-slug` and `specs/NNN-slug/` with the same number. If it refuses, the message says why. Fix the cause; don't work around it.
3. Refine with `/speckit-clarify`, then `/speckit-plan` and `/speckit-tasks`.
4. Open a PR titled `spec(NNN): <summary>` that links the issue. The other owner reviews. Squash merge.
5. Implementation happens in an implementation repository on `feat/NNN-slug`, only after the spec has merged here.

**An ADR or a charter change** (`type:adr`, `type:charter`): update `main`, then create `adr/NNN-slug` or `charter/NNN-slug` from it. Open a PR titled `adr(NNN): …` or `charter(NNN): …`.

`main` accepts changes only through pull requests, approved by the owner who didn't make the last push. There are no exceptions, including for repository admins.

## Public repository: no client data

Nothing identifying or commercially sensitive about a real client is committed here, even in a spec or research note. That includes real invoices, customer names, rates, addresses, and contact details. Specs describe real businesses in anonymized or synthetic form. Real client material lives outside this repository.
