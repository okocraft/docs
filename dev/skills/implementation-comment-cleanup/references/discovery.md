# Comment Discovery and Exclusions

This reference supports the [implementation comment cleanup skill](../SKILL.md). Use it to **find candidates**, not to declare which text is removable.

## Coverage

Check tracked, human-maintained files across application code, tests, build logic, and relevant source-adjacent configuration. Typical candidates include:

| Area | File families / examples | Comment forms to consider |
| --- | --- | --- |
| JVM source and build logic | `*.java`, `*.kt`, `*.kts`, `*.groovy`, `*.gradle`, `*.gradle.kts`, `settings.gradle*`, `build.gradle*` | ``//``, ``/* ... */``, documentation comments |
| Maven and JVM configuration | `pom.xml`, build-related `*.xml`, `gradle.properties`, `*.properties`, version catalogs (`*.toml`) | ``<!-- ... -->``, ``#`` / ``!`` as supported |
| Go | `*.go`, `go.mod`, `go.work` and handwritten build scripts | ``//``, ``/* ... */``, module-file trailing comments |
| TypeScript and related runtime/build scripts | `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.mjs`, `*.cjs`, `*.mts`, `*.cts`, `*.jsonc`, `tsconfig*.json` | ``//``, ``/* ... */``, JSDoc/TSDoc, triple-slash directives |
| Build infrastructure | `Makefile`, `GNUmakefile`, `*.mk`, `*.sh`, relevant `*.yml`, `*.yaml`, `*.toml` | ``#`` or configuration-specific syntax |

Scope build configuration deliberately: not every XML/YAML/properties file is executable build logic, but comments in a build script or CI workflow may contain critical assumptions.

### Candidate discovery

Prefer a tracked-file inventory before text searching; for example:

```sh
git status --short
git ls-files -- '*.java' '*.kt' '*.kts' '*.groovy' '*.gradle' '*.gradle.kts' \
  '*.go' '*.ts' '*.tsx' '*.js' '*.jsx' '*.mjs' '*.cjs' '*.mts' '*.cts' \
  '*.jsonc' 'tsconfig*.json' 'pom.xml' 'go.mod' 'go.work' \
  '*.toml' '*.properties' '*.xml' '*.yml' '*.yaml' '*.sh' 'Makefile' 'GNUmakefile'
```

Search likely delimiters in those paths. Sample *candidate* searches, not definitive parsers:

```sh
rg -n --glob '*.{java,kt,kts,groovy,gradle,go,ts,tsx,js,jsx,mjs,cjs,mts,cts,jsonc}' \
  '//|/\*|\*/' .
rg -n --glob '*.{xml}' '<!--|-->' .
rg -n --glob '*.{toml,properties,yml,yaml,sh,mk}' '^[[:space:]]*[#!]' .
```

Searches should additionally include build-script files with compound extensions (`*.gradle.kts`), extensionless build files, and trailing comment markers. Check files outside the default ignore rules only when explicitly in scope. Use syntax-aware tooling (parsers, language servers, IDE navigation) where available to establish which matches are comments. Match whole multiline comment units, not isolated lines. Strings containing URLs, template literals, regular expressions, and other syntax produce false positives. Some comments are embedded after statements and are not line-leading.

Do not use a broad replacement command based solely on the above expressions.

## Identify Comments That Must Not Be Treated as Ordinary Prose

**Documentation and legal notices (outside normal cleanup):**

- Java Javadoc, Kotlin KDoc, TypeScript/JSDoc/TSDoc, and Go doc comments (which may use ``//``), including public APIs and reusable components.
- Copyright and license headers, SPDX identifiers, legal notices, and tool-required attribution.
- Documentation files and comments inside generated or vendored sources.

**Compiler, build, and tool semantics (usually KEEP; investigate before touching):**

- Go build constraints and directives: ``//go:build``, ``// +build``, ``//go:generate``, ``//go:embed``, compiler/linker directives, and cgo preambles. In `go.mod`, ``// indirect`` can convey module metadata.
- TypeScript triple-slash references and ``@ts-check``, ``@ts-nocheck``, ``@ts-ignore``, ``@ts-expect-error``; ESLint/Biome/Deno lint controls; formatting or coverage directives; source-map comments; bundler/optimizer annotations such as ``/*#__PURE__*/``, ``/* @vite-ignore */``, or webpack magic comments.
- Language-level or build-system comments consumed by tools, such as formatter off/on regions, IDE inspection directives, shell shebangs, Makefile recipe semantics, and configuration pragmas.
- Generated-file markers (`Code generated ... DO NOT EDIT`) and test fixtures that intentionally contain comment text to exercise a parser or expected output.

An active directive should normally be **KEEP** with its tool purpose noted, even if it does not read like an explanation. When a suppression looks stale, establish through relevant lint/type checking that it is unnecessary before removing it. If the effect is uncertain, **ASK**. Avoid mechanical deletion of build-file comments until their tool-specific meaning has been checked.

## Exclusions and Search Quality

- Normally exclude dependency directories (`node_modules`, `vendor`), build outputs (`build`, `target`, `dist`), generated source, bundled/minified assets, lockfiles, and third-party copies. Record intentional exclusions rather than treating them as missing coverage.
- Check for files ignored by `rg` or Git when the user explicitly includes them; do not silently assume an ignored file has no relevant comments.
- A comment can span several lines or annotate a statement at the end of a line. Group such fragments by logical purpose.
- Compare branch and working-tree state before editing. Never overwrite unrelated user changes while cleaning comments.
