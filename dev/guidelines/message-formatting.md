# Message Formatting Guidelines

This document defines the formatting and localization standards for user-facing messages in OKOCRAFT projects.

The goals are to keep messages consistent across plugins, make translations predictable, and make message changes easy to review.

For Java declaration, loading, and `mcmsgdef` usage, see [Java Message Definitions and Localization](java-messages.md).

## 1. Requirement Language

The key words **MUST**, **SHOULD**, and **MAY** indicate requirement strength:

- **MUST**: Required unless an exceptional constraint makes compliance impossible.
- **SHOULD**: Expected unless there is a specific, documented reason not to follow it.
- **MAY**: Optional; use when appropriate.

## 2. Language Policy

English is the base language and the source of truth for message semantics.

New plugins and new message systems MUST support both:

- English; and
- Japanese.

English and Japanese are the default supported languages unless a project has a documented reason to use a different set.

When adding or changing a message:

1. define or update the English message first;
2. add or update the Japanese translation using the same key;
3. keep the same named placeholders and meaning across languages; and
4. allow word order and phrasing to differ when required by the target language.

For example:

~~~properties
# English
plugin.command.give.success=<gray>Gave <aqua><amount></aqua> <aqua><item></aqua> to <aqua><player></aqua>.</gray>

# Japanese
plugin.command.give.success=<gray>プレイヤー <aqua><player></aqua> に <aqua><item></aqua> を <aqua><amount></aqua>個付与しました。</gray>
~~~

The English text defines the intended meaning. It does not define the target language's word order.

## 3. Message Keys

Message keys SHOULD describe the purpose of a message rather than its literal wording.

Use lowercase names separated by dots. Use `kebab-case` for multi-word segments.

A typical structure is:

~~~text
<plugin>.<context>.<feature>.<state>
~~~

Examples:

~~~properties
box.command.deposit.success=
box.command.deposit.no-stock=
yaminabe.command.reload.config-failed=
kansokusha.command.search.no-results=
~~~

Use explicit suffixes when one operation has different recipients or outcomes:

~~~properties
plugin.command.give.success.sender=
plugin.command.give.success.target=
plugin.command.give.error.no-stock=
~~~

Message keys MUST NOT contain locale names.

~~~properties
# Do
plugin.command.reload.success=

# Do not
plugin.command.reload.success.en=
plugin.command.reload.success.ja=
~~~

Renaming a message key is an API and migration concern. Do not rename keys only to improve wording.

## 4. Placeholders

New message systems MUST use named placeholders when values are inserted into localized text.

Use lowercase `snake_case` names:

~~~text
<player>
<item>
<amount>
<player_name>
<item_name>
<remaining_time>
<max_page>
~~~

A placeholder name SHOULD describe the value it represents.

~~~properties
# Preferred
plugin.error.player-not-found=<red>Player <aqua><player></aqua> was not found.</red>

# Avoid
plugin.error.player-not-found=<red>Player <aqua><value></aqua> was not found.</red>
~~~

Every translation of the same key MUST use the same placeholder set. The order MAY differ.

Positional placeholders such as `{0}` and legacy placeholders such as `%player%` SHOULD NOT be introduced in new message systems. They MAY remain where an existing parser requires them.

Do not include localized units or surrounding prose inside a placeholder value. Keep the value reusable by each locale.

~~~properties
# Preferred
plugin.time.remaining=<gray><aqua><seconds></aqua> seconds remaining.</gray>

# Avoid
plugin.time.remaining=<gray><aqua><seconds_with_suffix></aqua> remaining.</gray>
~~~

## 5. MiniMessage

New message systems SHOULD use MiniMessage when the platform and localization layer support it.

Use colors semantically.

| Tag | Recommended use |
| --- | --- |
| `<gray>` | Normal messages and explanatory text |
| `<red>` | Errors, denied actions, and failures |
| `<aqua>` | Dynamic values, player names, commands, and highlighted data |
| `<green>` | Enabled or positive states |
| `<gold>` | Headings and interactive GUI labels |
| `<dark_gray>` | Separators and secondary visual elements |
| `<black>` | GUI titles where appropriate |

Prefer a neutral base color and highlight only meaningful values.

~~~properties
plugin.command.give.success=<gray>Gave <aqua><amount></aqua> <aqua><item></aqua> to <aqua><player></aqua>.</gray>
plugin.error.player-not-found=<red>Player <aqua><player></aqua> was not found.</red>
~~~

New messages SHOULD close MiniMessage tags explicitly.

~~~properties
# Preferred
plugin.error=<red>Player <aqua><player></aqua> was not found.</red>

# Legacy style; avoid in new messages
plugin.error=<red>Player <aqua><player><red> was not found.
~~~

Avoid styling every word independently. Formatting SHOULD communicate structure or meaning.

## 6. Sentences and Labels

Notifications, results, warnings, and errors SHOULD be complete sentences.

English complete sentences SHOULD:

- use sentence case;
- end with appropriate punctuation;
- prefer direct wording; and
- avoid unnecessary filler.

