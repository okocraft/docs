# Plugin Lifecycle and Resource Ownership Guidelines

This document defines lifecycle and resource-ownership conventions for OKOCRAFT plugins.

The central rule is simple: **the component that starts, registers, or acquires a resource owns its retirement unless ownership is explicitly transferred.**

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** describe requirement levels in this document.

These guidelines define defaults for new code and code being materially changed. Existing working implementations do not need to be migrated solely for stylistic consistency. Migration is appropriate when it addresses a concrete correctness, compatibility, security, or maintainability problem.

## 1. Lifecycle responsibilities

Keep each platform lifecycle phase focused on work that belongs to that phase.

For Paper plugins:

- bootstrap or Paper lifecycle events SHOULD be used for registrations that belong to those lifecycle APIs, such as reloadable command registration;
- `onLoad` SHOULD perform initialization that must happen before normal enable-time work when the platform contract requires it;
- `onEnable` SHOULD create runtime services, register ordinary runtime listeners, connect optional integrations, and start tasks needed for normal operation;
- `onDisable` SHOULD stop owned runtime activity and release resources that can outlive the plugin's enabled state.

A `JavaPlugin` constructor MUST NOT perform platform-dependent initialization or acquire runtime resources. Paper does not guarantee which platform APIs are available while the plugin constructor runs. Restrict plugin constructors and field initialization to side-effect-free object setup; use bootstrap or lifecycle APIs, `onLoad`, or `onEnable` according to the relevant platform contract.

Platform-neutral helper classes MAY acquire resources in constructors when their ownership and rollback behavior are explicit; this restriction is specifically about plugin entry-point initialization.

For Velocity and other platforms, apply the same ownership model to their corresponding initialization and shutdown events rather than copying Paper lifecycle method names into common code.

## 2. Resource ownership

Every long-lived resource MUST have an identifiable owner responsible for its retirement. The owner MAY be the platform when its lifecycle contract guarantees cleanup; otherwise the component that acquires or registers the resource owns it unless ownership is explicitly transferred.

Examples include:

- scheduled or repeating tasks;
- executor services and threads;
- database pools and connections;
- event listeners and event-bus subscriptions;
- translation sources;
- PlaceholderAPI or other plugin hooks;
- caches with background maintenance;
- file watchers;
- network clients;
- registrations in global or static registries.

If a component creates or registers one of these resources, that component SHOULD retain enough information to stop, unregister, close, or otherwise retire it.

Do not rely on process shutdown, class unloading, or garbage collection as the normal cleanup mechanism for a resource with explicit lifecycle operations.

## 3. Ownership transfer

Ownership MAY be transferred, but the transfer must be clear in the API.

A method that returns an `AutoCloseable`, task handle, registration handle, or service object can make ownership explicit. A method that silently registers global state without returning or storing a way to unregister it makes lifecycle correctness difficult to review.

When a child service is owned by a parent plugin component, the parent SHOULD close the child rather than duplicate the child's internal cleanup logic.

```java
final class Feature implements AutoCloseable {
    private final CancellableTask task;

    @Override
    public void close() {
        task.cancel();
    }
}
```

Prefer one clear ownership path over multiple unrelated callers that can all partially tear down the same resource.

## 4. Partial initialization

Initialization can fail after some resources have already been acquired.

Startup code MUST account for partial initialization. A failure must not leave background tasks, registrations, connections, or other resources active unintentionally.

Prefer constructing a service so that either:

- construction is side-effect free and a separate `start` operation acquires resources with rollback; or
- construction acquires all required resources and closes already-acquired resources before propagating a failure.

A plugin that cannot satisfy its required startup invariants SHOULD fail closed rather than continue in a partially enabled state.

Optional integrations MAY fail independently if the plugin can continue without them. Their failure path must still clean up any partially acquired integration resources.

## 5. Shutdown

Shutdown SHOULD be safe to execute once normal runtime activity has started, including after a partially successful startup when the platform can invoke shutdown in that state.

Cleanup operations SHOULD be idempotent where practical.

A shutdown sequence SHOULD generally:

1. prevent new work from being accepted;
2. cancel or stop recurring producers of work;
3. finish, discard, or persist outstanding state according to the feature contract;
4. unregister external hooks and listeners;
5. close owned clients, pools, executors, and other resources;
6. clear references that would otherwise keep obsolete runtime state reachable.

The exact order depends on dependencies between resources. Stop producers before consumers when producers can enqueue more work.

Do not start new asynchronous cleanup that can outlive plugin disable unless the platform explicitly provides a safe shutdown mechanism for it.

## 6. Scheduled tasks

A task MUST be cancelled or otherwise made unable to affect obsolete state when the feature or runtime state it belongs to is disabled, replaced, or reconfigured. Retain a task handle when cancellation is the retirement mechanism.

Work that can still complete after replacement MUST verify that its target state is still current before applying results. Task callbacks SHOULD also tolerate the target object disappearing before execution, especially for entity-owned and delayed Folia tasks.

Plugin-wide cancellation provided by a platform can be a useful final safety net, but it SHOULD NOT replace feature-level ownership when tasks are also replaced during reload or feature reconfiguration.

## 7. Executors and threads

Do not create a dedicated executor when the platform scheduler or an existing shared executor satisfies the requirement.

When a plugin does create an `ExecutorService`, scheduler, or thread, it MUST define who shuts it down.

Shutdown SHOULD use a bounded policy. Do not wait indefinitely for an executor from a server lifecycle thread.

