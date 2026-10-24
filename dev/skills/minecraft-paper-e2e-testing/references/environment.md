# Environment and Execution

Use the harness and helper plugin from [okocraft/public-ops `paper-e2e`](https://github.com/okocraft/public-ops/tree/main/paper-e2e) (clone it or use an existing checkout). Its README has the commands; this file explains the decisions and the pitfalls.

## 1. Prerequisites

| Need | Notes |
| --- | --- |
| Java matching the Minecraft version | Paper for current Minecraft needs a recent JDK (check the Paper requirements for the version). Use a JDK path in `--java` when several are installed. |
| Node.js 24+ and pnpm | The harness runs TypeScript directly with Node type stripping. |
| Gradle wrapper | Only to build the helper plugin. |
| Network | Paper (PaperMC Fill API), ViaVersion/ViaBackwards (Hangar), npm, Maven. Behind an HTTP proxy set `NODE_USE_ENV_PROXY=1` for the harness downloads. |

No Minecraft account and no human client are needed.

## 2. Build the environment

1. Build the plugin under test the way its repository documents (for example `./gradlew build`). Record the commit SHA.
2. Build the helper plugin (`paper-e2e/helper-plugin`, `./gradlew build`).
3. `node src/cli.ts prepare --dir <server-dir> --minecraft <version>` downloads Paper (SHA-256 verified) and, when the bot library does not support that version, ViaVersion and ViaBackwards.
4. Copy into `<server-dir>/plugins`: the plugin under test, its required dependencies (at the versions the project declares), and the helper plugin.
5. Start with the harness. It writes `eula.txt` and `server.properties` (loopback, `online-mode=false`, flat world, peaceful, small view distance) and deletes worlds for a fresh start.

Check that the plugin loaded: the log has `Enabling <Plugin>` and no `ERROR` or exception caused by it. Treat unrelated startup noise explicitly (for example flat world generator-settings warnings) and say so in the report.

If the Paper version you need is not available, use the nearest available version at or above the plugin's minimum, and record the difference.

## 3. Bots and protocol versions

Bots are real protocol clients (mineflayer). `chooseClientVersion` picks the newest client version the library supports.

- Server version supported by the library: connect natively.
- Server newer than the library: install ViaVersion + ViaBackwards on the server and connect with the newest supported client. **The report must say so**: packet shapes and client-visible behavior can differ from a native client.
- If neither works, run what you can and mark the rest `UNVERIFIED`.

Known harness behavior: the library's movement packets for recent versions can be rejected by the server ("Invalid move player packet"), so the harness drops movement packets after the teleport handshake. Bots stand still. Move them with `tp`; walking-dependent behavior is not tested this way.

## 4. Controlling the game

Prefer, in this order:

1. The plugin's real commands and permissions, run by a bot (an operator bot for admin commands). This also covers command registration and permissions.
2. Vanilla console commands: `tp`, `kill`, `effect`, `setblock`, `summon`, `gamerule`, `team`, `difficulty`, `data get`, `execute`.
3. Helper plugin commands: `e2epos` (read position), `e2espawn`/`e2ehealth`/`e2eexists` (entities), `e2eequip`, `e2eperm` (grant or deny a permission node), `e2elisten` (log an event class after all other listeners). They print structured `E2E <TAG> key=value` lines that the harness parses.

Observe in this order of strength: what a bot received (messages, packets), then server state read through the helper or `data get`, then log lines. Prefer a bot's received data for anything a player should see.

## 5. Execution

```sh
node src/cli.ts run --dir <server-dir> --minecraft <version> --java <java> <scenario>...
```

- Each scenario runs on a fresh server; the server is stopped gracefully so persistence checks work, and killed on harness exit.
- Output: `report.md`, `results.json`, and `<server-dir>/e2e-console.log` (every console line and every command sent).
- Exit code is non-zero when a check fails.

## 6. Pitfalls

- Gamerule and command names change between Minecraft versions (recent versions use snake_case such as `spawn_mobs`, `show_death_messages`). Check the server's own messages for `Unknown` errors.
- Chunks that are not entity-ticking freeze moving entities (for example a minecart driven toward a boundary). Use `forceload add` for the path.
- Do not kill the server with `pkill -f paper.jar` from a shell whose own command line contains the same text; use a pattern that cannot match itself, or the harness.
- Operators bypass WorldGuard by default. Use non-operator bots for protection checks and an operator bot as the bypass control.
- Waits are the main source of flakiness. Wait for an observable condition when you can; use fixed sleeps only for settling (chunks, scheduled tasks).
- Some systems resolve Gradle dependencies unreliably through restricted proxies. If Gradle cannot resolve artifacts that curl can fetch, say so, build with an equivalent tool for verification, and state the deviation in the report.
- Natural events are hard to reproduce. Plant the conditions (for raids: job-site blocks plus villagers that have claimed them, a bad omen effect, non-peaceful difficulty; the raid omen effect command alone does not start a raid).
