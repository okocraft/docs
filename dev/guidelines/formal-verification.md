# Formal Verification Guidelines

This document explains when and how OKOCRAFT Java projects should use formal methods to obtain **specific, reviewable correctness guarantees**. It complements [Testing Guidelines](java-testing.md), [Paper and Folia Scheduling and Threading](paper-folia-scheduling-and-threading.md), and [Minecraft / Paper End-to-End Testing](minecraft-paper-e2e-testing.md); it does not replace them.

Formal verification is **risk-based and optional by default**. Do not add proof infrastructure to every plugin or introduce new production abstractions solely to satisfy a prover.

The keywords **MUST**, **SHOULD**, and **MAY** express requirement strength for a project that chooses to undertake a verification effort.

## 1. What counts as verification

Distinguish the evidence before deciding what to claim:

| Method | Useful for | What a successful run establishes |
| --- | --- | --- |
| Deductive verification (JML with OpenJML or KeY) | Java method contracts, invariants, integer arithmetic | The specified property follows from the model, contracts, and assumptions accepted by the prover |
| Bounded model checking (JBMC) | Java bytecode, assertions, bounded paths | No counterexample was found **within the explicitly configured bounds and supported model** |
| State-machine model checking (TLA+ / TLC) | Concurrent saves, lifecycle transitions, distributed protocols | An invariant holds in **the finite, abstract model that was explored**, not automatically in the Java implementation |
| Property-based / randomized tests | Input ranges, arithmetic and state transitions | The property held for the generated test executions; this is **not a proof** |
| JVM concurrency stress testing (jcstress) | CAS, locks, visibility, ordering | The observed outcomes under the executed schedules; this is **not exhaustive proof** |
| JUnit, lightweight Paper tests, server E2E tests | Integrations, real game behavior, platform APIs | Evidence for the scenarios actually exercised |

A Java verifier's acceptance is not a proof about every JVM version, native dependency, platform implementation, or Minecraft server behavior. Proof claims always have a scope.

**MUST:** Never describe a bounded check, randomized test, passing build, unreviewed AI analysis, or abstract model result as a proof of the complete production plugin.

## 2. Choose valuable properties, not arbitrary classes

Prefer narrowly stated properties where a violation could lose player data, duplicate or destroy items, bypass permissions, corrupt persistent state, or cause an expensive operational failure.

| Area | Example property to investigate | Important boundary |
| --- | --- | --- |
| Item quantities / balances | Nonnegative quantities; saturation and overflow accounting; no unexplained creation or loss | Define legal arguments and external item sources/sinks |
| Inventory transfers and crafting | Successful transfer preserves the total across modeled containers; failure leaves the modeled state unchanged | Bukkit events, cancellation, other plugins and inventories are external effects |
| Batch stock changes | Either all requested decrements happen or none do | A lock only establishes an atomic region if all relevant paths participate |
| Persistence / reload | Completed saves preserve an agreed snapshot; failed writes remain pending; reload does not silently lose accepted updates | File-system failures, durability, retry and process crashes need explicit models |
| Async / Folia | Updates are linearizable or follow a documented ordering; obsolete tasks cannot mutate retired state | Scheduler ownership and JVM memory semantics cannot be inferred from a sequential proof |
| Permission / routing | A denied player cannot complete a protected transition under specified policy | Permission lookup, bypasses, server-kick fallback and third-party hooks must be included |
| Rewards / one-time actions | At most one successful claim per player and reward period | Date/time source, retries, crash recovery and multi-server state |

A property has higher value when it is a user-facing invariant, spans multiple call paths, and has a credible high-impact failure mode. Avoid proving trivial private getters while critical state transitions remain unexamined.

### 2.1 Candidate properties from existing OKOCRAFT repositories

These are **proposals for investigation, not verified results or confirmed defects**. Review the current revision and tests before using them in a project:

