---
name: implementation-comment-cleanup
description: Audit and clean existing implementation comments in source and build files. Classify comments as KEEP, REMOVE, REWRITE, or ASK with evidence; remove unjustified comments, rewrite useful ones, and consult the user for uncertainty without touching API documentation or semantic directives.
---

# Implementation Comment Cleanup

Use this skill when asked to audit or clean **existing implementation comments** in a repository or selected code area. Prefer leaving only comments that communicate useful, durable information unavailable from the code itself.

Read the [OKOCRAFT Implementation Comment Guidelines](../../guidelines/implementation-comments.md) first. This skill implements that policy, not the separate rules governing Javadoc and other API documentation comments.

For maintenance of this skill's Python helper and tests, follow the [Python Scripts and Tests guidelines](../../guidelines/python-scripts.md).

Use **cleanup mode** for requests to clean, remove, rewrite, or fix comments: investigate, apply safe comment-only edits, and report. Use **audit mode** for requests to audit, review, inspect, evaluate, or list comments: classify and propose actions without editing. If authorization to modify files is unclear, default to audit mode. Do not commit, push, open an issue, or create a PR unless requested.

## Principles

- **Burden of proof is on the comment.** Ask what a future maintainer would lose if it disappeared. Prefer **REMOVE** when focused investigation finds no concrete current value; do not preserve comments just because they might once have had a purpose.
- **Investigate proportionately.** Start with the statement and enclosing function/file; expand to directly relevant callers, tests, configuration, or external contracts only when the comment's claim requires it. Stop when the evidence supports a decision; do not trace every caller by default. Assume readers understand the language, common idioms, and basic project architecture; comments are not tutorials.
- **Explain current reasons, not history.** Current constraints, invariants, subtle ordering requirements, and exceptional algorithm-level intent may justify comments. Obvious narration, general API explanations, and past implementation discussions do not.
- **Do not erase credible uncertainty.** Use **ASK** only when a specific, plausible current constraint, warning, or unresolved obligation remains uncertain after focused investigation; do not escalate merely because an imagined purpose cannot be disproved.
- **Keep the change focused.** Make comment-only edits; do not refactor executable code or change public contracts merely to remove comments. Propose separate work if a code refactor would be the right solution.
- **Protect semantic comments.** Some comments affect compilation, testing, code generation, optimizers, lint, or licenses. Do not remove them based on appearance alone.
- **Follow repository conventions.** For rewritten implementation comments, use concise English unless a repository explicitly follows another convention.

## 1. Discover Comments and Define Scope

1. Read the target repository's agent instructions and local conventions. Record the requested scope, starting revision, and initial working-tree state (including staged, unstaged, and untracked files).
2. **Run the bundled discovery script** against the target repository. Do not construct ad hoc search commands when the script covers the file formats involved:

   ```sh
   python3 <skill-directory>/scripts/inventory_comments.py \
     --repo <target-repository> --output <temporary-report-path>/comment-candidates.json
   ```

   Use `--path <relative-file-or-directory>` (repeatable) to limit the scope if requested. The script deterministically enumerates tracked source/build files and produces paths, line ranges, candidate text, and advisory flags in JSON. See [discovery guidance](references/discovery.md) for its exact coverage and limitations.
3. Check the command's exit status and the generated JSON, including `scanned_files`, `excluded_files`, `unreadable_files`, and `scan_warnings`. An invalid or unmatched `--path` is an error; unreadable files and unterminated block-comment candidates make the scan incomplete (exit status 2). **Manually inspect affected files before claiming complete coverage**, including later comments that the scanner may have missed. Verify candidates against actual syntax and exclude false positives and out-of-scope documentation/legal/generated material. **Hints are not decisions.** Treat compiler, build, and linter directives as potentially semantic until their purpose is verified.
4. Group verified candidates into **comment units**: one independent explanation, task note, or directive. Consecutive lines conveying one idea (including a multiline block) are one unit; adjacent comments with independent purposes are separate units. An end-of-line comment is its own unit. A blank line normally separates units.
5. Check any explicitly requested, unsupported or untracked file families separately and disclose the supplemental search method. If a scan failed, files were unreadable, or parser limitations could affect coverage, do not claim exhaustive inventory. Perform classification in Section 2.

## 2. Classify Every In-scope Comment

Inventory **every verified, in-scope comment unit** from the discovery output (including those likely to remain unchanged), preserving its location and evidence. Assign exactly one evidence-based decision to each:

| Decision | Condition | Action |
| --- | --- | --- |
| **KEEP** | Provides a verified, enduring, non-obvious reason, assumption, constraint, invariant, or exceptional algorithm-level explanation; or is an active tool-consumed directive | Preserve it and record why |
| **REMOVE** | After focused investigation, no useful current information remains: it repeats clear code, explains common idioms, records irrelevant history, duplicates other content, or is verified obsolete | Remove only the comment |
| **REWRITE** | Contains a verified, useful current reason or constraint, but its wording is unclear, excessive, misleading, or mixed with history | Preserve only the useful information in an accurate, concise comment |
| **ASK** | A specific, credible constraint, task, or tooling effect cannot be resolved through relevant investigation; removing it could lose important information or behavior | Leave untouched and request a decision |

