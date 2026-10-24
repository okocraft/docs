---
name: minecraft-paper-e2e-testing
description: Run end-to-end tests of a Minecraft/Paper plugin against a real Paper server with real protocol clients (mineflayer bots), starting from the plugin's planned test operations, and report evidence-based PASS/FAIL/UNVERIFIED results. Use after planning with minecraft-paper-test-planning, or when asked to verify a plugin or a Minecraft/Paper update in a running server.
---

# Minecraft / Paper End-to-End Testing

Use this skill to **execute** in-game checks automatically: build a Paper test environment, connect bots over the real Minecraft protocol, run scenarios, and report what was observed. It does not decide what to test; that comes from planned operations (`OP-xxx` in the target repository's `TESTING.md`, produced by [Minecraft / Paper In-Game Test Planning](../minecraft-paper-test-planning/SKILL.md)).

Read the [E2E Testing Guidelines](../../guidelines/minecraft-paper-e2e-testing.md) first. They define when E2E is appropriate, the evidence rules, and the safety rules that this skill applies.

Tooling (TypeScript harness, helper plugin) lives in [okocraft/public-ops `paper-e2e`](https://github.com/okocraft/public-ops/tree/main/paper-e2e). Do not copy it into the target repository; use it from a checkout.

## Principles

- **Evidence over assertion.** A check passes only on something a client or the server produced. Never report a check as passed because it was planned, built, or reviewed.
- **Controls for negatives.** A "must not be delivered" check needs a control proving the observation channel works.
- **`UNVERIFIED` is a valid result.** Report what could not be run and why. Do not widen what a result proves.
- **Loopback only.** The test server is unauthenticated (`online-mode=false`). The harness refuses non-loopback binding; never work around it.
- **Do not publish without being asked.** Reproduce, diagnose, and propose a verified fix; push, open pull requests, merge, or release only on explicit request.
- Continue with the checks that can run when something in the environment fails. State exactly what was and was not confirmed.

## Stages

Run the stages in order. Each stage has a reference; read it when you reach the stage.

| Stage | Goal | Output | Reference |
| --- | --- | --- | --- |
| 0. Inputs | Know what to verify | Operations to run, target commit, versions | below |
| 1. Environment | A reproducible server, bots, and helper plugin | Prepared server directory, version record | [`environment.md`](references/environment.md) |
| 2. Scenarios | Turn operations into executable scenarios | One scenario per operation, with controls | [`scenarios.md`](references/scenarios.md) |
| 3. Execution | Run scenarios and collect evidence | `results.json`, `report.md`, server logs | [`environment.md`](references/environment.md) |
| 4. Report | Present results and defects honestly | Report following the template | [`report-template.md`](references/report-template.md) |

### Stage 0 — Inputs

1. Read the target repository's `TESTING.md` (`CB`, `DP`, `VP`, `OP`). If it is missing or stale, run the planning skill first, or tell the user which ad-hoc viewpoints you are using instead.
2. Record the target commit SHA (`git rev-parse HEAD`) and what changed.
3. Decide which operations to run: all baseline operations before a release, or only those affected by the change or by a Minecraft/Paper update.
4. Resolve ambiguities with the user instead of guessing when they change what is tested: target Minecraft/Paper version, plugins that must be present together, whether Folia matters (the helper plugin is Paper-only).

### Stage 1 — Environment

Build the server and bots as described in [`environment.md`](references/environment.md): Paper, the plugin under test and its dependencies, the helper plugin, and bots. Record every version.

### Stage 2 — Scenarios

Map each operation to a scenario as described in [`scenarios.md`](references/scenarios.md). Keep the mapping explicit (`OP-001` → `op-001-*.scenario.ts`). Saving scenarios in the target repository is optional; ask the user where they should live if they would be reused.

### Stage 3 — Execution

Run each scenario on a fresh server. Capture the console log and results. A scenario that throws is a `FAIL`; investigate whether the plugin or the scenario is wrong before reporting. Repeat a failing scenario once with logging before concluding. Do not retry until it passes.

### Stage 4 — Report

Write the report with [`report-template.md`](references/report-template.md). Include versions, protocol translation, evidence, defects with reproduction steps, and every unverified item with its reason. For defects, give a suspected cause and a minimal fix; verify the fix on a scratch copy before saying it works. Feed durable findings back into `TESTING.md` through the planning skill's Maintenance workflow.

## Completion Conditions

- Every executed operation has a result with evidence, and negatives have controls.
- Anything not run is listed as `UNVERIFIED` with the reason.
- Versions, the target commit, and any protocol translation are recorded.
- No code was pushed and no pull request was opened unless the user asked.
