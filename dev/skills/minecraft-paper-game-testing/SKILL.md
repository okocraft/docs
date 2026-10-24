---
name: minecraft-paper-game-testing
description: Analyze any Minecraft/Paper plugin's source and existing tests to produce or maintain a concise, reusable TESTING.md with observable in-game test viewpoints and operations, or identify only the additional in-game checks needed for a specific Minecraft/Paper update.
---

# Minecraft / Paper In-Game Test Design

Use this skill for Minecraft, Bukkit, and Paper plugins involving blocks, entities, inventories, worlds, commands, schedulers, persistence, or other game mechanics. It has two workflows:

1. **Persistent guidance (Role 1):** create or improve `TESTING.md` in the *target plugin repository*, based on its current implementation.
2. **Update-specific review (Role 2):** compare a Minecraft/Paper version change against the plugin's dependency points and produce an executable checklist for *this update only*.

For findings from an executed checklist that reveal a lasting testing gap, apply the **Maintenance** workflow below.

The goal is **release-relevant confidence from a small number of short, reproducible in-game operations**, not exhaustive regression coverage or one manual test per API call. Use the templates at [`references/testing-template.md`](references/testing-template.md) and [`references/update-checklist-template.md`](references/update-checklist-template.md). Adapt them to the target repository; do not copy placeholder entries into finished output.

## Rules for Both Roles

