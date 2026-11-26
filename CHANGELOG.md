# Changelog

One section per released version of the plugin. The release workflow publishes the section that matches `version` in `.claude-plugin/plugin.json` as the GitHub Release notes.

## Unreleased

### Mobile skill

- Android Back as part of the native baseline: close what is on top, then a second press at the root to leave, with `onBackButtonPress` on Android and history entries on the web; the listener that survives a page reload, and the capability it needs. Not run on a device.
- Android defaults to decide before shipping: backup and device transfer, the source of the target SDK, the version code fields, user CAs and cleartext for a server the user names.
- Reminders a server decides: push, or a foreground service with an open connection, with the service-type limits.
- Signing and 16 KB alignment when the artifact is signed after Gradle, per-ABI artifacts, and an emulator job for the built APK.

### Starter skill

- The Android page names three defaults of the generated project (Tauri's launcher icon, backup on, Back closing the app) and what to do about each; the verification record lists them as not run.

## 2.3.0

### Live debugging

- The plugin starts the `tauri` MCP server (`@hypothesi/tauri-mcp-server` 0.13.2, Tauri 2 only) through `.mcp.json`: screenshots, DOM snapshots, input, console and logcat output and IPC monitoring of a running app.
- New skill `tauri-live-debug`: when to use the server, how to check that its tools are available, the evidence-first procedure, which tools only read, and which references of the desktop and mobile skills to take for each symptom.
- Four commands: `/tauri-app-builder:bridge` adds the debug-only MCP bridge crate, `:debug` finds the cause of a symptom in the running app, `:build` builds a screen and checks each step live, `:verify` runs the acceptance checks the webview can show.
- The desktop and mobile skills point to the commands, and the desktop guide says what the webview cannot prove: the native frame, OS dialogs, tray, notifications after exit, installers and the task switcher.
- The server connected on a Windows machine (19 tools, 3 prompts). No app was driven with it, the commands were not run against an app, and a phone or emulator reaching the bridge was not checked.

## 2.2.0

### Starter skill

- New skill `tauri-starter`: starts a new Tauri 2 app, or wraps an existing web app in Tauri 2, for Windows and Android from one shared `src-tauri` core.
- The core has least-privilege capability files per platform, a Content Security Policy that is not null, window state and single instance on desktop, an opener limited to one address with a navigation guard, and logging.
- On Windows the WebView is recovered: a dead renderer is reloaded at most three times a minute and a dead WebView2 browser process restarts the app.
- A dependency-free script copies the template and refuses to overwrite anything; a second script checks the Android toolchain and stops without installing it.
- The adapt path detects the package manager, static output, router, base path, service worker and remote origins, refuses what cannot work and shows a diff before editing the project's own files.
- Run on Windows and on an Android 16 emulator; the live `tauri android dev` session, a phone, installers and macOS, Linux and iOS were not verified. See the skill's verification record.

## 2.1.0

### Desktop skill

- New reference on credentials, saved passwords and passkeys: the three needs behind "the system password wallet" and what each one uses on Windows.
- Storing the app's own secrets in the OS credential store through a keyring crate behind an app command.
- Windows has no OS API that hands an app the user's saved passwords; signing in through the system browser is the route that reuses them.
- Passkeys through Windows Hello and the WebAuthn API, with what is still unverified inside WebView2.
- Passkey sign-in added to the native feature menu.

### Mobile skill

- Android Credential Manager for the user's saved passwords and passkeys, the website association it needs, and its WebView support.

### Both

- Stronghold is marked as not for new work: a Tauri maintainer announced its deprecation and removal in Tauri 3.

## 2.0.0

Both skills now work in phases instead of going straight to changes.

### Desktop skill

- **Phase 1, assess:** a status of the app before anything changes: which standard changes are in place, which native features exist, which defects were found.
- **Phase 2, native baseline:** eleven standard changes that stop the app behaving like a web page are applied together, without a question for each one.
- **Phase 3, native features:** a menu of optional integrations is offered in one prompt, each with what the user gets and what it costs: dialog placement, title bar, close button and tray icon, start at login, second launch, window position, menu bar, notifications, taskbar status, links into the app, updates, the OS credential store, unlock with the OS, sign-in in the system browser, device access.
- Nothing beyond the baseline and the chosen features is added. A request about one thing still goes straight to it.

### Mobile skill

- The same order: assess with the capability inventory, apply the layout and permission baseline, then ask which native capabilities to add, since each one adds permissions and store declarations.

## 1.6.0

### Desktop skill

- The window's content never moves as a whole: locking the root of every WebView against overscroll is now a default, on Windows too, where a precision touchpad or a touchscreen makes the whole view slide and uncover the background.
- The lock is applied without waiting to observe the effect on a device; an audit can no longer defer it as "to be observed first".
- Explains why a full-height shell with hidden overflow does not prevent it, and that it is not WebView2's pull to refresh.
- New acceptance checks for the locked root.

### Mobile skill

- New section on overscroll and pull to refresh: lock the root, scroll inside each screen's container, match the background, and build pull to refresh as a gesture of the list that needs it.

## 1.5.0

### Desktop skill

- Asks the user whether the main window's close button quits the app or hides it to the tray, and whether the app starts at login (with its window or in the tray).
- Before the choice, explains how start at login works on each OS, which setting the app gains and where, and where the user can turn it off in the OS.
- Lists the project files each choice changes, to show the user before implementing.
- Both questions are open in every whole-app pass and in any task that adds background work, a tray icon or notifications.

### Repository

- Releases are published by a GitHub Actions workflow from the plugin version and this changelog.
- The README describes what each skill covers, when to use it and how it works.

## 1.4.0

### Desktop skill

- New reference for apps that keep running with their window closed: tray icon, close to tray, one restore path and start at login are decided together.
- Start at login with the official autostart plugin: what each OS writes, off until the user turns it on, the OS as the source of truth, and a launch argument to start in the tray.
- Explains why a windowed app cannot be a Windows service and what to use instead: a separate headless service binary, a Task Scheduler task, or a signed-in session with a startup entry.
- New acceptance checks for tray and start at login.

## 1.3.0

### Desktop skill

- Present unresolved product choices for dialog placement, the title bar, the main window's close action, and notification delivery together.
- In **Manual**, apply the user's explicit choices. In **Auto**, recommend an option for each open choice and wait for approval before implementing.
- Explain the effects on main window interaction, native window controls, running work, and notification delivery. Check that notification delivery works with the chosen close behavior.

## 1.2.0

- Hardened the standalone skill bundles, the boundaries between surfaces and the plugin validation.

## 1.1.0

- The desktop and mobile skills share one native plugin data file, mirrored into each skill so either works standalone.

## 1.0.0

- Initial release: the `tauri-native-desktop` and `tauri-native-mobile` skills.