Record **concrete evidence**, not only an abstract rule: relevant methods, call sites, tests, configuration, established API contracts, or active issues. Review the enclosing function/file first, then the nearest relevant call sites and tests, and broaden to module behavior or upstream contracts **only when a specific claim requires it**. Stop once sufficient evidence exists; exhaustive repository-wide tracing is not the default.

**Decision order:** Filter out-of-scope comments first. Preserve active tool directives. For prose comments, identify any current information remaining after removing obvious narration and history. If nothing useful remains, **REMOVE**; if the remaining information is valuable but poorly expressed, **REWRITE**; if valuable and accurate, **KEEP**. Choose **ASK** only if a concrete, plausible claim remains unresolved after proportionate investigation. Failure to disprove every hypothetical benefit is not, by itself, a reason to ask.

A multi-line comment with independent purposes (for example, an unfinished TODO followed by a current compatibility constraint) may contain **two units with different decisions**. Handle each separately: remove or defer the TODO as appropriate, and keep or rewrite the compatibility explanation only if the constraint is still valid.

Important boundaries:

- Describing what an immediately visible statement does is not useful; describing the non-obvious invariant maintained by a complex algorithm may be.
- A comment explaining why a seemingly simpler alternative is incorrect can be valuable even if the code already reads well.
- If eliminating the comment requires a meaningful code refactor, propose that refactor separately. **ASK** if removing the comment now would hide necessary intent.
- A bare PR or issue number is not a reason. Keep or rewrite a current technical constraint, with an authoritative reference if it genuinely helps.
- Verify before declaring a comment stale. Conflicting evidence means **ASK**, not speculative deletion.

### Existing TODO and FIXME Notes

Do not mistake removing a note for completing the work it describes.

1. Check whether the task is already completed, superseded, or duplicated using the code, tests, and relevant issue history. If verified, **REMOVE** the obsolete note.
2. If the work is still applicable and **legitimately deferrable**, check for a matching active issue. If verified, **REMOVE** the code TODO and record the issue in the report; the issue remains the task tracker.
3. If the work is still required but lacks a verified issue, or if its importance or safe deferral is unclear, **ASK** whether to implement it or track it in an issue. Leave the note intact until resolved; do not silently drop the work, create an issue, or refactor code without authorization. Flag correctness-critical unfinished work rather than treating issue creation as sufficient.
4. Any new work-in-progress TODO/FIXME introduced during cleanup must be resolved or removed before merge. Existing TODOs do not automatically justify unrelated implementation changes.

## 3. Apply Safe Edits and Escalate Ambiguity

In **cleanup mode**, apply clearly supported **REMOVE** and **REWRITE** decisions. Preserve **KEEP**. Leave **ASK** unchanged.

Ask the user only for genuine judgment calls, grouped when they share a rationale. Each question should include the exact location, brief excerpt, investigated evidence, what could be lost, and a recommended default if possible. Do not block safe independent edits while awaiting a decision. Incorporate answers before changing uncertain comments; if no answer is available, leave those comments untouched and list them as unresolved.

In **audit mode**, propose all actions without editing.

Review the complete diff to ensure no code, build settings, license text, generated marker, API contract, test fixture, lint/optimizer directive, or other semantically meaningful content changed unintentionally.

## 4. Validate and Report

- Run ``git diff --check <starting-revision>`` to inspect whitespace errors across tracked changes, including staged and unstaged edits, and review the diff against that revision. Compare with the recorded initial working-tree state to distinguish pre-existing changes from cleanup edits. Check any newly created, untracked files separately, since Git diff does not include them. Run focused formatting, build, lint, or tests when relevant; report checks that could not run rather than assuming success.
- Remember that removing a tooling directive may change compilation or behavior even when executable lines are untouched. Verify its purpose before classifying it as removable.
- Report findings using the [report template](references/report-template.md) alongside the script's JSON candidate inventory. Include **KEEP**, **REMOVE**, **REWRITE**, and **ASK**, with locations, concise reasons, and evidence. Group repetitive findings only if every location remains discoverable. Never interpret candidate counts as final comment counts without syntax review and grouping.
- Distinguish proposed from applied changes. Report classification counts, unresolved questions, excluded/generated areas, unchecked areas, and validation results. Do not count excluded material as removed.
- Keep extensive audit details in a separate report when needed, but do not commit it into the target repository unless asked. Do not fabricate issues, citations, test results, or certainty.

## Completion Conditions

- The requested source/build scope was covered, or omissions were disclosed.
- Every reviewed implementation comment has a reasoned **KEEP / REMOVE / REWRITE / ASK** disposition.
- Unnecessary comments were removed where safe; useful ones remain or were accurately rewritten.
- Ambiguous comments were not silently discarded, and unresolved user decisions are explicit.
- The final diff and applicable checks were reviewed and accurately reported.

Example invocations:

- "Audit source comments in this repository and list what to keep, remove, rewrite, or ask me about."
- "Clean redundant implementation and build-script comments, but ask me about uncertain ones."
- "Review this module's comments according to the OKOCRAFT implementation comment guideline (audit only)."
