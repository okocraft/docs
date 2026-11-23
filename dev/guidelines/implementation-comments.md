# Implementation Comment Guidelines

This document defines when to write and maintain comments about implementation details in OKOCRAFT projects.

The goal is to make code understandable primarily through the code itself, while preserving non-obvious information that future maintainers need to understand or safely change it.

This guideline applies to explanatory comments inside implementation code (such as `//` and `/* ... */` comments). **It does not govern documentation comments** such as Javadoc, which describe contracts and usage for API consumers. Documentation requirements for externally exposed APIs and reusable components remain separate and are not weakened by this guideline.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** describe requirement levels in this document.

These guidelines define defaults for new code and code being materially changed. Existing working code does not need to be rewritten solely for comment-style consistency.

## 1. Make the Code the Primary Explanation

**SHOULD:** Express information in code whenever it can be expressed clearly through naming, types, structure, control flow, or appropriate abstractions.

Before writing a comment to explain confusing code, consider whether the code itself could be improved by:

- renaming a variable, method, or type to convey its intent;
- simplifying a condition or control flow;
- extracting a conceptually meaningful method;
- representing a constraint through a type, validation, or assertion.

Do not introduce unnecessary abstractions, excessively long names, or fragmented methods merely to avoid a comment. Clear code is the objective, not zero comments.

**MUST NOT:** Add comments that merely restate immediately visible code.

For example, this comment adds no information:

```java
// Increment the retry count.
retryCount++;
```

## 2. Explain Non-obvious Reasons and Constraints

**SHOULD:** Use implementation comments primarily to explain **why** a non-obvious decision or constraint exists, rather than narrating **what** each statement does or **how** it executes.

Useful implementation comments may clarify:

- a constraint or surprising behavior of an external API or platform;
- why an otherwise simpler-looking implementation would be incorrect;
- an important assumption or invariant not adequately conveyed by the code;
- a subtle ordering, concurrency, compatibility, or failure-handling requirement.

For example:

```java
// Publish only after validation so a failed reload leaves the active configuration intact.
var replacement = parseAndValidate(source);
activeConfiguration = replacement;
```

The comment provides the invariant behind the implementation; it does not describe each statement.

**Exception:** A short explanation of **what** a complex algorithm or section establishes MAY be useful when its overall intent or invariant remains difficult to understand after reasonable improvements to the code. This is not a reason to narrate ordinary implementation steps.

Do not add a comment merely because the code takes effort to read. First determine whether the difficulty comes from unclear code or from genuinely necessary domain knowledge.

Assume readers are developers familiar with the programming language, its common idioms, and the project's basic architecture and domain. Implementation comments are not tutorials: do not explain standard language constructs, conventional framework usage, or general concepts that readers can learn from language or framework documentation. This assumption does not eliminate the need to explain non-obvious project-specific decisions or constraints.

## 3. Keep Comments Relevant to Future Maintenance

**SHOULD:** Write comments that would still be useful to someone reading or modifying the code later, without knowledge of the original development session.

Avoid comments that record:

- what was tried during implementation;
- who requested a change or what was discussed in review;
- why a particular commit or PR was created;
- temporary workarounds or plans that no longer apply;
- historical details that do not explain a current constraint.

Development history, alternative approaches considered, and the evolution of a decision belong in commits, PR descriptions, discussions, and issues. Preserve enough context there for a future maintainer to follow it through `git blame` and the associated change.

**SHOULD:** When a non-obvious implementation depends on a currently relevant external contract, describe that contract in the comment. A link to authoritative specifications or an upstream issue MAY be added when it materially helps verification; a bare issue or PR reference is not an explanation.

An earlier bug or incident may explain *how* the implementation came about, but the comment should explain *why the code must behave this way now*.

## 4. Treat TODO and FIXME as Temporary Work Notes

`TODO` and `FIXME` comments MAY be used while exploring or implementing a change, including reminders about work required before production.

**MUST:** Resolve or remove newly introduced work-in-progress `TODO` and `FIXME` comments before merging the change.

When work can legitimately be deferred, track it in an issue with the necessary context instead of leaving an implementation comment as a standing task list. An issue does not justify merging incomplete behavior that is required for correctness or the intended release.

Existing comments of this kind do not require unrelated cleanup solely to adopt this guideline, but SHOULD be addressed when the surrounding implementation is materially changed.

## 5. Maintain Comments with the Code

**MUST:** Keep implementation comments accurate when changing the behavior, assumptions, or constraints they describe. Update or remove a comment in the same change that makes it obsolete.

**SHOULD:** Prefer concise comments close to the relevant code. Avoid duplicating the same explanation across locations when it can be captured once at a meaningful boundary.

**SHOULD:** Write implementation comments in English unless the repository explicitly follows a different language convention.

Comments are not automatically better because they are detailed. A comment is useful when its information would otherwise be missing and remains valid as the code evolves.

## 6. Review Checklist

When adding or changing an implementation comment, check:

1. Can naming, structure, or types communicate this more clearly?
2. Does the comment add information that cannot reasonably be inferred from the code?
3. Is it explaining a current reason, constraint, or invariant rather than narrating obvious behavior?
4. If it describes *what*, is the complexity genuinely exceptional?
5. Is the information useful for future maintenance, rather than a record of the development process?
6. Are all newly introduced `TODO` / `FIXME` comments resolved or removed before merge, with any legitimately deferred work tracked in an issue?
7. Is the comment still accurate after the change?

## References

- [Google Engineering Practices — What to Look for in a Code Review](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- [Google Java Style Guide — Implementation Comments and Javadoc](https://google.github.io/styleguide/javaguide.html)
- [Martin Fowler and Kent Beck — Refactoring, "Comments"](https://www.informit.com/articles/article.aspx?p=2952392&seqNum=24)
- [John Ousterhout and Robert C. Martin — A Philosophy of Software Design vs Clean Code, "Comments"](https://github.com/johnousterhout/aposd-vs-clean-code#comments)
- [Linux Kernel Coding Style — Commenting](https://docs.kernel.org/process/coding-style.html)
