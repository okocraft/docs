# Game Test Checklist

<!-- One-time checklist for a specific Minecraft/Paper update. Fill with
     verified source and upstream evidence; do not copy transient UV/NEW-OP
     items verbatim into the plugin's persistent TESTING.md. -->

## Target

**Plugin:** <name and repository/ref>

**From:**
- Minecraft: <version>
- Paper: <version/build, or N/A with reason>

**To:**
- Minecraft: <version>
- Paper: <version/build, or N/A with reason>

**Upstream evidence:**
- <Official Minecraft release note URL>
- <Official Paper release note/changelog URL>
- <API diff, documentation, or issue URL if needed>

## Additional Viewpoints for This Update

<!-- If none are justified, write "None: <reason>" instead of inventing UVs. -->

### UV-001: <Specific observable check>

**Related update:** <What changed, version/build, and source URL.>

**Dependency:** DP-001

**Possible regression:** <Concrete observable in-game failure.>

**Affected behavior / viewpoint:** CB-001 / VP-001

**Covered by:** OP-001 | NEW-OP-001

**Reuse decision:** As-is | Verify-only | Modified | New

**Reason:** <Why this operation suffices, or why it must be altered/created.>

## Operation Checklist

### Environment

- [ ] The intended Minecraft/Paper server version is running with the target plugin build.
- [ ] The plugin enables successfully, without a plugin-related startup exception.
- [ ] Required permissions, configuration, players, and controlled world fixtures are ready.

### OP-001: <Existing operation from TESTING.md>

- [ ] Execute OP-001.

**Setup and operation:**
1. <Briefly repeat or precisely reference reproducible steps from TESTING.md.>
2. <Any update-specific modification, if required.>

**Normal verification:**
- [ ] <Expected observable result from the existing operation.>
- [ ] <Expected absence of an important negative effect, if relevant.>

**Additional checks for this update:**
- [ ] <UV-001: extra observation, or "None; existing criteria already cover UV-001".>

### NEW-OP-001: <Only if an existing operation cannot cover the change>

- [ ] Execute NEW-OP-001.

**Reason:** <Why no existing operation can reveal the regression.>

**Setup and operation:**
1. <Deterministic setup.>
2. <Exact action.>

**Verify:**
- [ ] <Specific observable PASS condition.>

## Log Check

- [ ] No plugin-related exception occurred during the operations above.

## Result

- [ ] PASS — all applicable checks passed.
- [ ] FAIL — at least one applicable check failed.

**Failure notes:** <Failed operation/UV, expected vs. actual result, reproducible steps, relevant log evidence, or "None".>

## Reviewed but No Additional Check

### <Significant upstream change reviewed>

**Source:** <Official changelog/API reference URL.>

**Reason:** <API not used, compile-only effect, covered by automated tests, existing operation already sufficient, or no observable failure path.>
