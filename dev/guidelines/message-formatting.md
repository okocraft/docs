# Message Formatting Guidelines

This document defines the writing, formatting, and localization standards for user-facing messages in OKOCRAFT projects.

It applies to chat messages, command feedback, GUI text, action bars, boss bars, kick messages, and other localized text shown to users. Java declaration and loading are covered by [Java Message Definitions and Localization](java-messages.md).

## 1. Requirement Language

The key words **MUST**, **SHOULD**, and **MAY** indicate requirement strength:

- **MUST**: Required unless an exceptional constraint makes compliance impossible.
- **SHOULD**: Expected unless there is a specific, documented reason not to follow it.
- **MAY**: Optional; use when appropriate.

## 2. Language Policy

English is the base language and the source of truth for message semantics.

New message systems MUST support both English and Japanese by default. Additional languages MAY be supported.

For every localized message:

- use the same message key in every language;
- preserve the same meaning and named placeholders;
- allow word order, grammar, and phrasing to change for natural translation; and
- treat the English text as the semantic reference, not as a sentence structure to copy literally.

~~~properties
# English
example.command.give.success=<gray>Gave <aqua><amount></aqua> items to <aqua><player></aqua>.</gray>

# Japanese
example.command.give.success=<gray>プレイヤー <aqua><player></aqua> に <aqua><amount></aqua>個付与しました。</gray>
~~~

## 3. Writing Principles

Messages SHOULD be concise, specific, and useful at the point where they are shown.

### 3.1 State the Outcome Directly

Prefer direct wording that tells the user what happened.

~~~properties
# Preferred
example.command.reload.failure=<red>Failed to reload the configuration. Check the console for details.</red>

# Avoid
example.command.reload.failure=<red>An unexpected problem occurred while attempting to perform the requested configuration reload operation.</red>
~~~

When the user can correct the problem, state the next action.

~~~properties
example.error.inventory-full=<red>Your inventory is full. Free at least one slot and try again.</red>
~~~

When the user cannot correct it, direct them to the appropriate next step.

~~~properties
example.error.data-load-failed=<red>Failed to load your data. Contact a server administrator.</red>
~~~

Do not expose stack traces or internal implementation details in normal user-facing messages.

### 3.2 Use Consistent Terminology

Use one term for one concept within a project.

Do not alternate between terms such as `configuration`, `config`, and `settings` unless they refer to different concepts.

Machine-facing identifiers such as commands, permission nodes, file names, IDs, and literal argument values MUST NOT be translated.

### 3.3 Distinguish Sentences from Labels

Notifications, results, warnings, and errors SHOULD be complete sentences with terminal punctuation.

~~~properties
example.command.reload.success=<gray>Reloaded the configuration.</gray>
example.error.player-not-found=<red>Player <aqua><player></aqua> was not found.</red>
~~~

Labels, headings, menu items, and short help descriptions SHOULD be concise phrases without terminal punctuation.

~~~properties
example.gui.back=<gold>Back</gold>
example.gui.next-page=<gold>Next page</gold>
example.command.help.reload=<gray>Reload the configuration</gray>
~~~

## 4. Message Keys

Message keys SHOULD describe the purpose of a message rather than its literal wording.

Use lowercase dot-separated segments and `kebab-case` within a segment.

A typical structure is:

~~~text
<plugin>.<context>.<feature>.<state>
~~~

Examples:

~~~text
box.command.deposit.success
box.command.deposit.no-stock
yaminabe.command.reload.config-failed
kansokusha.command.search.no-results
~~~

Use explicit suffixes when one operation has distinct recipients or outcomes:

~~~text
example.command.give.success.sender
example.command.give.success.target
example.command.give.error.no-stock
~~~

Message keys MUST NOT include locale names.

Do not rename a stable key only because the displayed wording changed. Treat key renames as a compatibility or migration change.

## 5. Named Placeholders

New message systems MUST use named placeholders for values inserted into localized text.

Use lowercase `snake_case` names that describe the value:

~~~text
<player>
<item>
<amount>
<player_name>
<remaining_time>
<max_page>
~~~

