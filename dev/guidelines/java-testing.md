# Testing Guidelines

This document defines the testing standards for okocraft Java, Paper, and Velocity projects.

The goal is to verify behavior that can regress as the code changes without unnecessarily coupling tests to implementation details or heavyweight runtime environments.

## 1. Requirement Language

The key words **MUST**, **SHOULD**, and **MAY** indicate requirement strength:

- **MUST**: Required unless an exceptional constraint makes compliance impossible.
- **SHOULD**: Expected unless there is a specific, documented reason not to follow it.
- **MAY**: Optional; use when appropriate for the behavior under test.

## 2. Core Principles

Tests should:

1. produce the same result locally and in CI;
2. use the lightest environment that can verify the behavior correctly;
3. distinguish platform or external-API boundaries from project-owned logic;
4. cover failure and boundary behavior as well as successful behavior; and
5. make the guaranteed behavior understandable from the test itself.

Coverage percentage is not a goal by itself. Do not add tests solely to increase line coverage.

### 2.1 Verify Observable Behavior

Prefer assertions about behavior that is meaningful to callers, users, or external systems. Typical examples include:

- return values;
- state changes;
- messages sent to a player or command sender;
- event cancellation state;
- inventory or equipment changes;
- scheduler registration and cancellation propagation;
- config-file creation, preservation, and reload behavior; and
- command availability, execution results, and suggestions.

**SHOULD:** Prefer assertions about externally observable behavior over assertions about object structure, incidental intermediate state, or internal call structure.

Avoid assertions about implementation details with no external meaning, such as the number of calls to a private method.

### 2.2 Use the Lightest Sufficient Environment

Use the least expensive environment that can correctly verify the behavior.

| Test type | Typical targets | Preferred approach |
| --- | --- | --- |
| Pure unit test | Calculation, parsing, value conversion, state transition | Real objects + JUnit |
| Boundary unit test | Bukkit / Paper / Velocity APIs, scheduler, event, sender | Mockito |
| Lightweight Paper test | `ItemStack`, data components, registries, Paper argument types | `TestServer` + real objects |
| Multi-component collaboration test | Command tree, menu transaction, editor workflow | Production classes + minimal mocks |
| Full-server test | Behavior that inherently requires world, tick, network, or plugin lifecycle | Separate task from the standard `test` suite |

**MUST:** Do not use a full-server test for behavior that can be verified without starting a full server.

**MUST:** Do not mock a type merely because it belongs to the Paper API. Prefer real value objects, such as a real `ItemStack`, when they can be used safely in the lightweight environment.

**MUST:** Do not treat behavior that depends on real server ticks, worlds, networking, or plugin lifecycle as verified by the lightweight `TestServer`.

## 3. Standard Test Infrastructure

### 3.1 JUnit and Mockito

Use JUnit Jupiter as the standard test framework and Mockito as the standard mocking library.

**MUST:** Manage JUnit and Mockito versions through the version catalog rather than declaring unrelated versions in individual projects.

**SHOULD:** Add another test library only when a recurring problem is difficult to express with JUnit, Mockito, or the standard library.

### 3.2 Lightweight `TestServer`

Some Paper APIs require Minecraft registry initialization even when the behavior does not require a running server. Use the test-only `TestServer` for these cases so tests can exercise real Paper value objects without starting a world, network stack, tick loop, or plugin lifecycle.

Paper-related tests should use automatic `TestServer` initialization rather than calling `TestServer.setUp()` individually.

**MUST:** Implement `TestServer` bootstrap so it can run at most once per JVM.

**MUST:** Keep Paper and Minecraft internal APIs required for bootstrap inside `testsupport`; ordinary tests must not reference those internals directly.

**SHOULD:** Keep a smoke test for `TestServer` so Paper upgrades fail at a diagnosable boundary. At minimum, verify that a real `ItemStack` and one registry-dependent feature work.

**SHOULD:** Avoid distributing `TestServer` as a shared binary library while repositories upgrade Paper independently. Share it only when the relevant repositories can keep their Paper versions aligned.

**MAY:** If the same bootstrap must be maintained in three or more repositories, consider extracting it as a source template, Gradle convention, or version-aligned test-fixture module.

