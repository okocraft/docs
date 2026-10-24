# Game Test Guidelines

<!-- Fill in this template using evidence from the target plugin repository.
     Copy CB/DP/VP/OP/CT entries as needed, then remove these instructions
     and all unsubstantiated placeholder entries. Never pin temporary update
     details here. Preserve existing IDs and never reuse retired IDs. -->

## Scope

Describe the plugin's game-facing functionality covered by these guidelines, the boundary with automated tests, and any durable environment/setup assumptions.

## Core Behaviors

### CB-001: <Observable behavior name>

**Description:** <What the player or administrator is promised, including exclusions where relevant.>

**Importance:** <Why failure would matter to a release.>

**Related code:**
- `<repository-relative/path:relevant symbol>`

## Platform Dependency Points

### DP-001: <Platform mechanism>

**Platform:** Minecraft | Paper | Bukkit API

**Usage:** <How the plugin depends on this mechanism.>

**Affected behaviors:**
- CB-001

**Regression risks:**
- <Specific plausible observable failure caused by a changed mechanism.>

**Relevant APIs / concepts:**
- `<API or game concept actually used>`

**Related code:**
- `<repository-relative/path:relevant symbol>`

## Game Test Viewpoints

### VP-001: <Observable requirement>

**Verify:** <Exact in-game condition that must hold.>

**Related behaviors:**
- CB-001

**Related dependency points:**
- DP-001

**Failure examples:**
- <What the player/administrator would observe if it regresses.>

## Operation Guidelines

### OP-001: <Short, reproducible operation name>

**Purpose:** <The multiple viewpoints this operation checks.>

**Setup:**
1. <Required controlled environment, config, player, permissions, or fixed world state.>

**Operation:**
1. <Exact in-game action, with command or interaction as appropriate.>
2. <Any required follow-up action.>

**Verify / PASS criteria:**
- <Expected visible outcome with a clear time or stopping condition where relevant.>
- <Important side effect that must NOT happen, when relevant.>

**Covers:**
- VP-001
- CB-001
- DP-001

**Typical duration:** <Optional; omit if not meaningful.>

**Notes:** <Optional reproducibility caveats; omit if none.>

## Conditional Test Areas

<!-- Not routine tests. Include only areas tied to a real dependency point. -->

### CT-001: <Platform-sensitive area>

**Trigger:** <Type of Minecraft/Paper change that would justify extra checks.>

**Related dependency points:**
- DP-001

**Possible regressions:**
- <User-visible failure this change could cause.>

**Recommended verification:** <Prefer an existing OP, optionally with a precise additional observation.>

## Test Design Notes

<Any plugin-specific fixture, world setup, permission, tick timing, or reproducibility guidance that will remain useful across releases.>

## Maintenance Rules

Update this file when:
- A Core Behavior is added, removed, or materially changed.
- The plugin changes how it depends on Minecraft, Bukkit, or Paper.
- A regression reveals an important missing durable viewpoint or dependency.
- An existing operation fails to detect a meaningful problem.
- A setup or operation is found to be unstable or unnecessarily long.

Keep CB/DP/VP/OP/CT identifiers stable across revisions. Never reassign a deleted identifier. Do not store one-off update notes, temporary UV IDs, or version-specific NEW-OP actions in this file.