- [Box `Stock`](https://github.com/okocraft/Box/blob/main/core/src/main/java/net/okocraft/box/core/model/stock/Stock.java): nonnegative quantities, overflow accounting, safe subtraction, and whether CAS operations have the intended sequential semantics.
- [Box `StockHolderImpl`](https://github.com/okocraft/Box/blob/main/core/src/main/java/net/okocraft/box/core/model/stock/StockHolderImpl.java): atomic multi-item decrement, returned values, and event/stock consistency.
- [Box `ItemCrafter`](https://github.com/okocraft/Box/blob/main/features/craft/src/main/java/net/okocraft/box/feature/craft/gui/util/ItemCrafter.java): bounds for multiplication, required ingredients, recipe output and remainder accounting.
- [Box `PerItemChangeState`](https://github.com/okocraft/Box/blob/main/core/src/main/java/net/okocraft/box/core/model/loader/state/PerItemChangeState.java): changes racing with snapshot and save, retry on storage error, and whether updates remain scheduled for persistence.
- [DailyRewards `ReceiveData`](https://github.com/okocraft/DailyRewards/blob/master/src/main/java/net/okocraft/dailyrewards/data/ReceiveData.java): claim deduplication, daily reset and asynchronous persistence.
- [ServerConnector `PlayerListener`](https://github.com/okocraft/ServerConnector/blob/master/src/main/java/net/okocraft/serverconnector/listener/PlayerListener.java): initial and subsequent connection permission rules and fallback exceptions.

Avoid treating one repository's example as an organization-wide requirement to verify that class.

## 3. Specify the claim before selecting the tool

A verification task **MUST** state:

1. **Property:** what must hold in domain language, including forbidden behavior and relevant observable effects.
2. **Preconditions:** valid inputs, state invariants, arithmetic limits and required permissions; invalid-input behavior should be defined separately.
3. **Postconditions:** successful and failed outcomes, return values, state changes, exceptions, and externally visible events.
4. **Boundary:** which production implementation and revision are covered, including models or adapters for Paper, Folia, Velocity, storage, clocks and third-party plugins.
5. **Concurrency and failures:** allowed interleavings, cancellation, exceptions, retries, crashes and incomplete writes, if relevant.
6. **Assumptions and exclusions:** anything the checker does not establish (including assumed method contracts and an abstract model's relation to production code).

Specifications **MUST** be reviewed against actual intended behavior, documentation, tests and platform contracts **independently of whether the verifier can prove them**. A proof of the wrong specification is not useful.

### 3.1 Example: saturating stock addition

For a nonnegative stock `old`, nonnegative increment `requested`, and `MAX = Integer.MAX_VALUE`, the intended mathematical model could be:

```text
assume 0 <= old <= MAX and 0 <= requested <= MAX
accepted = min(requested, MAX - old)
newStock = old + accepted
excess = requested - accepted

ensure 0 <= newStock <= MAX
ensure 0 <= accepted <= requested
ensure accepted + excess == requested
ensure newStock - old == accepted
```

These expressions use **mathematical integers**, not overflowing Java `int` arithmetic. A verifier must explicitly account for the conversion to Java integer semantics. Also check the implemented overflow result and event accounting; satisfying only `newStock <= MAX` would be too weak.

This example covers one abstract operation, **not** a proof of `Stock.add()`, `StockHolderImpl`, events, persistence, or concurrent execution.

### 3.2 Example: inventory transfer

Define the transfer's conservation rule in terms of the specific modeled source and destination:

```text
beforeSource + beforeDestination
  == afterSource + afterDestination
```

Account explicitly for intentionally created/consumed items, capped capacity, rejected amounts, crafting byproducts, event handlers, and partially completed external API calls. If those cannot be made atomic, do not claim an end-to-end atomic transfer solely because the stock counter is atomic.

## 4. Select a verification method

1. **Pure, sequential Java calculations and contracts:** consider [OpenJML](https://www.openjml.org/) or [KeY](https://www.key-project.org/). Start with a small piece of domain logic and well-defined JML pre/postconditions.
2. **Java bytecode and bounded paths:** consider [JBMC](https://github.com/diffblue/cbmc/blob/develop/doc/cprover-manual/jbmc-user-manual.md). Record loop bounds, unwind checks, relevant library models, and other completeness limits.
3. **Save/reload protocols, concurrent state transitions, routing:** consider [TLA+ / TLC](https://docs.tlapl.us/using%3Atlc%3Astart) for a small abstract state machine. Review how each model transition maps to production Java; finite-state exploration alone does not verify that mapping.
4. **CAS, VarHandle, locks and Java Memory Model outcomes:** add [jcstress](https://github.com/openjdk/jcstress) or another focused concurrency harness. A sequential JML proof does not establish concurrent correctness.
5. **Integrations with Paper/Folia/Velocity, Bukkit events, real inventories, world state or persistence:** keep JUnit, boundary tests and/or real-server E2E tests according to existing [Testing Guidelines](java-testing.md).

**MUST:** Check the selected tool's current support for the repository's actual Java language version, bytecode, libraries and concurrency features before investing in a proof. In particular, do not assume that a current Paper plugin's Java source or bytecode is accepted by every Java verifier.

A small, behaviorally equivalent, tool-compatible pure-Java component or mathematical model **MAY** be extracted when there is a real domain boundary. Document the abstraction and verify its correspondence to the production implementation; **do not** silently substitute a rewritten toy implementation and claim the original code was proved.

## 5. Workflow for engineers and coding agents

1. **Inspect:** read production code, adjacent tests, public contracts and relevant platform documentation. Start from a concrete failure mode, not a generic desire for more proofs.
2. **Write the claim:** create a short statement of the invariant, legal inputs, expected failure behavior, trusted dependencies and excluded cases. Identify which test or player-facing behavior establishes that this is the right contract.
3. **Choose the smallest verification boundary:** isolate pure logic only where the abstraction is faithful and maintainable. For state machines, name the Java operations corresponding to modeled transitions.
4. **Review the specification:** a human reviewer (preferably someone familiar with the feature) confirms that the claim does not weaken behavior to make proving easy.
5. **Run the checker:** use pinned toolchains, deterministic scripts/configuration, and a command reproducible outside the coding agent. Preserve counterexamples, proof obligations and logs.
6. **Cross-check behavior:** turn counterexamples into JUnit or integration regression tests when reproducible; use property-based tests or jcstress where the prover lacks coverage. Verify that implementation behavior still matches the abstract model.
7. **Record evidence and integrate:** publish a scoped verification record as described below. Only promote a check to required CI after it is reliable, maintainable and its limitations are clear.
8. **Maintain:** re-run affected checks on code, specification, dependency or tool changes; review whether changed behavior invalidates a previously proven claim.

### 5.1 AI-assisted proof work

Coding agents **MAY** propose invariants, pre/postconditions, JML annotations, state-machine models, test generators, counterexample interpretations and proof scripts. The proof tool, not the LLM's explanation, determines whether a check was accepted.

Agents **MUST NOT** silently weaken preconditions, omit difficult paths, replace production behavior with simpler assumptions, disable verification checks, or change both code and specification just to turn a failure green. Any such scope change requires explicit review and a corresponding update to the claimed guarantee.

Human review focuses on **specification validity, model-to-implementation correspondence, trusted assumptions and operational impact**, not merely the number of generated proof lines.

## 6. Evidence, status and CI operations

Each verification task **SHOULD** have a small, version-controlled record near the relevant module, such as `verification/README.md` or a scoped project document. Use the following template, adapting it to the selected tool:

```md
### FV-001: <domain guarantee>
- Owner: <maintainer/team>
- Target: <repository path, symbol and source commit>
- Property: <invariant, success/failure behavior>
- Preconditions: <valid inputs and environmental assumptions>
- Scope: <Java/runtime/tool model, bounds, scheduling, dependencies>
- Out of scope: <unverified behaviors>
- Method/tool: <tool + pinned version>
- Reproduce: <exact local/CI command>
- Evidence: <checked-in spec/config, logs/artifact location, result>
- Status: PROVED | MODEL_CHECKED | BOUNDED | TESTED | UNVERIFIED
- Reviewed by: <reviewer and date>
- Follow-up: <counterexample, open obligations or limitations>
```

Interpret result labels narrowly:

- **PROVED:** an accepted deductive proof for the stated implementation, property, assumptions and supported semantics.
- **MODEL_CHECKED:** the stated invariant was checked over the recorded model, constants and reachable state space (not the production implementation).
- **BOUNDED:** the configured bounded check completed without a counterexample; no general proof is implied.
- **TESTED:** executed scenarios passed; probabilistic or platform test results remain tests.
- **UNVERIFIED:** unsupported, inconclusive, timed out, skipped, invalidated, or not executed. Record the reason.
- A discovered counterexample or failing obligation is a **FAIL** with evidence, not a success status.

CI **SHOULD**:

- start with an opt-in or manually triggered verification job and a fast, deterministic scope;
- pin solver/verifier/runtime versions and store model/contract, command, inputs, bounds and result;
- use separate jobs or compatible toolchains if the prover cannot process the project's Java version;
- distinguish a verified result from an incomplete run, timeout, unsupported feature or skipped check;
- fail an established required proof job if its previously accepted obligations cease to verify;
- avoid blocking routine PRs on a slow experimental check until reliability and maintenance cost have been assessed.

Use the existing [Java Project, Gradle, and CI Guidelines](java-project-gradle-and-ci.md) for build conventions. Keep long-running state-space exploration or stress tests outside the ordinary fast `test` task when practical.

A successful verification job **MUST NOT** be reported as proof of behavior outside its stated scope. Preserve machine-readable results or logs when available, not only an AI-written summary.

## 7. Initial adoption for OKOCRAFT

A practical first experiment is **Box's stock quantity logic**, because there are existing [`StockTest`](https://github.com/okocraft/Box/blob/main/core/src/test/java/net/okocraft/box/core/model/stock/StockTest.java) and [`StockHolderTest`](https://github.com/okocraft/Box/blob/main/core/src/test/java/net/okocraft/box/core/model/stock/StockHolderTest.java) cases to help derive an intended contract.

1. Review the stock arithmetic contract with a maintainer; include `0`, `MAX`, insufficient quantities and overflow.
2. Establish whether a verifier can handle the **actual** target methods. If not, verify a small pure arithmetic kernel with a documented production binding; label any unverified correspondence clearly.
3. Keep concurrency as a **separate obligation**: the CAS/lock behavior needs explicit concurrent reasoning or focused stress tests.
4. Save the reproducible command, spec, limits and evidence before treating the result as a project guarantee.
5. Only then consider batch decrements, crafting arithmetic and persistence interleavings.

The goal of the experiment is **one useful, reproducible and honestly scoped guarantee**, not a proof-count metric or a claim that the entire plugin is bug-free.

## 8. Review checklist

- [ ] The claim prevents a realistic, meaningful failure and states the user-facing guarantee.
- [ ] Preconditions, invalid-input handling, observable effects and arithmetic semantics are explicit.
- [ ] The checked Java revision / model and all exclusions are documented.
- [ ] Platform, storage, clock, concurrency and external-plugin assumptions are reviewed.
- [ ] A human reviewed the specification separately from proof success.
- [ ] The verification command, tool version and evidence are reproducible.
- [ ] Bounded/model/test results are never mislabeled as production proofs.
- [ ] CI timeouts, skipped checks and unsupported features are reported as inconclusive.
- [ ] Existing JUnit, threading and E2E coverage remains appropriate.

## References

- [OpenJML documentation](https://www.openjml.org/documentation/)
- [KeY: Java coverage and limitations](https://keyproject.github.io/key-docs/user/SupportedFeatures/JavaCoverage/)
- [JBMC user manual](https://github.com/diffblue/cbmc/blob/develop/doc/cprover-manual/jbmc-user-manual.md)
- [TLA+ / TLC model checker](https://docs.tlapl.us/using%3Atlc%3Astart)
- [OpenJDK jcstress](https://github.com/openjdk/jcstress)