Implementation-specific bootstrap details belong in the non-normative reference notes rather than in the testing policy itself.

### 3.3 `testsupport`

Put only reusable, meaningful testing concepts in `testsupport`.

Typical examples include:

- `CommandTester`, which executes the real command tree through a Brigadier dispatcher;
- `TestSources`, which creates consistent sender, executor, and permission states;
- `TestIds`, which provides fixed identifiers; and
- `TestServer`, which hides registry bootstrap details.

**MUST:** Use `testsupport` to improve test readability, not to hide weaknesses in production API design behind a large test abstraction layer.

**SHOULD:** Consider extracting a helper when roughly the same meaningful setup appears in three or more places.

**SHOULD:** Name helpers after domain meaning rather than Mockito mechanics, for example `grant(...)`, `deny(...)`, or `authorizedViewer(...)`.

## 4. Test Structure and Design

### 4.1 Placement and Naming

Place tests in the same package structure as the corresponding production code.

Use `<TargetClassName>Test` as the default class name. When a concern needs to be separated, make that responsibility explicit in the suffix, for example:

- `PTimeCommandTest`
- `PTimeCommandPermissionTest`
- `EquipmentMenuAccessTest`
- `EquipmentMenuTransactionTest`
- `ArmorStandMenuLifecycleTest`
- `EditModeIntegrationTest`

**SHOULD:** Split a large test class by behavioral boundary, such as permission, transaction, or lifecycle, rather than by line count alone.

For test methods, prefer consistency with the existing codebase: `test` followed by the expected behavior.

```java
@Test
void testCommandIsHiddenWithDeniedPermission() {
}

@Test
void testLoadKeepsExistingFileUntouched() {
}
```

**MUST:** Do not use names such as `test1`, `works`, or `success` that fail to identify what behavior broke.

**SHOULD:** Include important preconditions in the name when they materially affect the scenario. Clauses such as `When...`, `With...`, `Without...`, and `On...` are acceptable.

### 4.2 One Scenario per Test

Each test should verify one scenario and its outcome. Multiple related assertions are appropriate when they describe the same behavior.

For example, one command execution may reasonably verify that:

- the command result is `1`;
- editor state changes; and
- a success message is sent to the player.

Do not combine separate scenarios, such as a successful path and a permission-denied path, in one test.

### 4.3 Keep Arrange, Act, and Assert Visible

Comments are optional, but setup, execution, and verification should be easy to distinguish from the code structure.

```java
Player player = playerWithPermission(Permissions.COMMAND_AXIS);
CommandSourceStack source = source(player);

execute(ArmorStandEditorCommand.axis(), source, "axis y");

Assertions.assertEquals(Axis.Y, PlayerEditorProvider.getEditor(player).getAxis());
Mockito.verify(player).sendMessage(Messages.COMMAND_AXIS_CHANGE.apply(Axis.Y));
```

**SHOULD:** Avoid filling the setup phase with assertions before exercising the subject under test, except when a fixture assumption itself must be verified.

### 4.4 Prefer Real Values; Mock Boundaries

Prefer real values for pure Java objects and Paper values that can be used safely with `TestServer`.

Typical real-value candidates include:

- `Instant`, `LocalTime`, `ZoneId`, and `Duration`;
- simple values such as `EulerAngle` and `Location`;
- `ItemStack` and item data;
- real config files under a temporary directory; and
- Brigadier `CommandDispatcher`.

Mocks are most appropriate at boundaries such as:

- `Player`, `CommandSender`, and `Server`;
- Bukkit, Paper, and Velocity schedulers;
- events;
- plugins; and
- APIs tied to world or entity lifecycle.

**MUST:** Do not mock something merely because it is a dependency. If the value itself is part of the behavior being tested, use the real value when practical.

Use Mockito `verify` when interaction with an external API is part of the contract, for example when:

- a message must be sent;
- an event must be cancelled;
- equipment must change; or
- a scheduled task's `cancel()` must be called.

**SHOULD:** Do not lock down detailed internal call order in production classes.

**MAY:** Use `InOrder` when ordering itself is part of the contract, such as notification order.

**MAY:** Use `ArgumentCaptor` or `argThat` when an argument is important but cannot otherwise be inspected directly.

