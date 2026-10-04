# AGENTS.md

This file applies to the entire `okocraft/docs` repository.

## Purpose

This repository contains shared technical documentation and development guidelines for OKOCRAFT projects.

Changes should define organization-level defaults and contracts. Do not copy project-specific implementation details into shared policy unless they demonstrate an established pattern that should apply across projects.

## Canonical Guidelines

Use the document that owns the relevant concern. Prefer cross-links over duplicating policy between documents.

| Concern | Canonical document |
| --- | --- |
| Java project structure, Gradle, dependencies, CI, Renovate | [Java Project, Gradle, and CI Guidelines](dev/guidelines/java-project-gradle-and-ci.md) |
| Test design and test scope | [Testing Guidelines](dev/guidelines/java-testing.md) |
| Paper/Folia scheduling, threading, ownership, async boundaries | [Paper and Folia Scheduling and Threading Guidelines](dev/guidelines/paper-folia-scheduling-and-threading.md) |
| Plugin lifecycle and long-lived resource ownership | [Plugin Lifecycle and Resource Ownership Guidelines](dev/guidelines/plugin-lifecycle-and-resource-ownership.md) |
| Configuration loading, validation, publication, and reload | [Configuration and Reload Guidelines](dev/guidelines/configuration-and-reload.md) |
| User-facing message wording, formatting, and localization | [Message Formatting Guidelines](dev/guidelines/message-formatting.md) |
| Java message declaration and localization architecture | [Java Message Definitions and Localization](dev/guidelines/java-messages.md) |

When a rule touches more than one concern, keep the detailed rule in the canonical document and make other documents reference it or state only the part needed for their own topic.

## Before Editing

Before changing or adding a guideline:

1. Read the existing guideline that owns the topic.
2. Read adjacent guidelines that may contain overlapping lifecycle, concurrency, configuration, testing, or localization rules.
3. Inspect current OKOCRAFT repositories when claiming that a pattern is established organization practice.
4. Verify platform or library behavior against current upstream documentation or source when the claim depends on Paper, Folia, Velocity, Gradle, GitHub Actions, Configurate, Adventure, or another external API.
5. Distinguish stable policy from current implementation details, versions, and examples.

Do not infer organization policy from a single repository when implementations differ across projects.

## Scope of Guidelines

Unless a document explicitly says otherwise, guidelines define defaults for new code and code being materially changed.

Existing working implementations do not need to be migrated solely for stylistic consistency. Recommend migration when it addresses a concrete correctness, compatibility, security, or maintainability problem.

Do not turn an observed legacy pattern into a new default merely because it still exists in a repository.

## Requirement Language

Use normative language deliberately:

- **MUST / MUST NOT**: correctness, compatibility, security, lifecycle, or organization-level invariants.
- **SHOULD / SHOULD NOT**: the expected default when valid exceptions exist.
- **MAY**: optional behavior or an explicitly permitted alternative.

Do not use a stronger requirement level than the platform contract or organization policy can support.

When the same invariant appears in multiple documents, keep its normative strength and terminology consistent.

## Technical Writing

Write for engineers who need to make implementation decisions.

- State the rule before the rationale.
- Prefer concrete ownership, lifecycle, and failure semantics over vague recommendations.
- Keep examples focused on the rule they demonstrate.
- Avoid unnecessary historical explanation in normative sections.
- Use stable terminology consistently across documents.
- Explain important exceptions next to the rule they qualify.
- Prefer short sections and descriptive headings over long narrative passages.
- Use relative links for documentation inside this repository.

Examples should illustrate policy, not silently create it.

## Version and API References

Avoid fixed dependency, Java, Minecraft, or tool versions in organization policy unless the version itself is the policy.

When an example requires a version-like value, prefer a placeholder or explain that the concrete value is repository-specific.

External API claims that can change over time should be verified before editing. Prefer official upstream documentation or source for normative statements.

## Cross-document Boundaries

Keep these boundaries explicit:

- Scheduling/thread ownership belongs in the Paper/Folia scheduling guideline; lifecycle owns cancellation and resource retirement.
- Configuration owns the reload prepare/commit boundary; lifecycle owns general resource retirement after replacement.
- Message formatting owns wording and localization conventions; Java messages owns declaration, loading, and translation architecture.
- Java project guidance owns build-system and dependency policy; testing owns test strategy and what behavior should be verified.

If a proposed change causes two documents to define the same general mechanism independently, consolidate the mechanism into one canonical document.

## Validation

For documentation-only changes:

- verify all relative links;
- verify referenced files exist on the target branch;
- search for contradictory requirement levels or stale wording in related guidelines;
- ensure examples do not accidentally pin transient versions or implementation details;
- ensure a new guideline is linked from `README.md`;
- ensure changes to organization policy are reflected in any related review checklist.

When changing behavior based on an external platform contract, record the upstream basis in the PR description when useful for reviewers.

## Pull Requests

Keep each PR focused on one coherent documentation concern.

A useful PR description should state:

- what policy or documentation changed;
- why the change is needed;
- what repositories or upstream sources were reviewed when relevant; and
- any intentional compatibility or migration implications.

Do not mark a PR ready for review while known contradictions with another guideline remain.
