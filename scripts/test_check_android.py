"""Tests for skills/tauri-starter/scripts/check-android.mjs (skipped when node is missing)."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/tauri-starter/scripts/check-android.mjs'
NODE = shutil.which('node')


@unittest.skipUnless(NODE, 'node is not installed')
class CheckAndroidTests(unittest.TestCase):
    def run_check(self, **env):
        drop = {'ANDROID_HOME', 'ANDROID_SDK_ROOT', 'NDK_HOME'} | ({'PATH'} if 'PATH' in env else set())
        base = {k: v for k, v in os.environ.items() if k.upper() not in drop}
        res = subprocess.run([NODE, str(SCRIPT)], capture_output=True, text=True, encoding='utf-8', env={**base, **env})
        return res, json.loads(res.stdout)

    def test_names_every_missing_variable_and_stops(self):
        res, report = self.run_check()
        self.assertEqual(res.returncode, 1)
        self.assertIn('ANDROID_HOME', report['missing'])
        self.assertIn('NDK_HOME', report['missing'])
        self.assertFalse(report['ok'])

    def test_complete_sdk_tree_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            sdk, ndk = Path(tmp) / 'sdk', Path(tmp) / 'ndk'
            for rel in ('platforms/android-36', 'build-tools/36.0.0', 'platform-tools'):
                (sdk / rel).mkdir(parents=True)
            (sdk / 'platform-tools/adb.exe').write_bytes(b'')
            (sdk / 'platform-tools/adb').write_bytes(b'')
            ndk.mkdir()
            _, report = self.run_check(ANDROID_HOME=str(sdk), NDK_HOME=str(ndk))
            for item in ('ANDROID_HOME', 'NDK_HOME', 'SDK platform', 'SDK build-tools', 'adb'):
                self.assertNotIn(item, report['missing'])

    def test_java_home_is_accepted_when_java_is_not_on_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            jdk = Path(tmp) / 'jdk'
            (jdk / 'bin').mkdir(parents=True)
            for name in ('java', 'java.exe'):
                (jdk / 'bin' / name).write_bytes(b'')
            _, report = self.run_check(JAVA_HOME=str(jdk), PATH=tmp)
            self.assertNotIn('JDK', report['missing'])

    def test_missing_jdk_is_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, report = self.run_check(JAVA_HOME=tmp, PATH=tmp)
            self.assertIn('JDK', report['missing'])

    def test_empty_sdk_tree_names_platform_build_tools_and_adb(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, report = self.run_check(ANDROID_HOME=tmp, NDK_HOME=tmp)
            for item in ('SDK platform', 'SDK build-tools', 'adb'):
                self.assertIn(item, report['missing'])


if __name__ == '__main__':
    unittest.main()
