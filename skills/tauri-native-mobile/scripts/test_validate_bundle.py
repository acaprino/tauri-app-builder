"""Portable-bundle regressions using isolated, anonymous fixtures."""
import hashlib
import importlib.util
import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import types
import unittest

SCRIPT = Path(__file__).with_name('validate_bundle.py')
_SPEC = importlib.util.spec_from_file_location('validate_bundle_under_test', SCRIPT)
VALIDATE_BUNDLE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(VALIDATE_BUNDLE)

class BundleValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for directory in ('scripts', 'references', 'audit', 'examples'):
            (self.root / directory).mkdir(parents=True)
        shutil.copy2(SCRIPT, self.root / 'scripts/validate_bundle.py')
        self.write('SKILL.md', '---\nname: tauri-native-mobile\ndescription: Useful mobile guidance\n---\n# Guide\nRead [camera](references/camera.md).\n')
        self.write('references/camera.md', '# Camera\nUse [the example](../examples/capture.txt).\n')
        self.write('audit/REVIEW.md', '# Review\nStructural checks only.\n')
        self.write('examples/capture.txt', 'Capture ownership example\n')
        self.write_json('audit/source-manifest.json', {'files': [self.entry('examples/capture.txt')]})
        self.write_json('audit/validation.json', {'ok': True, 'stale': True})

    def write(self, path, value):
        (self.root / path).write_text(value, encoding='utf-8')

    def write_json(self, path, value):
        self.write(path, json.dumps(value))

    def entry(self, path):
        return {'copy': path, 'sha256': hashlib.sha256((self.root / path).read_bytes()).hexdigest()}

    def run_validator(self, *extra_args, target=None, cli=False):
        target_dir = str(target if target is not None else self.root)
        if cli:
            cmd = [sys.executable, str(self.root / 'scripts/validate_bundle.py'), target_dir, *extra_args]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            report = json.loads(result.stdout) if result.stdout.strip().startswith('{') else None
            return result, report
        out_buf, err_buf = io.StringIO(), io.StringIO()
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            rc = VALIDATE_BUNDLE.main([target_dir, *extra_args])
        stdout, stderr = out_buf.getvalue(), err_buf.getvalue()
        result = types.SimpleNamespace(returncode=rc, stdout=stdout, stderr=stderr)
        report = json.loads(stdout) if stdout.strip().startswith('{') else None
        return result, report

    def assert_invalid(self, expected):
        result, _ = self.run_validator('--write')
        report = json.loads((self.root / 'audit/validation.json').read_text(encoding='utf-8'))
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertFalse(report['ok'], result.stderr)
        self.assertNotIn('stale', report)
        self.assertTrue(any(expected in error for error in report['errors']), report)
        self.assertNotIn('Traceback', result.stderr)

    def test_valid_bundle_needs_no_external_archive(self):
        result, report = self.run_validator(cli=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNotNone(report)
        self.assertTrue(report['ok'])
        self.assertEqual(report['preserved_sources_checked'], 1)
        self.assertEqual(report['local_links_checked'], 2)

    def test_default_run_is_read_only_and_leaves_validation_json_untouched(self):
        result, report = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(report['ok'])
        disk_report = json.loads((self.root / 'audit/validation.json').read_text(encoding='utf-8'))
        self.assertTrue(disk_report.get('stale'), 'Default check mode must not mutate audit/validation.json')

    def test_default_run_succeeds_when_validation_json_is_read_only(self):
        validation_file = self.root / 'audit/validation.json'
        os.chmod(validation_file, stat.S_IREAD)
        self.addCleanup(lambda: os.chmod(validation_file, stat.S_IWRITE | stat.S_IREAD))
        result, report = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(report['ok'], report)

    def test_code_fence_indexing_call_is_not_treated_as_markdown_link(self):
        self.write('references/camera.md', '# Camera\n```ts\nhandlers[0](event);\n```\nUse [the example](../examples/capture.txt).\n')
        result, report = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(report['ok'], report)

    def test_crlf_example_matches_lf_manifest_hash(self):
        lf_bytes = b'Capture ownership example\n'
        self.write_json('audit/source-manifest.json', {'files': [{'copy': 'examples/capture.txt', 'sha256': hashlib.sha256(lf_bytes).hexdigest()}]})
        (self.root / 'examples/capture.txt').write_bytes(b'Capture ownership example\r\n')
        result, report = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(report['ok'], report)

    def test_backtick_relative_escape_outside_bundle_is_rejected(self):
        self.write('references/camera.md', '# Camera\nSee `../../shared/native-plugins.md` and [example](../examples/capture.txt).\n')
        self.assert_invalid('outside bundle')

    def test_validates_other_skill_directory_and_enforces_skills_folder_name(self):
        plugin_root = self.root / 'plugin'
        desktop = plugin_root / 'skills/tauri-native-desktop'
        (desktop / 'references').mkdir(parents=True)
        (desktop / 'SKILL.md').write_text(
            '---\nname: tauri-native-desktop\ndescription: "Use when auditing Tauri 2 desktop behavior."\n---\n# Desktop\nRead [guide](references/guide.md).\n',
            encoding='utf-8',
        )
        (desktop / 'references/guide.md').write_text('# Guide\nDetails [Tauri docs].\n\nSee [sources](sources.md).\n', encoding='utf-8')
        (desktop / 'references/sources.md').write_text('# Sources\n\n## guide.md\n\n- Tauri docs: https://v2.tauri.app/\n', encoding='utf-8')
        result, report = self.run_validator(target=desktop)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(report['ok'], report)

        (desktop / 'SKILL.md').write_text(
            '---\nname: wrong-name\ndescription: "Use when auditing Tauri 2 desktop behavior."\n---\n# Desktop\nRead [guide](references/guide.md).\n',
            encoding='utf-8',
        )
        bad_result, bad_report = self.run_validator(target=desktop)
        self.assertNotEqual(bad_result.returncode, 0)
        self.assertTrue(any('name' in e for e in bad_report['errors']), bad_report)

    def test_missing_or_unused_bracketed_source_in_sectioned_sources_md_is_rejected(self):
        plugin_root = self.root / 'plugin2'
        desktop = plugin_root / 'skills/tauri-native-desktop'
        (desktop / 'references').mkdir(parents=True)
        (desktop / 'SKILL.md').write_text(
            '---\nname: tauri-native-desktop\ndescription: "Use when auditing Tauri 2 desktop behavior."\n---\n# Desktop\nRead [guide](references/guide.md).\n',
            encoding='utf-8',
        )
        (desktop / 'references/guide.md').write_text('# Guide\nCite [Missing Ref]. See [sources](sources.md).\n', encoding='utf-8')
        (desktop / 'references/sources.md').write_text('# Sources\n\n## guide.md\n\n- Unused Ref: https://v2.tauri.app/\n', encoding='utf-8')
        result, report = self.run_validator(target=desktop)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any('Missing source' in e for e in report['errors']), report)
        self.assertTrue(any('Unused source' in e for e in report['errors']), report)

    def test_citations_in_reference_without_sources_section_is_rejected(self):
        plugin_root = self.root / 'plugin2b'
        desktop = plugin_root / 'skills/tauri-native-desktop'
        (desktop / 'references').mkdir(parents=True)
        (desktop / 'SKILL.md').write_text(
            '---\nname: tauri-native-desktop\ndescription: "Use when auditing Tauri 2 desktop behavior."\n---\n# Desktop\nRead [guide](references/guide.md) and [extra](references/extra.md).\n',
            encoding='utf-8',
        )
        (desktop / 'references/guide.md').write_text('# Guide\nCite [Tauri docs]. See [sources](sources.md).\n', encoding='utf-8')
        (desktop / 'references/extra.md').write_text('# Extra\nCite [Unlisted Section Source].\n', encoding='utf-8')
        (desktop / 'references/sources.md').write_text('# Sources\n\n## guide.md\n\n- Tauri docs: https://v2.tauri.app/\n', encoding='utf-8')
        result, report = self.run_validator(target=desktop)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any('Unlisted Section Source' in e for e in report['errors']), report)

    def test_shared_native_plugins_drift_is_rejected(self):
        plugin_root = self.root / 'plugin3'
        shared = plugin_root / 'shared'
        skill_dir = plugin_root / 'skills/tauri-native-desktop'
        (skill_dir / 'references').mkdir(parents=True)
        shared.mkdir(parents=True)
        (shared / 'native-plugins.md').write_text('# Canonical\nVersion A\n', encoding='utf-8')
        (skill_dir / 'references/native-plugins-data.md').write_text('# Canonical\nVersion B\n', encoding='utf-8')
        (skill_dir / 'SKILL.md').write_text(
            '---\nname: tauri-native-desktop\ndescription: "Use when auditing Tauri 2 desktop behavior."\n---\n# Desktop\nRead [data](references/native-plugins-data.md).\n',
            encoding='utf-8',
        )
        result, report = self.run_validator(target=skill_dir)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any('native-plugins' in e for e in report['errors']), report)

    def test_empty_description_is_rejected(self):
        self.write('SKILL.md', '---\nname: tauri-native-mobile\ndescription:\n---\n# Body\n')
        self.assert_invalid('frontmatter')

    def test_empty_name_is_rejected(self):
        self.write('SKILL.md', '---\nname:\ndescription: Useful\n---\n# Body\n')
        self.assert_invalid('frontmatter')

    def test_empty_body_is_rejected(self):
        self.write('SKILL.md', '---\nname: tauri-native-mobile\ndescription: Useful\n---\n')
        self.assert_invalid('body')

    def test_unclosed_frontmatter_is_rejected(self):
        self.write('SKILL.md', '---\nname: tauri-native-mobile\ndescription: Useful\n')
        self.assert_invalid('frontmatter')

    def test_empty_reference_is_rejected(self):
        self.write('references/camera.md', '  \n')
        self.assert_invalid('Empty Markdown')

    def test_empty_linked_markdown_outside_references_is_rejected(self):
        self.write('examples/extra.md', '\n')
        self.write('references/camera.md', '[extra](../examples/extra.md)\n')
        self.assert_invalid('Empty Markdown')

    def test_missing_entrypoint_replaces_old_success(self):
        (self.root / 'SKILL.md').unlink()
        self.assert_invalid('SKILL.md')

    def test_missing_example_replaces_old_success(self):
        (self.root / 'examples/capture.txt').unlink()
        self.assert_invalid('capture.txt')

    def test_changed_example_is_rejected(self):
        self.write('examples/capture.txt', 'Changed')
        self.assert_invalid('hash mismatch')

    def test_missing_manifest_replaces_old_success(self):
        (self.root / 'audit/source-manifest.json').unlink()
        self.assert_invalid('source-manifest.json')

    def test_corrupt_manifest_replaces_old_success(self):
        self.write('audit/source-manifest.json', '{')
        self.assert_invalid('manifest')

    def test_invalid_manifest_schema_is_rejected(self):
        self.write_json('audit/source-manifest.json', {'files': [None]})
        self.assert_invalid('manifest entry')

    def test_external_copy_is_rejected(self):
        self.write_json('audit/source-manifest.json', {'files': [{'copy': '../outside.txt', 'sha256': '0' * 64}]})
        self.assert_invalid('outside bundle')

    def test_absolute_copy_is_rejected(self):
        self.write_json('audit/source-manifest.json', {'files': [{'copy': str(self.root / 'examples/capture.txt'), 'sha256': '0' * 64}]})
        self.assert_invalid('relative')

    def test_external_link_is_rejected(self):
        self.write('references/camera.md', '[outside](../../outside.md)\n')
        self.assert_invalid('outside bundle')

    def test_broken_link_is_rejected(self):
        self.write('references/camera.md', '[missing](missing.md)\n')
        self.assert_invalid('Missing link')

    def test_invalid_utf8_replaces_old_success(self):
        (self.root / 'references/camera.md').write_bytes(b'\xff')
        self.assert_invalid('Cannot read')

    def test_malformed_hash_is_rejected(self):
        self.write_json('audit/source-manifest.json', {'files': [{'copy': 'examples/capture.txt', 'sha256': 'bad'}]})
        self.assert_invalid('manifest entry')

    def test_quoted_whitespace_description_is_rejected(self):
        self.write('SKILL.md', '---\nname: tauri-native-mobile\ndescription: "  "\n---\n# Body\n')
        self.assert_invalid('frontmatter')

    def test_invalid_path_replaces_old_success(self):
        self.write_json('audit/source-manifest.json', {'files': [{'copy': 'bad\x00path', 'sha256': '0' * 64}]})
        self.assert_invalid('Invalid relative path')

    def test_missing_files_array_is_rejected(self):
        self.write_json('audit/source-manifest.json', {})
        self.assert_invalid('files must be an array')

    def test_duplicate_evidence_is_rejected(self):
        entry = self.entry('examples/capture.txt')
        self.write_json('audit/source-manifest.json', {'files': [entry, entry]})
        self.assert_invalid('Duplicate manifest entry')

if __name__ == '__main__':
    unittest.main()
