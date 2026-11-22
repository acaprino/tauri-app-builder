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
            found |= set(re.findall(r'\{\{\s*([A-Za-z][A-Za-z0-9_-]*)\s*\}\}', data.decode('utf-8', errors='ignore')))
        self.assertTrue(found, 'the template uses no placeholder at all')
        self.assertLessEqual(found, TOKENS)

    def test_csp_is_not_null(self):
        csp = load_json('tauri.conf.json')['app']['security']['csp']
        self.assertIsInstance(csp, str)
        self.assertIn('default-src', csp)

    def test_connect_src_allows_the_apps_own_origin(self):
        # an explicit connect-src replaces default-src, so without 'self' a packaged app cannot fetch its own files
        security = load_json('tauri.conf.json')['app']['security']
        for key in ('csp', 'devCsp'):
            directive = next(d for d in security[key].split(';') if d.strip().startswith('connect-src'))
            self.assertIn("'self'", directive, key)

    def test_rust_version_matches_the_crates_floor(self):
        cargo = tomllib.loads((CORE / 'Cargo.toml').read_text(encoding='utf-8'))
        major, minor, *_ = (int(x) for x in cargo['package']['rust-version'].split('.'))
        self.assertGreaterEqual((major, minor), (1, 90))  # tauri 2.12 and its plugins declare rust 1.90

    def test_capability_files_are_json_and_platform_scoped(self):
        desktop = load_json('capabilities/desktop.json')
        mobile = load_json('capabilities/mobile.json')
        desktop_platforms = {p.lower() for p in desktop['platforms']}
        mobile_platforms = {p.lower() for p in mobile['platforms']}
        self.assertIn('windows', desktop_platforms)
        self.assertIn('android', mobile_platforms)
        self.assertEqual(desktop_platforms & mobile_platforms, set())

    def test_opener_is_granted_for_one_scoped_url_only(self):
        for rel in ('capabilities/desktop.json', 'capabilities/mobile.json'):
            permissions = load_json(rel)['permissions']
            self.assertNotIn('opener:default', permissions, rel)
            scoped = [p for p in permissions if isinstance(p, dict) and p['identifier'] == 'opener:allow-open-url']
            self.assertEqual(len(scoped), 1, rel)
            self.assertTrue(scoped[0]['allow'], rel)

    def test_desktop_plugins_only_in_target_dependencies(self):
        cargo = tomllib.loads((CORE / 'Cargo.toml').read_text(encoding='utf-8'))
        self.assertFalse(DESKTOP_ONLY_CRATES & set(cargo['dependencies']))
        desktop_tables = [t['dependencies'] for key, t in cargo['target'].items() if 'android' in key and 'not' in key]
        self.assertEqual(len(desktop_tables), 1)
        self.assertLessEqual(DESKTOP_ONLY_CRATES, set(desktop_tables[0]))

    def test_webview2_recovery_is_windows_only_and_handles_process_failures(self):
        cargo = tomllib.loads((CORE / 'Cargo.toml').read_text(encoding='utf-8'))
        self.assertNotIn('webview2-com', cargo['dependencies'])
        windows_tables = [t['dependencies'] for key, t in cargo['target'].items() if key.replace(' ', '') == 'cfg(windows)']
        self.assertEqual(len(windows_tables), 1)
        self.assertIn('webview2-com', windows_tables[0])
        recovery = (CORE / 'src/recovery.rs').read_text(encoding='utf-8')
        for needle in ('add_ProcessFailed', 'request_restart', '#[cfg(test)]'):
            self.assertIn(needle, recovery)
        lib = (CORE / 'src/lib.rs').read_text(encoding='utf-8')
        self.assertIn('#[cfg(windows)]\nmod recovery;', lib)
        self.assertIn('recovery::install', lib)

    def test_lib_exposes_the_mobile_entry_point(self):
        lib = (CORE / 'src/lib.rs').read_text(encoding='utf-8')
        self.assertIn('#[cfg_attr(mobile, tauri::mobile_entry_point)]', lib)
        self.assertRegex(lib, r'pub fn run\(\)')
        self.assertIn('{{LIB_NAME}}::run()', (CORE / 'src/main.rs').read_text(encoding='utf-8'))

    def test_no_md_in_assets(self):
        self.assertEqual(list(ASSETS.rglob('*.md')), [])

    def test_no_generated_android_project(self):
        self.assertEqual([p for p in ASSETS.rglob('gen') if p.is_dir()], [])


class WebTemplateTests(unittest.TestCase):
    def test_tsconfig_leaves_the_vite_config_out(self):
        # vite.config.ts reads process.env; type-checking it would need @types/node, which the page does not use.
        tsconfig = json.loads((ASSETS / 'web/tsconfig.json').read_text(encoding='utf-8'))
        self.assertEqual(tsconfig['include'], ['src'])

    def test_new_apps_ignore_node_modules_and_dist(self):
        lines = (ASSETS / 'web/.gitignore').read_text(encoding='utf-8').split()
        self.assertIn('node_modules', lines)
        self.assertIn('dist', lines)


if __name__ == '__main__':
    unittest.main()
