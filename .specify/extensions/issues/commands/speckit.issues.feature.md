---
description: "Start a feature from an assigned GitHub issue: sync main, verify the issue, create the issue-numbered branch"
---

# Start Feature From Issue

Every feature starts from an existing, open GitHub issue that is assigned to the person running this command. The issue number becomes the feature number for **both** the git branch and the spec directory. This command handles setup only; the spec itself is written by the core specify workflow.

## User Input

```text
$ARGUMENTS
```

## 1. Get the issue number

Find the issue number in the user input (forms like `#42`, `issue 42`, `42:`).

If there is no issue number, **stop**. Tell the user that features start from an issue: open one in this repository, label it, assign it to themselves, then run the command again with its number. Do **not** create, label, or assign issues yourself.

## 2. Choose the short name

Generate a concise 2–4 word kebab-case short name from the feature description (e.g. `job-capture`, `report-export`). If the user supplied one, use theirs.

## 3. Run the script

From the repository root:

```
python .specify/extensions/issues/scripts/python/start_feature.py --json --issue <number> --short-name "<short-name>"
```

Run it **once**. The script fetches origin, fast-forwards the base branch if it is behind, verifies the issue (open, labeled, assigned to exactly one person who is the current GitHub user), checks the number is unused, and creates the branch.

## 4. If the script refuses

If the exit code is non-zero or the JSON contains `REFUSED`:

- **Stop.** Show the user the refusal message exactly as printed.
- Do **not** work around it. Do not create the branch manually, do not pick a different number, do not edit the issue, do not commit or stash on the user's behalf.
- Do not continue to the specification step.

Each refusal exists to prevent a specific collision between collaborators. Resolving it is the user's decision.

## 5. On success

The JSON contains `BRANCH_NAME`, `FEATURE_NUM`, `SPECIFY_FEATURE_DIRECTORY`, `ISSUE_URL`, `ISSUE_TITLE`, and `SYNC`.

- Report the branch, the issue title and URL, and the sync result.
- The specify workflow **must** use `SPECIFY_FEATURE_DIRECTORY` exactly as given for the spec directory. Do not auto-number a directory, and do not change the short name. The branch and the spec directory must carry the same number and slug.
- Include the issue reference (`#<number>`) in the spec header.
