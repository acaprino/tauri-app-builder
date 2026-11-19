# tauri-app-builder

A Claude Code plugin with two skills for building, auditing and shipping Tauri 2 apps that behave like native apps.

Tauri gives a web frontend a native shell: an OS window, a system WebView, a Rust backend and installers. What it does not give is native behavior. Out of the box the app still acts like a web page in a frame: a white flash at startup, selectable interface text, the browser's context menu and shortcuts, dialogs that ignore OS conventions, permissions that fail silently on a phone. These skills hold the knowledge for that layer, the part between the web UI and the operating system, so Claude handles it deliberately instead of leaving browser defaults in place.

The skills are documentation and decision guides that Claude loads when the task calls for them. They are not a library, a template or a CLI, and they add nothing to your app's dependencies.

| Skill | Platforms | Use it for |
|---|---|---|
| `tauri-native-desktop` | Windows, macOS, Linux | Windows and dialogs, title bar, tray and start at login, menus, notifications, installers and updates, keyboard and accessibility, WebView lifecycle and recovery |
| `tauri-native-mobile` | Android, iOS | Permissions, camera and microphone, sign-in, deep links, safe areas, location, NFC/BLE, biometrics, push and background work, file export, builds and store delivery |

## Install

```
/plugin marketplace add acaprino/tauri-app-builder
/plugin install tauri-app-builder@tauri-app-builder
```

To update later, run `/plugin marketplace update tauri-app-builder`.

Each skill also works on its own: copy `skills/tauri-native-desktop` or `skills/tauri-native-mobile` into `~/.claude/skills/` (all projects) or `.claude/skills/` (one project). Every skill folder carries its own copy of the shared plugin data for this reason.

## When to use it

Claude loads a skill by itself when the request matches. You can also name the skill in the prompt.

| You want to | Example request | Skill |
|---|---|---|
| Audit a whole desktop app | "Audit this Tauri app and tell me where it still behaves like a web page" | desktop |
| Choose native features | "Which native features could this app use? Let me pick" | desktop or mobile |
| Store secrets safely | "Keep the login token in the system credential store" | desktop |
| Make a desktop app feel native | "Make this app behave natively on Windows 11" | desktop |
| Fix the startup flash | "The window flashes white before the UI appears" | desktop |
| Decide where a dialog lives | "Should the settings dialog be a separate window?" | desktop |
| Choose the title bar | "I want a custom title bar but keep Snap Layouts" | desktop |
| Keep the app running in the background | "Closing the window should hide the app to the tray" | desktop |
| Start the app with the computer | "Start the app when the user signs in" | desktop |
| Send desktop alerts | "Notify the user when a job finishes while the window is hidden" | desktop |
| Remove browser behavior | "Remove the Edge right-click menu and the F5 reload" | desktop |
| Stop the whole view from dragging | "Pulling down moves the entire app and shows a white strip" | desktop or mobile |
| Survive WebView failures | "The app shows a blank page after the WebView crashes" | desktop |
| Package and update | "Set up the NSIS installer, signing and the updater" | desktop |
| Pick a plugin for a capability | "How do I store a token in the OS keychain?" | desktop or mobile |
| Port a web app to phones | "List what breaks when this web app runs on Android and iOS" | mobile |
| Fix a permission that never prompts | "The camera permission dialog never appears on Android" | mobile |
| Add native sign-in | "Add Google sign-in on Android without the external browser" | mobile |
| Handle notches and the keyboard | "Content hides under the status bar and the keyboard" | mobile |
| Add background delivery | "Send a reminder at an exact time even when the app is closed" | mobile |
| Export files | "The download button does nothing in the mobile app" | mobile |
| Debug a stale build | "The APK still shows the old UI after I rebuilt" | mobile |
| Ship to the stores | "Prepare the Play Store and App Store builds and the CI" | mobile |

Neither skill is for web-only restyling. Desktop behavior belongs to the desktop skill and Android/iOS work to the mobile skill; an app that ships on both uses both.

## What the desktop skill covers

| Area | What it handles |
|---|---|
| Windows and dialogs | Which surfaces stay in the main window (drawers, inspectors, in-page dialogs) and which need a separate OS window; owner and parent, modality, sizing, focus and the full close lifecycle |
| Frame | System or custom title bar, drag regions, Windows Snap Layouts, the macOS app menu, Mica, vibrancy and Liquid Glass, no white flash on the first frame |
| Background presence | Tray icon, close to tray, one restore path, start at login, starting in the tray, and when a Windows service fits |
| OS integration | Menus, single instance, deep links, window-state restore, badge and overlay icon, taskbar progress, exit and reopen, Linux file dialogs |
| Notifications | System notifications against in-app feedback, delivery while focused, hidden or exited, Windows toast identity, permissions, callbacks |
| Web layer | Bootstrap shared by every WebView, text selection and cursors, a root that never drags on overscroll, bounce in lists, scrollbars, WebView2 switches |
| Context menus | Removing the engine's menu, native or app-owned replacements, editing menus that keep working |
| Keyboard and accessibility | Disabling browser shortcuts and replacing the needed ones, zoom and text size, screen readers, forced colors, system accent, IME, a command registry |
| Boundaries | What each window may call and read: capabilities, credentials, events between windows |
| Recovery | The engine's error page, WebView process crashes, reload handled by the app, release builds that load the dev URL |
| Packaging and updates | NSIS, MSI, DMG and Linux packages, signing and notarization, updater artifacts and keys, sidecars, CI |
| Credentials and passkeys | The app's secrets in the OS credential store, the user's saved passwords, passkey sign-in with Windows Hello, why Stronghold is not for new work |
| Native plugins | Which core API or plugin covers a capability, and which have no official plugin (keychain, Windows Hello, OAuth, camera, location) |

