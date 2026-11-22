"""Validate the entire tauri-app-builder plugin and all bundled skills.

Read-only by default. Pass `--sync-shared` to copy `shared/native-plugins.md`
into each skill's `references/native-plugins-data.md` before validating.
"""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def load_bundle_validator(plugin_root):
    candidate = plugin_root / 'skills/tauri-native-mobile/scripts/validate_bundle.py'
    if not candidate.is_file():
        return None
    spec = importlib.util.spec_from_file_location('validate_bundle', candidate)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_frontmatter_description(skill_md_text):
    match = re.match(r'\A---\s*\n(.*?)\n---[ \t]*(?:\n|\Z)', skill_md_text, re.S)
    if not match:
        return ''
    header = match.group(1)
    values = re.findall(r'^description:[ \t]*(.*)$', header, re.M)
    value = values[0].strip() if len(values) == 1 else ''
    if value in ('|', '>', '|-', '>-'):
        block = re.search(r'^description:[^\n]*\n((?:[ \t]+[^\n]*(?:\n|$))+)', header, re.M)
        value = block.group(1).strip() if block else ''
    return value.strip('\"\'').strip()


def validate_plugin(plugin_root, sync_shared=False):
    plugin_root = Path(plugin_root).resolve()
    errors = []
    skills_checked = []

    plugin_json_path = plugin_root / '.claude-plugin/plugin.json'
    if not plugin_json_path.is_file():
        errors.append('Missing .claude-plugin/plugin.json')
    else:
        try:
            pj = json.loads(plugin_json_path.read_text(encoding='utf-8-sig'))
            if not isinstance(pj, dict):
                errors.append('Invalid .claude-plugin/plugin.json: root must be an object')
                pj = {}
            for key in ('name', 'version', 'description', 'license'):
                if not isinstance(pj.get(key), str) or not pj[key].strip():
                    errors.append(f'Invalid .claude-plugin/plugin.json: nonempty {key} required')
            icon_field = pj.get('icon')
            if isinstance(icon_field, str) and icon_field.strip():
                icon_path = (plugin_root / icon_field).resolve()
                if not icon_path.is_relative_to(plugin_root) or not icon_path.is_file():
                    errors.append(f'Missing plugin icon referenced in plugin.json: {icon_field}')
            elif not (plugin_root / '.claude-plugin/icon.png').is_file() and not (plugin_root / 'assets/icon.png').is_file():
                errors.append('Missing plugin icon (.claude-plugin/icon.png or icon field in plugin.json)')
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f'Invalid .claude-plugin/plugin.json: {type(exc).__name__}')

    marketplace_path = plugin_root / '.claude-plugin/marketplace.json'
    if not marketplace_path.is_file():
        errors.append('Missing .claude-plugin/marketplace.json')
    else:
        try:
            mj = json.loads(marketplace_path.read_text(encoding='utf-8-sig'))
            if not isinstance(mj, dict) or not isinstance(mj.get('name'), str) or not isinstance(mj.get('plugins'), list) or not mj['plugins']:
                errors.append('Invalid .claude-plugin/marketplace.json: name and nonempty plugins required')
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f'Invalid .claude-plugin/marketplace.json: {type(exc).__name__}')

    shared_path = plugin_root / 'shared/native-plugins.md'
    shared_text = None
    if not shared_path.is_file():
        errors.append('Missing shared/native-plugins.md')
    else:
        shared_text = shared_path.read_text(encoding='utf-8-sig').replace('\r\n', '\n')

    skills_dir = plugin_root / 'skills'
    skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir()) if skills_dir.is_dir() else []
    if not skill_dirs:
        errors.append('No skill directories found under skills/')

    if sync_shared and shared_text is not None:
        for sdir in skill_dirs:
            target = sdir / 'references/native-plugins-data.md'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(shared_text, encoding='utf-8', newline='\n')

    bundle_validator = load_bundle_validator(plugin_root)
    if bundle_validator is None:
        errors.append('Cannot load skills/tauri-native-mobile/scripts/validate_bundle.py')
        return {'ok': False, 'checked_at': datetime.now(timezone.utc).isoformat(), 'skills_checked': [], 'errors': errors}

    for sdir in skill_dirs:
        sname = sdir.name
        skills_checked.append(sname)
        res = bundle_validator.validate(sdir, expected_name=sname)
        for err in res['errors']:
            errors.append(f'{sname}: {err}')

        local_data = sdir / 'references/native-plugins-data.md'
        if not local_data.is_file():
            errors.append(f'{sname}: missing standalone copy references/native-plugins-data.md')
        elif shared_text is not None:
            local_text = local_data.read_text(encoding='utf-8-sig').replace('\r\n', '\n')
            if local_text != shared_text:
                errors.append(f'{sname}: references/native-plugins-data.md differs from shared/native-plugins.md')

        skill_md = sdir / 'SKILL.md'
        if skill_md.is_file():
            desc = extract_frontmatter_description(skill_md.read_text(encoding='utf-8-sig'))
            if not desc.startswith('Use when '):
                errors.append(f'{sname}: SKILL.md description must start with "Use when "')
            if 'Tauri 2' not in desc:
                errors.append(f'{sname}: SKILL.md description should explicitly name "Tauri 2"')

        openai_yaml = sdir / 'agents/openai.yaml'
        if not openai_yaml.is_file():
            errors.append(f'{sname}: missing agents/openai.yaml')
        else:
            ytext = openai_yaml.read_text(encoding='utf-8-sig')
            for field in ('display_name:', 'short_description:', 'default_prompt:'):
                if field not in ytext:
                    errors.append(f'{sname}: agents/openai.yaml missing {field}')
            if f'${sname}' not in ytext:
                errors.append(f'{sname}: agents/openai.yaml default_prompt must reference ${sname}')

        for md_file in sorted(sdir.rglob('*.md')):
            rel = md_file.relative_to(plugin_root).as_posix()
            text = md_file.read_text(encoding='utf-8-sig')
            if re.search(r'\bthe backup(?:\'s|\b)', text, re.I):
                errors.append(f'{rel}: contains orphan reference to "the backup"')
            for block in re.findall(r'^ {0,3}```json[ \t]*\r?\n(.*?)^ {0,3}```[ \t]*$', text, re.M | re.S):
                try:
                    json.loads(block)
                except json.JSONDecodeError as exc:
                    errors.append(f'{rel}: invalid JSON code block ({exc.msg} at line {exc.lineno})')

    return {
        'ok': not errors,
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'skills_checked': skills_checked,
        'errors': errors,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description='Validate the Tauri plugin repository and all its skills.')
    parser.add_argument('path', nargs='?', default=str(ROOT), help='Plugin root directory.')
    parser.add_argument('--sync-shared', action='store_true', help='Copy shared/native-plugins.md into each skill before validating.')
    args = parser.parse_args(argv)

    result = validate_plugin(Path(args.path), sync_shared=args.sync_shared)
    print(json.dumps(result, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
