"""Validate a self-contained skill bundle using only the Python standard library.

Checks structure, local links, code fences, sectioned source citations and
declared source hashes, not device behavior or semantic completeness.
Read-only by default; pass `--write` to refresh `audit/validation.json`.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def strip_fences(markdown):
    """Return `(unbalanced, prose_without_fenced_blocks)`."""
    fence_char = None
    fence_len = 0
    out = []
    for line in markdown.splitlines(keepends=True):
        stripped = line.rstrip('\r\n')
        if fence_char is None:
            m = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', stripped)
            if m and not (m.group(1)[0] == '`' and '`' in m.group(2)):
                fence_char = m.group(1)[0]
                fence_len = len(m.group(1))
                out.append('\n')
                continue
            out.append(line)
        else:
            if re.match(r'^ {0,3}' + re.escape(fence_char) + r'{' + str(fence_len) + r',}[ \t]*$', stripped):
                fence_char = None
                fence_len = 0
            out.append('\n')
    return fence_char is not None, ''.join(out)


def extract_citations(prose):
    """Extract bracketed citations like `[Name]` or `[`symbol`]` outside inline code and links."""
    placeholders = {}

    def keep_code_citation(match):
        key = f'__CITE_{len(placeholders)}__'
        placeholders[key] = match.group(1)
        return f'[{key}]'

    stage = re.sub(r'\[(`[^`\n]+`)\](?!\()', keep_code_citation, prose)
    stage = re.sub(r'`[^`\n]*`', ' ', stage)
    found = set()
    for raw in re.findall(r'\[([^\[\]\n]+)\](?!\()', stage):
        token = placeholders.get(raw, raw).strip()
        if not token or token in ('x', 'X') or token.startswith('^'):
            continue
        found.add(token)
    return found


def parse_sectioned_sources(prose):
    """Parse `## <file>.md` sections of `- Name: URL` entries in `references/sources.md`."""
    sections = {}
    current = None
    for line in prose.splitlines():
        heading = re.match(r'^##\s+([^\s#]+\.md)\s*$', line.strip())
        if heading:
            current = heading.group(1)
            sections.setdefault(current, set())
            continue
        if line.startswith('## '):
            current = None
            continue
        if current is not None:
            item = re.match(r'^-\s+(.+?):\s+https?://\S+\s*$', line.strip())
            if item:
                sections[current].add(item.group(1).strip())
    return sections


def validate(root, expected_name=None):
    root = Path(root).resolve()
    errors = []
    pages = set()
    prose_by_page = {}
    links = 0
    checked = 0

    def label(path):
        return path.relative_to(root).as_posix()

    def read(path):
        try:
            return path.read_text(encoding='utf-8-sig')
        except (OSError, UnicodeError) as exc:
            errors.append(f'Cannot read {label(path)}: {type(exc).__name__}')
            return None

    def local_path(value, context):
        if not isinstance(value, str) or not value.strip() or '\x00' in value:
            errors.append(f'Invalid relative path: {context}')
            return None
        value = value.replace('\\', '/')
        if Path(value).is_absolute() or PureWindowsPath(value).drive:
            errors.append(f'Path must be relative: {context}')
            return None
        try:
            candidate = (root / value).resolve()
        except (OSError, ValueError, RuntimeError):
            errors.append(f'Invalid relative path: {context}')
            return None
        if not candidate.is_relative_to(root):
            errors.append(f'Path outside bundle: {context}')
            return None
        return candidate

    target_name = expected_name or (root.name if root.parent.name == 'skills' else None)

    skill_path = root / 'SKILL.md'
    skill = read(skill_path)
    if skill is not None:
        match = re.match(r'\A---\s*\n(.*?)\n---[ \t]*(?:\n|\Z)(.*)\Z', skill, re.S)
        if not match:
            errors.append('Invalid skill frontmatter: missing delimiters')
        else:
            header, body = match.groups()
            for key in ('name', 'description'):
                values = re.findall(r'^' + key + r':[ \t]*(.*)$', header, re.M)
                value = values[0].strip() if len(values) == 1 else ''
                if value in ('|', '>', '|-', '>-'):
                    block = re.search(r'^' + key + r':[^\n]*\n((?:[ \t]+[^\n]*(?:\n|$))+)', header, re.M)
                    value = block.group(1).strip() if block else ''
                value = value.strip('\"\'').strip()
                if not value or value.startswith('#') or value.lower() in ('null', '~'):
                    errors.append(f'Invalid skill frontmatter: nonempty {key} required')
                elif key == 'name':
                    if len(value) > 64 or not NAME_RE.fullmatch(value):
                        errors.append('Invalid skill frontmatter: invalid name format')
                    elif target_name is not None and value != target_name:
                        errors.append(f'Invalid skill frontmatter: unexpected name {value!r} (expected {target_name!r})')
                elif key == 'description' and len(value) > 1024:
                    errors.append('Invalid skill frontmatter: description exceeds 1024 characters')
            if not body.strip():
                errors.append('Empty skill body')

    pending = [skill_path, *sorted((root / 'references').rglob('*.md'))]
    if (root / 'audit/REVIEW.md').exists():
        pending.append(root / 'audit/REVIEW.md')
    while pending:
        page = pending.pop()
        if page in pages:
            continue
        pages.add(page)
        data = skill if page == skill_path else read(page)
        if data is None:
            continue
        if not data.strip():
            errors.append(f'Empty Markdown: {label(page)}')
        unbalanced, prose = strip_fences(data)
        if unbalanced:
            errors.append(f'Unbalanced code fence: {label(page)}')
        prose_by_page[page] = prose

        # Detect relative parent paths inside inline backticks that escape the skill root.
        for code_span in re.findall(r'`([^`\n]+)`', prose):
            token = code_span.strip()
            if re.match(r'^\.\.(?:/[^\s`]+)+$', token):
                rel_from_page = (page.parent.relative_to(root) / token).as_posix()
                local_path(rel_from_page, f'inline path in {label(page)}')

        prose_no_code = re.sub(r'`[^`\n]*`', ' ', prose)
        # Inline Markdown links, including angle-delimited paths with spaces.
        for angled, plain in re.findall(r'\]\((?:<([^>]+)>|([^\s)]+))', prose_no_code):
            target = angled or plain
            if re.match(r'(?:https?://|mailto:|#)', target):
                continue
            links += 1
            target = unquote(target.split('#', 1)[0])
            if Path(target).is_absolute() or PureWindowsPath(target).drive:
                errors.append(f'Link must be relative: {label(page)}')
                continue
            relative = (page.parent.relative_to(root) / target).as_posix()
            resolved = local_path(relative, f'link in {label(page)}')
            if resolved is None:
                continue
            if not resolved.is_file():
                errors.append(f'Missing link: {label(page)}: {target}')
            elif resolved.suffix.lower() == '.md':
                pending.append(resolved)

    sources_page = root / 'references/sources.md'
    if sources_page in prose_by_page:
        sections = parse_sectioned_sources(prose_by_page[sources_page])
        if sections:
            for ref_name, defined in sorted(sections.items()):
                ref_page = root / 'references' / ref_name
                if ref_page not in prose_by_page:
                    errors.append(f'Missing reference file for sources.md section: {ref_name}')
                    continue
                cited = extract_citations(prose_by_page[ref_page])
                for missing in sorted(cited - defined):
                    errors.append(f'Missing source in sources.md ({ref_name}): [{missing}]')
                for unused in sorted(defined - cited):
                    errors.append(f'Unused source in sources.md ({ref_name}): [{unused}]')
            refs_root = root / 'references'
            for page, page_prose in sorted(prose_by_page.items()):
                if page == sources_page or not page.is_relative_to(refs_root):
                    continue
                rel_ref = page.relative_to(refs_root).as_posix()
                if rel_ref not in sections:
                    for missing in sorted(extract_citations(page_prose)):
                        errors.append(f'Missing source section in sources.md ({rel_ref}): [{missing}]')

    local_plugin_data = root / 'references/native-plugins-data.md'
    if len(root.parents) >= 2:
        shared_plugin_data = root.parents[1] / 'shared/native-plugins.md'
        if shared_plugin_data.is_file() and local_plugin_data.is_file():
            try:
                shared_text = shared_plugin_data.read_text(encoding='utf-8-sig').replace('\r\n', '\n')
                local_text = local_plugin_data.read_text(encoding='utf-8-sig').replace('\r\n', '\n')
                if shared_text != local_text:
                    errors.append('Out-of-sync shared data: references/native-plugins-data.md differs from shared/native-plugins.md')
            except (OSError, UnicodeError) as exc:
                errors.append(f'Cannot compare native-plugins data: {type(exc).__name__}')

    manifest_path = root / 'audit/source-manifest.json'
    require_manifest = manifest_path.exists() or (root / 'examples').exists() or (root / 'audit').exists()
    if require_manifest:
        manifest_text = read(manifest_path)
        if manifest_text is not None:
            try:
                manifest = json.loads(manifest_text)
            except json.JSONDecodeError:
                errors.append('Malformed source manifest JSON')
                manifest = None
            if manifest is not None:
                if not isinstance(manifest, dict) or not isinstance(manifest.get('files'), list):
                    errors.append('Invalid source manifest: files must be an array')
                else:
                    seen = set()
                    for index, entry in enumerate(manifest['files']):
                        if (
                            not isinstance(entry, dict)
                            or not isinstance(entry.get('copy'), str)
                            or not isinstance(entry.get('sha256'), str)
                            or not re.fullmatch(r'[a-fA-F0-9]{64}', entry['sha256'])
                        ):
                            errors.append(f'Invalid manifest entry {index}: copy and SHA-256 required')
                            continue
                        path = local_path(entry['copy'], f'manifest entry {index}')
                        if path is None:
                            continue
                        if path in seen:
                            errors.append(f'Duplicate manifest entry: {label(path)}')
                            continue
                        seen.add(path)
                        try:
                            content = path.read_bytes()
                        except OSError as exc:
                            errors.append(f'Cannot read {label(path)}: {type(exc).__name__}')
                            continue
                        checked += 1
                        expected_hash = entry['sha256'].lower()
                        raw_hash = hashlib.sha256(content).hexdigest()
                        if raw_hash != expected_hash:
                            lf_matches = False
                            try:
                                content.decode('utf-8')
                                lf_matches = hashlib.sha256(content.replace(b'\r\n', b'\n')).hexdigest() == expected_hash
                            except UnicodeDecodeError:
                                lf_matches = False
                            if not lf_matches:
                                errors.append(f'Source hash mismatch: {label(path)}')

    return {
        'ok': not errors,
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'active_markdown_files': len(pages),
        'local_links_checked': links,
        'preserved_sources_checked': checked,
        'errors': errors,
        'scope': 'Structure, local links, citations and declared hashes; not semantic coverage',
        'runtime_device_tests': 'not performed; document/package validation only',
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description='Validate a skill bundle.')
    parser.add_argument('path', nargs='?', default=str(ROOT), help='Skill root directory (defaults to parent of scripts/).')
    parser.add_argument('--write', action='store_true', help='Atomically refresh audit/validation.json.')
    args = parser.parse_args(argv)

    target_root = Path(args.path).resolve()
    result = validate(target_root)
    if args.write:
        report = target_root / 'audit/validation.json'
        temporary = report.with_suffix('.json.tmp')
        try:
            report.parent.mkdir(parents=True, exist_ok=True)
            temporary.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
            temporary.replace(report)
        except OSError as exc:
            result['ok'] = False
            result['errors'].append(f'Cannot replace validation report: {type(exc).__name__}')
            print('Could not refresh audit/validation.json; use this command result.', file=sys.stderr)
    print(json.dumps(result, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
