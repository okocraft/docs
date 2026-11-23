"""Deterministically inventory comment candidates in tracked source/build files.

Requires Python 3.15+ and Git; no third-party Python dependencies. This is a lexical candidate finder,
not an API-documentation classifier or an instruction to delete comments.
"""

import argparse
import bisect
import json
import posixpath
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

C_LIKE = {'.java', '.kt', '.kts', '.groovy', '.gradle', '.go', '.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.mts', '.cts', '.jsonc', '.json5'}
XML = {'.xml'}
HASH = {'.toml', '.properties', '.yml', '.yaml', '.sh', '.bash', '.zsh', '.mk'}
HASH_NAMES = {'Makefile', 'GNUmakefile', 'Dockerfile', 'Justfile', 'BUILD', 'WORKSPACE', 'MODULE.bazel', 'gradlew', 'mvnw'}
C_NAMES = {'go.mod', 'go.work'}
SKIP_DIRS = {'.git', '.gradle', '.next', 'node_modules', 'vendor', 'dist', 'target', 'build', 'out', 'generated', '__generated__'}
SKIP_NAMES = {'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock', 'Cargo.lock', 'gradle.lockfile'}
HINTS = (
    ('task', re.compile(r'\b(?:TODO|FIXME)\b', re.IGNORECASE)),
    ('legal', re.compile(r'\b(?:SPDX-License-Identifier|Copyright|All rights reserved)\b', re.IGNORECASE)),
    ('tool-directive', re.compile(r'(?:\bgo:(?:build|generate|embed|linkname|noescape|nosplit)\b|\+build\b|\b(?:@ts-(?:ignore|expect-error|check|nocheck)|eslint-|biome-|noinspection|@vite-ignore|webpack|sourceMappingURL|indirect\b)|#__PURE__|^\s*#!|<reference\b)', re.IGNORECASE)),
    ('generated-marker', re.compile(r'\b(?:DO NOT EDIT|@generated|Code generated)\b', re.IGNORECASE)),
)


def source_kind(name):
    path = PurePosixPath(name)
    if path.name in C_NAMES or path.suffix.lower() in C_LIKE:
        return 'slash'
    if path.suffix.lower() in XML:
        return 'xml'
    if path.name in HASH_NAMES or path.suffix.lower() in HASH:
        return 'hash'
    return None


def skip_reason(name):
    path = PurePosixPath(name)
    if any(part in SKIP_DIRS for part in path.parts[:-1]):
        return 'generated/dependency/build directory'
    if path.name in SKIP_NAMES or path.name.endswith(('.min.js', '.min.css', '.map')):
        return 'generated/lock/minified file'
    if re.search(r'(?:\.generated\.[^.]+|\.g\.ts|_gen\.go)$', path.name):
        return 'generated filename'
    return None


def line_number(newlines, pos):
    return bisect.bisect_left(newlines, pos) + 1


def hints(text):
    flags = [name for name, pattern in HINTS if pattern.search(text)]
    if text.lstrip().startswith(('/**', '///')):
        flags.append('documentation-candidate')
    return flags


def make_candidate(text, newlines, start, end, kind):
    raw = text[start:end]
    return {'start_line': line_number(newlines, start),
            'end_line': line_number(newlines, max(start, end - 1)),
            'kind': kind, 'text': raw, 'hints': hints(raw)}


def scan_slash(text, is_go=False, warnings=None):
    """Scan comments outside simple strings; handle JS template substitutions.

    Not a full grammar parser (notably JSX and regex literals). Any results
    remain candidates and must be syntax-checked before classification.
    """
    out = []
    if warnings is None:
        warnings = []
    newlines = [i for i, ch in enumerate(text) if ch == '\n']
    n = len(text)

    def quoted(i, delim):
        i += len(delim)
        while i < n:
            if text.startswith(delim, i):
                return i + len(delim)
            if text[i] == '\\' and len(delim) == 1:
                i += 2
            else:
                i += 1
        return i

    def template(i):
        i += 1
        while i < n:
            if text[i] == '\\':
                i += 2
            elif text[i] == chr(96):
                return i + 1
            elif text.startswith(chr(36) + '{', i):
                i = code(i + 2, interpolated=True)
            else:
                i += 1
        return i

    def code(i, interpolated=False):
        brace_depth = 0
        while i < n:
            if interpolated and text[i] == '}':
                if brace_depth == 0:
                    return i + 1
                brace_depth -= 1
                i += 1
                continue
            if interpolated and text[i] == '{':
                brace_depth += 1
            if text.startswith('//', i):
                end = text.find('\n', i)
                end = n if end < 0 else end
                out.append(make_candidate(text, newlines, i, end, 'line'))
                i = end
                continue
            if text.startswith('/*', i):
                end = text.find('*/', i + 2)
                if end < 0:
                    warnings.append({'line': line_number(newlines, i),
                                     'reason': 'Unterminated block-comment candidate; may be a regex literal. Manually inspect this file for missed comments.'})
                    end = n
                else:
                    end += 2
                out.append(make_candidate(text, newlines, i, end, 'block'))
                i = end
                continue
            if text.startswith('"""', i):
                i = quoted(i, '"""')
                continue
            if text[i] in ('"', "'"):
                i = quoted(i, text[i])
                continue
            if text[i] == chr(96):
                # Go backticks delimit raw strings; only JS/TS interpolates templates.
                i = quoted(i, chr(96)) if is_go else template(i)
                continue
            i += 1
        return i

    code(0)
    return out