Every translation of the same key MUST use the same placeholder set. Placeholder order MAY differ between languages.

~~~properties
# English
example.teleport=<gray>Teleported <aqua><player></aqua> to <aqua><world></aqua>.</gray>

# Japanese
example.teleport=<gray><aqua><player></aqua> を <aqua><world></aqua> にテレポートしました。</gray>
~~~

Do not put localized units or surrounding prose inside placeholder values.

~~~properties
# Preferred
example.time=<gray><aqua><seconds></aqua> seconds remaining.</gray>

# Avoid
example.time=<gray><aqua><seconds_with_unit></aqua> remaining.</gray>
~~~

Positional placeholders such as `{0}` and percent-style placeholders such as `%player%` SHOULD NOT be introduced in new systems. They MAY remain where an existing message parser requires them.

## 6. MiniMessage Formatting

New message systems SHOULD use MiniMessage when the platform and localization layer support it.

Use formatting to communicate meaning, not decoration.

| Tag | Recommended use |
| --- | --- |
| `<gray>` | Normal messages and explanatory text |
| `<red>` | Errors, denied actions, and negative states |
| `<aqua>` | Dynamic values, commands, and highlighted data |
| `<green>` | Enabled or positive states |
| `<gold>` | Headings and interactive GUI labels |
| `<dark_gray>` | Separators and secondary elements |
| `<black>` | GUI titles where appropriate |

Prefer a neutral base style with a small number of highlighted values.

~~~properties
example.command.give.success=<gray>Gave <aqua><amount></aqua> items to <aqua><player></aqua>.</gray>
example.error.player-not-found=<red>Player <aqua><player></aqua> was not found.</red>
~~~

Scope styles explicitly. Prefer closing a nested style over reopening the base style.

~~~properties
# Preferred
example.error=<red>Player <aqua><player></aqua> was not found.</red>

# Avoid in new messages
example.error=<red>Player <aqua><player><red> was not found.
~~~

Do not add color changes that do not convey structure, state, or emphasis.

## 7. Context-specific Text

### 7.1 Command Help

Command literals MUST begin with `/`.

For command syntax:

- use `<argument>` for required arguments;
- use `[argument]` for optional arguments; and
- use `[a/b]` for a small set of alternatives when the notation is unambiguous.

~~~text
/example give <player> <amount>
/example list [page]
/example setting [on/off]
~~~

Help descriptions SHOULD be short verb phrases and SHOULD NOT end with a period.

~~~properties
example.command.help.give=<aqua>/example give <player> <amount></aqua><dark_gray> - <gray>Give items to a player</gray>
~~~

Use the same argument names and terminology in help text and related error messages.

### 7.2 GUI Text

GUI labels SHOULD be short and scannable.

~~~properties
example.gui.back=<gold>Back</gold>
example.gui.close=<gold>Close</gold>
example.gui.increase=<gold>Increase</gold>
example.gui.decrease=<gold>Decrease</gold>
~~~

Interaction descriptions SHOULD state the input and result directly.

~~~properties
example.gui.deposit=<gray>Left-click to deposit <aqua><amount></aqua></gray>
example.gui.reset=<gray>Shift-click to reset</gray>
~~~

### 7.3 Multi-line Text

Use multiple lines only when they separate distinct information or actions.

For MiniMessage, use `<newline>` when one component requires multiple lines.

~~~properties
example.reset.confirm=<gray>This will reset all data.<newline><red>This action cannot be undone.</red><newline><gray>Run <aqua>/example reset confirm</aqua> to continue.</gray>
~~~

Do not use line breaks merely to compensate for wording that should be shortened.

### 7.4 Numbers and Units

Keep the numeric value separate from localized grammar.

English normally includes a space between a number and a written unit:

~~~properties
example.time=<gray><aqua><seconds></aqua> seconds remaining.</gray>
~~~

When singular and plural forms differ, localize the grammatical choice instead of embedding it in the placeholder value.

Implementation patterns for localized composite values are covered in [Java Message Definitions and Localization](java-messages.md).

