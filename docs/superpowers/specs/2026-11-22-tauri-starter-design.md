# tauri-starter: design

Status: approved by the author 2026-11-22, with the emulator as the default Android run target. Nothing in this document has been built.

## Intent

Add a third skill, `tauri-starter`, to the `tauri-app-builder` plugin. It starts a new Tauri 2 app, or wraps an existing web app in Tauri 2, for **Windows and Android**, from one shared `src-tauri` core. After the start, work moves to `tauri-native-desktop` and `tauri-native-mobile`.

Why: the plugin today only documents. The author wants to say "make me a new app" or "put this web app in Tauri" and have the plugin do it, the way the Imago package (`D:\Projects\imago`) ships a shell crate, a runnable demo and a documented wiring order, but without Imago's visual layer.

## Goals

1. New app: from an empty directory to a running Windows window and an installable Android APK by following the skill, on a machine whose Android toolchain is already set up. The skill checks for that toolchain and stops, naming what is missing and pointing to `tauri-native-mobile`; it does not install it (my call). The one-off toolchain install on the author's machine is a precondition of verification, not something the skill tests.
2. Adapt: add the core to an existing web project with additive changes only; the project's own browser scripts keep working.
3. One `src-tauri` core for both platforms, with per-platform dependencies and per-platform capability files.
4. Least privilege from the first commit: no `csp: null`, no `core:default` broadened by habit, no plugin without an observable behavior.
5. Honest verification: what ran, on what, at which resolved versions, written in `references/verification.md` inside the skill.

## Non-goals and anti-goals

- No visual layer: no tokens, CSS system, looks, glass, accents or icon pipeline. No UI framework in the "new" path.
- No macOS, Linux or iOS target in the starter. The core must not block them (`cfg` and per-platform capability files), but they are not verified.
- No auto-update, tray, notifications, deep links or sign-in by default. The two native skills own them.
- No script that calls `create-tauri-app` or `tauri init` (approach 3, rejected).
- Anti-goal: a starter that was never built. Anti-goal: a template that contradicts `setup-mobile.md`, `build-deploy-mobile.md`, `mobile-stale-builds.md`, `debugging-mobile.md` or the desktop skill's references. Anti-goal: an adaptation that breaks the host project's browser path.

## Approaches

1. **Third skill `tauri-starter` owning one template (chosen by the author).** One copy; clear trigger; `validate_plugin.py` already iterates every skill directory. Cost: a user who installs only one skill has no starter.
2. Template mirrored into both skills via `--sync-shared`. Each skill stays standalone. Cost: two copies to keep equal. Rejected by the author.
3. A script driving `create-tauri-app` plus patches. Always current with the CLI. Cost: network, framework detection in the adapt path, hard to verify. Rejected by the author.

## Constraints

