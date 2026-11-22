"""Static checks of skills/tauri-starter/assets (the template cannot be built until it is instantiated)."""
import json
from pathlib import Path
import re
import tomllib
import unittest

ASSETS = Path(__file__).resolve().parents[1] / 'skills/tauri-starter/assets'
CORE = ASSETS / 'core'
TOKENS = {'PRODUCT_NAME', 'IDENTIFIER', 'CRATE_NAME', 'LIB_NAME'}
DESKTOP_ONLY_CRATES = {'tauri-plugin-window-state', 'tauri-plugin-single-instance'}


def load_json(rel):
    return json.loads((CORE / rel).read_text(encoding='utf-8'))


class CoreTemplateTests(unittest.TestCase):
    def test_only_allowed_tokens(self):
        found = set()
        for path in ASSETS.rglob('*'):
            data = path.read_bytes() if path.is_file() else b''
            if b'\x00' in data:
                continue
            found |= set(re.findall(r'\{\{([A-Z][A-Z0-9_]*)\}\}', data.decode('utf-8', errors='ignore')))
        self.assertTrue(found, 'the template uses no placeholder at all')
        self.assertLessEqual(found, TOKENS)

    def test_csp_is_not_null(self):
        csp = load_json('tauri.conf.json')['app']['security']['csp']
        self.assertIsInstance(csp, str)
        self.assertIn('default-src', csp)

    def test_capability_files_are_json_and_platform_scoped(self):
        desktop = load_json('capabilities/desktop.json')
        mobile = load_json('capabilities/mobile.json')
        desktop_platforms = {p.lower() for p in desktop['platforms']}
        mobile_platforms = {p.lower() for p in mobile['platforms']}
        self.assertIn('windows', desktop_platforms)
        self.assertIn('android', mobile_platforms)
        self.assertEqual(desktop_platforms & mobile_platforms, set())

    def test_desktop_plugins_only_in_target_dependencies(self):
        cargo = tomllib.loads((CORE / 'Cargo.toml').read_text(encoding='utf-8'))
        self.assertFalse(DESKTOP_ONLY_CRATES & set(cargo['dependencies']))
        desktop_tables = [t['dependencies'] for key, t in cargo['target'].items() if 'android' in key and 'not' in key]
        self.assertEqual(len(desktop_tables), 1)
        self.assertLessEqual(DESKTOP_ONLY_CRATES, set(desktop_tables[0]))

    def test_lib_exposes_the_mobile_entry_point(self):
        lib = (CORE / 'src/lib.rs').read_text(encoding='utf-8')
        self.assertIn('#[cfg_attr(mobile, tauri::mobile_entry_point)]', lib)
        self.assertRegex(lib, r'pub fn run\(\)')
        self.assertIn('{{LIB_NAME}}::run()', (CORE / 'src/main.rs').read_text(encoding='utf-8'))

    def test_no_md_in_assets(self):
        self.assertEqual(list(ASSETS.rglob('*.md')), [])

    def test_no_generated_android_project(self):
        self.assertEqual([p for p in ASSETS.rglob('gen') if p.is_dir()], [])


if __name__ == '__main__':
    unittest.main()
