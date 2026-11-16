"""Validate a self-contained skill bundle using only the Python standard library.

Checks structure, local links and declared source hashes, not device behavior or
semantic completeness. The manifest uses relative `copy` paths and SHA-256.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def validate(root):
    root = root.resolve()
    errors = []
    pages = set()
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
                elif key == 'name' and value != 'tauri-native-mobile':
                    errors.append('Invalid skill frontmatter: unexpected name')
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
        if data.count('```') % 2:
            errors.append(f'Unbalanced code fence: {label(page)}')
        # Inline Markdown links, including angle-delimited paths with spaces.
        for angled, plain in re.findall(r'\]\((?:<([^>]+)>|([^\s)]+))', data):
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

    manifest_text = read(root / 'audit/source-manifest.json')
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
                    if not isinstance(entry, dict) or not isinstance(entry.get('copy'), str) or not isinstance(entry.get('sha256'), str) or not re.fullmatch(r'[a-fA-F0-9]{64}', entry['sha256']):
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
                    if hashlib.sha256(content).hexdigest() != entry['sha256'].lower():
                        errors.append(f'Source hash mismatch: {label(path)}')

    return {'ok': not errors,
            'checked_at': datetime.now(timezone.utc).isoformat(),
            'active_markdown_files': len(pages), 'local_links_checked': links,
            'preserved_sources_checked': checked, 'errors': errors,
            'scope': 'Structure, local links and declared hashes; not semantic coverage',
            'runtime_device_tests': 'not performed; document/package validation only'}


def main():
    result = validate(ROOT)
    report = ROOT / 'audit/validation.json'
    temporary = report.with_suffix('.json.tmp')
    try:
        report.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        temporary.replace(report)
    except OSError as exc:
        result['ok'] = False
        result['errors'].append(f'Cannot replace validation report: {type(exc).__name__}')
        print('Could not refresh audit/validation.json; use this command result.', file=sys.stderr)
    print(json.dumps(result, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
