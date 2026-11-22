"""Tests for skills/tauri-starter/scripts/instantiate.mjs (skipped when node is missing)."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / 'skills/tauri-starter/scripts/instantiate.mjs'
NODE = shutil.which('node')
BINARY = bytes([0x00, 0xFF, 0xFE]) + b'{{PRODUCT_NAME}}' + bytes([0x89, 0x00])

CARGO = '[package]\nname = "{{CRATE_NAME}}"\nversion = "0.1.0"\ndescription = "{{PRODUCT_NAME}}"\n\n[lib]\nname = "{{LIB_NAME}}"\n'
CONF = '{\n  "productName": "{{PRODUCT_NAME}}",\n  "identifier": "{{IDENTIFIER}}"\n}\n'
LIB = 'pub const NAME: &str = "{{PRODUCT_NAME}}";\n'
HTML = '<title>{{PRODUCT_NAME}}</title>\n'


@unittest.skipUnless(NODE, 'node is not installed')
class InstantiateTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.assets = self.tmp / 'assets'
        self.put('assets/core/Cargo.toml', CARGO)
        self.put('assets/core/tauri.conf.json', CONF)
        self.put('assets/core/src/lib.rs', LIB)
        self.put('assets/core/icons/icon.bin', BINARY)
        self.put('assets/web/index.html', HTML)

    def put(self, rel, content):
        path = self.tmp / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode('utf-8'))

    def run_script(self, target, mode='new', name='My App', ident='com.example.myapp', crate='my-app'):
        cmd = [NODE, str(SCRIPT), '--mode', mode, '--target', str(target), '--name', name,
               '--id', ident, '--crate', crate, '--assets', str(self.assets)]
        return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

    def snapshot(self, root):
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(Path(root).rglob('*')) if p.is_file()}

    def test_substitutes_all_four_tokens(self):
        target = self.tmp / 'app'
        res = self.run_script(target)
        self.assertEqual(res.returncode, 0, res.stderr)
        cargo = tomllib.loads((target / 'src-tauri/Cargo.toml').read_text(encoding='utf-8'))
        self.assertEqual(cargo['package']['name'], 'my-app')
        self.assertEqual(cargo['lib']['name'], 'my_app_lib')  # the suffix avoids a Windows output-name clash with the binary
        conf = json.loads((target / 'src-tauri/tauri.conf.json').read_text(encoding='utf-8'))
        self.assertEqual(conf, {'productName': 'My App', 'identifier': 'com.example.myapp'})
        self.assertEqual((target / 'index.html').read_text(encoding='utf-8'), '<title>My App</title>\n')
        written = json.loads(res.stdout.strip().splitlines()[-1])['written']
        self.assertIn('src-tauri/Cargo.toml', written)
        self.assertIn('index.html', written)

    def test_adapt_mode_writes_only_src_tauri(self):
        target = self.tmp / 'host'
        res = self.run_script(target, mode='adapt')
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertTrue((target / 'src-tauri/Cargo.toml').is_file())
        self.assertFalse((target / 'index.html').exists())

    def test_binary_files_are_copied_unchanged(self):
        target = self.tmp / 'app'
        self.assertEqual(self.run_script(target).returncode, 0)
        self.assertEqual((target / 'src-tauri/icons/icon.bin').read_bytes(), BINARY)

    def test_refuses_existing_src_tauri(self):
        target = self.tmp / 'app'
        self.put('app/src-tauri/keep.txt', 'mine')
        before = self.snapshot(target)
        res = self.run_script(target)
        self.assertEqual(res.returncode, 3, res.stderr)
        self.assertEqual(self.snapshot(target), before)

    def test_never_overwrites_an_existing_file(self):
        target = self.tmp / 'app'
        self.put('app/index.html', 'mine')
        before = self.snapshot(target)
        res = self.run_script(target)
        self.assertEqual(res.returncode, 3, res.stderr)
        self.assertEqual(self.snapshot(target), before)

    def test_target_path_with_space_works(self):
        target = self.tmp / 'my project dir'
        res = self.run_script(target)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertTrue((target / 'src-tauri/Cargo.toml').is_file())

    def test_special_characters_survive_json_toml_and_rust(self):
        target = self.tmp / 'app'
        name = 'Café & "Muro"'
        res = self.run_script(target, name=name)
        self.assertEqual(res.returncode, 0, res.stderr)
        conf = json.loads((target / 'src-tauri/tauri.conf.json').read_text(encoding='utf-8'))
        self.assertEqual(conf['productName'], name)
        cargo = tomllib.loads((target / 'src-tauri/Cargo.toml').read_text(encoding='utf-8'))
        self.assertEqual(cargo['package']['description'], name)
        self.assertEqual((target / 'src-tauri/src/lib.rs').read_text(encoding='utf-8'),
                         'pub const NAME: &str = "Café & \\"Muro\\"";\n')
        self.assertEqual((target / 'index.html').read_text(encoding='utf-8'),
                         '<title>Café &amp; &quot;Muro&quot;</title>\n')

    def test_rejects_invalid_arguments_before_writing(self):
        cases = [{'crate': 'My_Crate'}, {'ident': 'com..x'}, {'ident': 'nodots'}, {'name': ''}, {'mode': 'other'}]
        for kwargs in cases:
            target = self.tmp / 'bad'
            res = self.run_script(target, **kwargs)
            self.assertEqual(res.returncode, 2, f'{kwargs}: {res.stderr}')
            self.assertFalse(target.exists(), kwargs)

    def test_fails_when_a_token_remains(self):
        target = self.tmp / 'app'
        self.put('assets/core/src/typo.rs', 'const X: &str = "{{TYPO}}";\n')
        res = self.run_script(target)
        self.assertEqual(res.returncode, 4, res.stderr)
        self.assertFalse((target / 'src-tauri').exists())


if __name__ == '__main__':
    unittest.main()
