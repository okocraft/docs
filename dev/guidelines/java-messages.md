# Java Message Definitions and Localization

This document defines the standard Java architecture for localized user-facing messages in OKOCRAFT projects.

It covers message declaration, typed named arguments, bundled translations, runtime language files, and Adventure translation registration using [Siroshun09/mcmsgdef](https://github.com/Siroshun09/mcmsgdef).

For wording, formatting, placeholder naming, and Japanese writing rules, see [Message Formatting Guidelines](message-formatting.md).

## 1. Requirement Language

The key words **MUST**, **SHOULD**, and **MAY** indicate requirement strength:

- **MUST**: Required unless an exceptional constraint makes compliance impossible.
- **SHOULD**: Expected unless there is a specific, documented reason not to follow it.
- **MAY**: Optional; use when appropriate.

## 2. Standard Model

New Java message systems SHOULD use the following model:

1. declare message keys and English defaults in Java with `DefaultMessageDefiner`;
2. represent dynamic values as named MiniMessage translation arguments;
3. ship Japanese defaults as `languages/ja.properties`;
4. load user-editable files from the plugin data directory;
5. append missing defaults without overwriting existing values;
6. register one translation source with Adventure; and
7. send declared `MessageKey` values or typed `MessageKey.ArgN` results from application code.

English and Japanese MUST be the default supported locales. English MUST be the primary fallback locale.

The ownership model is:

| Source | Responsibility |
| --- | --- |
| Java message declarations | Keys, English defaults, Java argument types |
| Bundled `languages/ja.properties` | Japanese defaults |
| Runtime `languages/*.properties` | Administrator-editable translations |
| Adventure translation source | Locale selection and rendering |

Do not maintain the same English default independently in both Java and a bundled English file. Keep one source of truth.

## 3. Keep User-facing Text out of Application Logic

Localizable user-facing text MUST be declared in the message layer rather than written inline in commands, listeners, services, or GUI handlers.

~~~java
// Preferred
sender.sendMessage(Messages.PLAYER_NOT_FOUND.apply(playerName));

// Avoid
sender.sendMessage(Component.text("Player " + playerName + " was not found."));
~~~

This rule applies to text shown to players and other localized audiences.

It does not require internal logs, exception messages, metrics, or developer diagnostics to use the localization system unless they are also user-facing.

## 4. Dependency Management

Use `dev.siroshun.mcmsgdef:mcmsgdef` through the project's version catalog.

~~~toml
[versions]
mcmsgdef = "<approved-version>"

[libraries]
mcmsgdef = { module = "dev.siroshun.mcmsgdef:mcmsgdef", version.ref = "mcmsgdef" }
~~~

~~~kotlin
dependencies {
    implementation(libs.mcmsgdef)
}
~~~

Do not copy a version number from this guideline. Use the version approved by the project and keep it managed with the rest of the dependency catalog.

## 5. Declare Messages in Java

Use `DefaultMessageDefiner` to declare a key together with its English default.

~~~java
public final class Messages {

    private static final DefaultMessageDefiner DEFINER =
        DefaultMessageDefiner.create();

    public static final MessageKey RELOAD_SUCCESS = DEFINER.define(
        "example.command.reload.success",
        "<gray>Reloaded the configuration.</gray>"
    );

    private Messages() {
        throw new UnsupportedOperationException();
    }
}
~~~

`DefaultMessageDefiner#define` records the English default and returns the corresponding `MessageKey`.

New keys SHOULD be namespaced by project or plugin:

~~~text
example.command.reload.success
example.command.player-not-found
~~~

This reduces collisions because Adventure's global translator is process-wide.

A message class SHOULD own a cohesive domain, such as command messages, restart messages, or GUI messages. Large projects MAY use multiple message classes and definers.

### 5.1 Expose English Defaults to the Loader

Expose the collected defaults without allowing callers to mutate them.

~~~java
@Contract(pure = true)
public static @NotNull @UnmodifiableView Map<String, String> defaultMessages() {
    return DEFINER.getCollectedMessages();
}
~~~

A multi-module project MAY aggregate multiple default maps at the language-provider boundary.

Message keys MUST be unique within one registered translation source. Do not rely on map insertion order to resolve accidental duplicate keys.

## 6. Declare Typed Named Arguments

Messages with dynamic values SHOULD use the typed `MessageKey.ArgN` wrappers returned by `MessageKey#with`.

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

The order passed to `with(...)` defines the Java parameter order of `apply(...)`.

The names passed to `Argument.*` define the placeholders used by localized MiniMessage text.

~~~properties
# English
example.command.give.success=<gray>Gave <aqua><amount></aqua> items to <aqua><player></aqua>.</gray>

# Japanese
example.command.give.success=<gray>プレイヤー <aqua><player></aqua> に <aqua><amount></aqua>個付与しました。</gray>
~~~

The translation can reorder placeholders without changing the Java call site.

### 6.1 Select the Argument Representation

Use the representation that preserves the intended semantics.

| API | Use for |
| --- | --- |
| `Argument.string` | Plain text values |
| `Argument.numeric` | Numeric values |
| `Argument.component` | Styled, interactive, or independently translatable components |

Examples:

~~~java
player -> Argument.string("player", player)
amount -> Argument.numeric("amount", amount)
player -> Argument.component("player", player.name().hoverEvent(player))
~~~

Do not flatten a `Component` to a string when its styling, hover event, or nested translation should be preserved.

### 6.2 Reuse Placeholders by Meaning

When several messages use the same named value with the same rendering semantics, define one reusable `Placeholder<T>`.

~~~java
private static final Placeholder<String> PLAYER =
    player -> Argument.string("player", player);

private static final Placeholder<Long> SECONDS =
    seconds -> Argument.numeric("seconds", seconds);
~~~

Do not reuse a placeholder only because the Java type matches. Its name and rendering semantics must also match.

## 7. Package Japanese Defaults

For a new project, use this resource layout:

~~~text
src/main/resources/
└── languages/
    └── ja.properties
~~~

The Japanese resource MUST use the same keys and named placeholders as the English Java declarations.

~~~properties
example.command.reload.success=<gray>設定ファイルを再読み込みしました。</gray>
example.command.player-not-found=<red>プレイヤー <aqua><player></aqua> は見つかりませんでした。</red>
~~~

English SHOULD remain in Java declarations rather than being duplicated in `languages/en.properties`.

Existing projects MAY retain another resource layout when changing it would create an unnecessary migration.

## 8. Load Runtime Language Files

Runtime language files are administrator-editable configuration. Existing values MUST NOT be overwritten during normal startup or reload.

Use `DirectorySource.propertiesFiles(...)` and configure English and Japanese as baseline locales:

~~~java
DirectorySource.propertiesFiles(dataDirectory.resolve("languages"))
    .defaultLocale(Locale.ENGLISH, Locale.JAPANESE)
    .primaryLocale(Locale.ENGLISH);
~~~

Use `MessageProcessors.appendMissingMessagesToPropertiesFile(...)` to add only missing defaults.

A typical default-message loader is:

~~~java
private @Nullable Map<String, String> loadDefaultMessages(
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

Attach it to the source:

~~~java
DirectorySource.propertiesFiles(dataDirectory.resolve("languages"))
    .defaultLocale(Locale.ENGLISH, Locale.JAPANESE)
    .primaryLocale(Locale.ENGLISH)
    .messageProcessor(
        MessageProcessors.appendMissingMessagesToPropertiesFile(
            this::loadDefaultMessages
        )
    );
~~~

With this pattern:

- a missing runtime locale file can be created from defaults;
- a newly added key is appended to an existing runtime file; and
- an administrator's existing value is preserved.

`PropertiesFile` reads and writes UTF-8.

## 9. Register and Replace the Translation Source

Each plugin SHOULD register one stable, uniquely named translation source.

~~~java
private static final Key LANGUAGE_KEY =
    Key.key("example", "languages");
~~~

For a plugin that never reloads messages, `loadAndRegister(...)` is sufficient:

~~~java
DirectorySource.propertiesFiles(dataDirectory.resolve("languages"))
    .defaultLocale(Locale.ENGLISH, Locale.JAPANESE)
    .primaryLocale(Locale.ENGLISH)
    .messageProcessor(
        MessageProcessors.appendMissingMessagesToPropertiesFile(
            this::loadDefaultMessages
        )
    )
    .loadAndRegister(LANGUAGE_KEY);
~~~

### 9.1 Reloadable Plugins

A reloadable plugin SHOULD keep a reference to its registered source and replace it explicitly.

Build the new source first. Only replace the current source after loading succeeds.

~~~java
private Translator messageSource;

private void loadMessages() throws IOException {
    Translator nextSource = DirectorySource.propertiesFiles(
            getDataFolder().toPath().resolve("languages")
        )
        .defaultLocale(Locale.ENGLISH, Locale.JAPANESE)
        .primaryLocale(Locale.ENGLISH)
        .messageProcessor(
            MessageProcessors.appendMissingMessagesToPropertiesFile(
                this::loadDefaultMessages
            )
        )
        .loadAsMiniMessageTranslationStore(LANGUAGE_KEY);

    var globalTranslator = GlobalTranslator.translator();

    if (this.messageSource != null) {
        globalTranslator.removeSource(this.messageSource);
    }

    globalTranslator.addSource(nextSource);
    this.messageSource = nextSource;
}
~~~

This ordering preserves the current translations if loading the replacement fails.

On plugin disable, remove the registered source when practical:

~~~java
if (this.messageSource != null) {
    GlobalTranslator.translator().removeSource(this.messageSource);
    this.messageSource = null;
}
~~~

Do not repeatedly register replacement sources without removing the old source.

## 10. Send Declared Messages

`MessageKey` implements `ComponentLike` and renders as an Adventure translatable component.

Send a message without arguments directly:

~~~java
sender.sendMessage(Messages.RELOAD_SUCCESS);
~~~

Apply a typed message before sending it:

~~~java
sender.sendMessage(
    Messages.PLAYER_NOT_FOUND.apply(playerName)
);
~~~

Application code SHOULD use the declared message constant rather than reconstructing a translation key.

~~~java
// Preferred
sender.sendMessage(Messages.PLAYER_NOT_FOUND.apply(playerName));

// Avoid
sender.sendMessage(
    Component.translatable(
        "example.command.player-not-found",
        Component.text(playerName)
    )
);
~~~

The declaration layer should be the place where reviewers verify the key, English default, placeholder names, and Java argument types.

## 11. Localized Values and Composite Messages

A dynamic value MAY itself be a translatable component.

Use `Argument.component` for domain values whose display name depends on locale.

~~~java
private static final Placeholder<Axis> AXIS =
    axis -> Argument.component(
        "axis",
        Component.translatable(
            "example.axis." + axis.name().toLowerCase(Locale.ENGLISH)
        )
    );
~~~

Prefer this to converting a localizable enum or domain value directly to English text.

The same approach applies to modes, states, biome names, item labels, and other independently localized concepts.

Composite values MAY be built from translation keys when grammar depends on locale. For example, a duration formatter can select singular or plural translation keys and pass the resulting component as one named argument.

~~~java
private static final Placeholder<Long> REMAINING_TIME =
    seconds -> Argument.component(
        "remaining_time",
        formatTime(seconds)
    );
~~~

Keep localized grammar in localized components rather than concatenating English fragments in application code.

## 12. Multi-module Projects

Keep message declarations close to the module or domain that owns the behavior.

~~~text
common/
  CommandMessages.java
  RestartMessages.java

paper/
  PaperCommandMessages.java
~~~

The platform entry point MAY aggregate multiple English default maps before loading the translation source.

When aggregating independently maintained message sets, duplicate keys SHOULD be detected rather than silently overwritten.

The final registered source key MUST still be unique to the plugin.

## 13. Validation and Tests

Message infrastructure SHOULD be tested at the behavior it guarantees.

Useful tests include:

- English defaults and bundled Japanese defaults contain the expected keys;
- loading adds missing defaults;
- loading preserves an existing customized value;
- a missing baseline locale file is created from defaults; and
- reload replaces the previous translation source without leaving duplicate sources.

Do not add a test for every sentence solely to mirror resource contents. Test the localization contract and behavior that can regress.

Follow [Testing Guidelines](java-testing.md) for general test structure.

## 14. Legacy Systems and Migration

Existing OKOCRAFT projects use several generations of message infrastructure.

Do not migrate a stable project only to make it structurally identical to this guide.

When adding messages to an existing system:

- preserve its parser and file contract;
- preserve administrator-edited runtime files;
- avoid mixing incompatible placeholder syntaxes; and
- adopt this architecture when a deliberate message-system migration is already in scope.

A migration to `mcmsgdef` SHOULD be a dedicated change that verifies:

- existing key compatibility;
- English and Japanese coverage;
- placeholder semantics;
- runtime file preservation;
- translator registration and reload behavior; and
- user-facing output after the migration.

## 15. Reference Implementation

A minimal declaration:

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

Usage:

~~~java
sender.sendMessage(Messages.RELOAD_SUCCESS);
sender.sendMessage(Messages.PLAYER_NOT_FOUND.apply(playerName));
~~~

Use the loader and lifecycle patterns from sections 8 and 9 rather than duplicating them in each message class.

## 16. Review Checklist

Before merging a Java message change, verify that:

- localizable user-facing text is declared in the message layer;
- the English default is declared in Java;
- the Japanese default exists;
- the key is namespaced and stable;
- localized variants use the same named placeholders;
- the selected `Argument.*` representation preserves the value semantics;
- application code uses declared message constants;
- English and Japanese are configured as baseline locales;
- English is the primary locale;
- missing defaults are appended without overwriting runtime customizations;
- the translation-source key is unique;
- reloadable plugins replace rather than accumulate sources; and
- message text follows [Message Formatting Guidelines](message-formatting.md).