~~~properties
plugin.command.reload.success=<gray>Reloaded the configuration.</gray>
plugin.command.reload.failure=<red>Failed to reload the configuration.</red>
plugin.error.no-permission=<red>You do not have permission to use this command.</red>
~~~

Labels, headings, menu items, and list entries SHOULD be short phrases and SHOULD NOT be forced into full sentences.

~~~properties
plugin.gui.back=<gold>Back</gold>
plugin.gui.close=<gold>Close</gold>
plugin.gui.next-page=<gold>Next page</gold>
plugin.gui.current-stock=<gray>Current stock</gray>
~~~

Do not add terminal punctuation to labels unless it has a functional purpose.

## 7. Tone and Technical Writing

Messages SHOULD be concise, specific, and actionable.

State what happened before implementation details.

~~~properties
# Preferred
plugin.command.reload.failure=<red>Failed to reload the configuration. Check the console for details.</red>

# Avoid
plugin.command.reload.failure=<red>An unexpected problem occurred while attempting to perform the requested configuration reload operation.</red>
~~~

When the user can correct the problem, state the next action.

~~~properties
plugin.error.inventory-full=<red>Your inventory is full. Free at least one slot and try again.</red>
~~~

When the user cannot correct it, direct them to the appropriate next step.

~~~properties
plugin.error.data-load-failed=<red>Failed to load your data. Contact a server administrator.</red>
~~~

Avoid implementation terminology unless users need it to resolve the problem.

Use one term consistently for one concept. For example, do not alternate between `configuration`, `config`, and `settings` unless they refer to different things.

## 8. Error Messages

Error messages SHOULD identify the failed condition as specifically as practical.

~~~properties
plugin.error.player-not-found=<red>Player <aqua><player></aqua> was not found.</red>
plugin.error.invalid-number=<red><aqua><input></aqua> is not a valid number.</red>
plugin.error.no-permission=<red>You do not have permission to use this command.</red>
~~~

If a raw error message is useful, introduce it with stable user-facing text.

~~~properties
plugin.error.exception=<red>The operation failed. Error: <white><error></white></red>
~~~

Do not expose stack traces or internal exception details in normal player-facing messages.

## 9. Command Help

Command literals MUST begin with `/`.

For documentation-style command syntax:

- use `<argument>` for required arguments;
- use `[argument]` for optional arguments; and
- use `[a/b]` for a small set of alternatives when the notation is unambiguous.

Examples:

~~~text
/plugin give <player> <amount>
/plugin list [page]
/plugin setting [on/off]
~~~

A command-help entry SHOULD visually separate the command from its description.

~~~properties
plugin.command.help.give=<aqua>/plugin give <player> <amount></aqua><dark_gray> - <gray>Give items to a player</gray>
~~~

Help descriptions SHOULD be short verb phrases and SHOULD NOT end with a period.

Use the same terminology in argument names, help text, and related error messages.

## 10. GUI Text

GUI labels SHOULD be short and scannable.

~~~properties
plugin.gui.back=<gold>Back</gold>
plugin.gui.close=<gold>Close</gold>
plugin.gui.increase=<gold>Increase</gold>
plugin.gui.decrease=<gold>Decrease</gold>
~~~

Interaction descriptions SHOULD start with the input or action when practical.

~~~properties
plugin.gui.deposit=<gray>Left-click to deposit <aqua><amount></aqua></gray>
plugin.gui.withdraw=<gray>Right-click to withdraw <aqua><amount></aqua></gray>
plugin.gui.reset=<gray>Shift-click to reset</gray>
~~~

For MiniMessage content, use `<newline>` when one component needs multiple lines.

~~~properties
plugin.gui.description=<gray>Click to change the setting<newline>Shift-click to reset</gray>
~~~

If a project does not use MiniMessage, use the line-break mechanism provided by that message system.

## 11. Numbers and Units

English SHOULD normally include a space between a number and a written unit.

~~~properties
plugin.time.remaining=<gray><aqua><seconds></aqua> seconds remaining.</gray>
~~~

Pluralization SHOULD be handled explicitly when singular and plural forms differ.

~~~properties
plugin.time.second=<gray><aqua><seconds></aqua> second</gray>
plugin.time.seconds=<gray><aqua><seconds></aqua> seconds</gray>
~~~

Do not make a placeholder responsible for selecting localized grammar.

## 12. Multi-line Messages

Use multiple lines only when they improve readability or separate distinct actions.

~~~properties
plugin.command.reset.confirmation=<gray>This will reset all data.<newline><red>This action cannot be undone.</red><newline><gray>Run <aqua>/plugin reset confirm</aqua> to continue.</gray>
~~~

For command help, prefer one command per line.

Do not use line breaks merely to compensate for overly long wording. Shorten the message first.

## 13. Japanese Localization

Japanese translations follow the general rules above plus the conventions in this section.

### 13.1 Tone

Normal notifications, results, warnings, and errors SHOULD generally use polite `です・ます` style.

