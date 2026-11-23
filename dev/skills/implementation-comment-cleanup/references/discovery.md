# Comment Candidate Discovery

Use the bundled [`scripts/inventory_comments.py`](../scripts/inventory_comments.py) as the **standard discovery mechanism** for the [implementation comment cleanup skill](../SKILL.md). The script finds potential comments; it does not decide whether they are comments, documentation, directives, or removable prose.

## Run the Script

From any directory, with Python 3.11+ and Git available:

```sh
python3 <skill-directory>/scripts/inventory_comments.py \
  --repo <target-repository> \
  --output <temporary-directory>/comment-candidates.json
```

Restrict the scan with repeatable `--path src/main` or `--path build.gradle.kts` arguments (relative to the target repository root). Paths such as `./src` are normalized, and `--path .` scans the whole repository. Missing, unsupported-only, absolute, or outside-repository scope paths fail with an explicit error rather than reporting a successful empty scan. Omit `--output` to print JSON to standard output.

**Do not rewrite or improvise the search patterns for supported files.** When the requested scope contains unsupported syntax, inventory that part with an appropriate method and explicitly report the supplemental coverage. Do not imply the built-in script scanned it.

The script reads the **current worktree** of Git-tracked files (including staged and unstaged edits). It does not edit files, download packages, read ignored/untracked files, or follow symlinks. Record the initial Git state separately so existing user changes are not attributed to cleanup edits.

## Deterministic Output

JSON includes:

| Field | Meaning |
| --- | --- |
| `schema_version` | Format version |
| `scope` | Requested path restrictions |
| `scanned_files` | Tracked, readable files scanned |
| `excluded_files` | Files skipped by deterministic generated/dependency/path rules, with reasons |
| `unreadable_files` | Tracked files that could not be read |
| `scan_warnings` | Incomplete lexical scans requiring manual inspection, with path, line, and reason |
| `candidates` | Each potential comment's path, start/end line, lexical kind, original candidate text, and advisory `hints` |
| `notes` | Known limits of discovery |

The output is deterministically ordered by tracked path and candidate position. Its count is **not** the number of implementation comment units: confirmation, exclusion, and grouping happen afterward.

An explicit `--path` that selects no supported tracked files causes an argument error (exit status 2). Unreadable files or lexical scan warnings also return status 2. In particular, an unterminated `/*` candidate may actually be a JavaScript regex literal: the scanner then cannot reliably enumerate subsequent comments in that file. Inspect the named file manually rather than trusting the candidate list. Resolve or disclose all gaps; successful execution alone does not prove lexical completeness.

## File Coverage

The standard script includes the source and build file families needed for initial use:

- Java/JVM source and build scripts, including Gradle, Kotlin DSL and Groovy DSL; Maven XML, properties, version catalogs;
- Go source and module/workspace files;
- TypeScript/JavaScript source and common variants, including TSX/JSX, and comment-bearing JSONC/JSON5;
- Shell, Makefiles, YAML, TOML, XML, and relevant build/configuration formats.

It recognizes `//`, `/* ... */`, XML comments, and broad `#`/`!` candidate patterns as appropriate. Multiline and trailing comments are included. Known generated, dependency, minified, and lockfile paths are skipped with reasons.

File-extension coverage is intentionally explicit and maintained in the script; do not duplicate file globs in the skill instructions. Add support and tests in the script when permanent new coverage is needed.

## Filter and Classify After Discovery

1. **Check the candidate:** confirm that the reported token is really a comment. The scanner is lexical, not a complete language parser; JSX, template literals, regular expressions, shell expansions, and quoted configuration values can produce false positives or omissions. Unterminated block-comment candidates produce explicit warnings, but other ambiguous syntax can still need manual review. Inspect the source syntax and use language tooling where helpful.
2. **Exclude out-of-scope material:** Javadoc/KDoc/JSDoc/TSDoc, Go API documentation comments (often written with `//`), license and copyright notices, generated and vendored material, and test fixtures whose comment-looking text is part of the test data. Record exclusions without counting them as removed.
3. **Protect semantic comments:** Go build constraints, `//go:generate`, `//go:embed`, cgo directives, `// indirect` in module files; TypeScript triple-slash references and `@ts-` annotations; ESLint/formatter controls; source maps, optimizer/bundler annotations, shell shebangs, and build pragmas. These may alter compilation or tool behavior. **Active directives normally remain KEEP**; investigate uncertain directives before modifying them.
4. **Group comment units:** one independent explanation, task, or directive is one review unit. Multiple nearby explanations with different purposes are separate units even if the script reports one contiguous block.
5. **Decide:** apply the SKILL's KEEP / REMOVE / REWRITE / ASK criteria using actual surrounding code, tests, and relevant contracts. Advisory `hints` such as task, documentation candidate, legal, or tool directive **never** authorize automatic deletion or retention.

If a tracked file is unexpectedly missing from `scanned_files`, investigate whether its extension is supported, a skip rule applies, it is unreadable, or it falls outside the requested scope. Record all unreviewed files and why.

## Local Verification

The skill's bundled self-contained tests can be run without additional dependencies:

```sh
python3 -m unittest discover -s <skill-directory>/tests -v
```

These validate inventory behavior on temporary Git repositories; they do not replace per-repository validation of the resulting cleanup diff.
