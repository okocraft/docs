# OKOCRAFT AGENTS.md

This document defines the shared development instructions for coding agents working in OKOCRAFT repositories.

It is intended to be reusable across the organization. A repository MAY add more specific instructions for its own architecture, platform, build, or release process. Repository-specific instructions take precedence where they are more specific, but they SHOULD NOT weaken correctness, security, lifecycle, or compatibility requirements defined by the shared guidelines.

## Canonical Guidelines

The complete organization guidelines live in `okocraft/docs`:

- [Java Project, Gradle, and CI Guidelines](https://github.com/okocraft/docs/blob/main/dev/guidelines/java-project-gradle-and-ci.md)
- [Testing Guidelines](https://github.com/okocraft/docs/blob/main/dev/guidelines/java-testing.md)
- [Paper and Folia Scheduling and Threading Guidelines](https://github.com/okocraft/docs/blob/main/dev/guidelines/paper-folia-scheduling-and-threading.md)
- [Plugin Lifecycle and Resource Ownership Guidelines](https://github.com/okocraft/docs/blob/main/dev/guidelines/plugin-lifecycle-and-resource-ownership.md)
- [Configuration and Reload Guidelines](https://github.com/okocraft/docs/blob/main/dev/guidelines/configuration-and-reload.md)
- [Message Formatting Guidelines](https://github.com/okocraft/docs/blob/main/dev/guidelines/message-formatting.md)
- [Java Message Definitions and Localization](https://github.com/okocraft/docs/blob/main/dev/guidelines/java-messages.md)

Use those documents as the source of truth when a task touches the corresponding area. This file summarizes the defaults that most implementation work should follow.

## 1. Before Making Changes

Before editing code:

1. Read the repository's own `AGENTS.md`, README, build files, and relevant module structure.
2. Identify the target platforms and runtime boundaries, such as Paper, Folia, Velocity, or shared code.
3. Inspect nearby code and tests before introducing a new abstraction or pattern.
4. Prefer an existing project or organization convention when it already solves the problem correctly.
5. Verify current upstream behavior when the change depends on an external API or tool whose contract may have changed.

Do not infer an organization-wide rule from a single repository when implementations differ across projects.

Do not refactor unrelated code merely to make it match a newer preferred style.

## 2. Scope and Migration

Shared guidelines define defaults for new code and code being materially changed.

Existing working implementations do not need to be migrated solely for stylistic consistency. Migrate when there is a concrete correctness, compatibility, security, or maintainability benefit.

Preserve compatibility with existing public APIs, persistent data, configuration files, message keys, and operator workflows unless the task explicitly changes that contract.

## 3. Change Discipline

Keep changes focused on the requested behavior.

- Do not introduce abstractions without a real boundary or repeated need.
- Prefer small, explicit components over frameworks created for hypothetical future use.
- Preserve established naming and module boundaries unless changing them is part of the task.
- Avoid broad cleanup in the same change as a behavioral fix unless the cleanup is necessary to make the fix correct.
- Keep shared/common modules free from platform APIs unless the module intentionally owns that platform dependency.

When a change crosses modules or platforms, make ownership and data flow explicit.

## 4. Java Projects, Build, and Dependencies

New Java projects SHOULD use Gradle with the Kotlin DSL. Existing supported Maven projects do not need to migrate solely for consistency.

For Gradle projects:

- use the Gradle Wrapper;
- prefer the established OKOCRAFT Gradle plugins when they already provide the required convention;
- use version catalogs for non-trivial dependency sets;
- choose the narrowest dependency scope that matches the runtime and public API contract; and
- keep platform-specific dependencies in platform-specific modules.

Do not bundle a dependency merely because it happens to simplify local resolution. If the target platform contract or an explicit OKOCRAFT policy provides a dependency to plugins, do not package another copy into that platform artifact.

Do not hard-code current Java, Minecraft, dependency, or tool versions into shared policy. Use the versions selected by the repository and current platform requirements.

Use reusable workflows from `okocraft/workflows` and shared Renovate presets from `okocraft/renovate-config` where applicable.

## 5. Testing

Test observable behavior rather than implementation details.

Use the lightest test environment that can verify the behavior correctly.

Tests SHOULD cover relevant:

- successful behavior;
- failure behavior;
- boundary values;
- lifecycle transitions;
- replacement or reload failure;
- concurrency behavior where shared state is involved; and
- platform adapters where the platform contract is part of the behavior.

Do not add mocks merely to reproduce an entire Paper or Velocity runtime. Separate project-owned logic from platform boundaries so the logic can be tested directly.

A change that fixes a reproducible bug SHOULD include a regression test when the behavior can be tested deterministically.

Use the repository's documented build or verification command before considering the change complete.

## 6. Paper and Folia Scheduling

For Paper-only or Paper/Folia code, use Paper's scheduling APIs directly. Do not create a Paper-vs-Folia scheduler abstraction merely to select different scheduler implementations.

Introduce a scheduling abstraction when application logic genuinely crosses platform boundaries, such as shared Paper and Velocity code.

Choose the scheduler according to the platform state being accessed:

- region-owned entity or player state: entity scheduler;
- location, block, or chunk state: region scheduler;
- state explicitly owned by Folia's global region: global region scheduler;
- blocking I/O or work independent of tick-owned state: async scheduler.

The global region scheduler is not a universal main thread.

Async code MUST NOT read or mutate region-owned state unless the platform contract explicitly permits that operation.

Outbound-only player operations MAY be performed asynchronously when they do not read or mutate region-owned player, entity, world, or chunk state and the operation is known to be safe off-thread. Sending an already-constructed Adventure message is a typical example. Do not generalize this exception to the `Player` API as a whole.

When crossing an async boundary:

1. capture required platform state on its owner;
2. convert it to immutable or independently thread-safe data;
3. perform blocking work asynchronously;
4. schedule state-changing results back to the correct owner; and
5. revalidate assumptions before applying the result.

Do not synchronously wait for another region or async operation from a tick-owning scheduler.

Shared mutable state accessed by multiple regions or async tasks MUST have an explicit concurrency model.

## 7. Task and Resource Lifecycle

Every long-lived resource MUST have an identifiable owner responsible for retirement. The platform MAY be the owner when its lifecycle contract guarantees cleanup.

This applies to:

- scheduled tasks;
- executors and threads;
- database pools and clients;
- listeners and subscriptions;
- translation sources;
- external plugin integrations;
- caches with background work;
- static/global registrations; and
- other resources that can outlive a method call.

The component that acquires or registers a resource owns it unless ownership is explicitly transferred.

A task MUST be cancelled or otherwise made unable to affect obsolete state when its feature or runtime state is disabled, replaced, or reconfigured.

A `JavaPlugin` constructor MUST NOT perform platform-dependent initialization or acquire runtime resources. Use the appropriate bootstrap/lifecycle API, `onLoad`, or `onEnable`.

Startup code must handle partial initialization. If required initialization fails, clean up resources already acquired and fail closed rather than leaving a partially active plugin.

Shutdown and cleanup SHOULD be idempotent where practical. Continue cleanup after one independent resource fails to close.

Stop producers of work before closing the resources or consumers they depend on.

## 8. Configuration and Reload

Paper-side configuration SHOULD use the Configurate runtime provided by Paper.

A Paper plugin artifact MUST NOT bundle or shade its own Configurate runtime. A module that imports Configurate still needs an appropriate compile-time-only dependency when shared build logic does not supply one.

Prefer typed configuration models over scattered raw node access.

Configuration must be validated before becoming active.

Treat reload as prepare then commit:

1. read and deserialize the next configuration;
2. validate and normalize it;
3. prepare dependent state where possible;
4. publish the new coherent runtime state at a clear commit point; and
5. retire the previous state.

Before the commit point, failure MUST leave the previous runtime state active and newly prepared resources must be retired.

After the commit point, failure while retiring old resources is a cleanup failure; do not claim rollback unless the implementation actually provides it.

Do not overwrite administrator-edited configuration merely to regenerate defaults or normalize formatting.

Avoid blocking configuration file I/O on Folia region, entity, or global tick threads when it can be performed asynchronously.

## 9. User-facing Messages and Localization

English is the semantic source of truth for user-facing messages.

New message systems MUST support English and Japanese by default.

Keep localizable user-facing text out of application logic. Declare messages through the project's message layer and send message keys/components from commands, listeners, services, and GUI code.

For new Java message systems, prefer the current OKOCRAFT `mcmsgdef` architecture:

- English defaults declared in Java;
- named MiniMessage arguments;
- Japanese defaults in language resources;
- runtime-editable language files;
- missing defaults appended without overwriting existing administrator values; and
- one registered Adventure translation source per plugin message system.

Use named placeholders for new systems. Preserve the same placeholder set across translations while allowing natural word order.

Do not translate machine-facing commands, permissions, identifiers, file names, or literal values.

For Japanese:

- use natural Japanese rather than word-for-word translation;
- use polite `です・ます` style for normal sentences;
- use `。` for complete sentences and omit terminal punctuation for labels/headings;
- keep numeric counters and units naturally attached, such as `<amount>個` and `<seconds>秒`.

Preserve legacy placeholder or color syntax when an existing parser requires it. Do not migrate legacy message formats as an unrelated side effect.

## 10. External APIs and Current Behavior

When implementation correctness depends on Paper, Folia, Velocity, Gradle, Configurate, Adventure, GitHub Actions, or another external system, verify the current contract before making a normative or architectural decision.

Prefer official upstream documentation or source.

Do not rely on incidental runtime implementation details as if they were a supported API contract.

Do not copy a concrete dependency or Java version from shared documentation; use the repository's approved version source.

## 11. Review Before Completion

Before considering a change complete, verify that:

- the implementation follows repository-local instructions and the applicable shared guidelines;
- no unrelated migration or refactor was introduced;
- platform/thread ownership is correct;
- long-lived resources have retirement behavior;
- reload/replacement failure leaves runtime state coherent;
- tests cover the changed behavior where practical;
- the repository's verification command succeeds or any inability to run it is clearly reported;
- user-facing messages follow localization conventions;
- platform-provided dependencies are not bundled accidentally; and
- documentation and examples do not encode transient versions as permanent policy.

For pull requests, summarize the behavioral change, important design decisions, verification performed, and any compatibility or migration impact.