~~~properties
plugin.command.reload.success=<gray>設定ファイルを再読み込みしました。</gray>
plugin.command.reload.failure=<red>設定ファイルの再読み込みに失敗しました。</red>
plugin.error.player-not-found=<red>プレイヤー <aqua><player></aqua> は見つかりませんでした。</red>
~~~

Labels, headings, menu items, and command-help descriptions SHOULD use concise non-sentence forms.

~~~properties
plugin.gui.back=<gold>戻る</gold>
plugin.gui.next-page=<gold>次のページ</gold>
plugin.command.help.reload=<gray>設定を再読み込みする</gray>
~~~

Avoid unnecessary subjects when the context already identifies the user.

~~~properties
# Preferred
plugin.error.no-permission=<red>権限がありません。</red>

# Usually unnecessary
plugin.error.no-permission=<red>あなたにはこの操作を行う権限がありません。</red>
~~~

Use `あなた` when it prevents ambiguity or is intentionally part of the message tone.

### 13.2 Punctuation

Complete Japanese sentences SHOULD normally end with `。`.

~~~properties
plugin.command.reload.success=<gray>再読み込みしました。</gray>
plugin.error.invalid-number=<red>有効な数値ではありません。</red>
~~~

Labels, headings, GUI items, and short command-help descriptions SHOULD NOT end with `。`.

Use Japanese punctuation in Japanese prose. Use `！` rather than `!` when an exclamation mark is appropriate.

Progress messages MAY use `...` when consistent with the project:

~~~properties
plugin.command.reload.start=<gray>再読み込みしています...</gray>
~~~

Do not overuse exclamation marks or ellipses.

### 13.3 Placeholders and Spacing

Placeholders that behave as independent nouns SHOULD generally be separated from surrounding Japanese text with a half-width space when that improves readability.

~~~properties
plugin.error.player-not-found=<red>プレイヤー <aqua><player></aqua> は見つかりませんでした。</red>
plugin.stock=<gray>プレイヤー <aqua><player></aqua> の在庫</gray>
~~~

Do not insert a space between a number and a Japanese counter or unit.

~~~properties
plugin.amount=<gray><aqua><amount></aqua>個追加しました。</gray>
plugin.time=<gray>残り <aqua><seconds></aqua>秒です。</gray>
plugin.limit=<red><aqua><limit></aqua>文字以内で指定してください。</red>
plugin.page=<gray><aqua><page></aqua>ページ</gray>
~~~

This applies to common counters and units such as `個`, `秒`, `分`, `時間`, `日`, `文字`, `行`, `回`, and `ページ`.

The placeholder itself SHOULD contain only the value.

### 13.4 Commands and Machine-facing Values

Keep command literals unchanged.

~~~properties
plugin.command.tip=<gray><aqua>/plugin reload</aqua> で設定を再読み込みできます。</gray>
~~~

Do not translate command names, literal argument values, permission nodes, file names, IDs, or other machine-facing identifiers.

~~~properties
plugin.error.invalid-mode=<red>モードは <aqua>all</aqua> または <aqua>item</aqua> を指定してください。</red>
~~~

### 13.5 Terminology

Choose one Japanese term for each user-facing concept and use it consistently.

For example, avoid alternating between the following unless they intentionally refer to different concepts:

~~~text
再読込
再読み込み
リロード
~~~

Prefer natural Japanese over a word-for-word translation of English.

~~~properties
# English
plugin.command.give.success=<gray>Gave <aqua><amount></aqua> <aqua><item></aqua> to <aqua><player></aqua>.</gray>

# Natural Japanese
plugin.command.give.success=<gray>プレイヤー <aqua><player></aqua> に <aqua><item></aqua> を <aqua><amount></aqua>個付与しました。</gray>
~~~

## 14. Legacy Formats

Existing OKOCRAFT repositories contain older message formats, including:

~~~text
&7 / &c / &b    Legacy color codes
%player%        Percent-style placeholders
{0}             Positional placeholders
~~~

These formats MAY remain when required for compatibility.

New message systems SHOULD NOT introduce them when MiniMessage and named arguments are available.

When modifying an existing project:

- preserve the current parser contract unless migration is intentional;
- do not mix placeholder syntaxes in one message system; and
- do not perform a syntax migration as an unrelated side effect of a feature change.

A syntax migration SHOULD be a dedicated change.

## 15. Review Checklist

Before merging a message change, verify that:

- new messages have both English and Japanese definitions;
- English defines the intended semantics;
- every locale uses the same named placeholder set;
- new placeholder names use descriptive `snake_case`;
- MiniMessage formatting has a semantic purpose;
- new MiniMessage markup uses explicit closing tags where practical;
- complete sentences use appropriate punctuation;
- labels and command-help descriptions remain concise;
- errors state what failed and provide corrective action when useful;
- machine-facing values are not translated;
- Japanese counters and units are attached directly to their numeric value; and
- legacy syntax is used only when required by the existing message system.
