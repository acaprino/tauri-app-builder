#!/usr/bin/env node
// Copies the starter template into a target directory and substitutes four placeholders:
// {{PRODUCT_NAME}}, {{IDENTIFIER}}, {{CRATE_NAME}} and {{LIB_NAME}} (the crate name with "-" as "_" and a "_lib" suffix:
// a library named like the binary makes Cargo warn about clashing output files on Windows).
// Usage: node instantiate.mjs --mode <new|adapt> --target <dir> --name <product> --id <reverse-dns> --crate <kebab-case>
// Exit codes: 0 done, 2 invalid argument, 3 would overwrite something, 4 a placeholder remains.
// Nothing is written unless every check passes.
import { existsSync, mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';

const fail = (code, message) => {
  console.error(message);
  process.exit(code);
};

let args;
try {
  const options = Object.fromEntries(['mode', 'target', 'name', 'id', 'crate', 'assets'].map((k) => [k, { type: 'string' }]));
  args = parseArgs({ options }).values;
} catch (error) {
  fail(2, error.message);
}

const { mode, target, name, id, crate } = args;
if (mode !== 'new' && mode !== 'adapt') fail(2, '--mode must be "new" or "adapt"');
if (!target) fail(2, '--target is required');
// Tauri's config schema: productName must match ^[^/\\:*?"<>|]+$ (checked before any file is written).
if (!name || /[\u0000-\u001f\u007f/\\:*?"<>|]/.test(name)) fail(2, '--name must be non-empty, without control characters and without / \\ : * ? " < > |');
if (!/^[A-Za-z][A-Za-z0-9-]*(\.[A-Za-z][A-Za-z0-9-]*)+$/.test(id ?? '')) fail(2, '--id must be a reverse-DNS identifier such as com.example.app');
if (!/^[a-z][a-z0-9]*(-[a-z0-9]+)*$/.test(crate ?? '')) fail(2, '--crate must be lowercase kebab-case such as my-app');

const targetRoot = resolve(target);
if (existsSync(targetRoot) && !statSync(targetRoot).isDirectory()) fail(2, `--target is not a directory: ${targetRoot}`);

const assets = resolve(args.assets ?? join(dirname(fileURLToPath(import.meta.url)), '..', 'assets'));
const walk = (dir) => readdirSync(dir, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(join(dir, e.name)) : [join(dir, e.name)]));

// Template folder, and where it lands under the target.
const sources = [['core', 'src-tauri'], ...(mode === 'new' ? [['web', '']] : [])];
const plan = sources.flatMap(([folder, into]) => {
  const root = join(assets, folder);
  if (!existsSync(root)) fail(2, `template folder missing: ${root}`);
  return walk(root).map((file) => ({ file, dest: join(targetRoot, into, relative(root, file)) }));
});

if (existsSync(join(targetRoot, 'src-tauri'))) fail(3, `${join(targetRoot, 'src-tauri')} already exists; nothing was written`);
const clashes = plan.filter((p) => existsSync(p.dest));
if (clashes.length) fail(3, `would overwrite: ${clashes.map((p) => p.dest).join(', ')}; nothing was written`);

// Product names are escaped for the file type they land in; the other values are validated above.
const quoted = (s) => JSON.stringify(s).slice(1, -1);
const html = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const escapers = { '.json': quoted, '.toml': quoted, '.rs': quoted, '.ts': quoted, '.js': quoted, '.mjs': quoted, '.html': html };
const decoder = new TextDecoder('utf-8', { fatal: true });
const remaining = [];

const outputs = plan.map(({ file, dest }) => {
  const bytes = readFileSync(file);
  let text;
  try {
    text = bytes.includes(0) ? null : decoder.decode(bytes);
  } catch {
    text = null;
  }
  if (text === null) return { dest, data: bytes };
  const ext = file.slice(file.lastIndexOf('.'));
  const values = { PRODUCT_NAME: (escapers[ext] ?? ((s) => s))(name), IDENTIFIER: id, CRATE_NAME: crate, LIB_NAME: `${crate.replaceAll('-', '_')}_lib` };
  const data = text.replace(/\{\{([A-Z][A-Z0-9_]*)\}\}/g, (token, key) => {
    if (key in values) return values[key];
    remaining.push(`${relative(assets, file)}: ${token}`);
    return token;
  });
  return { dest, data };
});

if (remaining.length) fail(4, `placeholders left in the template: ${remaining.join(', ')}; nothing was written`);

for (const { dest, data } of outputs) {
  mkdirSync(dirname(dest), { recursive: true });
  writeFileSync(dest, data);
}
console.log(JSON.stringify({ written: outputs.map((o) => relative(targetRoot, o.dest).split(sep).join('/')) }));
