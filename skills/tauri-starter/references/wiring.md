# Wiring: what the core contains and in what order

The core is `src-tauri/`. This is the order in which it is put together and what each part is for.

## 1. Rust, once at start (`src/lib.rs`, function `run`)

1. `main.rs` only calls the library's `run`; the `#[cfg_attr(mobile, tauri::mobile_entry_point)]` attribute on `run` is what lets Android start the same code.
2. Desktop-only plugins are added first and only under `#[cfg(desktop)]`: single instance (it must be the first plugin registered, so a second launch focuses the first window) and window state (size and place survive a restart). Their crates sit in the Cargo target table that excludes Android and iOS, because those plugins have no mobile support.
3. Logging, the opener and the navigation guard follow on every platform. The guard lets only the app's own origin load in the webview (`tauri://localhost`, `http(s)://tauri.localhost`, and the dev server in debug builds only) and sends web links to the system browser.
4. `platform_name` is the one command the page calls, so there is something to prove that IPC works.
5. On Windows, `setup` calls `recovery::install` for the main window (`src/recovery.rs`, see section 6). It is compiled only on Windows.

## 2. Capabilities (`capabilities/`)

One file per platform: `desktop.json` for Windows, macOS and Linux, `mobile.json` for Android and iOS. Each grants the main window `core:default` (the standard baseline) and one scoped permission, `opener:allow-open-url` for `https://tauri.app` only, which is what the demo button uses; widen the scope to the addresses your app really opens. Anything else is refused. To grant more, read the permission names from the installed plugin (the build generates the schemas under `gen/schemas`), add them to the file of the platform that needs them and check the call in the running app. A capability cannot grant an Android runtime permission; see `tauri-native-mobile`.

## 3. Content Security Policy (`tauri.conf.json`)

`csp` is a real policy, never null. `devCsp` is the same plus `ws:` so the Vite reload socket works in development; it is not used by packaged builds. Widen the policy only for origins the user names. Observed on Windows: a script created at run time is blocked in the packaged build, while `tauri dev` does not enforce the policy on the dev server's page, so check the policy on a packaged build. Inline scripts already in the built HTML are allowed because Tauri adds nonces to them.

## 4. The page (`src/main.ts`, `index.html`)

It uses only the core API: one command and two plugin calls, one granted and one refused on purpose. The `viewport-fit=cover` meta tag and the `env(safe-area-inset-*)` padding keep the page clear of the bars on iOS and on an Android WebView from M136, the first that reports the bars to the page. On an older Android WebView the page is drawn under the bars, and no version shrinks the layout for the keyboard. Before shipping on Android, give the insets an owner as `tauri-native-mobile` describes (its Android insets and keyboard reference has the code and the checks); the template adds no native code for it. `vite.config.ts` binds the dev server to `TAURI_DEV_HOST` when it is set, which is how a device reaches it.

## 5. What is not here

Updater, tray, notifications, deep links, sign-in, a custom title bar and dialogs. Each is a decision for `tauri-native-desktop` or `tauri-native-mobile`; check their references and the plugin map before adding one.

On Android the generated project also keeps three defaults the core does not change: Tauri's launcher icon, data backup switched on, and Back closing the app at the first page. `android.md` section 3 says what to do about each.

Failed navigations, an unresponsive renderer, frames and windows other than `main` are not covered by the recovery in section 6; see the recovery reference of `tauri-native-desktop` for them.

## 6. WebView2 recovery (Windows, `src/recovery.rs`)

Without it, a WebView2 renderer that dies leaves the engine's own error page on screen and the app never recovers. The module registers a `ProcessFailed` handler on the main window's WebView2 (`webview2-com`, a Windows-only dependency whose version must match the one `tauri` resolves) and decides by the kind of failure:

- Renderer exited: reload the page, at most three times per minute. After that the engine's error page stays and the log says why, so a page that crashes at once does not reload forever.
- Browser process exited: restart the app, but only while the window still exists, because a normal exit also ends that process. A restart loses in-memory state; an app with unsaved work must persist it first.
- Anything else: logged only.

The handler copies what it needs and returns, and the reload or restart runs from another thread after a short delay, as WebView2 requires of its callbacks. The decisions and the retry limit have unit tests (`cargo test --lib` in an instantiated project, on Windows). To prove the whole thing on a real app, give the app its own WebView2 user-data folder with `WEBVIEW2_USER_DATA_FOLDER`, then stop only the processes whose command line carries that folder: the one with `--type=renderer` (the page must come back and the log shows the reload), and the one without a `--type` (the app must restart with a new process id). Never stop every `msedgewebview2.exe`: other applications use it.
