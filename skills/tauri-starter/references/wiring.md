# Wiring: what the core contains and in what order

The core is `src-tauri/`. This is the order in which it is put together and what each part is for.

## 1. Rust, once at start (`src/lib.rs`, function `run`)

1. `main.rs` only calls the library's `run`; the `#[cfg_attr(mobile, tauri::mobile_entry_point)]` attribute on `run` is what lets Android start the same code.
2. Desktop-only plugins are added first and only under `#[cfg(desktop)]`: single instance (it must be the first plugin registered, so a second launch focuses the first window) and window state (size and place survive a restart). Their crates sit in the Cargo target table that excludes Android and iOS, because those plugins have no mobile support.
3. Logging, the opener and the navigation guard follow on every platform. The guard lets only the app's own origin load in the webview (`tauri://localhost`, `http(s)://tauri.localhost`, and the dev server in debug builds only) and sends web links to the system browser.
4. `platform_name` is the one command the page calls, so there is something to prove that IPC works.

## 2. Capabilities (`capabilities/`)

One file per platform: `desktop.json` for Windows, macOS and Linux, `mobile.json` for Android and iOS. Each grants the main window `core:default` and `opener:default` and nothing else. To grant more, read the permission names from the installed plugin (the build generates the schemas under `gen/schemas`), add them to the file of the platform that needs them and check the call in the running app. A capability cannot grant an Android runtime permission; see `tauri-native-mobile`.

## 3. Content Security Policy (`tauri.conf.json`)

`csp` is a real policy, never null. `devCsp` is the same plus `ws:` so the Vite reload socket works in development; it is not used by packaged builds. Widen the policy only for origins the user names. Observed on Windows: a script created at run time is blocked in the packaged build, while `tauri dev` does not enforce the policy on the dev server's page, so check the policy on a packaged build. Inline scripts already in the built HTML are allowed because Tauri adds nonces to them.

## 4. The page (`src/main.ts`, `index.html`)

It uses only the core API: one command and two plugin calls, one granted and one refused on purpose. The `viewport-fit=cover` meta tag and the `env(safe-area-inset-*)` padding handle device insets; check them on a device. `vite.config.ts` binds the dev server to `TAURI_DEV_HOST` when it is set, which is how a device reaches it.

## 5. What is not here

Updater, tray, notifications, deep links, sign-in, a custom title bar and dialogs. Each is a decision for `tauri-native-desktop` or `tauri-native-mobile`; check their references and the plugin map before adding one.

WebView2 recovery is not included either. Observed on Windows: killing the WebView2 renderer process of a running app leaves the engine's own error page on screen and the app does not recover by itself. Recovery needs a `ProcessFailed` handler written against the project's lockfile; the approach and its limits are in `tauri-native-desktop` (its recovery reference), and the way to prove it works is the same kill test: stop the app's `msedgewebview2.exe` process started with `--type=renderer` and see whether the window recovers.
