# Minecraft / Paper End-to-End Testing Guidelines

This document defines when and how OKOCRAFT projects run end-to-end (E2E) tests against a real Paper server with real Minecraft protocol clients.

It complements [Testing Guidelines](java-testing.md), which owns unit and lightweight integration tests, and the [Minecraft / Paper In-Game Test Planning](../skills/minecraft-paper-test-planning/SKILL.md) skill, which decides **what** to verify. The [Minecraft / Paper End-to-End Testing](../skills/minecraft-paper-e2e-testing/SKILL.md) skill describes **how** to run it.

The key words **MUST**, **SHOULD**, and **MAY** have the same meaning as in the Testing Guidelines.

## 1. When to use E2E tests

E2E tests are slow and environment-heavy. Use them only for behavior that a lighter test cannot prove, which matches [Testing Guidelines §7.3](java-testing.md): plugin lifecycle, connected players, behavior spanning ticks, real entity or world state, and integration between plugins.

- A behavior that is deterministic outside a server MUST be covered by a unit or lightweight integration test instead.
- Compile-time compatibility alone is not a reason to run an E2E test.
- E2E tests SHOULD be run before a release, after changes to code paths that touch the platform, and for Minecraft/Paper updates that the planning skill marks as relevant. They are not part of the normal `test` task.

## 2. Separate planning from execution

Planning and execution are different activities and SHOULD be kept apart:

1. **Planning** produces observable viewpoints and operations (`VP-xxx`, `OP-xxx` in `TESTING.md`). It needs repository knowledge, not a running server.
2. **Execution** builds the environment, turns operations into executable scenarios, runs them, and reports what was observed.

Execution MUST start from planned operations. If `TESTING.md` is missing or stale, run the planning skill first, or state explicitly which ad-hoc viewpoints were used.

## 3. Evidence rules

An E2E result is only as good as the evidence behind it.

- A check MUST assert on what a client or the server actually produced: received chat or system messages, received packets, server log lines, entity or player state read back from the server. Building the plugin, reading code, or seeing a command succeed is not a pass.
- Every recorded result MUST carry its evidence (the observation, not a restatement of the expectation).
- Negative behavior ("this must NOT be delivered") MUST be paired with a control that shows the observation channel works, for example the same action outside the protected area.
- Compare with the platform's own behavior when the plugin claims to reproduce it (for example run the same scenario without the plugin).
- A result is `PASS`, `FAIL`, or `UNVERIFIED`. Anything not run, or run in a way that cannot support the claim, is `UNVERIFIED` with the reason. Never report it as `PASS`.
- Distinguish what was verified at the protocol or event level from what was seen on a real client. Headless bots cannot verify rendering.

## 4. Environment rules

- The test server runs with `online-mode=false`. It MUST bind only to a loopback address and MUST NOT be exposed. The shared harness refuses to start otherwise.
- Test-only plugins (such as the E2E helper) MUST NOT be installed on production servers.
- Every scenario SHOULD start from a fresh world and plugin data so results do not depend on earlier runs. Persistence checks restart the server on purpose and stop it gracefully.
- Use the real command and permission path for configuration under test (for example the plugin's own commands run by an operator bot) when that path is what users rely on. Use console commands and the helper plugin only to set up conditions.
- Pin and record the Minecraft, Paper, Java, dependency, and client versions used.

## 5. Protocol client limits

Bot libraries lag behind Minecraft releases. When a bot library does not support the server version, a supported client version MAY connect through a protocol translation layer (ViaVersion and ViaBackwards). If so:

- the report MUST state the translation and that client-visible behavior may differ from a native client;
- results that depend on translated data (for example packet shapes) SHOULD be cross-checked on the newest server version the bot supports natively when practical.

## 6. Reporting and follow-up

A report MUST include the tested commit, the environment and versions, per-check `PASS` / `FAIL` / `UNVERIFIED` with evidence, the commands or scenarios executed, defects found with reproduction steps and logs, and every `UNVERIFIED` item with its reason. The skill provides a template.

For a defect:

- report reproduction steps, evidence, suspected cause, and a minimal fix;
- verify a proposed fix on a scratch copy (rerun the failing scenario and a control) before presenting it as working;
- do not push, open pull requests, merge, or release without an explicit request.

Durable lessons (new viewpoints, unreliable operations, platform pitfalls) go back into `TESTING.md` through the planning skill's Maintenance workflow, not into the report.

## 7. Shared tooling

The reference harness (TypeScript, mineflayer) and the E2E helper plugin live in [okocraft/public-ops `paper-e2e`](https://github.com/okocraft/public-ops/tree/main/paper-e2e). Projects SHOULD use them instead of building their own, and propose improvements there. Paper/Folia thread ownership still applies: the helper plugin is Paper-only, so a Paper run does not establish Folia safety (see [Paper and Folia Scheduling and Threading](paper-folia-scheduling-and-threading.md)).

## 8. Review checklist

- [ ] The E2E test covers behavior that a lighter test cannot prove.
- [ ] Scenarios trace back to `OP-xxx` / `VP-xxx` (or the ad-hoc viewpoints are stated).
- [ ] Every result has evidence; negative checks have a control.
- [ ] Items that were not run are `UNVERIFIED` with a reason.
- [ ] The server is loopback-only; versions and any protocol translation are recorded in the report.
- [ ] No push, pull request, or release was made without an explicit request.