Stub only the interactions required by the subject under test.

**MUST:** Do not create unused stubbing merely to make a mock appear realistic.

**SHOULD:** If one mock starts stubbing many unrelated methods, consider whether the production code needs clearer responsibility boundaries before adding more test helpers.

Use `verifyNoMoreInteractions()` only when additional interaction would itself violate the contract. Applying it universally makes tests unnecessarily sensitive to refactoring.

### 4.5 Limit Static Mocking

`Mockito.mockStatic` is acceptable for isolating static boundaries in existing designs, but it should not be the default for new code.

**SHOULD:** For new code, prefer injecting a small replaceable collaborator or platform abstraction when practical.

**MUST:** Scope static mocks with try-with-resources.

```java
try (MockedStatic<Bukkit> bukkit = Mockito.mockStatic(Bukkit.class)) {
    // Stub and execute.
}
```

### 4.6 Failure and Boundary Cases

A behavior is not considered adequately tested when only its successful path is covered.

For each change, add at least one applicable failure or boundary case. Examples include:

- null, empty, or missing input;
- invalid format;
- permission denied or unset;
- missing target entity;
- no inventory space;
- a game mode in which the operation is rejected;
- scheduler rejection;
- reload or file-read failure;
- an operation that must preserve existing state;
- value wrap-around; and
- timezone or DST boundaries.

When an exception is expected, also verify that no invalid side effect occurred before the exception when that distinction matters.

## 5. Target-Specific Guidelines

### 5.1 Pure Logic

For calculations, conversions, parsers, schedules, and state machines, prefer tests without mocks.

**MUST:** Include meaningful boundary values rather than testing only representative successful values.

Examples include:

- forward and reverse direction;
- first, last, and wrap-around values;
- empty input;
- invalid input;
- DST gaps and overlaps; and
- preserving the original object when mutation is not part of the contract.

When the same property is tested across a set of inputs, `@ParameterizedTest` is appropriate. Prefer parameterization over copying cases that differ only in test data.

### 5.2 Commands

Test commands through the real Brigadier command tree whenever practical instead of calling handler methods directly.

This allows the same test surface to cover:

- node permissions;
- sender and executor constraints;
- argument parsing;
- command result; and
- suggestions.

A thin `CommandTester` adapter per Paper or Velocity platform is recommended.

For each command, cover the applicable cases:

1. successful execution;
2. permission unset;
3. permission explicitly denied;
4. only a similar but different permission is granted;
5. a console executes a player-only command;
6. self-targeting versus targeting another player;
7. invalid arguments;
8. suggestion visibility;
9. success and failure messages; and
10. resulting state changes or external-API side effects.

**SHOULD:** When permissions have a hierarchy or an `others` concept, verify independence between permissions in dedicated tests.

### 5.3 Event Listeners

For event listeners, no-op conditions are as important as the successful path.

Explicitly test relevant early-return conditions, for example:

- interaction is from the off hand;
- action type is not applicable;
- the item is not the edit tool;
- permission is missing; or
- entity type is not applicable.

**SHOULD:** For ignored cases, verify both that state is unchanged and that important side effects did not occur.

```java
Mockito.verify(event, Mockito.never()).setCancelled(true);
Assertions.assertEquals(Axis.X, editor.getAxis());
```

### 5.4 Menu and Inventory Transactions

Inventory behavior has many branches. Test the transition from an input operation to the final inventory or equipment state.

Separate concerns where useful:

- **access**: who may operate the menu;
- **transaction**: how items move;
- **lifecycle**: open, close, and invalidation behavior; and
- **provider**: sharing or reusing a menu for the same target.

**MUST:** Do not combine conditions whose behavior differs by game mode, such as survival, creative, and spectator.

**SHOULD:** Test Minecraft-specific interactions such as cursor, hotbar, offhand, and clone as separate scenarios when they have distinct behavior.

### 5.5 Platform Adapters and Schedulers

For adapters that abstract Paper, Velocity, or Folia differences, verify both platform-API selection and lifecycle propagation for returned tasks.

Examples include:

