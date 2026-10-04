# OKOCRAFT Documentation

Shared technical documentation and development guidelines for OKOCRAFT projects.

## Development Guidelines

| Area | Guide | Scope |
| --- | --- | --- |
| Project and build | [Java Project, Gradle, and CI Guidelines](dev/guidelines/java-project-gradle-and-ci.md) | Project structure, build systems, dependencies, CI, shared workflows, and Renovate |
| Testing | [Testing Guidelines](dev/guidelines/java-testing.md) | Test design, test scope, mocking, platform boundaries, and behavioral verification |
| Scheduling and threading | [Paper and Folia Scheduling and Threading Guidelines](dev/guidelines/paper-folia-scheduling-and-threading.md) | Paper/Folia scheduler ownership, async boundaries, cross-region work, and Folia safety |
| Lifecycle | [Plugin Lifecycle and Resource Ownership Guidelines](dev/guidelines/plugin-lifecycle-and-resource-ownership.md) | Plugin lifecycle, resource ownership, cleanup, replacement, and failure handling |
| Configuration | [Configuration and Reload Guidelines](dev/guidelines/configuration-and-reload.md) | Configurate, typed configuration, validation, publication, reload, and migration |
| Message writing | [Message Formatting Guidelines](dev/guidelines/message-formatting.md) | User-facing wording, message keys, MiniMessage, placeholders, English, and Japanese |
| Message implementation | [Java Message Definitions and Localization](dev/guidelines/java-messages.md) | Java message declarations, `mcmsgdef`, translations, runtime language files, and Adventure registration |

## Shared Agent Instructions

[AGENTS.md](AGENTS.md) provides the organization-wide baseline instructions for coding agents working across OKOCRAFT repositories. It is intentionally concise: it routes agents to the relevant canonical guideline, defines only cross-cutting invariants, and is intended to be referenced or adopted by individual repositories.

Repository-specific instructions may add stricter or more detailed rules for local architecture, build, platform, or release requirements. The documents in this repository remain the canonical detailed guidance.

## License

This project is under the Apache License version 2.0. Please read [LICENSE](LICENSE) for more info.

Copyright © 2026, OKOCRAFT and Siroshun09
