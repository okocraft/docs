# Writing Scenarios

A scenario turns one planned operation (`OP-xxx`) into code that creates the condition, performs the action, and records evidence. The harness provides `defineScenario`, `E2eEnv` (server + bots + helper wrappers) and `Recorder`. See `paper-e2e/harness/examples` for a runnable example.

## 1. Mapping from TESTING.md

| TESTING.md | Scenario |
| --- | --- |
| `OP-xxx` Setup | `setupCommands` and the bots in `bots`, plus setup at the start of `run` |
| `OP-xxx` Operation | The actions in `run` (bot chat/commands, console commands, teleports) |
| `OP-xxx` Verify / PASS criteria | `recorder.check(...)` calls with evidence |
| `Covers` (`VP`, `CB`, `DP`) | The `covers` list, copied as-is |

One scenario per operation keeps the traceability simple. Merge several observations into one scenario when the operation does, as planned.

## 2. Shape of a scenario

```ts
export default defineScenario({
  id: "OP-001",
  title: "…",
  covers: ["VP-001", "CB-001"],
  bots: ["Admin", "A", "B"],
  setupCommands: ["gamerule spawn_mobs false", "op Admin"],
  async run(env, recorder) {
    // 1. create the condition (regions, teams, entities, permissions)
    // 2. perform the action
    // 3. record what was observed, with evidence
  },
});
```

`recorder.check(id, title, ok, evidence, covers)` requires non-empty evidence. Use `recorder.unverified(...)` for anything the scenario cannot establish.

## 3. Rules for good scenarios

- **Assert on observations.** Use `bot.messages` (text and translation key), `bot.packets`, helper output (`env.position`, `env.helper`), and server log lines. Do not assert that a command "ran".
- **Pair every negative with a control.** For "player A must not receive X", also assert that player B does, in the same run. For "action denied", also assert it succeeds for an allowed actor or outside the protected area.
- **Count, do not just detect.** Count deliveries to catch duplicates.
- **Use fixed, deterministic setups.** Teleport players to known coordinates, spawn entities with fixed names, set difficulty and gamerules, and clear bot buffers (`env.clearAll()`) right before the action.
- **Reset between actions.** Put players and entities back (or spawn fresh ones) so one step does not change the next step's starting state. Players who die respawn automatically; re-teleport them.
- **Check the whole matrix when the plugin has rules.** For allow/deny/unset flags or modes, enumerate the cases (member, non-member, bypass, outside) instead of a single happy path.
- **Compare with the platform when the plugin reproduces platform behavior.** Run the same scenario without the plugin and compare, instead of relying on remembered expectations.
- **Test persistence through a graceful restart.** Stop the server, check the file, start again with `fresh: false`, and observe behavior, not only the file.
- **Test permissions through the real path.** Grant or deny the node with `env.permission(...)` (LuckPerms), then run the command as a non-operator bot and assert on the server's answer and on the unchanged behavior. Check the default, granted, and denied states.
- **Record the exact observation.** Put the received text, packet name, coordinates, or counts in the evidence string.

## 4. Useful recipes

| Need | How |
| --- | --- |
| Operator-only setup through real commands | `op <name>` from the console, then the bot sends the command (for WorldEdit/WorldGuard: `//pos1`, `//pos2`, `/rg define`, `/rg flag`) |
| Kill a player and observe the death message | console `kill <name>`; read `messages` whose `translate` starts with `death.` and the death screen packet (`death_combat_event`) |
| Entity interaction | `e2espawn`, then `bot.raw.activateEntity(...)` / `bot.raw.attack(...)`; read health with `e2ehealth` |
| Equipment changes | `e2eequip <player> <slot> <material>` |
| Teams | console `team add/join/modify` |
| Observe an event's final state | `e2elisten <fully.qualified.EventClass>` (logs after all listeners ran) |
| Vehicles | place a rideable entity, drive it with repeated velocity from a helper or command, and sample the passenger's position |

## 5. Common causes of wrong results

- The control channel is broken (the bot died, was disconnected, or missed messages), so a "not received" result is meaningless. Always include the control.
- A previous step left state behind (dead players, leftover entities, active effects).
- Timing: the observation window is too short for scheduled work, or the check ran before the server applied a teleport.
- The scenario, not the plugin, is wrong. Before reporting a plugin defect, look at the server log and reproduce once more with extra logging.