- delay `0` uses `runNow`;
- non-zero delay uses `runDelayed`;
- repeating tasks receive the correct interval;
- wrapper `cancel()` propagates to the platform task's `cancel()`; and
- teleport paths switch correctly between Folia and non-Folia environments.

**MUST:** Never wait for real time in scheduler tests.

### 5.6 Config and Resources

For config behavior, verify the file-level contract in addition to Java object field values.

Use JUnit `@TempDir` for tests involving config files or generated files.

**MUST:** Do not depend on real files in the repository or on a user- or environment-specific temporary directory.

**SHOULD:** Where applicable, verify the file lifecycle, including:

- preserving an existing file;
- writing initial content when a file is missing;
- creating parent directories;
- handling an empty file or empty map;
- failing on invalid format; and
- reading back content that was written.

For language resources, verify at least that:

- all bundled locales have the same key set; and
- every translation key generated by production code exists in every locale.

Snapshot the complete contents of a resource only when formatting itself is part of the contract.

### 5.7 State, Copy, and Data Objects

For state objects such as editor state or armor stand data, verify:

- initial state;
- state after mutation;
- copies preserving all required values;
- mutable values being cloned rather than shared when necessary; and
- reset or unload operations removing residual state.

## 6. Determinism and Isolation

### 6.1 Time and Asynchronous Behavior

**MUST:** Do not use `Thread.sleep` in tests.

**MUST:** For logic that depends on the current time, inject or specify `Clock`, `Instant`, `Duration`, or an equivalent deterministic time source.

Use fixed values such as `Clock.fixed(...)` or a fixed `Instant`. Where relevant, use real boundary data such as DST gaps and overlaps.

For scheduler abstractions, use one of the following instead of waiting for real time:

- a test scheduler that executes immediately;
- a mock of the scheduler API; or
- verification that cancellation propagates to the returned task object.

### 6.2 Randomness and Environment-Dependent Data

Test data must be reproducible and meaningful to the reader.

**MUST:** Do not use random UUIDs, the current wall-clock time, an environment-dependent locale, or unseeded randomness when those values can affect test behavior.

**MUST:** When production behavior depends on randomness, make the test deterministic by injecting the random source or by using a fixed seed.

**SHOULD:** When randomized test data is intentionally used, make the seed reproducible so a failure can be rerun with the same input sequence.

**SHOULD:** When identity itself is not important, use fixed values such as those in `TestIds`.

**SHOULD:** Keep values needed to understand an assertion visible in the test. Avoid over-abstraction that forces readers to follow many helpers to understand a case.

### 6.3 Test Independence and Shared State

Tests must be independently executable.

**MUST:** Tests must not depend on execution order or on another test having run before them.

**MUST:** Each test must establish the mutable state required for its scenario rather than relying on state produced by another test.

**MUST:** Restore production static state changed by a test, for example in `@AfterEach`.

```java
@AfterEach
void tearDown() {
    PlayerEditorProvider.unloadAll();
}
```

JVM-wide one-time initialization such as registry bootstrap is an exception, but individual tests should not mutate that shared initialization state.

### 6.4 Flaky Tests

A flaky test is a defect in the test, its fixture, the test infrastructure, or the behavior under test. It must not be normalized as an expected CI condition.

**MUST:** Do not hide flaky tests with CI-only sleeps, retries, or execution-order dependencies.

**SHOULD:** Fix the root cause of a flaky test rather than making retries part of the permanent test strategy.

## 7. Coverage, CI, and Full-Server Tests

### 7.1 Coverage Policy

Do not set a repository-wide numeric coverage target.

Evaluate test completeness based on changed behavior and regression risk rather than a percentage. For each pull request, ask whether:

- every new meaningful branch is exercised by a meaningful test;
- a bug fix has a regression test that fails before the fix;
- newly introduced permission or failure paths are tested;
- platform-specific branches are verified on each relevant path; and
- a public behavior change is explained by the test name and scenario rather than only by changing an assertion value.

If a coverage tool is introduced, use it first as a diagnostic for locating untested areas, not as a repository-wide percentage gate.

### 7.2 Local and CI Execution

Use the repository Gradle wrapper for standard verification:

```bash
./gradlew test
```

For pull-request CI, prefer the following as the authoritative command when other checks are also included:

