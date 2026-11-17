"""Regression tests for repository-level plugin validation and shared-data sync."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import types
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_SCRIPT = REPO_ROOT / 'skills/tauri-native-mobile/scripts/validate_bundle.py'
PLUGIN_SCRIPT = Path(__file__).with_name('validate_plugin.py')
_SPEC = importlib.util.spec_from_file_location('validate_plugin_under_test', PLUGIN_SCRIPT)
VALIDATE_PLUGIN = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(VALIDATE_PLUGIN)


class PluginValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / '.claude-plugin').mkdir(parents=True)
        (self.root / 'shared').mkdir(parents=True)
        (self.root / 'scripts').mkdir(parents=True)
        if PLUGIN_SCRIPT.exists():
            shutil.copy2(PLUGIN_SCRIPT, self.root / 'scripts/validate_plugin.py')

        self.write_json('.claude-plugin/plugin.json', {
            'name': 'tauri-app-builder',
            'version': '1.1.0',
            'description': 'Build, audit and ship Tauri 2 apps.',
            'license': 'MIT',
        })
        self.write_json('.claude-plugin/marketplace.json', {
            'name': 'tauri-app-builder',
            'description': 'Skills for Tauri 2 apps.',
            'owner': {'name': 'tester'},
            'plugins': [{'name': 'tauri-app-builder', 'source': './', 'description': 'Skills for Tauri 2 apps.'}],
        })
        (self.root / '.claude-plugin/icon.png').write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 32)
        self.write('README.md', '# Plugin\n' + (' word' * 45) + '\n')
        self.write('shared/native-plugins.md', '# Shared native plugins\nCanonical table.\n')

        for skill_name in ('tauri-native-desktop', 'tauri-native-mobile'):
            sdir = self.root / 'skills' / skill_name
            (sdir / 'references').mkdir(parents=True)
            (sdir / 'agents').mkdir(parents=True)
            if skill_name == 'tauri-native-mobile':
                (sdir / 'scripts').mkdir(parents=True)
                shutil.copy2(BUNDLE_SCRIPT, sdir / 'scripts/validate_bundle.py')
            self.write(
                f'skills/{skill_name}/SKILL.md',
                f'---\nname: {skill_name}\ndescription: "Use when building or auditing Tauri 2 {skill_name} apps."\n---\n'
                f'# {skill_name}\nRead [data](references/native-plugins-data.md).\n',
            )
            self.write(f'skills/{skill_name}/references/native-plugins-data.md', '# Shared native plugins\nCanonical table.\n')
            self.write(
                f'skills/{skill_name}/agents/openai.yaml',
                f'interface:\n  display_name: "{skill_name}"\n  short_description: "Tauri 2 helper"\n  default_prompt: "Use ${skill_name} on this app."\n',
            )

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline='\n')

    def write_json(self, rel, obj):
        self.write(rel, json.dumps(obj, indent=2) + '\n')

    def run_plugin_validator(self, *args):
        out_buf, err_buf = io.StringIO(), io.StringIO()
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            rc = VALIDATE_PLUGIN.main([str(self.root), *args])
        stdout, stderr = out_buf.getvalue(), err_buf.getvalue()
        result = types.SimpleNamespace(returncode=rc, stdout=stdout, stderr=stderr)
        report = json.loads(stdout) if stdout.strip().startswith('{') else None
        return result, report

    def test_valid_dual_skill_plugin_passes(self):
        result, report = self.run_plugin_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report['ok'], report)
        self.assertEqual(sorted(report['skills_checked']), ['tauri-native-desktop', 'tauri-native-mobile'])

    def test_missing_openai_yaml_is_rejected(self):
        (self.root / 'skills/tauri-native-mobile/agents/openai.yaml').unlink()
        result, report = self.run_plugin_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any('openai.yaml' in e for e in report['errors']), report)

    def test_description_not_starting_with_use_when_is_rejected(self):
        self.write(
            'skills/tauri-native-mobile/SKILL.md',
            '---\nname: tauri-native-mobile\ndescription: "Build and debug Tauri 2 mobile apps."\n---\n# Mobile\nRead [data](references/native-plugins-data.md).\n',
        )
        result, report = self.run_plugin_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any('Use when' in e for e in report['errors']), report)

    def test_orphan_backup_phrase_is_rejected(self):
        self.write('skills/tauri-native-mobile/references/extra.md', "# Note\nThe backup's claim was wrong.\n")
        result, report = self.run_plugin_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(any('backup' in e.lower() for e in report['errors']), report)

    def test_sync_shared_updates_skill_copies(self):
        self.write('shared/native-plugins.md', '# Shared native plugins\nUpdated v2 table.\n')
        drift_res, drift_rep = self.run_plugin_validator()
        self.assertNotEqual(drift_res.returncode, 0)
        self.assertTrue(any('native-plugins' in e for e in drift_rep['errors']), drift_rep)

        sync_res, sync_rep = self.run_plugin_validator('--sync-shared')
        self.assertEqual(sync_res.returncode, 0, sync_res.stdout + sync_res.stderr)
        self.assertTrue(sync_rep['ok'], sync_rep)
        for skill_name in ('tauri-native-desktop', 'tauri-native-mobile'):
            self.assertEqual(
                (self.root / f'skills/{skill_name}/references/native-plugins-data.md').read_text(encoding='utf-8'),
                '# Shared native plugins\nUpdated v2 table.\n',
            )


if __name__ == '__main__':
    unittest.main()
