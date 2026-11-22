#!/usr/bin/env node
// Checks the Android toolchain the starter needs. It installs nothing: it prints one JSON line
// {"ok": boolean, "missing": [names]} and exits 1 when anything is missing, so the caller stops and tells the user.
import { existsSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

const isDir = (p) => Boolean(p) && existsSync(p) && statSync(p).isDirectory();
const hasEntry = (dir) => isDir(dir) && readdirSync(dir).length > 0;
const run = (cmd, args) => spawnSync(cmd, args, { encoding: 'utf8' });

const missing = [];

// A JDK is found through JAVA_HOME (what Gradle and Tauri use) or, failing that, on the PATH.
const javaHome = process.env.JAVA_HOME;
const javaInHome = isDir(javaHome) && ['java', 'java.exe'].some((f) => existsSync(join(javaHome, 'bin', f)));
if (!javaInHome && run('java', ['-version']).status !== 0) missing.push('JDK');

const sdk = process.env.ANDROID_HOME;
if (!isDir(sdk)) {
  missing.push('ANDROID_HOME');
} else {
  if (!hasEntry(join(sdk, 'platforms'))) missing.push('SDK platform');
  if (!hasEntry(join(sdk, 'build-tools'))) missing.push('SDK build-tools');
  if (!['adb', 'adb.exe'].some((f) => existsSync(join(sdk, 'platform-tools', f)))) missing.push('adb');
}

// A real NDK folder holds source.properties; an empty or wrong folder is not an NDK.
if (!isDir(process.env.NDK_HOME) || !existsSync(join(process.env.NDK_HOME, 'source.properties'))) missing.push('NDK_HOME');

const rustup = run('rustup', ['target', 'list', '--installed']);
if (rustup.error || rustup.status !== 0) {
  missing.push('rustup');
} else {
  for (const target of ['aarch64-linux-android', 'x86_64-linux-android']) {
    if (!rustup.stdout.split(/\s+/).includes(target)) missing.push(`Rust target ${target}`);
  }
}

console.log(JSON.stringify({ ok: missing.length === 0, missing }));
process.exit(missing.length === 0 ? 0 : 1);
