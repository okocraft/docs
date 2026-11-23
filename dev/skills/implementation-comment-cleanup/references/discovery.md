# Comment Candidate Discovery

Use the bundled [`scripts/inventory_comments.py`](../scripts/inventory_comments.py) as the **standard discovery mechanism** for the [implementation comment cleanup skill](../SKILL.md). The script finds potential comments; it does not decide whether they are comments, documentation, directives, or removable prose.

## Run the Script

From any directory, with Python 3.9+ and Git available:

```sh
python3 <skill-directory>/scripts/inventory_comments.py \
  --repo <target-repository> \
  --output <temporary-directory>/comment-candidates.json
```

Restrict the scan with repeatable ``--path src/main`` or ``--path build.gradle.kts`` arguments (relative to the target repository root). Omit ``--output`` to print JSON to standard output.

**Do not rewrite or improvise the search patterns for supported files.** When the requested scope contains unsupported syntax, inventory that part with an appropriate method and explicitly report the supplemental coverage. Do not imply the built-in script scanned it.

The script reads the **current worktree** of Git-tracked files (including staged and unstaged edits). It does not edit files, download packages, read ignored/untracked files, or follow symlinks. Record the initial Git state separately so existing user changes are not attributed to cleanup edits.

## Deterministic Output

JSON includes:

| Field | Meaning |
| --- | --- |
| ``schema_version`` | Format version |
| ``scope`` | Requested path restrictions |
| ``scanned_files`` | Tracked, readable files scanned |
| ``excluded_files`` | Files skipped by deterministic generated/dependency/path rules, with reasons |
| ``unreadable_files`` | Tracked files that could not be read |
| ``candidates`` | Each potential comment's path, start/end line, lexical kind, original candidate text, and advisory ``hints`` |
| ``notes`` | Known limits of discovery |

The output is deterministically ordered by tracked path and candidate position. Its count is **not** the number of implementation comment units: confirmation, exclusion, and grouping happen afterward.

A nonzero exit code or unreadable files means discovery was incomplete. Resolve or disclose gaps; never claim full coverage based solely on a successful scan.

## File Coverage

The standard script includes the source and build file families needed for initial use:

- Java/JVM source and build scripts, including Gradle, Kotlin DSL and Groovy DSL; Maven XML, properties, version catalogs;
- Go source and module/workspace files;
- TypeScript/JavaScript source and common variants, including TSX/JSX, and comment-bearing JSONC/JSON5;
- Shell, Makefiles, YAML, TOML, XML, and relevant build/configuration formats.

It recognizes ``//``, ``/* ... */``, XML comments, and broad ``#``/``!`` candidate patterns as appropriate. Multiline and trailing comments are included. Known generated, dependency, minified, and lockfile paths are skipped with reasons.

File-extension coverage is intentionally explicit and maintained in the script; do not duplicate file globs in the skill instructions. Add support and tests in the script when permanent new coverage is needed.

## Filter and Classify After Discovery

1. **Check the candidate:** confirm that the reported token is really a comment. The scanner is lexical, not a complete language parser; URLs, Go raw strings, JSX, template literals, regular expressions, shell expansions, and quoted configuration values can produce false positives or omissions. Inspect the source syntax and use language tooling where helpful.
2. **Exclude out-of-scope material:** Javadoc/KDoc/JSDoc/TSDoc, Go API documentation comments (often written with ``//``), license and copyright notices, generated and vendored material, and test fixtures whose comment-looking text is part of the test data. Record exclusions without counting them as removed.
3. **Protect semantic comments:** Go build constraints, ``//go:generate``, ``//go:embed``, cgo directives, ``// indirect`` in module files; TypeScript triple-slash references and ``@ts-`` annotations; ESLint/formatter controls; source maps, optimizer/bundler annotations, shell shebangs, and build pragmas. These may alter compilation or tool behavior. **Active directives normally remain KEEP**; investigate uncertain directives before modifying them.
4. **Group comment units:** one independent explanation, task, or directive is one review unit. Multiple nearby explanations with different purposes are separate units even if the script reports one contiguous block.
5. **Decide:** apply the SKILL's KEEP / REMOVE / REWRITE / ASK criteria using actual surrounding code, tests, and relevant contracts. Advisory ``hints`` such as task, documentation candidate, legal, or tool directive **never** authorize automatic deletion or retention.

If a tracked file is unexpectedly missing from ``scanned_files``, investigate whether its extension is supported, a skip rule applies, it is unreadable, or it falls outside the requested scope. Record all unreviewed files and why.

## Local Verification

The skill's bundled self-contained tests can be run without additional dependencies:

```sh
python3 -m unittest discover -s <skill-directory>/tests -v
```

These validate inventory behavior on temporary Git repositories; they do not replace per-repository validation of the resulting cleanup diff.