- **Versions.** The skills' reference snapshot is tauri 2.12.5 (`tauri-native-desktop/references/guide.md`); Tauri 3.x is not covered. The CLI installed globally on the author's machine is `tauri-cli 2.10.1`, older than that snapshot. The starter pins the CLI per project as an npm dev dependency (`npm run tauri -- ...`, as in `build-deploy-mobile.md`), so the global CLI is left alone. Declared versions in the template are the snapshot's; `verification.md` records the **lockfile-resolved** versions (tauri, tauri-build, each plugin, `@tauri-apps/cli`, Rust, Node, JDK, Gradle, AGP, Kotlin, SDK platform, build-tools, NDK).
- **Validator rules** (`validate_plugin.py`, `validate_bundle.py`):
  - `SKILL.md` frontmatter: `name` equals the directory, `description` starts with "Use when ", names "Tauri 2", is at most 1024 characters.
  - `agents/openai.yaml` with `display_name:`, `short_description:`, `default_prompt:`; the prompt references `$tauri-starter`.
  - `references/native-plugins-data.md` must equal `shared/native-plugins.md` (use `--sync-shared`).
  - Links and inline `../` paths must stay inside the skill ("Path outside bundle"). The starter names `tauri-native-desktop` and `tauri-native-mobile` in prose, never by relative link.
  - Do not create `examples/` or `audit/` in the skill: either one makes the validator demand `audit/source-manifest.json`. Template files live in `assets/`.
  - `validate_plugin.py` scans every `.md` under the skill, `assets/` included: balanced fences, every ```json block must parse (no placeholders, comments or ellipses in json fences), no phrase "the backup". Keep `.md` files out of `assets/`.
  - Bracketed citations are only policed when `references/sources.md` exists. The starter has none; it states sources as plain links.
- **Author's machine (observed 2026-11-22).**
  - Windows Home with a hypervisor present; Developer Mode on (symlinks allowed); long paths on.
  - Present: Rust 1.99.1, Node 24.14.1, JDK 17, Visual Studio Build Tools 2022, WebView2 157.0.4341.60, `tauri-cli 2.10.1`.
  - Absent: Android SDK platforms/build-tools/platform-tools/NDK/emulator (only `extras`, `licenses`, `sources` under `%LOCALAPPDATA%\Android\Sdk`), Android Rust targets, `ANDROID_HOME`, `NDK_HOME`, `adb`.
  - **Disk: C: has 1.2 GB free, D: has 74 GB.** `.cargo` 2.6 GB, `.rustup` 5.3 GB, `.gradle` 2.3 GB and the npm cache 1.4 GB already sit on C:. All new toolchain, caches, `CARGO_HOME` and verification projects go to D:. The project and `CARGO_HOME` must share a volume: `setup-mobile.md` warns that plugin-source paths on a different volume break the Kotlin build, so keeping `CARGO_HOME` on C: is not an option, and freeing space on C: would not remove the need. The variables are set only in a verification shell script (`D:\tmp\starter-check\env.ps1`), not persistently. The existing `.cargo` (it holds the global `tauri-cli 2.10.1`) is left untouched. A persistent change is made only if the author asks. A step stops when D: has under 10 GB free or C: under 500 MB (my call).
  - Whether the emulator gets hardware acceleration is not known; `emulator -accel-check` decides after install.

## Design

### Skill layout (my call)

```text
skills/tauri-starter/
  SKILL.md                    trigger, the two procedures in order, hand-off
  agents/openai.yaml
  assets/
    core/                     the src-tauri overlay, shared by both paths
    web/                      the minimal frontend, "new" path only
  references/
    new-app.md                empty directory to running app
    adapt-web-app.md          detection, changes, refusal cases
    wiring.md                 order of wiring and what each part is for
    android.md                the toolchain check (names what is missing, then stops) and what the starter adds on top of the mobile skill's setup
    verification.md           what ran, versions, what did not run
    native-plugins-data.md    mirror of shared/native-plugins.md
  scripts/
    instantiate.mjs           copy, substitute, check
