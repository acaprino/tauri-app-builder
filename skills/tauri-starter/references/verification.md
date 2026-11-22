# Verification record

What was run, on what, and what was not. Date: 2026-11-22. A result here is an observation on one machine, not a guarantee for other versions: compare the lockfile of your own project.

## Machine and versions

- This record has two parts: the first runs (new app, Android, adapt) used the template before the WebView2 recovery was added; the recovery was then tested on its own scratch app, and its Android build is listed below.
- Windows 10.0.26200 Home (x86_64), WebView2 runtime 157.0.4341.60, Visual Studio Build Tools 2022.
- Rust 1.99.1, Node 24.14.1, JDK 17.0.19. These are the only versions run. The floors the docs state (Rust 1.90, Node 20.19 or 22.12) come from the packages' metadata and were not run.
- Crates as resolved by `Cargo.lock`: tauri 2.12.7, tauri-build 2.7.6, tauri-runtime-wry 2.12.5, wry 0.57.3, webview2-com 0.39.1, tauri-plugin-log 2.10.2, tauri-plugin-opener 2.7.3, tauri-plugin-single-instance 2.5.5, tauri-plugin-window-state 2.5.0. The plugin map lists window-state 2.5.1; that release was not on crates.io on this date, so the template asks for `2.5`.
- npm as resolved: @tauri-apps/cli 2.12.6, @tauri-apps/api 2.12.5, vite 8.3.8, typescript 5.9.3.
- Android: Gradle 9.6.1, Android Gradle plugin 9.3.1, Kotlin 2.2.10, compile and target SDK 37 (platform installed by Gradle), minSdk 24, build-tools 36.0.0, NDK 28.2.13676358, emulator 37.3.10, system image Android 16 (API 36) Google APIs x86_64, run headless (`-no-window`, software GPU) with Windows Hypervisor Platform acceleration.

## New app

| Check | Result | Note |
|---|---|---|
| Instantiate, `npm install`, `tauri dev` opens a window on Windows | passed | |
| Page shows "Running on windows" | passed | |
| Granted plugin call (opener) | passed | `opener: allowed` |
| Plugin call not granted | passed | refused with the ACL message |
| Opener scope | passed on Windows | `https://tauri.app` allowed, `https://example.org` refused with `Not allowed to open url`; the Android capability file has the same scope; the Windows build validated both files, but the Android app was not re-run |
| Packaged origin | passed on Windows | `http://tauri.localhost` (also seen on Android) |
| Navigation guard on an external link | passed | the window stays on the app and the log line is written; the browser opening was not seen on Windows (on Android Chrome started) |
| A request to the app's own origin from a packaged build | passed after a fix | the first policy blocked it (`connect-src` had no `'self'`), the corrected one allowed it |
| Log lines | passed | on the terminal in dev |
| Window size and place restored after a restart | passed | dev run and packaged build |
| Single instance | passed | second launch exits, the minimized first window comes to the front |
| CSP blocks a script created at run time | passed in the packaged build | `tauri dev` does not enforce it on the dev server's page |
| Packaged build without bundling, run without the dev server | passed | `tauri build --no-bundle` |
| Installers and bundles | not run | |
| WebView2 recovery: renderer killed | passed | the page returned in about 1 s with the same app process, in the debug and the packaged app; the test instance had its own WebView2 data folder and only its own processes were stopped |
| WebView2 recovery: reload limit | passed | the fourth kill within a minute was not reloaded, the log says the limit is reached and the engine's error page stays |
| WebView2 recovery: browser process killed | passed on the packaged app | the app restarted with a new process id and showed the page; one app process afterwards |
| Normal close after the recovery code is installed | passed | no restart, no process left |
| Recovery unit tests | passed | five tests on the decisions and the retry limit (`cargo test --lib`, Windows) |
| Recovery on a navigation failure, an unresponsive renderer, frames, other windows | not covered | |

## Android

| Check | Result | Note |
|---|---|---|
| Toolchain check script | passed | unit tests, and run on this machine with and without the variables |
| `android init --skip-targets-install`, x86_64 debug APK | passed | 133.9 MB, native code x86_64 only, minSdk 24 |
| Install and run on the emulator | passed | page below the status bar, origin `http://tauri.localhost/` |
| Granted call, refused call, navigation guard, CSP, log in logcat, Back closes the app | passed | the refused call says `Plugin not found` (desktop-only plugin) |
| DevTools through `adb forward` | passed | used to drive the page |
| `tauri android dev` with Vite on `TAURI_DEV_HOST` | not verified | Gradle finished, the CLI never installed or started the app, three tries |
| x86_64 debug APK of the revision with the WebView2 recovery | built, not run | 133.8 MB; the recovery code is Windows-only and compiles out on Android, so only the build was repeated |
| `aarch64` debug APK | built, not run | native code arm64-v8a only, 133.4 MB; nothing arm64 was available to run it on |
| A physical phone | not run | none was connected |
| Release or bundle build, signing | not run | |

## Adapt

| Check | Result | Note |
|---|---|---|
| Detection on five fixtures | passed | existing Tauri with pnpm, non-root base path, server-rendered Next.js, remote origins, service worker |
| Script refuses an existing `src-tauri` | passed | exit 3, nothing written |
| Vite plus React sample with a history router | passed | window on Windows (dev and packaged), debug APK on the emulator, a route loaded directly |
| The sample's own dev and build scripts afterwards | passed | same output file list and the same hashed file name |
| Remote origins loaded or blocked at run time | not run | the origins were only listed |
| Real installs with pnpm, yarn or bun | not run | |

## Not covered

macOS, Linux and iOS targets; custom title bars, tray, notifications, deep links, updater and sign-in (see `tauri-native-desktop` and `tauri-native-mobile`).
