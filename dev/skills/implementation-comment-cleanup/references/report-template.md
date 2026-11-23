# Implementation Comment Cleanup Report — [target / scope]

- **Mode:** audit / cleanup
- **Baseline:** [commit / starting revision]
- **Coverage:** [files and directories actually reviewed, including build logic]
- **Excluded:** [documentation comments, generated/third-party files, license text, etc.]
- **Not reviewed:** [paths or file families, if any; otherwise "None"]
- **Discovery output:** [path to JSON produced by scripts/inventory_comments.py]
- **Discovery limitations:** [unreadable_files, excluded_files, unsupported syntax, supplemental checks; or "None"]

## Decision Summary

| Decision | Count | Applied | Pending |
| --- | ---: | ---: | ---: |
| KEEP | 0 | — | — |
| REMOVE | 0 | 0 | 0 |
| REWRITE | 0 | 0 | 0 |
| ASK | 0 | — | 0 |

Counts apply to **in-scope comment units**, not individual lines. One unit expresses one independent explanation, task, or directive; related consecutive lines are one unit, but independent adjacent notes count separately. Do not count excluded comments as removed. When an ASK is resolved, reclassify it under its final decision and record the answer below.

## Comment Inventory

Record all reviewed units; keep a discoverable entry for each, even when grouping repeated findings. Line numbers refer to the **starting revision**, unless otherwise noted.

| Location (path:line or symbol) | Decision | What information would be lost if removed? / Evidence | Proposed or applied action |
| --- | --- | --- | --- |
| `path/to/file:42` | KEEP | [Current non-obvious invariant, validated in relevant code/test] | Unchanged |
| `path/to/other:17` | REMOVE | [Nearby name and expression already convey all content] | Removed / Proposed |
| `path/to/other:58` | REWRITE | [Current external constraint still applies; historical wording is not useful] | [Short replacement / proposed] |
| `path/to/build:11` | ASK | [Cannot verify whether tool consumes this annotation] | Unchanged; ask user |

When many findings share a rationale, summarize it once and list **every affected location**, rather than emitting hundreds of nearly identical explanations. Distinguish factual evidence from interpretations.

## Decisions Required from User

For each unresolved **ASK**, state:

1. **Where:** path, line, symbol, and a short comment excerpt.
2. **Evidence:** what was inspected and what remains unknown.
3. **Tradeoff:** what might be lost if removed versus what is gained.
4. **Question:** a concrete decision the user can answer, with a recommended default if appropriate.

Do not treat an unanswered question as approval. Leave the affected comment untouched.

## Resolved Questions

For each answered **ASK**, record the location, the user's decision or newly verified evidence, the final KEEP / REMOVE / REWRITE classification, and whether a change was applied. Update the decision counts to reflect final classifications. If no questions were resolved, write "None."

| Location | User decision or new evidence | Final classification | Applied change |
| --- | --- | --- | --- |
| [path:line] | [answer and supporting context] | [KEEP / REMOVE / REWRITE] | [yes / no] |

## Applied Changes

- **Removed:** [locations and concise reasons]
- **Rewritten:** [locations, meaning preserved, and why]
- **Not changed:** [KEEP and pending ASK summary]
- **Out of scope:** [any refactor, unresolved bug, or task requiring an issue]

## Validation

| Check | Result | Notes |
| --- | --- | --- |
| Diff inspection | PASS / FAIL / NOT RUN | [Confirm no accidental code/tooling changes] |
| ``git diff --check <starting-revision>`` | PASS / FAIL / NOT RUN | [Include staged + unstaged changes; check new untracked files separately] |
| Relevant build/lint/tests | PASS / FAIL / NOT RUN | [Exact command or reason unavailable] |

**Final status:** [completed scope / partial coverage; unresolved decisions; material risks]
