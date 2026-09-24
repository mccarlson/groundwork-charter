# Workflow

**Status:** Draft · **Owners:** [owner-1], [owner-2] · **Last reviewed:** 2026-09-24

How work moves from idea to merged code across the charter repository and the implementation repositories. Every rule states what it prevents and what enforces it. A rule with no enforcement is marked **convention** and is only as strong as the people and agents following it.

> **Vocabulary rule.** Nothing under `process/` names the product, its domain, or its vendors. Project specifics live under `product/`. This keeps `process/` reusable by copying the directory. CI enforces it with a denylist defined in `product/`.

---

## 1. Repositories

| Repository | Holds | Never holds |
|---|---|---|
| **Charter** | Constitution, specs, plans, tasks, ADRs, mockups, research | Anything an application needs to run |
| **Implementation** (one or more) | Application code, schema, migrations, tests, infrastructure | Specs or decisions (it links to them) |

All repositories are cloned as siblings under one parent directory. Implementation repos find the charter at `../<charter>/`, as declared in their `CLAUDE.md`.

**Runtime invariant:** if deleting the charter repository would break a running system, something is in the wrong repository.

## 2. Identifiers

**Every unit of work starts as an issue in the charter repository. The issue number is its ID.**

| Rule | Prevents | Enforced by |
|---|---|---|
| Feature, ADR, and research numbers are charter issue numbers, zero-padded to 3 digits (`#42` → `042`). | Two people picking the same number. GitHub assigns issue numbers server-side, so they can't collide. | `issues` extension: requires an issue number, uses it for both the branch and the spec directory |
| Numbers skip values; pull requests share the counter. Gaps are expected. Never renumber. | Renumbering that breaks branch names and links in other repos. | Convention |
| Slugs are kebab-case, at most 4 words, fixed when the spec branch is created, and never changed after. | Branch names in the two repos drifting apart. | `issues` extension (format) + CI (branch ↔ spec match, §5) |
| DB migrations in implementation repos are named by UTC timestamp (`20260924T1412Z_add_assets.sql`). The migration runner applies any unapplied migration, not only newer ones. | Merge order and timestamp order disagreeing when two branches both add migrations. | Runner behavior + contract test |

## 3. Issues

| Rule | Prevents | Enforced by |
|---|---|---|
| Every issue has exactly one assignee, and that person is its owner. Nobody works on an unassigned issue, and only the owner starts work on one. | Work nobody owns, and two people starting the same item. | `issues` extension refuses issues that are unassigned, have several assignees, or are assigned to someone else |
| Handing an issue off means reassigning it and commenting why. | Ownership that's assumed but never recorded. | Convention |
| Every issue has a type label: `type:feature`, `type:adr`, `type:research`, `type:bug`, or `type:charter`. | Work with no clear place in the lifecycle. | Issue templates |
| A feature issue stays open until its spec **and** its implementation have both merged. The implementation PR closes it with `Closes <owner>/<charter>#NNN`. | A feature marked done when only the spec exists. | PR template + CI |
| If a spec is amended after implementation starts, the amendment PR is linked on the issue, and the implementation owner acknowledges it before continuing. | Code built against a spec that changed underneath it. | CI drift check (§5) + convention |

## 4. Branches

| Repository | Prefix | Used for |
|---|---|---|
| Charter | `spec/NNN-slug` | Feature spec, plan, and tasks |
| Charter | `adr/NNN-slug` | Architecture decision record |
| Charter | `charter/NNN-slug` | Changes to constitution, `process/`, templates, extensions |
| Implementation | `feat/NNN-slug` | Implements `specs/NNN-slug/` |
| Implementation | `fix/NNN-slug` | Bug fix tracked by a charter issue |
| Implementation | `chore/NNN-slug` | Tooling, dependencies, CI |

| Rule | Prevents | Enforced by |
|---|---|---|
| Branch names match `^(spec\|adr\|charter\|feat\|fix\|chore)/\d{3,}-[a-z0-9-]+$`. | Branches that can't be traced to an issue. | GitHub ruleset + CI |
| One issue per branch. | PRs that bundle unrelated changes and can't be reviewed or reverted cleanly. | Convention |
| Branches merge within about 3 working days, or get rebased onto main. | Long-lived branches that go stale and conflict. | Convention |

## 5. Spec before code

| Rule | Prevents | Enforced by |
|---|---|---|
| `feat/NNN-slug` can only be created once `specs/NNN-slug/` (spec, plan, tasks) has merged to charter main. | Code with no approved spec behind it. | Implementation CI: fails if `specs/NNN-slug/` isn't on charter main |
| The implementation PR records the charter commit it was built against: `Charter-Ref: <sha>`. | Not knowing which version of the spec the code implements. | PR template + CI |
| CI fails if `specs/NNN-slug/` changed on charter main after `Charter-Ref`. | Code merging against a spec that changed after it was written (see §3). | Implementation CI drift check |
| Shared-contract changes (schema, provider interface, pricing API) land in their own PR, before features that depend on them. | Two feature branches each changing a shared contract in different ways. | Convention + CODEOWNERS paths |