def scan_xml(text):
    newlines = [i for i, ch in enumerate(text) if ch == '\n']
    out = []
    pos = 0
    while True:
        start = text.find('<!--', pos)
        if start < 0:
            break
        end = text.find('-->', start + 4)
        end = len(text) if end < 0 else end + 3
        out.append(make_candidate(text, newlines, start, end, 'xml'))
        pos = end
    return out


def scan_hash(text):
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        # Broad candidate discovery: the actual grammar decides whether # or !
        # denotes a comment (e.g., TOML/YAML quotes, shell expansion).
        match = re.search('[#!]', line)
        if match:
            out.append({'start_line': i, 'end_line': i, 'kind': 'hash-candidate',
                        'text': line[match.start():], 'hints': hints(line[match.start():])})
    return out


def normalize_scope(path):
    path = path.replace('\\', '/')
    if not path or path.startswith('/') or re.match(r'^[A-Za-z]:', path):
        raise ValueError(f'--path must be relative to the repository: {path!r}')
    normalized = posixpath.normpath(path)
    if normalized == '..' or normalized.startswith('../'):
        raise ValueError(f'--path must remain inside the repository: {path!r}')
    return '' if normalized == '.' else normalized


def inventory(repo, paths=()):
    proc = subprocess.run(['git', '-C', str(repo), 'ls-files', '-z'], capture_output=True, check=True)
    names = sorted(p.decode('utf-8', 'surrogateescape') for p in proc.stdout.split(b'\0') if p)
    scope = tuple(normalize_scope(p) for p in paths)
    for p in scope:
        if not any((not p or name == p or name.startswith(p + '/'))
                   and source_kind(name) and not skip_reason(name) for name in names):
            raise ValueError(f'--path {p or "."!r} matches no tracked, supported source/build files')
    result = {'schema_version': 1, 'scanned_files': [], 'excluded_files': [], 'unreadable_files': [],
              'scan_warnings': [], 'candidates': [], 'scope': [p or '.' for p in scope],
              'notes': ['Candidates are not confirmed comments; syntax, directives and documentation status require review.',
                        'Only tracked files are scanned; ignored and untracked files are not included.',
                        'The slash scanner is not a full parser; inspect complex syntax such as JSX/regex and embedded templates.']}
    for name in names:
        if scope and not any(not p or name == p or name.startswith(p + '/') for p in scope):
            continue
        kind = source_kind(name)
        if not kind:
            continue
        reason = skip_reason(name)
        if reason:
            result['excluded_files'].append({'path': name, 'reason': reason})
            continue
        file_path = repo / name
        if file_path.is_symlink():
            result['excluded_files'].append({'path': name, 'reason': 'symlink (not followed)'})
            continue
        try:
            data = file_path.read_text(encoding='utf-8')
        except (OSError, UnicodeError) as exc:
            result['unreadable_files'].append({'path': name, 'reason': type(exc).__name__})
            continue
        result['scanned_files'].append(name)
        scanner = {'slash': scan_slash, 'xml': scan_xml, 'hash': scan_hash}[kind]
        warnings = []
        items = scan_slash(data, is_go=PurePosixPath(name).suffix == '.go', warnings=warnings) if kind == 'slash' else scanner(data)
        for warning in warnings:
            result['scan_warnings'].append({'path': name, **warning})
        for item in items:
            result['candidates'].append({'path': name, **item})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'), help='Target Git repository root')
    parser.add_argument('--path', action='append', default=[], help='Restrict scan to a relative file/subtree; repeatable')
    parser.add_argument('--output', type=Path, help='Write JSON to this file instead of stdout')
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    try:
        result = inventory(repo, args.path)
    except subprocess.CalledProcessError as exc:
        parser.error('Cannot list tracked files: ' + str(exc))
    except ValueError as exc:
        parser.error(str(exc))
    data = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.write_text(data, encoding='utf-8')
        print(f'Scanned {len(result["scanned_files"])} files; {len(result["candidates"])} candidates; '
              f'{len(result["excluded_files"])} excluded; {len(result["unreadable_files"])} unreadable; '
              f'{len(result["scan_warnings"])} scan warnings. Output: {args.output}')
    else:
        sys.stdout.write(data)
    for warning in result['scan_warnings']:
        print(f'WARNING: {warning["path"]}:{warning["line"]}: {warning["reason"]}', file=sys.stderr)
    if result['unreadable_files'] or result['scan_warnings']:
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
