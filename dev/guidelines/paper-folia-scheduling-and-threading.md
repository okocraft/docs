# Paper and Folia Scheduling and Threading Guidelines

This document defines scheduling and threading conventions for OKOCRAFT plugins that run on Paper, Folia, or both Paper and Velocity.

The primary goal is correctness under Folia's regionized threading model without adding platform abstractions that do not provide a real boundary.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** describe requirement levels in this document.

## 1. Platform boundary

### Paper-only and Paper/Folia plugins

A plugin that targets only Paper, or both Paper and Folia, SHOULD call the Paper scheduling APIs directly.

Do not introduce a scheduler abstraction only to distinguish Paper from Folia. Paper supports the global, region, async, and entity scheduler APIs used for Folia-compatible code and handles them appropriately when running on Paper.

For code that is intended to support Folia, prefer the Folia-compatible scheduler APIs even when the plugin also runs on Paper.

```java
server.getGlobalRegionScheduler();
server.getRegionScheduler();
server.getAsyncScheduler();
entity.getScheduler();
```

Do not use Folia detection merely to choose between a Bukkit scheduler and a Folia scheduler. Detect Folia only when behavior genuinely differs by server implementation.

### Shared Paper and Velocity code

When application logic is shared between Paper and Velocity, platform-specific scheduling SHOULD be hidden behind an abstraction owned by the shared code.

The abstraction SHOULD describe the scheduling capability required by the application rather than mirror every method of either platform API.

```java
interface Scheduler {
    CancellableTask schedule(Runnable task, Duration delay, Duration interval);
}
```

Paper and Velocity modules then provide platform adapters. Platform API types SHOULD NOT leak into a common module unless that module intentionally depends on the platform.

Do not add this abstraction to a Paper-only project preemptively.

## 2. Choose the scheduler by ownership

Choose a scheduler based on the state that the task accesses, not based on where the calling code happens to be running.

| Task owns or accesses | Scheduler |
| --- | --- |
| A specific entity or player | Entity scheduler |
| Blocks, chunks, or location-bound world state | Region scheduler |
| Global server state not owned by a region | Global region scheduler |
| Blocking I/O or work independent of server tick state | Async scheduler |

### Entity scheduler

Use `entity.getScheduler()` for operations whose ownership follows an entity.

This includes delayed or deferred work that later reads or modifies an entity. An entity can move between regions between scheduling and execution, so a location captured earlier is not a substitute for the entity scheduler.

Use the retired callback when the operation needs explicit handling for an entity that is removed before execution.

### Region scheduler

Use the region scheduler for operations tied to a location, block, or chunk.

```java
server.getRegionScheduler().execute(plugin, location, () -> {
    location.getBlock().setType(material);
});
```

Do not use the region scheduler for entity-owned operations merely because the entity currently occupies that region.

### Global region scheduler

Use the global region scheduler only for work that is not owned by a specific region or entity.

Do not treat the global region scheduler as Folia's equivalent of a universal main thread. Running on the global region does not grant access to arbitrary region-owned state.

### Async scheduler

Use the async scheduler for work that does not require ownership of server tick state, such as database access, HTTP requests, and other blocking I/O.

Code running asynchronously MUST NOT read or mutate region-owned Bukkit/Paper state unless the API explicitly documents that operation as thread-safe.

The platform async scheduler is appropriate for ordinary off-thread work. A plugin MAY own a dedicated executor when it needs isolation, bounded concurrency, or a lifecycle that the platform scheduler does not provide. Such an executor must be shut down by its owner.

## 3. Crossing an async boundary

Separate platform-state access from blocking work.

A typical operation SHOULD follow this sequence:

1. Read the required server state on the owning entity or region scheduler.
2. Convert that state into immutable or independently thread-safe data.
3. Perform blocking I/O or bounded computation off the tick-owning scheduler.
4. Schedule the result back onto the scheduler that owns the affected server state.
5. Revalidate assumptions that may have changed while the async work was running.

Do not rely on a `Player`, `Entity`, `World`, `Chunk`, `Block`, or mutable platform object remaining safe or valid after crossing an async boundary.

Prefer stable identifiers and immutable values, such as UUIDs, keys, primitive values, records, or immutable collections, when data must cross scheduler boundaries.

## 4. Cross-region operations

Folia regions can execute independently and concurrently. Code MUST NOT assume that two locations are owned by the same ticking thread.

If an operation touches multiple independent regions, decompose it into region-owned operations where possible. Do not solve cross-region access by moving the entire operation to the global scheduler.

