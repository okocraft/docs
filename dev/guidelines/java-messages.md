# Java Message Definitions and Localization

This document defines the standard Java message architecture for OKOCRAFT projects.

It covers message declaration in code, named arguments, loading localized `.properties` files, Adventure translation registration, and the recommended use of [Siroshun09/mcmsgdef](https://github.com/Siroshun09/mcmsgdef).

For wording, MiniMessage style, placeholder naming, and Japanese-specific rules, see [Message Formatting Guidelines](message-formatting.md).

## 1. Requirement Language

The key words **MUST**, **SHOULD**, and **MAY** indicate requirement strength:

- **MUST**: Required unless an exceptional constraint makes compliance impossible.
- **SHOULD**: Expected unless there is a specific, documented reason not to follow it.
- **MAY**: Optional; use when appropriate.

## 2. Standard Architecture

New Java projects SHOULD use this model:

1. declare message keys and their English defaults in Java;
2. represent dynamic values with named Adventure MiniMessage arguments;
3. provide Japanese defaults in a bundled `ja.properties` file;
4. load user-editable locale files from the plugin data directory;
5. add missing keys without overwriting existing user values;
6. register the resulting translations with Adventure's `GlobalTranslator`; and
7. send `MessageKey` or applied typed message keys directly as Adventure components.

English and Japanese MUST be the default locales for new OKOCRAFT message systems.

The intended ownership is:

| Source | Purpose |
| --- | --- |
| Java message declarations | Message keys, English defaults, argument types |
| Bundled `ja.properties` | Japanese default translations |
| Runtime `languages/*.properties` | User-editable translations |
| `GlobalTranslator` | Runtime locale resolution and rendering |

Do not maintain the same English default independently in both Java and a bundled English resource file. Keep one source of truth.

## 3. Dependency

Use `dev.siroshun.mcmsgdef:mcmsgdef` through the project's version catalog.

At the time this guideline was written, current OKOCRAFT projects use `mcmsgdef 1.3.0`.

~~~toml
[versions]
mcmsgdef = "1.3.0"

[libraries]
mcmsgdef = { module = "dev.siroshun.mcmsgdef:mcmsgdef", version.ref = "mcmsgdef" }
~~~

~~~kotlin
dependencies {
    implementation(libs.mcmsgdef)
}
~~~

Keep the version in the version catalog rather than declaring independent versions in individual modules.

`mcmsgdef` requires Java 21+ and Adventure with MiniMessage translation support.

## 4. Declare Messages with `DefaultMessageDefiner`

Create one `DefaultMessageDefiner` for a cohesive message set.

~~~java
public final class Messages {

    private static final DefaultMessageDefiner DEFINER = DefaultMessageDefiner.create();

    public static final MessageKey RELOAD_SUCCESS = DEFINER.define(
        "example.command.reload.success",
        "<gray>Reloaded the configuration.</gray>"
    );

    private Messages() {
        throw new UnsupportedOperationException();
    }
}
~~~

`DefaultMessageDefiner#define` does two things:

- records the English default text; and
- returns a `MessageKey` for use by application code.

New message keys SHOULD include a project or plugin namespace, such as `example.command...`.

This is especially important because Adventure's global translator is shared process-wide.

### 4.1 Expose Default Messages for Loading

The language loader needs access to the collected English defaults.

For a single message class, expose the collected map as an unmodifiable view:

~~~java
@Contract(pure = true)
public static @NotNull @UnmodifiableView Map<String, String> defaultMessages() {
    return DEFINER.getCollectedMessages();
}
~~~

For a multi-module project, each module MAY own its own definer. The language-loading layer can merge the collected maps.

Message keys MUST be unique across all definers registered into the same translation source.

## 5. Declare Named Arguments

Messages with dynamic values SHOULD use `MessageKey.ArgN` produced by `MessageKey#with`.

Use Adventure MiniMessage translation `Argument` values to bind Java values to named placeholders.

~~~java
private static final Placeholder<String> PLAYER =
    player -> Argument.string("player", player);

private static final Placeholder<Integer> AMOUNT =
    amount -> Argument.numeric("amount", amount);

public static final MessageKey.Arg2<String, Integer> GIVE_SUCCESS = DEFINER
    .define(
        "example.command.give.success",
        "<gray>Gave <aqua><amount></aqua> items to <aqua><player></aqua>.</gray>"
    )
    .with(PLAYER, AMOUNT);
~~~

The argument functions passed to `with(...)` define the Java parameter order of `apply(...)`.

The names supplied to `Argument.*` define the placeholders available to localized MiniMessage text.

For example:

~~~properties
# English
example.command.give.success=<gray>Gave <aqua><amount></aqua> items to <aqua><player></aqua>.</gray>

# Japanese
example.command.give.success=<gray>プレイヤー <aqua><player></aqua> に <aqua><amount></aqua>個付与しました。</gray>
~~~

The Japanese translation can reorder `<player>` and `<amount>` without changing the Java call site.

### 5.1 Choose the Appropriate Argument Type

Use the narrowest representation that preserves the intended output.

Use `Argument.string` for plain string data:

~~~java
player -> Argument.string("player", player)
~~~

Use `Argument.numeric` for numbers that should remain numeric:

~~~java
amount -> Argument.numeric("amount", amount)
~~~

Use `Argument.component` when the value already has Adventure structure, such as hover events, nested translations, or styled text:

~~~java
player -> Argument.component("player", player.name().hoverEvent(player))
~~~

~~~java
biome -> Argument.component(
    "biome",
    Component.translatable("biome.minecraft." + biome.value())
)
~~~

Do not flatten a component into a string when its styling, events, or translation behavior should be preserved.

### 5.2 Reuse Placeholders

When multiple messages use the same semantic argument, define a reusable `Placeholder<T>`.

~~~java
private static final Placeholder<String> PLAYER =
    player -> Argument.string("player", player);

private static final Placeholder<Long> SECONDS =
    seconds -> Argument.numeric("seconds", seconds);
~~~

Shared project-level placeholder utilities MAY be used when the same conversion semantics are required across multiple message classes.

Do not reuse a placeholder only because the Java type matches. The placeholder name and rendering semantics must also match.

## 6. Send Messages

`MessageKey` implements `ComponentLike` and renders as an Adventure translatable component.

A message without arguments can be sent directly:

~~~java
sender.sendMessage(Messages.RELOAD_SUCCESS);
~~~

For a typed message, call `apply(...)`:

~~~java
sender.sendMessage(Messages.GIVE_SUCCESS.apply(player.getName(), amount));
~~~

Application code SHOULD use declared message constants instead of reconstructing translation keys manually.

~~~java
// Preferred
sender.sendMessage(Messages.PLAYER_NOT_FOUND.apply(playerName));

// Avoid
sender.sendMessage(Component.translatable("example.command.player-not-found", Component.text(playerName)));
~~~

Keeping construction in the message declaration layer gives reviewers one place to verify keys, placeholder names, argument types, and English defaults.

## 7. Package Japanese Defaults

For a new project, place bundled non-English defaults under a language resource directory:

~~~text
src/main/resources/
└── languages/
    └── ja.properties
~~~

The Japanese file MUST contain the same keys and named placeholders as the English declarations.

~~~properties
example.command.reload.success=<gray>設定ファイルを再読み込みしました。</gray>
example.command.give.success=<gray>プレイヤー <aqua><player></aqua> に <aqua><amount></aqua>個付与しました。</gray>
~~~

English SHOULD remain in Java declarations rather than being duplicated in `languages/en.properties`.

Existing projects MAY retain another resource layout when changing it would create an unnecessary migration.

## 8. Load Runtime Language Files

Use `DirectorySource.propertiesFiles(...)` to load the plugin's user-editable language directory.

The standard locale configuration is:

~~~java
DirectorySource.propertiesFiles(dataDirectory.resolve("languages"))
    .defaultLocale(Locale.ENGLISH, Locale.JAPANESE)
    .primaryLocale(Locale.ENGLISH);
~~~

`defaultLocale(Locale.ENGLISH, Locale.JAPANESE)` ensures both default locale files participate in loading even when they do not yet exist.

`primaryLocale(Locale.ENGLISH)` configures English as the fallback locale for the resulting Adventure translation store.

### 8.1 Supply Default Messages

Use `MessageProcessors.appendMissingMessagesToPropertiesFile(...)` so missing entries are added without replacing user-customized values.

A typical loader is:

~~~java
private @Nullable Map<String, String> loadDefaultMessageMap(
    @NotNull Locale locale
) throws IOException {
    if (locale.equals(Locale.ENGLISH)) {
        return Messages.defaultMessages();
    }

    try (InputStream input = getClass()
        .getClassLoader()
        .getResourceAsStream("languages/" + locale + ".properties")) {
        return input != null ? PropertiesFile.load(input) : null;
    }
}
~~~

Then attach it to the directory source:

~~~java
DirectorySource.propertiesFiles(dataDirectory.resolve("languages"))
    .defaultLocale(Locale.ENGLISH, Locale.JAPANESE)
    .primaryLocale(Locale.ENGLISH)
    .messageProcessor(
        MessageProcessors.appendMissingMessagesToPropertiesFile(
            this::loadDefaultMessageMap
        )
    );
~~~

The append-missing processor preserves existing entries and writes only missing defaults.

This behavior is important because runtime language files are administrator-editable configuration, not generated files that may be overwritten on every startup.

## 9. Register with Adventure

For a plugin that loads messages only once, `loadAndRegister(...)` is the shortest form:

~~~java
DirectorySource.propertiesFiles(dataDirectory.resolve("languages"))
    .defaultLocale(Locale.ENGLISH, Locale.JAPANESE)
    .primaryLocale(Locale.ENGLISH)
    .messageProcessor(
        MessageProcessors.appendMissingMessagesToPropertiesFile(
            this::loadDefaultMessageMap
        )
    )
    .loadAndRegister(Key.key("example", "languages"));
~~~

The translation-source key MUST be unique to the plugin.

Use a stable key such as:

~~~java
Key.key("example", "languages")
~~~

Do not reuse another plugin's translator key.

## 10. Reloading Messages

A project that supports language reloads SHOULD remove its previous translation source before registering a replacement.

Prefer keeping a reference to the registered source:

~~~java
private static final Key LANGUAGE_KEY = Key.key("example", "languages");

private Translator messageSource;

private void loadMessages() throws IOException {
    if (this.messageSource != null) {
        GlobalTranslator.translator().removeSource(this.messageSource);
    }

    var source = DirectorySource.propertiesFiles(
            getDataFolder().toPath().resolve("languages")
        )
        .defaultLocale(Locale.ENGLISH, Locale.JAPANESE)
        .primaryLocale(Locale.ENGLISH)
        .messageProcessor(
            MessageProcessors.appendMissingMessagesToPropertiesFile(
                this::loadDefaultMessageMap
            )
        )
        .loadAsMiniMessageTranslationStore(LANGUAGE_KEY);

    GlobalTranslator.translator().addSource(source);
    this.messageSource = source;
}
~~~

On plugin disable, remove the registered source when practical:

~~~java
if (this.messageSource != null) {
    GlobalTranslator.translator().removeSource(this.messageSource);
    this.messageSource = null;
}
~~~

Do not leave obsolete translation sources registered after a reload.

If an existing project already removes sources by matching `Translator#name()`, it MAY keep that approach, but retaining the exact source reference is easier to reason about.

## 11. Multi-module Projects

A multi-module project SHOULD keep message declarations near the code that owns the behavior.

For example:

~~~text
common/
  CommandMessages.java
  RestartMessages.java

paper/
  PaperCommandMessages.java
~~~

Each domain can own a `DefaultMessageDefiner`.

The language provider can merge English defaults:

~~~java
private static Map<String, String> mergeDefaults(
    List<DefaultMessageDefiner> definers
) {
    Map<String, String> messages = new LinkedHashMap<>();

    for (DefaultMessageDefiner definer : definers) {
        messages.putAll(definer.getCollectedMessages());
    }

    return messages;
}
~~~

Prefer failing a test or validation step on duplicate keys rather than silently relying on `putAll` ordering when independently maintained modules can collide.

The final translator source SHOULD still be unique to the plugin or platform module that registers it.

## 12. Localized Sub-components

A placeholder can itself contain a translatable component.

Use this for domain values that need independent localization.

~~~java
private static final Placeholder<Axis> AXIS =
    axis -> Argument.component(
        "axis",
        Component.translatable(
            "example.axis." + axis.name().toLowerCase(Locale.ENGLISH)
        )
    );
~~~

This is preferable to converting an enum directly to English text before translation.

~~~java
// Avoid when the value is user-facing and localizable
axis -> Argument.string("axis", axis.name())
~~~

The same principle applies to biome names, modes, states, item labels, and other domain concepts with their own translation keys.

## 13. Derived and Composite Messages

It is acceptable to compose translated components when a value itself requires localized formatting.

For example, a duration formatter can return a `ComponentLike` built from singular and plural translation keys, then pass that component as a named argument:

~~~java
private static final Placeholder<Long> REMAINING_TIME =
    seconds -> Argument.component("remaining_time", formatTime(seconds));
~~~

Keep grammar decisions in the localized message layer rather than concatenating English fragments around raw values.

When a concept has language-dependent singular or plural forms, define separate keys or use another explicit localization mechanism.

## 14. Properties File Behavior

`mcmsgdef`'s `PropertiesFile` reads and writes UTF-8.

The default directory loader returns an empty map when a locale file does not exist.

The append-missing processor can therefore create a missing locale file and append its defaults on first load.

Do not assume runtime language files are immutable resources. Administrators may edit them.

When adding a new message key:

- add the English default in Java;
- add the Japanese default resource entry; and
- let the append-missing processor add the new key to existing runtime locale files.

Do not overwrite the entire runtime file only to add new defaults.

## 15. Recommended Example

A minimal message declaration:

~~~java
public final class Messages {

    private static final DefaultMessageDefiner DEFINER =
        DefaultMessageDefiner.create();

    private static final Placeholder<String> PLAYER =
        player -> Argument.string("player", player);

    public static final MessageKey RELOAD_SUCCESS = DEFINER.define(
        "example.command.reload.success",
        "<gray>Reloaded the configuration.</gray>"
    );

    public static final MessageKey.Arg1<String> PLAYER_NOT_FOUND = DEFINER
        .define(
            "example.command.player-not-found",
            "<red>Player <aqua><player></aqua> was not found.</red>"
        )
        .with(PLAYER);

    public static @NotNull Map<String, String> defaultMessages() {
        return DEFINER.getCollectedMessages();
    }

    private Messages() {
        throw new UnsupportedOperationException();
    }
}
~~~

Bundled Japanese defaults:

~~~properties
example.command.reload.success=<gray>設定ファイルを再読み込みしました。</gray>
example.command.player-not-found=<red>プレイヤー <aqua><player></aqua> は見つかりませんでした。</red>
~~~

Runtime loading:

~~~java
private static final Key LANGUAGE_KEY =
    Key.key("example", "languages");

private void loadMessages() throws IOException {
    DirectorySource.propertiesFiles(
            getDataFolder().toPath().resolve("languages")
        )
        .defaultLocale(Locale.ENGLISH, Locale.JAPANESE)
        .primaryLocale(Locale.ENGLISH)
        .messageProcessor(
            MessageProcessors.appendMissingMessagesToPropertiesFile(
                locale -> {
                    if (locale.equals(Locale.ENGLISH)) {
                        return Messages.defaultMessages();
                    }

                    try (InputStream input = getResource(
                        "languages/" + locale + ".properties"
                    )) {
                        return input != null
                            ? PropertiesFile.load(input)
                            : null;
                    }
                }
            )
        )
        .loadAndRegister(LANGUAGE_KEY);
}
~~~

Usage:

~~~java
sender.sendMessage(Messages.RELOAD_SUCCESS);
sender.sendMessage(Messages.PLAYER_NOT_FOUND.apply(playerName));
~~~

For a reloadable plugin, use the source-retention pattern from [Reloading Messages](#10-reloading-messages) instead of repeatedly calling `loadAndRegister`.

## 16. Legacy and Migration

Existing OKOCRAFT projects use several generations of message infrastructure.

Do not migrate a stable project only to make it look identical to this document.

When adding a new message to an existing system:

- follow that system's parser contract;
- preserve existing runtime language files;
- avoid mixing incompatible placeholder syntaxes; and
- use the standard architecture when a deliberate message-system migration is already in scope.

A migration to `mcmsgdef` SHOULD be a dedicated change with explicit verification of:

- existing message keys;
- English and Japanese parity;
- placeholder semantics;
- runtime file preservation;
- reload behavior; and
- translator registration and removal.

## 17. Review Checklist

Before merging a Java message change, verify that:

- the English default is declared in code;
- the Japanese default exists;
- the key follows the project's namespace;
- all localized variants use the same named placeholder set;
- `Argument.string`, `Argument.numeric`, or `Argument.component` matches the value semantics;
- application code uses the declared `MessageKey` rather than a raw translation-key string;
- English and Japanese are configured as default locales;
- English is the primary locale;
- missing defaults are appended without overwriting customized runtime values;
- the translation-source key is unique;
- reloadable plugins remove the previous translation source; and
- message text follows [Message Formatting Guidelines](message-formatting.md).
