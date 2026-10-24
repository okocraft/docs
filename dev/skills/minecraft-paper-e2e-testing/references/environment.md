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

Check the versions before starting, because a mismatch fails late and unclearly: `node --version` (24+), `pnpm --version`, and `java --version` (the harness passes `--java`; recent Paper needs Java 25, while the machine's default may be older). If the required runtime is not installed, install it before doing anything else instead of working around it.

## 2. Build the environment

1. Build the plugin under test the way its repository documents (for example `./gradlew build`). Record the commit SHA.
2. Build the helper plugin (`paper-e2e/helper-plugin`, `./gradlew build`).
3. `node src/cli.ts prepare --dir <server-dir> --minecraft <version>` downloads Paper (SHA-256 verified) and, when the bot library does not support that version, ViaVersion and ViaBackwards.
4. Copy into `<server-dir>/plugins`: the plugin under test, its required dependencies (at the versions the project declares), and the helper plugin.
5. Start with the harness. It writes `eula.txt` and `server.properties` (loopback, `online-mode=false`, flat world, peaceful, small view distance) and deletes worlds for a fresh start.

Every scenario starts with fresh worlds only. Plugin data and server files survive between scenarios (`ops.json`, `usercache.json`, the plugin's own data folder, LuckPerms data), so a result can depend on an earlier scenario. List what must be reset with `--reset <path>` (relative to the server directory, repeatable), for example `--reset plugins/<Plugin> --reset ops.json --reset usercache.json --reset plugins/LuckPerms`.

Check that the plugin loaded: the log has `Enabling <Plugin>` and no `ERROR` or exception caused by it. Treat unrelated startup noise explicitly (for example flat world generator-settings warnings) and say so in the report. `No key layers in MapLike[{}]` is printed as `ERROR` on every start of the flat test world and is harmless; `server.errors()` in the harness already skips it, so use that for error scans.

If the Paper version you need is not available, use the nearest available version at or above the plugin's minimum, and record the difference.

## 3. Bots and protocol versions

Bots are real protocol clients (mineflayer). `chooseClientVersion` picks the newest client version the library supports.

- Server version supported by the library: connect natively.
- Server newer than the library: install ViaVersion + ViaBackwards on the server and connect with the newest supported client. **The report must say so**: packet shapes and client-visible behavior can differ from a native client.
- If neither works, run what you can and mark the rest `UNVERIFIED`.

Per-bot options are set where the bot is declared (`bots: [{ username, recordPackets, locale }]`, or `env.join`). `recordPackets` is a regular expression on packet names; the default keeps only death and merchant packets, so declare what the check needs (for example `/world_particles|sound_effect|system_chat/`). `locale` sets the client language (`ja_JP`) for plugins that translate messages per player.

Known harness behavior: the library's movement packets for recent versions can be rejected by the server ("Invalid move player packet"), so the harness drops movement packets after the teleport handshake. Bots stand still. Move them with `tp`; walking-dependent behavior is not tested this way.

## 4. Controlling the game

Prefer, in this order:

1. The plugin's real commands and permissions, run by a bot (an operator bot for admin commands). This also covers command registration and permissions.
2. Vanilla console commands: `tp`, `kill`, `effect`, `setblock`, `summon`, `gamerule`, `team`, `difficulty`, `data get`, `execute`.
3. Helper plugin commands: `e2epos` (read position), `e2espawn`/`e2ehealth`/`e2eexists` (entities), `e2eequip`, `e2elisten` (log an event class after all other listeners). They print structured `E2E <TAG> key=value` lines that the harness parses.

Observe in this order of strength: what a bot received (messages, packets), then server state read through the helper or `data get`, then log lines. Prefer a bot's received data for anything a player should see.

### Permissions

For checks that depend on permissions, use a real permission plugin: `prepare --plugin luckperms` installs LuckPerms, and scenarios call `env.permission(player, node, "true" | "false" | "unset")` (`lp user <player> permission ...`).

- Do not op the bot under test: operators get Bukkit's `default: op` permissions, which hides missing grants. Use an operator bot only as the "allowed" control.
- Cover the default state (no grant), an explicit grant, and an explicit denial.
- The user must exist: let the bot join first, then set the node. LuckPerms looks users up by lowercase name; if the log says the user was not found, check the name before concluding anything about the plugin.
- `lp user <name> permission check <node>` shows what LuckPerms resolved. It proves the setup, not the plugin's behavior, so it never replaces the observation below.
- Confirm the effect from what the bot receives, and take a control from before the grant, as the permission plugin's own log line only shows that the node was stored.

## 5. Execution

```sh
node src/cli.ts run --dir <server-dir> --minecraft <version> --java <java> <scenario>...
```

- Each scenario runs on a fresh server; the server is stopped gracefully so persistence checks work, and killed on harness exit.
- Output: `report.md`, `results.json`, and the console log of every scenario in `<out>/logs/<scenario id>.log` (every console line and every command sent). `<server-dir>/e2e-console.log` only holds the last run, because each scenario starts a new log.
- Exit code is non-zero when a check fails.

### Keeping a run short

Measured on a real run (28 server starts for 9 scenarios, about 20 minutes of server time): about half of the time is boot, bot joining and shutdown, which every fresh server pays, and most of the rest is fixed sleeps. Plan for it:

- Use `--parallel <n>` (at most one worker per CPU core) to run independent scenarios at once. Each still gets a fresh server on its own port. Four sample scenarios took 86 s one after another and 35 s with four workers.
- The first `run` creates a start-up archive (`<server-dir>/.e2e/app.jsa`); each later start is about 5 s faster. Delete it after changing Java or `paper.jar`.
- After a fix, re-run only what is needed with `--only <id>`; run the whole set once at the end. Re-runs and exploratory probes were a large share of the measured server time.
- Explore on one long-lived server (start it once, send commands, read the log) instead of starting a server per question, then write the result down as a scenario.
- Wait for the condition: `sayUntil`, `helper`, `permission`, `waitFor` and `runUntil` return when the server has answered. A check that something does **not** happen needs a fixed window; keep it as short as the plugin's own timing allows (a cooldown sets the minimum) and give it a control.
- When a build step fails on a rate limit (Gradle 429), do not wait with fixed sleeps and retry blindly. Fall back to the offline/`mavenLocal` route at once and state the deviation.
- Run long steps in the background and check a condition (a file, a log line) instead of sleeping for a guessed time.

## 6. Pitfalls

- Gamerule and command names change between Minecraft versions (recent versions use snake_case such as `spawn_mobs`, `show_death_messages`). Check the server's own messages for `Unknown` errors.
- Chunks that are not entity-ticking freeze moving entities (for example a minecart driven toward a boundary). Use `forceload add` for the path.
- Do not kill the server with `pkill -f paper.jar` from a shell whose own command line contains the same text; use a pattern that cannot match itself, or the harness.
- A teleport to integer coordinates puts the player at the block center (`tp A 10 64 10` gives `10.5 64 10.5`). Compare positions with that offset, or with a tolerance, or a correct plugin looks like a failure.
- Operators bypass WorldGuard by default. Use non-operator bots for protection checks and an operator bot as the bypass control.
- Waits are the main source of flakiness. Wait for an observable condition when you can; use fixed sleeps only for settling (chunks, scheduled tasks).
- Some systems resolve Gradle dependencies unreliably through restricted proxies. If Gradle fails with HTTP 429 from Maven Central, retry after a short wait; if it keeps failing, or cannot resolve artifacts that curl can fetch, say so, build with an equivalent tool for verification, and state the deviation in the report.
- Natural events are hard to reproduce. Plant the conditions (for raids: job-site blocks plus villagers that have claimed them, a bad omen effect, non-peaceful difficulty; the raid omen effect command alone does not start a raid).