## What the mobile skill covers

| Area | What it handles |
|---|---|
| Migration inventory | Every browser-dependent action in a web app (downloads, popup login, capture, timers, clipboard, links) and the native adapter each one needs |
| Permissions | The chain from Tauri capability to manifest or entitlement to runtime grant; denial, cancellation and recovery |
| Camera and media | Camera, gallery and microphone capture, cancellation and timeouts |
| Sign-in | Native Google and Firebase sign-in, Apple sign-in, other OAuth, callback lifecycle and deep links |
| Layout | Safe areas, the on-screen keyboard, a screen that never drags as a whole on overscroll, older WebView engines |
| Device features | Geolocation and geofencing, NFC and Bluetooth LE, biometric unlock and credential protection, saved passwords and passkeys through Credential Manager |
| Background work | Push, background jobs, offline sync, notifications, exact alarms and snooze |
| Files | ZIP export, downloads, save and share |
| Purchases | In-app purchases |
| Performance | IPC streaming and high-frequency rendering |
| Builds and debugging | Toolchain setup, stale builds, device investigation, a verification matrix |
| Release | Play Store and App Store delivery, mobile CI, dependency updates |

## How the skills work

**Three steps, in order.** For a whole app, both skills work the same way:

1. **Assess.** Claude reads the project and reports where the app stands. Nothing changes yet.
2. **Native baseline.** The standard changes that every Tauri app needs are applied together, without a question for each: no white flash, interface text that does not select, no browser shortcuts or browser menu, content that does not drag as a whole, no engine error page.
3. **Your choice of native features.** Claude offers a menu and adds only what you pick. On desktop: dialog placement, title bar, tray icon and close behavior, start at login, notifications, the OS credential store, sign-in in the system browser, updates and more. On mobile: camera, sign-in, location, push, biometrics, file export and the other device capabilities.

A request about one thing, such as the startup flash, goes straight to it.

**The lightest level that fits.** The desktop skill separates four levels: a surface inside the main window, a native OS control or service, a separate window with web content, and a fully native interface. It starts from the first. Making an app native does not mean turning every panel into an OS window.

**Product choices are asked, not assumed.** For each feature in the menu the skill says what the app has today, what you would get and what it costs. Some choices need more explanation, and get it:

- where each dialog opens
- system or custom title bar
- whether the close button quits the app or hides it to the tray
- whether the app starts at login, how that works on each OS, which setting it adds and which files change
- which events become system notifications

You answer each one (**Manual**) or approve a recommended set (**Auto**).

**Evidence over appearance.** Both skills trace a feature through the whole chain and keep inspected code, a passing build, automated tests and behavior observed on the installed app apart. The desktop skill ships an acceptance checklist; the mobile skill ships a verification matrix. Something that was not tested is reported as not tested.

**Sourced and dated.** Statements in the references cite the Tauri, plugin and OS documentation they come from, with the version examined. Points that could not be confirmed are marked unverified.

## Native plugin map

Each skill maps capabilities to plugins for its platforms and names the capabilities with no official plugin. The data lives in [`shared/native-plugins.md`](shared/native-plugins.md): the support level of the 31 official plugins on all five platforms, the maintained plugins and the community candidates. It is mirrored in each skill's `references/native-plugins-data.md`.

## Repository layout

| Path | Content |
|---|---|
| `skills/tauri-native-desktop/` | `SKILL.md` and 19 reference files |
| `skills/tauri-native-mobile/` | `SKILL.md`, 37 reference files, example adapters and its own validator |
| `shared/native-plugins.md` | Plugin data shared by both skills |
| `scripts/` | Plugin validator and its tests |
| `CHANGELOG.md` | What changed in each version |

## Limits

The skills are documentation and decision guides. Plugin support levels are copied from the official plugin manifests on the date stated in each file; no plugin was built or run, and no feature was exercised on a device. Recheck versions against your lockfile and verify on the installed app. Tauri 1 and Tauri 3 are not covered.

## Validate the plugin and skill bundles

```
python scripts/validate_plugin.py
python -m unittest discover -s scripts -p "test_*.py"
cd skills/tauri-native-mobile
python scripts/validate_bundle.py
python -m unittest discover -s scripts -p "test_*.py"
```

After editing `shared/native-plugins.md`, run `python scripts/validate_plugin.py --sync-shared` to update both standalone skill copies.

## Releases

A release is a version bump in `.claude-plugin/plugin.json` plus a matching section in [`CHANGELOG.md`](CHANGELOG.md). When that reaches `main`, the release workflow runs the validators, creates the `vX.Y.Z` tag and publishes the GitHub Release with that section as its notes. The validator fails when the changelog has no section for the current version.

## License

MIT. See [LICENSE](LICENSE).
