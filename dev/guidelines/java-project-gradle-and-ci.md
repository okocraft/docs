# Java Project, Gradle, and CI Guidelines

This document defines the default project structure, Gradle dependency management, and continuous-integration conventions for OKOCRAFT Java repositories.

The goal is to keep repositories predictable and maintainable while centralizing organization-wide build behavior in the existing shared tooling.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** describe requirement levels in this document.

These guidelines define defaults for new code and code being materially changed. Existing working implementations do not need to be migrated solely for stylistic consistency. Migration is appropriate when it addresses a concrete correctness, compatibility, security, or maintainability problem.

## 1. Build system

New Java projects SHOULD use Gradle with the Kotlin DSL. Existing projects using another supported build system, such as Maven, do not need to migrate solely for consistency.

A repository that uses Gradle MUST include and use the Gradle Wrapper. Gradle documentation and CI SHOULD invoke `./gradlew` rather than depend on a system-installed Gradle version.

Do not hand-edit generated wrapper scripts or the wrapper JAR. Update the wrapper through Gradle and commit the resulting wrapper files together.

A multi-module build SHOULD keep organization-wide build policy in the root build where practical and keep module build files focused on module-specific dependencies and packaging.

## 2. Java version

The Java language/toolchain version and the Java version used by CI MUST remain compatible and SHOULD be the same unless the repository intentionally tests multiple runtimes.

Use the version selected by current OKOCRAFT platform requirements and shared build tooling. Do not copy a Java version into multiple build files when one root declaration can configure the whole build.

When updating the Java version, update build configuration, CI inputs, local run tasks, and release/deployment workflows as one change.

## 3. Shared Gradle plugins

Prefer the established `dev.siroshun.gradle.plugins` plugins used across OKOCRAFT repositories for common Java, bundling, publication, and related build behavior.

For example, repositories that use `jcommon` SHOULD configure common Java and test behavior through its extension rather than reproduce equivalent task configuration in every subproject.

```kotlin
plugins {
    alias(libs.plugins.jcommon)
}

jcommon {
    setupJUnit(libs.junit.bom)
    setupMockito(libs.mockito)
}
```

The exact Java version in an individual repository may change over time; the important rule is to keep the version centralized and aligned with CI.

Do not add custom build logic when an existing shared plugin already defines the same organization-wide convention.

Project-specific behavior MAY remain local when moving it into shared tooling would make the shared plugin depend on one project's requirements.

## 4. Version catalogs

Repositories with non-trivial dependency sets SHOULD use `gradle/libs.versions.toml` as the primary catalog for dependency and Gradle-plugin coordinates.

Prefer aliases over repeated string coordinates in build scripts.

```toml
[versions]
junit = "..."

[libraries]
junit-bom = { module = "org.junit:junit-bom", version.ref = "junit" }

[plugins]
jcommon = { id = "dev.siroshun.gradle.plugins.jcommon", version.ref = "gradle-plugins" }
```

Alias names SHOULD describe the role of the dependency consistently. Existing OKOCRAFT projects commonly use prefixes such as `platform-` for platform APIs and clear names such as `junit-bom` or `slf4j-api` for shared libraries.

Do not introduce a second version catalog without a concrete boundary that justifies it.

## 5. Dependency scopes

Choose the narrowest Gradle dependency scope that matches the runtime contract.

Use `compileOnly` or `compileOnlyApi` for APIs supplied by the target platform when the plugin JAR must not contain them.

Use `implementation` for libraries that are private implementation details and are packaged or otherwise supplied by the plugin's distribution strategy.

Use `api` only when downstream consumers of the module need the dependency on their compile classpath as part of the module's public API.

Use `testImplementation` and `testRuntimeOnly` for test-only dependencies.

A dependency that the target platform contract, or an explicit OKOCRAFT platform policy, defines as provided to plugins MUST NOT be bundled into that platform's plugin artifact merely for dependency-resolution convenience.

Before adding an exclusion or forcing a version, document or make evident the conflict being solved. Avoid broad exclusions that can hide required transitive dependencies.

## 6. Platform modules

When a project supports multiple platforms, platform dependencies SHOULD stay in platform-specific modules.

A common module SHOULD contain application logic that can be expressed without importing Paper or Velocity APIs. Platform adapters SHOULD translate between the common model and platform APIs.

A typical layout is:

```text
project/
├── common/
├── paper/
└── velocity/
```

Use platform-prefixed module names when they improve clarity in larger builds, for example `platform-paper` and `platform-velocity`.

Do not create a common module solely to make a small single-platform project appear more modular.

## 7. Repositories

Use the minimum set of artifact repositories required by the build.

Repository declarations SHOULD be centralized where the build structure permits it. Prefer helper methods from shared OKOCRAFT Gradle plugins, such as the existing Paper repository setup, over repeated repository URLs.

Do not add `mavenLocal()` to normal build resolution unless the project has a documented local-development workflow that requires it. A developer's local Maven repository is not reproducible CI input.