```

### Core contents (my call: the smallest set; each item is something observed running)

| Item | Platform | Observed by |
|---|---|---|
| `lib.rs` plus `main.rs` split, mobile entry point | both | Android APK starts; `npm run tauri dev` starts on Windows |
| Capability files per platform, least privilege | both | Denied command returns an ACL error; allowed one works; the build's generated schema accepts both files |
| Content Security Policy that is not null | both | Page loads; an inline script outside the policy is blocked |
| `window-state` | Windows | Move and resize, close, relaunch: same geometry |
| `single-instance` | Windows | Launch twice: second launch focuses the first |
| `opener` plus a navigation guard | both (Android: URLs only) | External link opens the system browser; the webview stays on the app origin |
| `log` | both | Lines appear in the dev terminal and in logcat |
| WebView2 recovery | Windows | Kill the WebView2 renderer process; the window recovers. Included only if `tauri-native-desktop`'s `recovery.md` approach can be exercised this way; otherwise left out and pointed to |

Desktop-only plugins sit behind `cfg(desktop)` and target-specific dependencies. The exact capability `platforms` field and its values come from the schema the build generates under `gen/schemas` and from the Tauri capabilities docs, not from memory. Plugin support is checked against `shared/native-plugins.md` (window-state and single-instance: Windows full, Android none; opener: Windows full, Android partial; log: full on both).

System title bar stays the default. Custom title bar, close behavior, dialog placement and notification delivery are the desktop skill's Manual or Auto choices, not starter defaults.

### The "new" path

`assets/web` is plain HTML and TypeScript with Vite, no framework: viewport and safe-area setup, the page reads the platform and calls one command. Vite binds to `TAURI_DEV_HOST` and its reachability is verified (`setup-mobile.md`).

### The "adapt" path

Detect: package manager, framework, dev command and URL, build command and output directory, router mode, base path, service worker.

Changes to the host project (my call on the policy). New files and keys are added directly: `src-tauri/` from the core, `@tauri-apps/cli` as a dev dependency, a `tauri` script, `.gitignore` entries. `devUrl`, `frontendDist`, `beforeDevCommand` and `beforeBuildCommand` are set in the new `tauri.conf.json` from the detection. Edits to files the host already owns (dev-server host binding for Android in `vite.config`, a service-worker or PWA plugin switch, `package.json` scripts) are shown as a diff and applied only after the user approves; without approval the skill stops. No Tauri import is added to the app's source.

Remote origins (my call). Detection also lists the remote origins the app uses: API base URLs, CDN scripts and fonts, sign-in redirects. The skill shows the list and asks which to allow. It never widens the CSP, the navigation guard or the capabilities silently. It also tells the user that the packaged origin differs from the dev server's, which changes CORS and cookie behavior for backends that expect the web origin (the builder confirms the exact origin per platform).

Refuse, or stop and say why:
- No static output and the app needs a server at runtime (server-rendered Next.js without static export, Nuxt without generate, API routes, server-set cookies).
- A non-root base path or a hash/history routing setup the asset protocol cannot serve: warn and show the change.
- Service worker or PWA caching enabled in the packaged build (`mobile-stale-builds.md`, step 5): disable it for the packaged build or stop.

Browser path check: the project's original dev and build scripts run unchanged after adaptation.

### Parameters

Placeholders: product name, identifier (reverse-DNS), crate name (the library name is derived from it). `scripts/instantiate.mjs` (Node, no dependencies; Node is present in any Tauri project, Python is not guaranteed) copies `assets/`, substitutes, refuses a target that already has `src-tauri/`, and fails if any placeholder remains. `gen/android` is never shipped: it is generated by `tauri android init` after the identifier is set.

### Plugin-level changes

- `skills/tauri-starter/` as above, plus `scripts/instantiate.mjs`.
- `scripts/test_validate_plugin.py`: the fixture copies and the expected skill list (lines 47, 86, 118 today) gain the third skill; new tests for the instantiate script (substitution, placeholder check, refusal of an existing `src-tauri`).
- `scripts/validate_plugin.py`: the "dual-skill" description string becomes neutral.
- `README.md`: skill table row, a "Start an app" line in Install, Limits (the starter is the one part built and run, and only on the platforms and versions recorded in `verification.md`), validation commands.
- `.claude-plugin/plugin.json` and `marketplace.json`: descriptions mention the starter; version 1.3.0 to 1.4.0.
- `python scripts/validate_plugin.py --sync-shared` once, to create the third mirror.

## Verification plan

Test the procedure, not a hand-built project.

1. Work in a short path outside the repository (`D:\tmp\starter-check\...`), never in `assets/`, because `.gitignore` covers none of `target/`, `node_modules/` or `gen/`.
2. Instantiate from `assets/` by following `SKILL.md` literally: once for "new", once for "adapt" against a real sample web app (Vite plus React, history routing). The refusal cases are checked with small fixtures, plus one fixture whose source calls a remote API and loads a CDN font, to check the origin listing (a static check, not run). The Vite sample has no backend, so it cannot show this.
3. Windows: `npm run tauri dev`, then a build and launch of the executable; observe every row of the core table. Record bundling as not covered unless it is run.
4. Android: install toolchain on D:, `tauri android init`, debug APK for `x86_64` and `aarch64`, `adb install -r`, observe page, insets, back button, `chrome://inspect`; also a live `tauri android dev` session over `TAURI_DEV_HOST`.
5. Android run target: the **emulator is the default and the required one** (author's decision). The author's physical phone, over adb, is an extra check and never a substitute. If the emulator cannot run (no hardware acceleration), stop and tell the author before using the phone as a stand-in, and record that in `verification.md`; with neither, the result is "built, not run".
6. `verification.md` records: date, machine, resolved versions, each check as passed, failed or not run.

Global changes this plan makes to the author's machine, all after approval:
- Android SDK command-line tools, platform-tools, one platform, build-tools, NDK r28 or newer, emulator and one x86_64 system image, installed under `D:\Android\Sdk` (estimate 8 to 12 GB, to confirm).
- Rust targets `aarch64-linux-android` and `x86_64-linux-android` (small, under `.rustup` on C:).
- Environment variables `ANDROID_HOME`, `NDK_HOME`, `ANDROID_USER_HOME` (AVDs), `GRADLE_USER_HOME`, `CARGO_HOME` and the npm cache location, all pointing to D: and set per shell by `env.ps1`. No persistent user-level change.
- Only if the accel check fails: enabling Windows Hypervisor Platform (administrator and a reboot), asked at that moment.

## Success criteria

1. New app: empty directory to a running Windows window using only the skill; Android debug APK installs and shows the page on the emulator.
2. Adapt: the sample web app runs in a window on Windows and as an APK on the emulator; its original `npm run dev` still works.
3. `python scripts/validate_plugin.py` and `python -m unittest discover -s scripts -p "test_*.py"` pass; the bundle validator passes on the third skill; no placeholder remains after instantiation.
4. `verification.md` exists and the README Limits sentence matches it.

## Open for the author

None. Answered: the author has a phone, and the emulator is the default run target.

## Left to the builder

Exact file contents of the template; exact plugin versions within the reference snapshot; the Vite configuration; the Content Security Policy string; whether WebView2 recovery makes the first cut; the NDK and SDK platform versions that satisfy `build-deploy-mobile.md` (16 KB page size); script error messages; the sample web app's framework if Vite plus React proves unsuitable.