```bash
./gradlew check
```

**MUST:** Use the repository Gradle wrapper rather than a system-installed Gradle.

**MUST:** Keep the same test task runnable locally and in CI.

Because registry bootstrap may rely on JVM-wide state, enable test parallelization only after confirming the thread safety of `TestServer` and the relevant Paper internals.

### 7.3 When to Add Full-Server Tests

Keep the standard suite focused on unit and lightweight integration tests.

Add a separate full-server test task only when the behavior inherently requires capabilities such as:

- plugin enable or disable lifecycle;
- entity lifecycle in a real world;
- behavior spanning server ticks;
- networking or connected players;
- real Paper or Folia scheduler thread ownership; or
- real integration with another plugin.

When introduced, keep full-server tests separate from the normal `test` task, for example under an `integrationTest` task. Prioritize keeping the normal test suite fast and stable.

## 8. Pull Request Checklist

Before opening a pull request, verify the following for new or changed tests:

- [ ] The test name identifies the behavior that would be broken if the test failed.
- [ ] The test uses the lightest environment that can verify the behavior correctly.
- [ ] Assertions focus on observable behavior rather than incidental implementation details.
- [ ] Real values are used where they are more appropriate than mocks.
- [ ] Mocks are concentrated at platform, I/O, lifecycle, or similar boundaries.
- [ ] The change includes an applicable failure or boundary case in addition to the successful path.
- [ ] If permissions are involved, unset, denied, and allowed states have been considered.
- [ ] Time and asynchronous behavior do not depend on `Thread.sleep` or wall-clock time.
- [ ] Randomness that affects behavior is deterministic or injected.
- [ ] The test can run independently of test execution order.
- [ ] Any modified static state is restored after the test.
- [ ] Static mocks are scoped with try-with-resources.
- [ ] A full server is not required merely because the test needs Paper registry initialization.
- [ ] A bug fix includes a regression test that fails before the fix.
- [ ] A flaky test is fixed at its root cause rather than masked with permanent retries.

## Appendix A. Reference Implementation Notes

> This appendix is **non-normative**. It records implementation details and repository snapshots that informed these guidelines. These details may change without changing the policy above.

### A.1 Baseline Repositories

The original guideline was derived from tests in the following repository revisions:

- [okocraft/Yaminabe](https://github.com/okocraft/Yaminabe) at `d04ab36141322cd4f1ab2c3d8ef8673b94977da3`
- [okocraft/ArmorStandEditor](https://github.com/okocraft/ArmorStandEditor) at `c6224e8988cb9c94cec31c43e258926c6b63792e`

These revisions are reference points, not requirements for current implementations.

### A.2 Gradle Configuration Pattern

The baseline repositories use the following shared configuration pattern:

```kotlin
jcommon {
    setupJUnit(libs.junit.bom)
    setupMockito(libs.mockito)
}
```

Test dependencies are generally separated by responsibility:

```kotlin
testImplementation(libs.junit.jupiter)
testImplementation(libs.platform.paper) // When required by Paper tests
testImplementation(libs.slf4j.api)      // When required by TestServer bootstrap
testRuntimeOnly(libs.slf4j.simple)
```

### A.3 `TestServer` Bootstrap Details

At the time of the baseline revisions, `TestServer` was responsible for the minimum Paper and Minecraft initialization required by lightweight tests, including:

- bootstrapping Minecraft and Paper registries;
- loading data-driven registries and tags;
- initializing item data components;
- configuring registries for `CraftRegistry`; and
- initializing dispatcher or context state required by Paper command argument types.

It did not start:

- a Bukkit `Server`;
- a world;
- networking;
- a tick loop; or
- plugin lifecycle.

The baseline configuration registered a JUnit extension through `META-INF/services/org.junit.jupiter.api.extension.Extension` and enabled extension auto-detection for the test task:

```kotlin
tasks.test {
    systemProperty("org.slf4j.simpleLogger.cacheOutputStream", "true")
    systemProperty("junit.jupiter.extensions.autodetection.enabled", "true")
}
```

These details are intentionally kept out of the normative sections because they are coupled to Paper, CraftBukkit, and NMS implementation versions.