Avoid holding a lock while calling Paper APIs or scheduling work onto another region. Cross-region coordination SHOULD exchange immutable data or application-level messages rather than share mutable world state.

When an operation requires a result from another region, design it as an asynchronous workflow instead of blocking one region until another region completes.

## 5. Shared application state

State that can be accessed from multiple regions or async tasks MUST have an explicit concurrency model.

Use one of the following approaches:

- confine mutable state to one scheduler or owner;
- publish immutable snapshots;
- use concurrent collections or atomic primitives for genuinely shared state;
- use narrowly scoped synchronization when ownership cannot be established.

A plain `HashMap`, mutable collection, or mutable object MUST NOT become shared merely because access was safe on traditional single-threaded Paper.

Thread-safe storage does not make the objects stored inside it thread-safe. For example, a concurrent map containing mutable entity-related objects still requires correct entity or region ownership when those objects are used.

## 6. Blocking and expensive work

Region, entity, and global scheduler tasks SHOULD remain short and non-blocking.

The following work SHOULD NOT run on a tick-owning scheduler when it can block for a meaningful amount of time:

- database queries and transactions;
- HTTP or other network requests;
- large file reads or writes;
- waiting on futures, latches, locks, or other threads;
- expensive serialization, compression, or bulk computation.

Do not call `Future#get`, `CompletableFuture#join`, or equivalent blocking waits from a region, entity, or global scheduler to wait for async work. Continue the operation asynchronously and schedule the result back to the correct owner.

CPU-heavy work SHOULD use bounded concurrency so it cannot consume the server's available worker capacity without limit.

## 7. Task lifetime and cancellation

Keep a task handle when the task has a lifetime shorter than the plugin or when explicit cancellation is part of the feature lifecycle.

Repeating and delayed tasks SHOULD be cancelled when their owning feature is disabled, replaced, or reconfigured.

A task that can outlive the object that created it SHOULD verify that the target state is still valid before applying a result.

Cancellation SHOULD be idempotent. Cleanup code SHOULD tolerate a task that has already completed or already been cancelled.

Platform abstractions used by shared Paper/Velocity code SHOULD expose cancellation semantics without leaking platform-specific task types.

## 8. Time representation

Use `Duration` for application-level time values when practical. Convert to platform-specific units at the platform boundary.

This keeps common logic independent from tick units and makes delays easier to read.

Use ticks when the operation is intentionally tied to Minecraft ticks rather than wall-clock time.

Do not assume that a number of ticks represents an exact wall-clock duration under server load.

## 9. Folia support declaration

Set `folia-supported: true` only when the plugin has been designed and reviewed for Folia's ownership model.

The declaration alone does not make a plugin Folia-safe.

Before adding or retaining the declaration, verify at least the following:

- entity operations use entity ownership correctly;
- location-bound world operations use region ownership correctly;
- global tasks do not access arbitrary region-owned state;
- async tasks do not access unsafe server state;
- shared mutable state has a concurrency model;
- blocking work is kept off tick-owning schedulers;
- repeating and long-lived tasks have appropriate cleanup.

## 10. Testing

Scheduler-dependent application logic SHOULD be separated enough to test state transitions without requiring timing-sensitive integration tests.

For Paper/Folia-specific behavior, tests SHOULD cover at least:

- selecting the correct owner for entity and location operations;
- handling entities that disappear before delayed execution;
- applying async results after the original state has changed;
- cancellation and repeated cleanup;
- concurrent access to shared application state where applicable.

A Paper-only unit test that executes all callbacks on one test thread is not sufficient evidence of Folia safety.

## 11. Review checklist

Before merging scheduling or threading changes, verify that:

- Paper-only or Paper/Folia code uses Paper scheduling APIs directly unless another platform boundary requires abstraction.
- Shared Paper/Velocity logic keeps platform scheduling behind a common boundary.
- Every deferred server-state operation has an identifiable entity, region, or global owner.
- Entity work uses the entity scheduler rather than a captured location.
- Async work does not access unsafe Bukkit/Paper state.
- Data crossing an async or region boundary is immutable or explicitly thread-safe.
- No tick-owning task waits synchronously for I/O or another scheduler.
- Shared mutable state has a documented concurrency strategy.
- Long-lived tasks are cancelled or otherwise retired with their owning feature.
- `folia-supported: true` is backed by actual Folia-safe behavior.

## References

- [PaperMC: Supporting Paper and Folia](https://docs.papermc.io/paper/dev/folia-support/)
- [PaperMC: Folia overview](https://docs.papermc.io/folia/reference/overview/)
- [PaperMC: Velocity scheduler](https://docs.papermc.io/velocity/dev/scheduler-api/)
