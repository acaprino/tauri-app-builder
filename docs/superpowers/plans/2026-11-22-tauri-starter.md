# tauri-starter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a third skill, `tauri-starter`, that starts a new Tauri 2 app or wraps an existing web app, for Windows and Android, from one shared `src-tauri` core, verified by running it.

**Architecture:** One template (`assets/core` is the `src-tauri` overlay for both paths, `assets/web` is the frontend for the new-app path only). A dependency-free Node script copies the template and substitutes four placeholders. Everything else is procedure prose in `SKILL.md` and `references/`, and is tested by following it literally in `D:\tmp\starter-check`, never inside the repository.

**Tech Stack:** Tauri 2.12.x crates, `@tauri-apps/cli` per project, Vite with plain TypeScript, Node 24 (`instantiate.mjs`), Python 3.13 `unittest` (plugin tests), PowerShell (verification shell), Android SDK/NDK on D:.

**Spec:** `docs/superpowers/specs/2026-11-22-tauri-starter-design.md` (read it with this plan; the "Left to the builder" list there is genuinely the implementer's to decide).

## Global Constraints

- The skills' reference snapshot is tauri 2.12.5 (`tauri-native-desktop/references/guide.md`); Tauri 3.x is not covered.
- The starter pins the CLI per project as an npm dev dependency (`npm run tauri -- ...`); the global `tauri-cli 2.10.1` is left alone.
- `SKILL.md` frontmatter: `name` equals the directory, `description` starts with "Use when ", names "Tauri 2", is at most 1024 characters.
- `agents/openai.yaml` with `display_name:`, `short_description:`, `default_prompt:`; the prompt references `$tauri-starter`.
- `references/native-plugins-data.md` must equal `shared/native-plugins.md` (use `--sync-shared`).
- Links and inline `../` paths stay inside the skill; sibling skills are named in prose, never linked.
- No `examples/` or `audit/` in the skill. No `.md` files in `assets/`. No placeholders, comments or ellipses in json fences.
- No visual layer, no UI framework in the new path. System title bar stays the default.
- Core items are only those in the spec's table; desktop-only plugins sit behind `cfg(desktop)` and target-specific dependencies.
- Never build inside `assets/`. Work in a short path outside the repository (`D:\tmp\starter-check\...`).
- All new toolchain, caches, `CARGO_HOME` and verification projects go to D:. Variables are set only per shell by `D:\tmp\starter-check\env.ps1`, not persistently. The existing `.cargo` is left untouched.
- A step stops when D: has under 10 GB free or C: under 500 MB.
- The emulator is the default and the required Android run target; the phone is an extra check, never a substitute.
- Work on branch `feat/tauri-starter`. Nothing is committed on `main`; every commit step runs only with the author's OK. Leave `dialoghi-wireframe.html` alone.

## Review Focus

1. **Target already holds a `src-tauri/`** (or the path has spaces or non-ASCII): instantiate must refuse without overwriting, and work on a path with a space. Pinned in Task 2.
2. **Product name with accents, quotes or ampersand** (for example `Café & "Muro"`) or an invalid crate name or identifier: values must land correctly in JSON, TOML and Rust, or be rejected before any file is written. Pinned in Task 2.
3. **A placeholder left after copy** (a typo'd token in a template file): instantiate must fail non-zero, and the template must contain no token outside the four allowed. Pinned in Tasks 2 and 3.
4. **Android toolchain absent, or the emulator has no acceleration:** the skill names what is missing and stops; the verification stops and tells the author. Pinned in Tasks 5 and 6.
5. **Host app with a different package manager, an existing `@tauri-apps/cli`, remote API or CDN origins, or a service worker:** adapt must detect, show diffs, list origins, and never widen the CSP silently. Pinned in Task 7.

---

### Task 1: Skill skeleton that passes the validators

**Files:**
- Create: `skills/tauri-starter/SKILL.md`, `skills/tauri-starter/agents/openai.yaml`, `skills/tauri-starter/references/native-plugins-data.md` (by `--sync-shared`)
- Modify: `scripts/test_validate_plugin.py:47,86,118`, `scripts/validate_plugin.py` (the "dual-skill" argparse description)
- Test: `scripts/test_validate_plugin.py`

**Interfaces:**
- Produces: skill directory `skills/tauri-starter/` with `name: tauri-starter`; later tasks add files under it and never touch this frontmatter.

- [ ] **Step 1: Create the branch** `git switch -c feat/tauri-starter` from `main`. Expected: `git status` shows only the untracked wireframe and the spec/plan files.
- [ ] **Step 2: Write the failing test.** In `test_validate_plugin.py` add `'tauri-starter'` to the two skill-name tuples (lines 47 and 118) and change line 86 to `self.assertEqual(sorted(report['skills_checked']), ['tauri-native-desktop', 'tauri-native-mobile', 'tauri-starter'])`.
- [ ] **Step 3: Run it to see it fail.** `python -m unittest discover -s scripts -p "test_validate_plugin.py"`. Expected: FAIL on the skill list.
- [ ] **Step 4: Create the skill.** `SKILL.md`: frontmatter per the constraints; body states the trigger (new app, or wrap a web app, Windows and Android), the two paths in order, the Android toolchain check-and-stop, and hand-off to `tauri-native-desktop` and `tauri-native-mobile` by name. `openai.yaml` mirrors the sibling skills' shape. Neutralize the argparse description string in `validate_plugin.py`.
- [ ] **Step 5: Mirror the plugin map.** `python scripts/validate_plugin.py --sync-shared`. Expected: `"ok": true`, three skills checked.
- [ ] **Step 6: Run the unit tests.** Same command as Step 3. Expected: PASS.
- [ ] **Step 7: Commit** (with OK): `git add scripts skills/tauri-starter docs && git commit -m "feat: add tauri-starter skill skeleton"`.

### Task 2: `instantiate.mjs` copies and substitutes

**Files:**
- Create: `skills/tauri-starter/scripts/instantiate.mjs`, `scripts/test_instantiate.py`
- Test: `scripts/test_instantiate.py` (skips when `node` is absent)

**Interfaces:**
- Produces: CLI `node instantiate.mjs --mode <new|adapt> --target <dir> --name <product> --id <reverse-dns> --crate <kebab-case>`. Copies `assets/core/` to `<target>/src-tauri/`; with `--mode new` also copies `assets/web/` to `<target>/`. Substitutes `{{PRODUCT_NAME}}`, `{{IDENTIFIER}}`, `{{CRATE_NAME}}`, `{{LIB_NAME}}` (the crate name with `-` replaced by `_`). Prints one JSON line `{"written": [...]}`. Exit codes: 0 ok, 2 invalid argument (nothing written), 3 target already has `src-tauri/` (nothing written), 4 a placeholder remains.
- Consumes: templates from Tasks 3 and 4 (tests here use a tiny fixture template through `--assets <dir>`, an extra flag for tests only).

- [ ] **Step 1: Write the failing tests** in `test_instantiate.py`, each calling the script on a temp dir: `test_substitutes_all_four_tokens`, `test_refuses_existing_src_tauri` (exit 3, target tree unchanged), `test_target_path_with_space_works`, `test_special_characters_in_name_survive_json_and_toml` (name `Café & "Muro"`: the written `tauri.conf.json` parses and `productName` equals it; the written Cargo.toml parses with `tomllib`), `test_rejects_invalid_crate_and_identifier` (`My_Crate`, `com..x`: exit 2, nothing written), `test_fails_when_a_token_remains` (fixture contains `{{TYPO}}`: exit 4).
- [ ] **Step 2: Run to see them fail.** `python -m unittest scripts.test_instantiate -v`. Expected: FAIL, script missing.
- [ ] **Step 3: Implement** `instantiate.mjs` (no dependencies): validate arguments before any write; escape the product name per file type (JSON string, TOML basic string, Rust string literal) rather than one global replace; scan every written file for `{{`.
- [ ] **Step 4: Run to see them pass.** Same command. Expected: PASS.
- [ ] **Step 5: Commit** (with OK): `git commit -m "feat: add instantiate script for the starter"`.

### Task 3: Core template, checked statically

**Files:**
- Create: `skills/tauri-starter/assets/core/{Cargo.toml,build.rs,tauri.conf.json,capabilities/desktop.json,capabilities/mobile.json,src/lib.rs,src/main.rs,icons/*}`, `scripts/test_core_template.py`
- Test: `scripts/test_core_template.py`

**Interfaces:**
- Produces: a template whose only tokens are the four of Task 2, with the table of the spec: `lib.rs` exposing `pub fn run()` with `#[cfg_attr(mobile, tauri::mobile_entry_point)]`; `main.rs` calling it; `window-state`, `single-instance` behind `cfg(desktop)`; `opener` plus a navigation guard; `log`; capability files per platform; a CSP that is not null.
- Icons: a neutral placeholder generated once with `tauri icon` (my call: the spec is silent and Windows needs `icon.ico`); the author replaces it with `tauri icon`.

- [ ] **Step 1: Write the failing tests:** `test_only_allowed_tokens` (every `{{X}}` in `assets/` is one of the four), `test_csp_is_not_null`, `test_capability_files_are_json_and_platform_scoped` (each has a `platforms` field; no platform appears in both), `test_desktop_plugins_only_in_target_dependencies` (`window-state` and `single-instance` appear in Cargo.toml only under a desktop `[target.'cfg(...)'.dependencies]` table), `test_no_md_in_assets`, `test_no_generated_android_project` (no `gen/` directory under `assets/`: `tauri android init` creates it after the identifier is set).
- [ ] **Step 2: Run to see them fail.** Expected: FAIL, template missing.
- [ ] **Step 3: Write the template.** Take plugin versions from the snapshot in `shared/native-plugins.md`; take the capability `platforms` field and values from the schema the build generates under `gen/schemas` (generate it once in the scratch project of Task 4 and correct the files if the test there disagrees). Decide WebView2 recovery after Task 4's experiment; until then it is not in the template.
- [ ] **Step 4: Run to see them pass.** Expected: PASS.
- [ ] **Step 5: Run `python scripts/validate_plugin.py`.** Expected: `"ok": true`.
- [ ] **Step 6: Commit** (with OK).

### Task 4: New-app path runs on Windows

**Files:**
- Create: `skills/tauri-starter/assets/web/{index.html,package.json,vite.config.ts,tsconfig.json,src/main.ts}`, `skills/tauri-starter/references/{new-app.md,wiring.md}`
- Modify: `skills/tauri-starter/SKILL.md` (link the two references), `skills/tauri-starter/assets/core/*` (corrections found by running)

**Interfaces:**
- Consumes: `instantiate.mjs` CLI (Task 2), the core (Task 3).
- Produces: `new-app.md` (empty directory to running app, literal commands) and `wiring.md` (order of wiring and what each part is for). The page reads the platform and calls one command; Vite binds `TAURI_DEV_HOST`; `viewport-fit=cover` and safe-area setup.

- [ ] **Step 1: Write `assets/web`, `new-app.md`, `wiring.md`.** The procedure is the test: no step may rely on knowledge outside it.
- [ ] **Step 2: Instantiate by following `SKILL.md` literally** in `D:\tmp\starter-check\new1` (`env.ps1` loaded; D: and C: floors checked first).
- [ ] **Step 3: Run `npm install`, then `npm run tauri dev`.** Expected: a window opens showing the page and the platform name.
- [ ] **Step 4: Observe each row of the spec's table** and record pass or fail: window-state (move, resize, close, relaunch, same geometry), single-instance (second launch focuses the first), opener plus guard (external link opens the default browser, the window stays on the app origin), `log` (lines in the terminal), CSP (an inline script outside the policy is blocked), ACL (a plugin command not granted in the capability is denied, a granted one works; the page carries one button for each).
- [ ] **Step 5: WebView2 recovery experiment:** kill the renderer (`taskkill /F /IM msedgewebview2.exe` on its renderer child only) and see whether `tauri-native-desktop`'s `recovery.md` approach recovers the window. Include it in the core only if it does; otherwise leave it out and point to `recovery.md` in `wiring.md`.
- [ ] **Step 6: `npm run tauri build -- --no-bundle`, launch the executable,** repeat the window-state check on the packaged build. Record bundling as not covered.
- [ ] **Step 7: Re-run Task 3 tests and the validators.** Expected: PASS and `"ok": true`.
- [ ] **Step 8: Commit** (with OK).

### Task 5: Android toolchain on D: and the free-space gate

**Files:**
- Create (outside the repository): `D:\tmp\starter-check\env.ps1`
- Test: run the gate with an impossible floor

**Interfaces:**
- Produces: `env.ps1` exporting `ANDROID_HOME`, `NDK_HOME`, `ANDROID_USER_HOME`, `GRADLE_USER_HOME`, `CARGO_HOME`, `npm_config_cache`, all under D:, and a function `Assert-Space -DMinGB 10 -CMinMB 500` that throws when under the floors. Every later command in Tasks 6 and 7 starts with `. env.ps1; Assert-Space`.

- [ ] **Step 1: Write `env.ps1`.** Do not persist anything.
- [ ] **Step 2: Test the gate.** `Assert-Space -DMinGB 9999`. Expected: throws and names the drive. Then with defaults. Expected: passes now (D: 74 GB, C: 1.2 GB).
- [ ] **Step 3: Install SDK pieces under `D:\Android\Sdk`:** command-line tools, platform-tools, one platform, build-tools, NDK r28 or newer (16 KB page rule in `build-deploy-mobile.md`), emulator, one x86_64 system image. State in one line what is installed and where, then run `sdkmanager --list_installed`. Expected: each piece listed.
- [ ] **Step 4: Add Rust targets** `aarch64-linux-android` and `x86_64-linux-android`. Expected: `rustup target list --installed` lists both.
- [ ] **Step 5: Acceleration check:** `emulator -accel-check`. Expected: acceleration usable. If not, stop and tell the author; enabling Windows Hypervisor Platform needs administrator and a reboot and is asked at that moment.
- [ ] **Step 6: Create the AVD and boot it.** Expected: `adb devices` lists an emulator in state `device`.

### Task 6: `android.md` and the new-app path on the emulator

**Files:**
- Create: `skills/tauri-starter/references/android.md`
- Modify: `skills/tauri-starter/SKILL.md`, `references/new-app.md`

**Interfaces:**
- Produces: a checklist the skill runs before any Android step: JDK, SDK platform, build-tools, NDK, the two Rust targets, `ANDROID_HOME`, `NDK_HOME`, `adb`; each missing item is named and the skill stops, pointing to `tauri-native-mobile`. It never installs.

- [ ] **Step 1: Write the failing check.** In a shell where `ANDROID_HOME` is unset, follow `android.md` on `new1`. Expected (the test): the skill names `ANDROID_HOME` as missing and stops. Before `android.md` exists this fails.
- [ ] **Step 2: Write `android.md`** from the verified Task 5 steps and from `setup-mobile.md`, `build-deploy-mobile.md`, `mobile-stale-builds.md`, `debugging-mobile.md`; it states only what the starter adds.
- [ ] **Step 3: Re-run Step 1.** Expected: stops, names the missing variable. Then with `env.ps1` loaded: the check passes.
- [ ] **Step 4: `npm run tauri -- android init`, then `npm run tauri -- android build --apk --debug --target x86_64`.** Expected: an APK exists; inspect its application ID and packaged assets.
- [ ] **Step 5: Install and run on the emulator:** `adb install -r <apk>`. Expected: the page shows, insets are correct, the back button behaves; `chrome://inspect` shows the WebView. Then `npm run tauri -- android dev` over `TAURI_DEV_HOST` and edit the page to see the update.
- [ ] **Step 6: Phone, as an extra check only:** build `aarch64`, install over adb. Record the result separately.
- [ ] **Step 7: Run the validators** (`validate_plugin.py` and the unit tests). Expected: PASS.
- [ ] **Step 8: Commit** (with OK).

### Task 7: Adapt path, Windows and emulator

**Files:**
- Create: `skills/tauri-starter/references/adapt-web-app.md`
- Modify: `skills/tauri-starter/SKILL.md`
- Create (outside the repository): fixtures and the sample app under `D:\tmp\starter-check\`

**Interfaces:**
- Consumes: `instantiate.mjs --mode adapt` (core only).
- Produces: `adapt-web-app.md` with detection (package manager, framework, dev command and URL, build command and output directory, router mode, base path, service worker, existing `src-tauri` or `@tauri-apps/cli`, remote origins), the change policy (new files directly; edits to host files as a shown diff, applied only on approval), the refusal cases, and the browser-path check.

- [ ] **Step 1: Build the fixtures.** A real sample (Vite plus React, history routing, no backend) and five small fixtures: server-rendered Next.js without static export, service worker enabled, remote API plus CDN font, a non-root `base` path, an already-Tauri project with `pnpm`.
- [ ] **Step 2: Write the failing procedure test.** Follow `SKILL.md` on each fixture before `adapt-web-app.md` exists. Expected: no consistent refusal or listing (FAIL).
- [ ] **Step 3: Write `adapt-web-app.md`.**
- [ ] **Step 4: Re-run on the fixtures.** Expected: Next.js refused with the reason; service worker flagged; non-root `base` warned with the change shown; remote origins listed and the CSP left unchanged until the author picks; the `pnpm` project keeps its package manager and does not get a second CLI.
- [ ] **Step 5: Adapt the sample.** Expected: diff shown for each edit of a host file; after approval `npm run tauri dev` opens the sample on Windows; the debug APK runs on the emulator.
- [ ] **Step 6: Browser path.** The sample's original `npm run dev` and `npm run build` still work. Expected: unchanged output.
- [ ] **Step 7: Run the validators.** Expected: PASS.
- [ ] **Step 8: Commit** (with OK).

### Task 8: Verification record and plugin-level docs

**Files:**
- Create: `skills/tauri-starter/references/verification.md`
- Modify: `README.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: the observations of Tasks 4, 6 and 7.
- Produces: `verification.md` listing date, machine, lockfile-resolved versions (tauri, tauri-build, each plugin, `@tauri-apps/cli`, Rust, Node, JDK, Gradle, AGP, Kotlin, SDK platform, build-tools, NDK) and each check as passed, failed or not run; README and manifests consistent with it.

- [ ] **Step 1: Write the failing check.** `python scripts/validate_plugin.py` after setting `plugin.json` version to `1.4.0` while README still says two skills. A consistency test `test_readme_lists_all_skills` in `scripts/test_validate_plugin.py` asserts each skill directory name appears in `README.md`. Expected: FAIL.
- [ ] **Step 2: Write `verification.md`** from the recorded results; not-run items stay "not run".
- [ ] **Step 3: Update README** (skill table row, a start line in Install, the Limits sentence matching `verification.md`, the validation commands), `plugin.json` (1.4.0, description) and `marketplace.json` (description).
- [ ] **Step 4: Run all checks.** `python scripts/validate_plugin.py`, `python -m unittest discover -s scripts -p "test_*.py"`, and the mobile skill's own `python scripts/validate_bundle.py` from its directory. Expected: all pass, no placeholder in any instantiated project.
- [ ] **Step 5: Commit** (with OK), then ask the author how to integrate the branch.