Thread factories SHOULD use recognizable names for long-lived plugin-owned threads so diagnostics can identify their owner.

A plugin-owned thread MUST NOT continue using plugin classes or platform state after the plugin has been disabled.

## 8. Event and external registrations

Registrations outside the plugin object's natural lifetime require explicit cleanup.

Examples include translation registries, third-party APIs, static registries, service managers, and manually registered event systems.

When the registration API returns a handle, store and close/unregister that handle. When it requires the original listener or source instance, retain that instance for cleanup.

Paper lifecycle registrations SHOULD use the lifecycle API when the registration is designed to be reapplied by Paper during a server lifecycle event. Register a lifecycle handler once for a given plugin lifecycle. Paper invokes lifecycle-managed command registration again when its registration lifecycle requires it. A plugin configuration reload MUST NOT register a duplicate lifecycle handler merely to re-register the same commands.

Platform-managed listener registration MAY rely on platform cleanup at plugin disable when the platform contract guarantees it, but explicit feature-level unregistering is still appropriate when a listener must be removed before plugin disable or during reload.

## 9. Database and network resources

Connection pools, database clients, HTTP clients with owned resources, and similar services SHOULD have a lifecycle no longer than the component that owns them.

Close pools and clients during shutdown or replacement.

Do not close a shared externally owned client from a plugin component that merely borrowed it.

Long-running database or network operations SHOULD support cancellation or bounded timeouts where practical so shutdown is not indefinitely delayed by external systems.

Persistent data that must be durable at shutdown SHOULD also be saved during normal operation. `onDisable` MUST NOT be the only durability mechanism for important state because abnormal process termination can skip normal shutdown.

## 10. Reload and replacement

Reload is a resource replacement operation, not a second startup layered over the first one.

When configuration changes require a service to be replaced:

1. validate the new configuration;
2. prepare the replacement service when safe;
3. switch new work to the replacement at the commit point;
4. retire the previous service.

Before the commit point, replacement failure MUST leave the previous service in use and newly prepared resources must be retired. After the commit point, a failure while retiring the previous service is a cleanup failure and does not by itself roll back the replacement.

Do not register a second repeating task, listener, or external hook without retiring the first one unless duplicate registration is an intentional part of the feature.

Services that can be reloaded independently SHOULD encapsulate their own resource ownership instead of making the main plugin class know every cleanup detail.

## 11. Common and platform modules

In multi-platform projects, common code SHOULD express lifecycle in platform-neutral terms such as `start`, `close`, or a small application-specific lifecycle interface.

Paper and Velocity entry points SHOULD adapt their platform events to that common lifecycle.

Do not expose `JavaPlugin`, `ProxyServer`, Paper task types, or Velocity task types to common application logic solely for cleanup. Pass the minimum capability or an owned service abstraction instead.

`AutoCloseable` is appropriate for many application services because it makes resource ownership visible without introducing a platform dependency.

## 12. Static state

Avoid mutable static state whose lifetime implicitly spans plugin reloads or test cases.

When static registration is required by an external API, provide a matching explicit unregister/reset operation and invoke it during shutdown.

Static accessors to the current plugin or service SHOULD be treated as borrowed references, not ownership. The static holder must not keep a disabled plugin instance reachable indefinitely.

Tests SHOULD reset global state they modify so test order does not affect results.

## 13. Failure handling

Cleanup SHOULD continue after an individual resource fails to close when the remaining resources can still be retired safely.

When multiple cleanup operations can fail, log each relevant failure or aggregate them rather than abandoning the rest of shutdown after the first exception.

Do not suppress a startup failure merely to reach an enabled state. Record the root cause and leave the plugin in a state consistent with the platform lifecycle.

Lifecycle logs SHOULD describe state transitions and failures concisely. Avoid routine success logs for every internal resource unless they provide operational value.

## 14. Testing

Lifecycle-heavy components SHOULD be testable independently of the platform entry point.

Tests SHOULD cover relevant cases such as:

- successful start and close;
- close after partial initialization;
- repeated close when cleanup is designed to be idempotent;
- replacement during reload;
- task cancellation;
- unregistering external registrations;
- failure of one cleanup step without leaking the remaining resources.

A test should assert externally relevant lifecycle behavior, not only that private fields were set to `null`.

## 15. Review checklist

Before merging lifecycle-related changes, verify that:

- every long-lived resource has a clear owner responsible for retirement, including platform ownership where guaranteed by contract;
- resource acquisition has a corresponding retirement operation;
- `JavaPlugin` constructors do not perform platform-dependent initialization or acquire runtime resources;
- Paper lifecycle-managed registrations use the lifecycle API rather than ad hoc reload registration;
- required initialization fails closed rather than leaving partial runtime state active;
- partial initialization cleans up resources already acquired;
- shutdown stops producers before closing resources they depend on;
- tasks are cancelled or otherwise made unable to affect obsolete state when their feature or runtime state ends;
- plugin-owned executors and clients are closed with bounded shutdown behavior;
- external and static registrations are explicitly removed when required;
- reload replaces resources instead of layering duplicate registrations or tasks;
- common modules express lifecycle without unnecessary Paper or Velocity types;
- important persistent state does not depend exclusively on `onDisable` for durability;
- cleanup remains effective when one individual close operation fails.

## References

- [PaperMC: Lifecycle API](https://docs.papermc.io/paper/dev/api/lifecycle/)
- [PaperMC: Command registration](https://docs.papermc.io/paper/dev/command-api/basics/registration/)