- Inspect repository evidence before making claims. Distinguish verified behavior from assumptions, and include repository-relative paths (and relevant symbols where useful).
- Start with **player- or administrator-observable guarantees**. An API is a dependency, not automatically a manual test.
- Include a viewpoint only if there is a plausible, concrete observable regression. Prefer failures that would block release or cause harmful unintended behavior, including important **negative behaviors** (for example, protected data or blocks must not change).
- Compile-time incompatibility alone is not a reason for an in-game check. Do not duplicate behavior sufficiently verified by existing automated tests without a runtime-specific risk.
- Merge viewpoints into existing operations wherever possible. Prefer commands, fixed setups, controlled world states, and planted resources over random natural generation or rare events.
- State **exact actions and observable pass conditions**. Avoid "looks fine", "test the API", or log-only checks for behavior that should also be visible in game.
- Optimize detection value relative to execution time. Do not add a separate operation when an existing operation can observe the same failure.
- Honor the actual plugin's advertised server support. Paper and Folia have different ownership implications; never assume that a one-thread Paper exercise establishes Folia safety.
- Treat [OKOCRAFT Testing Guidelines](https://github.com/okocraft/docs/blob/main/dev/guidelines/java-testing.md) as the general automated-test policy. For relevant changes, also consult [Paper and Folia Scheduling and Threading](https://github.com/okocraft/docs/blob/main/dev/guidelines/paper-folia-scheduling-and-threading.md).
- Never claim that a test passed unless it was actually run. A proposed checklist is not evidence of a passing server test.

## Role 1 — Create or Improve Persistent Game Test Guidelines

### 1. Inspect the target repository

Read the relevant README, plugin metadata (`plugin.yml` / `paper-plugin.yml`), build files, configuration and defaults, main plugin class, listener and command registrations, permissions, scheduler usage, persistence, and existing unit/integration tests. Inspect the code behind the behaviors being documented, including block, entity, inventory, and world interactions where applicable.

Read the existing `TESTING.md` first if present; check whether its assertions, paths, and operations still agree with the implementation. Do not silently carry over stale claims. If it is absent, create it when requested.

### 2. Identify Core Behaviors (`CB-xxx`)

Record the minimal set of player- or administrator-observable promises whose failure could justify blocking a release. For each behavior document:

- what it guarantees and why its failure matters;
- relevant source locations;
- if useful, important exclusions (what must **not** happen).

Do not classify method names or low-level implementation details as behaviors.

### 3. Map Platform Dependency Points (`DP-xxx`)

For each relevant Minecraft, Bukkit, or Paper mechanism, record its platform, how the plugin uses it, affected `CB` IDs, specific ways an upstream change could break those behaviors, relevant APIs/game concepts, and source locations.

Make the causal link explicit: **platform mechanism → plugin usage → possible in-game failure**. Examples of mechanisms (only when actually used) include block state, events, tags, entity/chunk lifecycle, item representation, commands, persistence, and scheduling.

### 4. Define Game Test Viewpoints (`VP-xxx`)

Separate **what must be observed** from **how to produce it**. Each viewpoint must have a clear, observable verify statement, linked `CB` and `DP` IDs, and at least one plausible failure example. Include significant unintended side effects, not only the successful path.

Do not include viewpoints with no runtime regression path or those already adequately guaranteed by a lighter automated test.

### 5. Consolidate Operation Guidelines (`OP-xxx`)

Group multiple viewpoints into as few repeatable in-game operations as practicable. Every operation needs:

- **Purpose:** which guarantees are exercised together;
- **Setup:** controlled server, player, permission, config, or world conditions;
- **Operation:** numbered actions an operator can perform;
- **Verify:** concrete, human-observable PASS conditions, including absence of prohibited behavior;
- **Covers:** `VP`, `CB`, and `DP` IDs.

Add typical duration and troubleshooting/reproducibility notes only when useful. Prefer a single operation checking several outcomes over many isolated tests. Make preconditions and expected results explicit so a different operator can repeat the test.

### 6. Index Conditional Test Areas (`CT-xxx`)

Document platform-sensitive areas that merit **additional checks only if a relevant upstream change occurs**. For each area specify the triggering type of change, related `DP` IDs, possible user-visible regressions, and a targeted verification approach.

Candidate areas, when relevant, include region/entity scheduling, inventory/items, entity lifecycle, worlds/chunks, block states, tags, particles/sounds, events, persisted data/serialization, and commands/permissions. **Do not make `CT` entries part of every release's baseline checklist.**

### 7. Efficiency and consistency review

Before saving `TESTING.md`, verify that:

- each important `CB` traces to a relevant `DP`, `VP`, and at least one `OP` where runtime confirmation is warranted;
- every `OP` covers meaningful viewpoints, is practical and deterministic, and has objective PASS conditions;
- repeated setups and operations have been consolidated; low-value, automated-test-only, and speculative checks have been removed;
- negative behaviors with serious consequences are covered;
- source paths and behavior claims match current code.

Use [`references/testing-template.md`](references/testing-template.md) as the document structure. Treat it as durable design knowledge, **not** a version-specific test run.

## Role 2 — Identify Checks for a Minecraft / Paper Update

**Required inputs:** target repository source; its current `TESTING.md`; old and new Minecraft versions; old and new Paper versions/builds as applicable; and official upstream change information. If a version or source is missing, explicitly identify the gap rather than fabricate changes. When `TESTING.md` is missing or stale, explain the limitation and recommend or perform Role 1 first if authorized.

### 1. Load current test knowledge

Read all five sections of `TESTING.md` (`CB`, `DP`, `VP`, `OP`, `CT`) and validate them against current implementation. Pay attention to relevant platform calls and behavior paths not yet described.

### 2. Inspect version-specific upstream changes

Use official Minecraft release notes and Paper release notes/changelogs as primary evidence; consult official API documentation, API diffs, or upstream issues where necessary. Cite source URLs and the specific old → new versions/builds actually reviewed.

Classify material changes as **directly relevant**, **potentially relevant**, or **unrelated** based on the plugin's code, `DP` entries, and `CT` triggers. Do not simply summarize an entire changelog. Investigate a potentially relevant change far enough to establish or rule out an observable impact.

### 3. Trace impacts

For each candidate, establish:

**upstream change → dependency point → possible regression → core behavior → viewpoint → observable in-game failure**.

If this chain cannot be reasonably supported, do not add a manual check merely as a precaution. Say when an association is uncertain.

### 4. Define update-specific viewpoints (`UV-xxx`)

Record only checks genuinely added by this update, with the upstream reference, affected dependency, concrete regression risk, and planned operation.

For each `UV`, evaluate reuse in this order:

1. **As-is:** an existing `OP` already checks the risk.
2. **Verify-only:** append an extra observation to an existing `OP`.
3. **Modified:** minimally adjust an existing operation or setup.
4. **New:** add `NEW-OP-xxx` only if none of the above can expose the failure.

Use `UV` and `NEW-OP` IDs only inside this update's checklist; they are not permanent `TESTING.md` IDs.

### 5. Produce an ordered, executable checklist

Use [`references/update-checklist-template.md`](references/update-checklist-template.md). Include the runtime environment/startup check; necessary baseline `OP` actions with their normal pass criteria; inline extra checks for this update; new operations only where justified; a plugin-related log/exception check; and PASS/FAIL plus failure notes.

If one action covers both normal and update-specific checks, show those checks together under that action. If no additional viewpoints are justified, state that explicitly; still describe the ordinary checks to run. Do not mark checkboxes as completed based on analysis alone.

### 6. Record significant exclusions

In **Reviewed but No Additional Check**, briefly explain major seemingly relevant upstream changes that did *not* justify extra actions: unused API, compile-only compatibility, sufficient automated coverage, existing operation already covering the risk, or no observable regression path. Do not enumerate every unrelated changelog line.

## Maintenance — Feed Back Durable Findings

Keep these two information classes separate:

- **`TESTING.md`:** enduring plugin guarantees, dependency points, viewpoints, reusable operations, conditional change triggers, reproducibility notes, and generalizable lessons from actual regressions.
- **Update checklist:** particular Minecraft/Paper versions or builds, this update's upstream changes, `UV` IDs, one-off observations, and `NEW-OP` actions.

Update persistent `TESTING.md` only when the plugin behavior changes, a platform dependency changes, a significant regression reveals a missing durable viewpoint, an important dependency is discovered, or an operation proves unreliable or unable to catch a relevant failure. Carry over **the lasting test design insight**, not the release-specific instructions.

Keep existing `CB` / `DP` / `VP` / `OP` / `CT` IDs stable; do not repurpose deleted IDs. Use fresh IDs for new items and update all references. After editing, recheck the source-to-behavior-to-operation mapping.

## Completion Conditions

**Role 1:** implementation-aligned behaviors and dependencies; observable viewpoints; a small, reproducible set of operations with explicit PASS criteria; conditional areas; no unnecessary manual/automated duplication.

**Role 2:** cited upstream changes and impact mapping; only justified extra viewpoints; reuse of existing operations before new ones; ordered, concrete actions and pass conditions; exclusions explained; operator can record PASS/FAIL.

Example invocations:

- "Create in-game testing guidelines for this Paper plugin and write TESTING.md."
- "Review TESTING.md against the current source and simplify the test operations."
- "For the Minecraft/Paper update from [old] to [new], generate an additional in-game test checklist."
- "Incorporate enduring lessons from this test run into TESTING.md."