## 8. Tests

New behavior SHOULD include automated tests when the logic can be tested deterministically outside a running server.

Use JUnit Jupiter for unit tests and Mockito where mocking is appropriate, following the shared Gradle setup used by current OKOCRAFT projects.

Prefer testing application logic directly instead of reproducing large parts of the Paper or Velocity runtime with mocks.

Platform-specific tests are appropriate for adapters, registration, serialization, scheduler selection, and other code whose behavior depends on the platform contract.

A test SHOULD describe behavior rather than implementation details so routine refactoring does not require unrelated test rewrites.

## 9. Build verification

For Gradle repositories, `./gradlew build` is the default local verification command unless the repository documents another verification task. Repositories using another build system SHOULD document an equivalent clean-checkout verification command.

A pull request SHOULD be buildable from a clean checkout using only committed build files and declared external repositories.

Generated artifacts, IDE state, local credentials, and locally published dependencies MUST NOT be required for a normal CI build.

Warnings that indicate an upcoming Java, Gradle, or plugin incompatibility SHOULD be addressed before they become release blockers.

## 10. GitHub Actions

Repositories SHOULD use reusable workflows from `okocraft/workflows` instead of duplicating organization-wide Gradle or Maven CI logic.

A repository workflow SHOULD primarily declare repository-specific inputs such as:

- Java version;
- artifact/package name;
- additional permissions required by that repository;
- repository-specific build or deployment steps that cannot live in the shared workflow.

```yaml
jobs:
  build:
    uses: okocraft/workflows/.github/workflows/gradle.yml@v1
    with:
      java-version: '<project Java version>'
      package-name: Example-Build-${{ github.run_number }}
```

Do not copy a reusable workflow into each repository to make a one-off modification. Prefer extending the shared workflow when the behavior is broadly applicable, or add a small repository-local job when it is not.

CI and local builds SHOULD execute equivalent verification tasks through the repository's selected build system.

## 11. Workflow security

GitHub Actions SHOULD receive only the permissions required by their jobs.

Third-party actions SHOULD be pinned according to the organization-wide Renovate policy. Do not weaken digest or version pinning locally without a documented reason.

Secrets MUST NOT be printed, committed, passed to untrusted pull-request code, or exposed through build artifacts.

Release and deployment credentials SHOULD be limited to the jobs that need them.

## 12. Renovate

Repositories SHOULD extend the shared configurations in `okocraft/renovate-config` for the ecosystems they use.

For a typical Java/Gradle repository, use the organization presets for GitHub Actions and Gradle rather than reproducing package rules locally.

Repository-local Renovate rules SHOULD describe exceptions or repository-specific behavior. Rules that apply broadly across OKOCRAFT SHOULD be added to the shared configuration instead.

Do not ignore a dependency indefinitely without documenting why it cannot be upgraded. Prefer a narrowly scoped ignore rule for a known compatibility constraint.

## 13. Publishing and packaged dependencies

Library modules intended for consumption by other projects SHOULD distinguish their public API dependencies from implementation details.

Plugin distributions SHOULD make bundled dependencies explicit through the project's established bundling mechanism. Do not rely accidentally on a dependency being present because another plugin or server component happens to ship it.

Conversely, do not bundle platform-provided APIs and libraries when the runtime contract says they are supplied by the platform.

Published artifacts SHOULD include enough version metadata to identify the source version during diagnostics.

## 14. Project documentation

A repository README SHOULD state the minimum information needed to build and understand the project:

- what the project provides;
- the target platform when relevant;
- the normal build command;
- license information or a link to the license.

Repository-specific development procedures SHOULD be documented near the code they affect. Do not duplicate organization-wide guidance into every README; link to shared guidance instead.

## 15. Review checklist

Before merging build or CI changes, verify that:

- for Gradle repositories, the Gradle Wrapper is present and is the documented way to run the build;
- Java versions in Gradle and CI are aligned;
- common build behavior uses established OKOCRAFT Gradle plugins where applicable;
- dependencies and plugin versions are centralized in `libs.versions.toml` when appropriate;
- dependency scopes match the runtime and public API contract;
- platform-provided libraries are not bundled accidentally;
- shared Paper/Velocity projects keep platform dependencies in platform modules;
- the repository's documented verification command succeeds from a clean checkout;
- GitHub Actions reuse `okocraft/workflows` where applicable;
- workflow permissions and secrets are narrowly scoped;
- Renovate extends shared OKOCRAFT presets and local rules are true exceptions;
- repository-specific build behavior is documented without duplicating organization-wide policy.

## References

- [Gradle: Wrapper](https://docs.gradle.org/current/userguide/gradle_wrapper.html)
- [Gradle: Version catalogs](https://docs.gradle.org/current/userguide/version_catalogs.html)
- [OKOCRAFT reusable workflows](https://github.com/okocraft/workflows)
- [OKOCRAFT Renovate configuration](https://github.com/okocraft/renovate-config)
