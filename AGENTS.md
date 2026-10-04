# OKOCRAFT Agent Instructions

This file is the shared baseline for coding agents working in OKOCRAFT repositories.

Keep it as a short map and set of cross-cutting invariants. Detailed policy belongs in `okocraft/docs`; repository- or module-specific instructions should add only the context needed for that scope.

## How to Work

- Investigate before changing code or making claims about it. Read the relevant files, tests, and nearby configuration instead of guessing.
- Read only the guidance relevant to the task. Do not preload every guideline or repository document for small changes.
- Follow established local patterns when they are compatible with the applicable OKOCRAFT guideline and platform contract.
- Keep the change focused. Do not migrate or refactor unrelated working code solely for stylistic consistency.
- Preserve existing public APIs, configuration, persistent data, message keys, and operator workflows unless the task intentionally changes them.
- For complex or multi-stage work, keep a lightweight plan and update it as evidence changes. Do not require planning artifacts for trivial edits.
- Within the available permissions, continue through implementation and relevant non-destructive verification without asking for approval at every routine step.
- Ask when a decision materially changes scope, compatibility, externally visible behavior, or requires an irreversible/destructive action that was not requested.

When the agent harness supports hierarchical instructions, use the most specific applicable repository or module instructions. If instructions conflict or would weaken a correctness, security, lifecycle, or compatibility invariant, surface the conflict instead of guessing.

## Canonical Guidance

Read the detailed guideline only when the task touches that concern:

| Concern | Source of truth |
| --- | --- |
| Java project structure, Gradle, dependencies, CI, Renovate | [Java Project, Gradle, and CI](https://github.com/okocraft/docs/blob/main/dev/guidelines/java-project-gradle-and-ci.md) |
| Test design and scope | [Testing](https://github.com/okocraft/docs/blob/main/dev/guidelines/java-testing.md) |
| Paper/Folia scheduling, threading, async boundaries | [Paper and Folia Scheduling and Threading](https://github.com/okocraft/docs/blob/main/dev/guidelines/paper-folia-scheduling-and-threading.md) |
| Plugin lifecycle and long-lived resources | [Plugin Lifecycle and Resource Ownership](https://github.com/okocraft/docs/blob/main/dev/guidelines/plugin-lifecycle-and-resource-ownership.md) |
| Configuration, validation, reload | [Configuration and Reload](https://github.com/okocraft/docs/blob/main/dev/guidelines/configuration-and-reload.md) |
| User-facing wording and localization | [Message Formatting](https://github.com/okocraft/docs/blob/main/dev/guidelines/message-formatting.md) |
| Java message declarations and translation loading | [Java Messages and Localization](https://github.com/okocraft/docs/blob/main/dev/guidelines/java-messages.md) |

Do not duplicate a detailed guideline into local agent instructions. Point to the source of truth and add only repository-specific exceptions or facts.

## Cross-cutting Invariants

- New code and materially changed code SHOULD follow current guidelines. Existing working code does not need migration solely for consistency.
- Do not introduce an abstraction without a real boundary or repeated need.
- Keep common/shared modules free of platform APIs unless the module intentionally owns that platform dependency.
- Verify current upstream documentation or source before relying on a changing external contract such as Paper, Folia, Velocity, Gradle, Configurate, Adventure, or GitHub Actions.
- Do not treat incidental runtime implementation details as supported platform contracts.
- Every long-lived task, registration, executor, pool, client, or other resource MUST have a clear owner and retirement path.
- Replacement and reload logic MUST have a clear commit point. Failure before commit leaves the previous working state active; cleanup failure after commit is not implicit rollback.
- Tests SHOULD verify observable behavior with the lightest environment that proves it correctly.
- A bug fix SHOULD include a regression test when the behavior is deterministic and reasonably testable.
- Do not encode transient Java, Minecraft, dependency, or tool versions as organization policy unless the version itself is the intended rule.

## Paper, Folia, and Velocity

When relevant, read the scheduling and lifecycle guidelines before implementation.

- Paper-only or Paper/Folia code SHOULD call Paper scheduling APIs directly. Do not add a Paper-vs-Folia scheduler wrapper merely to select scheduler implementations.
- Introduce a scheduler abstraction when shared application logic genuinely crosses platform boundaries, such as Paper and Velocity.
- Access region-owned entity/player state on the entity scheduler; location/block/chunk state on the region scheduler; explicitly global-region-owned state on the global scheduler; blocking I/O off tick-owning schedulers.
- The global region scheduler is not a universal main thread.
- Async code MUST NOT read or mutate region-owned state unless the platform contract permits it.
- Outbound-only operations known to be safe off-thread, such as sending an already-constructed Adventure message without reading player/world state, MAY remain async. Do not generalize this to the `Player` API as a whole.
- A `JavaPlugin` constructor MUST NOT perform platform-dependent initialization or acquire runtime resources.

## Configuration and Messages

When relevant, read the corresponding detailed guideline before implementation.

- Paper-side configuration SHOULD use Paper's Configurate runtime; the Paper artifact MUST NOT bundle its own Configurate runtime.
- Validate and prepare configuration before publication. Do not overwrite administrator-edited configuration merely to regenerate defaults.
- English is the semantic source of truth for user-facing messages, and new message systems MUST support English and Japanese by default.
- Keep localizable text out of application logic. New Java message systems SHOULD follow the current OKOCRAFT `mcmsgdef` architecture and use named placeholders.

## Completion

A coding task is complete when the requested behavior is implemented and the available evidence supports it.

Before finishing:

1. run the repository's relevant tests, build, lint, or other verification commands;
2. fix failures caused by the requested change and rerun the affected checks;
3. review the final diff for unintended scope, compatibility changes, and generated or temporary files;
4. report verification that could not be run and why; and
5. summarize material behavior or compatibility implications.

Do not publish, release, deploy, merge, or perform destructive data changes unless the user or repository workflow explicitly requires it.

## Maintaining These Instructions

Keep this file concise and provider-neutral.

- Prefer a conditional rule ("when changing configuration, ...") over an unconditional instruction that consumes context on unrelated tasks.
- Prefer positive, executable guidance over long lists of prohibitions.
- Move workflow-specific detail to the canonical guideline, repository documentation, or scoped local instructions.
- Remove stale, redundant, or model-specific scaffolding when current agents no longer need it.
- Do not add a rule unless it changes an agent decision that cannot be reliably inferred from the code, task, or linked documentation.
