"""Portable-bundle regressions using isolated, anonymous fixtures."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('validate_bundle.py')

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

    def run_validator(self):
        result = subprocess.run([sys.executable, str(self.root / 'scripts/validate_bundle.py')], capture_output=True, text=True, encoding='utf-8')
        report = json.loads((self.root / 'audit/validation.json').read_text(encoding='utf-8'))
        return result, report

    def assert_invalid(self, expected):
        result, report = self.run_validator()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertFalse(report['ok'], result.stderr)
        self.assertNotIn('stale', report)
        self.assertTrue(any(expected in error for error in report['errors']), report)
        self.assertNotIn('Traceback', result.stderr)

    def test_valid_bundle_needs_no_external_archive(self):
        result, report = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(report['ok'])
        self.assertEqual(report['preserved_sources_checked'], 1)
        self.assertEqual(report['local_links_checked'], 2)

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
