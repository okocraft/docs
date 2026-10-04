# Configuration and Reload Guidelines

This document defines configuration loading, validation, publication, and reload conventions for OKOCRAFT plugins.

For Paper plugins, Configurate is the standard configuration library. Paper provides Configurate at runtime, so Paper-side plugins should use the server-provided library instead of bundling another copy.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** describe requirement levels in this document.

These guidelines define defaults for new code and code being materially changed. Existing working implementations do not need to be migrated solely for stylistic consistency. Migration is appropriate when it addresses a concrete correctness, compatibility, security, or maintainability problem.

## 1. Configuration library

Paper-side code SHOULD use Configurate for structured configuration.

A Paper plugin artifact MUST NOT shade or bundle its own Configurate runtime. If shared code also targets a platform that does not provide Configurate, package or otherwise supply Configurate only for that platform's runtime; do not include the additional runtime in the Paper artifact.

Paper provides the runtime, but a module that imports Configurate must still have Configurate on its compile classpath unless shared build logic already supplies it. Use a compile-time-only dependency such as `compileOnly`, or `compileOnlyApi` when Configurate types are intentionally part of the module's public compile API. The Paper artifact MUST NOT package that dependency.

Do not mix Bukkit `FileConfiguration`, Configurate, and custom YAML parsers in one new configuration system without a concrete interoperability requirement.

## 2. Configuration model

Prefer a typed configuration model over scattered path lookups.

Configuration parsing SHOULD produce an application-level object that represents a complete, validated configuration snapshot.

```java
@ConfigSerializable
public class PluginConfig {
    private boolean enabled = true;
    private Duration timeout = Duration.ofSeconds(30);
}
```

The rest of the plugin SHOULD depend on the typed model rather than retain and query a mutable `ConfigurationNode` throughout the codebase.

Keep serialization concerns near the configuration boundary. Business logic SHOULD NOT need to know YAML paths, Configurate node structure, or serializer implementation details.

## 3. Defaults

A new installation SHOULD receive a usable default configuration.

Creating a missing default file MUST NOT overwrite an existing administrator-edited file.

Defaults SHOULD exist in one authoritative place. Avoid maintaining the same default independently in a resource file, field initializer, loader fallback, and documentation unless those copies are generated or tested for consistency.

Use defaults for genuinely optional settings. Do not silently replace malformed required values with defaults when doing so would hide an operator error.

## 4. Validation

Loading a configuration consists of more than parsing YAML.

A configuration MUST be validated before it becomes active. Validation SHOULD include domain constraints that the serializer cannot express by itself, such as:

- positive or bounded durations;
- non-empty identifiers;
- valid enum-like values;
- mutually exclusive settings;
- required relationships between sections;
- values supported by the current platform or Minecraft version.

Validation errors SHOULD identify the affected setting and the expected constraint.

```text
Invalid configuration: restart.countdown must be greater than or equal to 5 seconds.
```

Do not defer predictable configuration errors until the affected feature happens to run.

Normalization MAY convert equivalent valid input into an application-friendly representation, but it SHOULD NOT conceal invalid input.

## 5. Initial load

Configuration required for safe startup MUST be loaded and validated before dependent features are registered or started.

If required configuration cannot be loaded during startup, the plugin SHOULD fail closed: log the cause clearly and avoid enabling features with partially initialized state.

Do not leave a plugin apparently enabled when its required configuration failed to initialize and the plugin cannot operate correctly.

Optional integrations MAY fail independently when the plugin can still provide its documented core behavior.

## 6. Reload as a transaction

A reload MUST NOT mutate live configuration incrementally while parsing and validation are still in progress.

Use a prepare-then-publish sequence:

1. Read the configuration source.
2. Deserialize it into a new configuration object.
3. Validate and normalize the new object.
4. Prepare dependent state that can be created safely before publication.
5. Publish the new configuration as one logical change.
6. Retire resources that belonged only to the previous configuration.

Before the publication/commit point, a reload failure MUST leave the previously active runtime state in service, and any newly prepared resources MUST be retired.

A reload MUST NOT intentionally publish a partially prepared runtime state. Publication SHOULD replace a coherent runtime-state snapshot in one logical step where practical.

```java
PluginConfig next = loader.load(path);
ValidatedConfig validated = validator.validate(next);
RuntimeState prepared = RuntimeState.prepare(validated);

RuntimeState previous = current.getAndSet(prepared);
previous.close();
```

The exact implementation may differ, but the prepare/commit boundary must remain clear. Failures while retiring the previous state after publication are cleanup failures; they do not by themselves roll back the published state. Report or aggregate those failures and continue retiring independent resources. Do not claim rollback after publication or external side effects unless the implementation actually provides it.

