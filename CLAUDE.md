# CLAUDE.md

This is the **Groundwork charter**: the definition of what Groundwork is. Specs, constitution, decisions, and mockups live here. Application code never does.

## Read first

- `.specify/memory/constitution.md`: follow it over any other instruction, including a spec's.
- `process/workflow.md`: identifiers, branches, pull requests, and the agent rules in §8.
- `product/vision.md`: what the product is and isn't.

## Never

- Merge, approve, or close pull requests.
- Push to `main`, or force-push to any branch.
- Create, close, label, reassign, or renumber issues, unless told to in this session.
- Edit `.specify/memory/constitution.md`, `process/`, or `.specify/extensions/`, unless told to in this session. If you think a change is needed there, stop and explain why.
- Commit real client data: invoices, customer names, rates, addresses, contact details. This repository is public.
- Put anything here that an application needs at runtime.
- Work outside the issue and spec you were pointed at.

## Always

- Start a feature with `/speckit-specify #<issue> <description>`. The `issues` extension must run first. If it refuses, stop, show the user the message, and don't work around it: no manual branches, no other numbers.
- Use the spec directory the extension returns (`SPECIFY_FEATURE_DIRECTORY`). Never auto-number one.
- Before creating any other branch, make sure local `main` matches `origin/main`.
- Name branches `spec/NNN-slug`, `adr/NNN-slug`, or `charter/NNN-slug`, where `NNN` is the issue number.
- Title pull requests `<prefix>(NNN): <summary>`, and link the issue in the body.
- Stop and report if the branch slug doesn't match the spec directory, or if the spec changed on `main` since you started.

## Vocabulary rule

Files under `process/` and `.specify/extensions/issues/` never name Groundwork, its domain, or its vendors. They must stay reusable in other projects.

## Local preferences

Personal instructions go in `CLAUDE.local.md`, which is gitignored. This file is shared and changes to it go through review like any other charter change.