## 6. Sync before authoring

| Rule | Prevents | Enforced by |
|---|---|---|
| Before `/speckit-specify` or creating any branch: fetch, and make sure local main matches `origin/main`. | Writing a spec against an old constitution or without seeing the other owner's latest work. | `issues` extension fetches and fast-forwards main when it is behind; refuses if main has local commits or the working tree is dirty |
| A PR can merge only if its branch is up to date with main. | Merging something that was only ever tested against an old main. | Branch protection: *require branches to be up to date* |

## 7. Pull requests

Branch protection on `main` in **every** repository:

- Require a pull request. No direct pushes, and no local merges pushed to main.
- Require 1 approving review from someone other than the author.
- Require status checks to pass.
- Require the branch to be up to date before merging.
- Block force pushes and branch deletion.
- **Do not allow bypassing these settings, including for administrators.** Otherwise either owner, or an agent using that owner's credentials, can skip every rule above.

| Rule | Prevents | Enforced by |
|---|---|---|
| PR title: `<prefix>(NNN): summary`, e.g. `feat(042): quick-add tiles`. | History that can't be traced to issues. | CI title check |
| Squash merge only. The squash commit keeps the PR title. | Noisy history. One commit per issue keeps revert and blame simple. | Repository merge settings |
| The PR template requires the issue link, the spec reference, and, for charter PRs, a list of the specs and plans the change affects. | Changes whose impact nobody checked. | PR template + CI |
| Constitution PRs stay open for at least 24 hours before merging. | One owner changing the rules while the other is away. | Convention (can be automated later) |

**Two owners means every merge has both.** The author writes it and the other owner approves it, so every change, shared contracts included, already has both people on it. CODEOWNERS dual approval only matters once a third contributor joins. Configure it now anyway so it's in place when that happens.

## 8. Agents

Agents use their developer's GitHub credentials. **Any rule not enforced by GitHub is only as strong as the agent's compliance.** Branch protection (§7) is what stops an agent that misbehaves.

**Agents never:**
- merge, approve, or close pull requests
- push to main or force-push to any branch
- create, close, reassign, or renumber issues unless told to in the current session
- edit the constitution, `process/`, `.specify/extensions/`, or shared-contract paths unless told to in the current session
- work outside the issue and spec they were pointed at

**Agents must:**
- check sync (§6) before `/speckit-specify` or creating a branch
- stop and report if the branch slug doesn't match the spec directory
- stop and report if the spec changed on charter main since the `Charter-Ref` they're working from
- stop and explain, not work around, when a rule blocks them

**Enforced by:**

- **`CLAUDE.md`** in each repo states the rules.
- **`.claude/hooks/guard_bash.py`**, a PreToolUse hook committed with the repo, parses every Bash command an agent runs, including compound commands and `bash -c`. It **denies** the "never" list above: merging, closing, approving, or requesting changes on PRs; pushing to main in any form; force-pushing; deleting remote branches; committing or non-fast-forward merging on local main; GitHub writes through `gh api`; and changing workflows, repository settings, or secrets. It **asks** the user before issue and label changes, since agents make those only when told to.
- **`.claude/settings.json`** repeats the common deny forms as plain permission rules in case the hook can't run, and **asks** before any edit to the constitution, `process/`, `.specify/extensions/`, `.github/`, `CLAUDE.md`, the vocabulary denylist, or the settings and hook themselves. That keeps an agent from weakening its own guardrails.
- **Branch protection** (§7) is the final backstop. It holds even if a session runs with permissions bypassed.

The hook sees only commands an agent runs through Claude Code's Bash tool. Commands a script runs internally, and shell writes to protected files, are caught by review and CI, not by the hook.

## 9. Enforcement summary

| Layer | Enforces | Applies to |
|---|---|---|
| GitHub branch protection / rulesets | PR required, review, up-to-date, no force-push, branch names | Humans and agents, server-side |
| CI (charter) | Vocabulary rule, required frontmatter, dead cross-references, PR title | Every charter PR |
| CI (implementation) | Spec exists on charter main, `Charter-Ref` present, drift check, PR title | Every implementation PR |
| Spec Kit `issues` extension | Issue-number IDs, branch prefix, sync, owner check, number collisions | `/speckit-specify` (runs as a mandatory pre-hook) |
| Claude Code hook and settings (`.claude/`) | Denied git and gh operations (§8), user confirmation for issue changes and edits to protected paths | Agent sessions, both machines |
| Convention | Everything marked *convention* above | Only good faith |

## 10. Changing this document

Open a `type:charter` issue, branch `charter/NNN-slug`, and state which rules change and why. Both owners review. A removed or reversed rule is a MINOR constitution version bump; a clarification is a PATCH.