## 7. Publishing configuration safely

Treat active configuration as an immutable snapshot whenever practical.

If configuration can be read by multiple Folia regions or asynchronous tasks, publication MUST have a defined memory-visibility and concurrency model. Common choices include a `volatile` reference or `AtomicReference` to an immutable configuration object.

Do not mutate a shared configuration object in place during reload.

A feature that needs derived values SHOULD preferably receive an immutable derived settings object instead of repeatedly traversing the raw configuration tree.

## 8. Reloading dependent resources

Some settings control resources with their own lifecycle, such as scheduled tasks, database pools, caches, listeners, or external integrations.

Resources required by the next configuration SHOULD be prepared before the commit point when the resource contract permits it. If preparation fails, retire newly prepared resources and keep the previous runtime state active. After publication, retire resources that belong only to the previous state; failures during retirement are cleanup failures rather than implicit rollback.

Do not close a working exclusive resource before validation and preparation unless its contract makes overlap impossible. If a replacement requires downtime or destructive side effects before commit, document the weaker rollback guarantee explicitly.

## 9. File I/O and scheduler context

Configuration file access is blocking I/O.

Runtime reload commands SHOULD avoid performing potentially slow file I/O on a Folia region, entity, or global tick thread. Read and parse the file asynchronously when practical, then publish or apply platform-owned changes on the appropriate scheduler.

Startup loading MAY be synchronous when the plugin cannot proceed until configuration is available. Keep startup work bounded and avoid unrelated network access in the configuration loader.

Configuration parsing code SHOULD NOT access Bukkit/Paper world or entity state. Resolve platform state after parsing, on the scheduler that owns that state.

## 10. Saving and rewriting configuration

Do not rewrite an administrator's configuration merely because it was loaded successfully.

Automatic rewriting can remove comments, reorder keys, or make upgrades difficult to review. Save configuration only when the plugin intentionally owns the changed value or when migration requires a rewrite.

When a migration changes persistent configuration:

- make the migration explicit;
- preserve user values whenever possible;
- validate the migrated result before replacing the original;
- avoid destructive rewrites without a recovery path;
- log a concise migration result.

A schema or configuration version MAY be used when migrations cannot be inferred safely.

## 11. Unknown and deprecated settings

Unknown settings SHOULD normally be preserved when the chosen loading/saving approach permits it, especially when configuration may be read by multiple plugin versions during deployment or rollback.

Deprecated settings SHOULD have a defined transition policy. When a deprecated setting is still accepted, log a warning that names the replacement and, when useful, the version in which support is expected to be removed.

Do not silently reinterpret an old setting with materially different semantics.

## 12. Errors and logging

Configuration errors are operator-facing diagnostics and SHOULD be actionable.

A useful error identifies:

- which file failed;
- which setting is invalid when known;
- what constraint was violated;
- the underlying exception when it helps diagnose parsing or I/O failure.

Do not log secrets, credentials, access tokens, or complete connection strings containing credentials.

User-facing reload commands SHOULD report success only after the new configuration has been validated and published.

On failure, report that the reload failed and that the previous configuration remains active when that guarantee applies.

## 13. Testing

Configuration code SHOULD be testable without starting a full server when possible.

Tests SHOULD cover:

- loading the default configuration;
- representative customized values;
- invalid syntax;
- invalid domain values;
- missing optional values and their defaults;
- missing required values;
- reload failure preserving the previous snapshot;
- migrations when the plugin supports them;
- serializers for custom value types.

When a configuration controls resource replacement, test both successful replacement and failure before publication.

## 14. Review checklist

Before merging configuration changes, verify that:

- Paper-side configuration uses the Configurate runtime provided by Paper rather than bundling another copy.
- Configuration is converted into a typed application-level model.
- Existing user configuration is not overwritten when defaults are created.
- Domain validation happens before the configuration becomes active.
- Required startup configuration fails closed when invalid.
- Reload prepares and validates new state before publishing it.
- Failures before the reload commit point leave the previous runtime state active and retire newly prepared resources.
- Active configuration is immutable or has an explicit concurrency model.
- Runtime file I/O does not block a Folia tick-owning scheduler unnecessarily.
- Resource replacement has explicit ownership and cleanup.
- Automatic saves do not unexpectedly rewrite administrator-managed files.
- Errors identify the affected setting without exposing secrets.

## References

- [PaperMC: Plugin configuration](https://docs.papermc.io/paper/dev/plugin-configurations/)
- [SpongePowered Configurate](https://github.com/SpongePowered/Configurate)
