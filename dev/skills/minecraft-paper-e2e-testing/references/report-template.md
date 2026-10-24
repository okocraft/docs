# E2E Test Report Template

Fill in with facts from the run. Remove sections that do not apply. Never mark a check `PASS` unless it ran and the evidence supports it.

```markdown
# <Plugin> E2E Test Report

## 1. Target and environment

- Repository and commit: `<owner/repo>@<sha>` (<what changed>)
- Minecraft / Paper: `<version>` build `<n>`; Java `<version>`
- Dependencies and other plugins (with versions): …
- Bot library and client protocol: `<library version>`, client `<version>`
- **Protocol translation:** none | ViaVersion + ViaBackwards `<version>` (client-visible behavior may differ from a native client)
- Harness / helper plugin revision: `okocraft/public-ops@<sha>`
- Constraints of this environment: …

## 2. Results

| Operation / check | Result | Executed | Expected | Actual / evidence |
| --- | --- | --- | --- | --- |
| OP-001 … | PASS / FAIL / UNVERIFIED | commands or scenario | … | received messages, packets, positions, log lines |

Summary: PASS n / FAIL n / UNVERIFIED n

## 3. Evidence

Selected server log lines and bot-received data that justify the results.

## 4. Defects

For each defect:
- **Summary** and affected viewpoint (`VP-xxx`)
- **Reproduction steps** (exact commands)
- **Observed vs expected** with logs
- **Suspected cause** (file and symbol) and how confident you are
- **Minimal fix** and the evidence that it works (failing scenario now passes; control still passes). State if it was verified only on a scratch copy.

## 5. Not verified

Each item with the reason (environment limit, missing client support, Folia, rendering, unavailable dependency, …).

## 6. Assessment

Is the target releasable? Base it only on what was observed, name the blockers, and name the residual risk from the unverified items.
```

Language: write the report in the language the user uses. Keep IDs and commands unchanged.
