---
name: implementation-comment-cleanup
description: Audit and clean existing implementation comments in source and build files. Classify comments as KEEP, REMOVE, REWRITE, or ASK with evidence; remove unjustified comments, rewrite useful ones, and consult the user for uncertainty without touching API documentation or semantic directives.
---

# Implementation Comment Cleanup

Use this skill when asked to audit or clean **existing implementation comments** in a repository or selected code area. Prefer leaving only comments that communicate useful, durable information unavailable from the code itself.

Read the [OKOCRAFT Implementation Comment Guidelines](../../guidelines/implementation-comments.md) first. This skill implements that policy, not the separate rules governing Javadoc and other API documentation comments.

Default to **cleanup mode** when asked to clean comments: investigate, make safe comment-only edits, and report. Use **audit mode** when asked only to inspect or propose: classify without editing. Do not commit, push, open an issue, or create a PR unless requested.

## Principles

- **Burden of proof is on the comment.** Ask what a future maintainer would lose if this comment disappeared. If no concrete benefit survives examination of the code, prefer **REMOVE**.
- **Investigate before deciding.** Read neighboring code, relevant callers, tests, configuration, and authoritative external contracts as needed. Assume readers understand the language, common idioms, and basic project architecture; comments are not tutorials.
- **Explain current reasons, not history.** Current constraints, invariants, subtle ordering requirements, and exceptional algorithm-level intent may justify comments. Obvious narration, general API explanations, and past implementation discussions do not.
- **Do not delete uncertainty.** If a comment might encode an active constraint or warning and the evidence is insufficient, **ASK** instead of guessing.
- **Keep the change focused.** Make comment-only edits; do not refactor executable code or change public contracts merely to remove comments. Propose separate work if a code refactor would be the right solution.
- **Protect semantic comments.** Some comments affect compilation, testing, code generation, optimizers, lint, or licenses. Do not remove them based on appearance alone.
- **Follow repository conventions.** For rewritten implementation comments, use concise English unless a repository explicitly follows another convention.

## 1. Discover Comments and Define Scope

1. Read the target repository's agent instructions and local conventions. Record the requested scope, starting revision, and initial working-tree state (including staged, unstaged, and untracked files) so pre-existing changes can be distinguished from cleanup edits.
2. Inspect tracked, human-maintained **source, tests, build scripts, and relevant configuration files**. Consult [discovery guidance](references/discovery.md) for candidate searches and comments consumed by tools.
3. Exclude generated, vendored, minified, or third-party content from edits, along with copyright notices and documentation comments. Record excluded scope rather than classifying it as removable.
4. Search for all applicable comment forms, including multiline and trailing comments. A text search is only candidate discovery: verify lexical context so URL literals, strings, regular expressions, and other non-comments are not misclassified. Check files that the text search might miss.
5. Treat a logically connected block of lines as one **comment unit**. Identify its repository-relative path, line range or symbol, and relevant code context. Inventory **all** in-scope units, including comments that will remain unchanged. If the scan is incomplete, state exactly which areas were not reviewed.

Do not infer documentation-comment status from syntax alone. For example, Go documentation can use ordinary ``//`` comments, whereas ``/** ... */`` may contain directives rather than API documentation. Recognize purpose and location, not just delimiters.

## 2. Classify Every In-scope Comment

Each comment unit receives one evidence-based decision:

| Decision | Condition | Action |
| --- | --- | --- |
| **KEEP** | Provides a verified, enduring, non-obvious reason, assumption, constraint, invariant, or exceptional algorithm-level explanation; or is an active tool-consumed directive | Preserve it and record why |
| **REMOVE** | Repeats clear code, explains common idioms, contains irrelevant history, duplicates information elsewhere, or is verified obsolete | Remove only the comment |
| **REWRITE** | Provides useful, verified information but is inaccurate in wording, verbose, misleading, partly historical, or fails to state the current constraint clearly | Preserve the essential information in a smaller accurate comment |
| **ASK** | Importance or truth cannot be established; potential workaround/invariant might matter; an unfinished TODO needs a disposition; or a comment may have tooling effects | Leave untouched and request a decision |

Record **concrete evidence**, not only an abstract rule: relevant methods, call sites, tests, configuration, established API contracts, or linked active issues. To justify **REMOVE**, establish that no necessary *why* would be lost. Do not classify by length, age, or language alone.

Important boundaries:

- Describing what an immediately visible statement does is not useful; describing the non-obvious invariant maintained by a complex algorithm may be.
- A comment explaining why a seemingly simpler alternative is incorrect can be valuable even if the code already reads well.
- If eliminating the comment requires a meaningful code refactor, propose that refactor separately. **ASK** if removing the comment now would hide necessary intent.
- A bare PR or issue number is not a reason. Keep or rewrite a current technical constraint, with an authoritative reference if it genuinely helps.
- Verify before declaring a comment stale. Conflicting evidence means **ASK**, not speculative deletion.

### Existing TODO and FIXME Notes

Do not mistake removing a note for completing the work it describes.

- **REMOVE** notes only when their task is demonstrably completed, superseded, duplicated, or already tracked in a verified issue and no code reminder is needed.
- If work is still necessary and not demonstrably tracked, **ASK** whether to fix it or create/identify an issue. Do not silently drop the obligation or create issues without permission.
- Any new work-in-progress TODO/FIXME introduced during cleanup must be resolved or removed before merge, as required by the guideline.
- Existing TODOs do not automatically justify unrelated implementation changes. Report unresolved matters clearly.

## 3. Apply Safe Edits and Escalate Ambiguity

In **cleanup mode**, apply clearly supported **REMOVE** and **REWRITE** decisions. Preserve **KEEP**. Leave **ASK** unchanged.

Ask the user only for genuine judgment calls, grouped when they share a rationale. Each question should include the exact location, brief excerpt, investigated evidence, what could be lost, and a recommended default if possible. Do not block safe independent edits while awaiting a decision. Incorporate answers before changing uncertain comments; if no answer is available, leave those comments untouched and list them as unresolved.

In **audit mode**, propose all actions without editing.

Review the complete diff to ensure no code, build settings, license text, generated marker, API contract, test fixture, lint/optimizer directive, or other semantically meaningful content changed unintentionally.

## 4. Validate and Report

- Run ``git diff --check <starting-revision>`` to inspect whitespace errors across tracked changes, including staged and unstaged edits, and review the diff against that revision. Compare with the recorded initial working-tree state to distinguish pre-existing changes from cleanup edits. Check any newly created, untracked files separately, since Git diff does not include them. Run focused formatting, build, lint, or tests when relevant; report checks that could not run rather than assuming success.
- Remember that removing a tooling directive may change compilation or behavior even when executable lines are untouched. Verify its purpose before classifying it as removable.
- Report findings using the [report template](references/report-template.md). Include **KEEP**, **REMOVE**, **REWRITE**, and **ASK**, with locations, concise reasons, and evidence. Group repetitive findings only if every location remains discoverable.
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
- "Review this module's comments according to the OKOCRAFT implementation comment guideline."
