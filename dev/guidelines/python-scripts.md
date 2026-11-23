# Python Scripts and Tests for Agent Skills

This guide applies to Python helper scripts shipped with OKOCRAFT agent skills and to the tests that validate them. Its goal is small, readable, predictable utilities whose outputs and failures can be trusted by both people and agents.

Prefer the Python standard library for runtime code. This is a default, not a ban on dependencies: introduce third-party packages only when they materially improve correctness or maintainability, and document why they are required. Avoid unrelated refactoring solely to adopt this guide.

## 1. Design an Explicit Contract

**SHOULD:** Before implementing a script, specify:

- its inputs: command-line arguments, paths, environment variables, and required external tools;
- its outputs: standard output, standard error, files, and machine-readable formats;
- its exit-status meanings, including invalid input and partial failure;
- its side effects and safety boundaries (read-only, generated files, network access, changes to a target repository);
- its minimum supported Python version and any other runtime requirements.

Prefer the simplest interface sufficient for the skill. If an agent consumes the output, use a stable, documented structure such as JSON, and distinguish successful empty results from incomplete or invalid scans. A schema version is useful for outputs consumed by other tools.

Avoid making a successful return code imply that a partial or uncertain operation completed fully. Report skipped, unreadable, or unsupported inputs explicitly.

## 2. Write Readable, Maintainable Python

**SHOULD:** Follow [PEP 8](https://peps.python.org/pep-0008/) and use Ruff for consistent linting. Prioritize comprehension over brevity or avoiding every duplicate line.

- Use descriptive names for operations and values. Extract focused functions when they clarify meaningful responsibilities, not merely to reduce line counts.
- Keep parsing, domain decisions, and output formatting separate where practical. Favor explicit control flow over dense one-liners or clever expressions.
- Use type hints when they clarify non-obvious data shapes and function boundaries; they are not mandatory annotations for every local value.
- Use `pathlib`, context managers, and explicit encodings when reading or writing text files.
- Handle expected errors at an appropriate boundary; do not use broad `except Exception` to hide an incomplete operation.
- Use `subprocess.run` with argument arrays and explicit error handling for external commands; avoid `shell=True` unless a shell is genuinely necessary and inputs are controlled.
- Treat paths and external data as untrusted until validated. Avoid following symlinks, overwriting user changes, or deleting files without deliberate authorization.
- Keep implementation comments governed by the [Implementation Comment Guidelines](implementation-comments.md). Explain durable non-obvious reasons rather than ordinary language constructs.

Prefer small modules or scripts with an ordinary `main()` and `if __name__ == '__main__':` entry point. Do not introduce a framework, plugin loader, or abstraction layer for a single straightforward script.

## 3. Test Observable Behavior and Failure Paths

**SHOULD:** Write tests for behavior whose failure would matter to the skill, not tests for every line or private helper. Python's built-in `unittest` is sufficient by default.

For a command-line script, cover as applicable:

1. **Normal operation:** realistic input produces the intended output and exit status.
2. **Boundaries and exclusions:** optional arguments, empty inputs, file scoping, generated/ignored paths, and repeatable operations.
3. **Malformed or unsafe inputs:** invalid paths, missing required tools or files, wrong encodings, and unexpected input syntax.
4. **Partial failure:** unreadable files, ambiguous parsing, external-command errors, and truthful reporting rather than silent success.
5. **Output contracts:** JSON shape, stable ordering when promised, diagnostics, and correct separation of stdout and stderr.
6. **Regressions:** each substantive bug fix receives a focused test that fails on the old behavior.

Use `tempfile.TemporaryDirectory` and isolated fixtures. For a Git-aware script, initialize temporary repositories rather than making assumptions about the developer's checkout. Test the public command-line interface with `subprocess` where possible, and test internal functions directly only when they represent meaningful independent logic.

Keep tests deterministic, independent of network availability and developer-specific paths, and safe to run repeatedly. Assert outcomes rather than incidental implementation details. Do not treat a passing test as proof of behaviors or environments it did not exercise.

## 4. Verify Changes Locally and in CI

For Python scripts under `dev/skills`, this repository runs:

- **Ruff lint:** `ruff check dev/skills`, with the version pinned in `requirements-dev.txt` and rules in `ruff.toml`;
- **syntax compilation:** `python -m compileall -q dev/skills`;
- **unit tests:** `python -m unittest discover -s dev/skills/implementation-comment-cleanup/tests -v` for the existing comment cleanup skill.

The [Python Skill Scripts workflow](../../.github/workflows/python-skills.yml) runs linting and tests on pull requests and on `main`, targeting the current stable Python release (currently Python 3.15). There is no older-version compatibility commitment for these internal helper scripts. When a new stable minor release is adopted, update the workflow, Ruff target, and documented runtime requirement together. Future skills with Python code SHOULD add focused tests and register them in the workflow rather than assuming the current test command discovers every skill.

The runtime scripts do not import Ruff: `requirements-dev.txt` contains tooling for maintainers and CI, not runtime requirements. Renovate updates that tooling through the shared Python preset.

Before finalizing a script change, inspect the diff for unintended behavior, rerun the relevant tests, and state any verification that was not possible. Avoid artificial test-count or coverage-percentage targets; tests should provide meaningful evidence for risky and observable behavior.

## References

- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [The Python Standard Library](https://docs.python.org/3/library/index.html)
- [unittest — Unit testing framework](https://docs.python.org/3/library/unittest.html)
- [subprocess — Subprocess management](https://docs.python.org/3/library/subprocess.html)
- [tempfile — Temporary files and directories](https://docs.python.org/3/library/tempfile.html)
- [Ruff — Linter](https://docs.astral.sh/ruff/linter/)
- [GitHub Actions — Building and testing Python](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)