## 8. Japanese Localization

Japanese translations follow the general rules above plus the conventions in this section.

### 8.1 Tone

Normal notifications, results, warnings, and errors SHOULD generally use polite `です・ます` style.

~~~properties
example.command.reload.success=<gray>設定ファイルを再読み込みしました。</gray>
example.command.reload.failure=<red>設定ファイルの再読み込みに失敗しました。</red>
~~~

Labels, headings, menu items, and short help descriptions SHOULD use concise non-sentence forms.

~~~properties
example.gui.back=<gold>戻る</gold>
example.gui.next-page=<gold>次のページ</gold>
example.command.help.reload=<gray>設定を再読み込みする</gray>
~~~

Avoid unnecessary subjects when context already identifies the user.

~~~properties
# Preferred
example.error.no-permission=<red>権限がありません。</red>

# Usually unnecessary
example.error.no-permission=<red>あなたにはこの操作を行う権限がありません。</red>
~~~

### 8.2 Punctuation

Complete Japanese sentences SHOULD normally end with `。`.

Labels, headings, GUI items, and short help descriptions SHOULD NOT end with `。`.

Use Japanese punctuation in Japanese prose. When an exclamation mark is appropriate, use `！` rather than `!`.

Progress messages MAY use `...` when consistent with the project:

~~~properties
example.command.reload.start=<gray>再読み込みしています...</gray>
~~~

Do not overuse exclamation marks or ellipses.

### 8.3 Placeholder Spacing

Placeholders that act as independent nouns SHOULD generally be separated from surrounding Japanese text with half-width spaces when this improves readability.

~~~properties
example.error.player-not-found=<red>プレイヤー <aqua><player></aqua> は見つかりませんでした。</red>
example.stock=<gray>プレイヤー <aqua><player></aqua> の在庫</gray>
~~~

Do not insert a space between a number and a Japanese counter or unit.

~~~properties
example.amount=<gray><aqua><amount></aqua>個追加しました。</gray>
example.time=<gray>残り <aqua><seconds></aqua>秒です。</gray>
example.limit=<red><aqua><limit></aqua>文字以内で指定してください。</red>
~~~

This applies to counters and units such as `個`, `秒`, `分`, `時間`, `日`, `文字`, `行`, `回`, and `ページ`.

### 8.4 Commands and Identifiers

Keep command literals and other machine-facing values unchanged.

~~~properties
example.command.tip=<gray><aqua>/example reload</aqua> で設定を再読み込みできます。</gray>
example.error.invalid-mode=<red>モードは <aqua>all</aqua> または <aqua>item</aqua> を指定してください。</red>
~~~

### 8.5 Natural Translation

Prefer natural Japanese over word-for-word translation.

The English message defines the intended meaning; it does not require the same syntax or phrase order.

Choose one Japanese term for each concept and use it consistently. For example, do not alternate among `再読込`, `再読み込み`, and `リロード` unless they intentionally mean different things.

## 9. Legacy Compatibility

Existing OKOCRAFT projects contain older formats, including legacy color codes, percent-style placeholders, and positional placeholders.

~~~text
&7 / &c / &b
%player%
{0}
~~~

These formats MAY remain where compatibility requires them.

When working in an existing message system:

- preserve its parser contract unless migration is intentionally in scope;
- do not mix incompatible placeholder syntaxes;
- do not migrate message syntax as an unrelated side effect of another change; and
- apply this guide to wording and semantics where the existing format allows it.

A syntax migration SHOULD be a dedicated change.

## 10. Review Checklist

Before merging a message change, verify that:

- English and Japanese definitions exist for every new message;
- English expresses the intended semantics clearly;
- every locale uses the same named placeholder set;
- message keys and placeholder names follow the naming rules;
- formatting communicates meaning rather than decoration;
- sentences and labels use appropriate punctuation;
- errors state what failed and provide a next action when useful;
- machine-facing values are not translated;
- Japanese spacing and counters follow the Japanese rules; and
- legacy syntax is used only when required by the existing system.
