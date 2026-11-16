# Native plugin map (Windows, macOS, Linux)

Part of the tauri-native-desktop references: versions, scope and limits are in [guide.md](guide.md). Bracketed names are sources; their URLs are in [sources.md](sources.md).

Which plugin or core API gives a native capability on desktop, and where none exists. Support levels and notes are copied from each plugin's `[package.metadata.platforms.support]` in the official plugins-workspace `v2` branch, observed 2026-11-16. They are the maintainers' declaration, not a test on your package: compare the lockfile and verify each command you use. [official plugins table], [plugin manifests].

## Selection order

1. **Tauri core**: menus, tray, window effects, badge, progress bar and window management are in the `tauri` crate, not in plugins ([os-integration.md](os-integration.md), [frame.md](frame.md)).
2. **Official plugin** with `full` or `partial` support on every shipped OS. Read the note.
3. **Rust crate behind an app command** when the OS service has no plugin (keychain, Windows Hello). The command gets its own capability and input validation ([boundaries.md](boundaries.md)).
4. **Community plugin**, after reading its native source, permissions, last release and open issues.

A WebView API (`getUserMedia`, `navigator.geolocation`, Web Notifications) follows the engine's permission model and differs between WebView2, WKWebView and WebKitGTK: treat it as a per-engine fallback to test, not as the native path.

Every plugin needs five matching pieces: JS package, Rust crate, registration in the builder, platform prerequisites and a capability scoped to the windows that call it.

## Official plugins on desktop

All are `full` on Windows, macOS and Linux unless noted.

| Need | Plugin (crate `tauri-plugin-…`) | Desktop limit / note |
|---|---|---|
| Open/save/message dialogs | `dialog` 2.8.4 | Linux backend choice in [os-integration.md](os-integration.md) |
| Disk access | `fs` 2.7.1 | No write access to `$RESOURCES` on macOS and Linux; on Windows, MSI/NSIS `perMachine` and `both` installs need admin rights to write there |
| Keep user-granted paths across restarts | `persisted-scope` 2.4.3 | Register after `fs` |
| Desktop notifications | `notification` 2.8.1 | Windows: only works for installed apps; shows the PowerShell name and icon in development ([notifications.md](notifications.md)) |
| Biometric prompt | `biometric` 2.5.0 | **macOS only** on desktop; Windows and Linux `none` |
| Login callback, URL handler | `deep-link` 2.6.3 | macOS `partial`: links must be registered in config, no runtime registration |
| Open URL or file in the default app, reveal in file manager | `opener` 2.7.3 | Scope the allowed targets |
| Second launch, forwarded arguments | `single-instance` 2.5.5 | Register first ([os-integration.md](os-integration.md)) |
| Restore window size and position | `window-state` 2.5.1 | — |
| Place a window at a known position, tray-relative | `positioner` 2.4.0 | — |
| Start at login | `autostart` 2.7.0 | Product choice, user-controllable |
| System-wide shortcuts | `global-shortcut` 2.4.1 | Needs a stronger reason than in-app shortcuts |
| In-app updates | `updater` 2.14.1 | Signing required |
| Clipboard (text, image, HTML) | `clipboard-manager` 2.5.0 | — |
| Settings | `store` 2.5.1 | Not encrypted: no credentials |
| Encrypted vault | `stronghold` 2.4.0 | App-managed vault, not the OS credential store |
| SQL databases | `sql` 2.6.0 | — |
| HTTP, upload, WebSocket from Rust | `http` 2.9.0, `upload` 2.5.0, `websocket` 2.5.1 | Scope the allowed URLs |
| Logging | `log` 2.10.2 | — |
| OS, version, arch, locale | `os` 2.4.0 | — |
| Exit, relaunch | `process` 2.4.0 | Restart and locks in [recovery.md](recovery.md) |
| Child processes, sidecars | `shell` 2.6.0 | Scope every command and argument |
| Command-line arguments | `cli` 2.5.0 | — |
| Assets over localhost | `localhost` 2.4.0 | The plugin page warns of considerable security risks |

Declared `none` on all three desktop systems: `barcode-scanner`, `geolocation`, `haptics`, `nfc`, `torch`.

## Needs with no official desktop plugin

Do not promise these from the official catalog. The middle column names the native service to reach; none of these paths was built or tested for this skill.

| Need | Native service | Decision |
|---|---|---|
| Credentials and tokens | Windows Credential Manager; macOS Keychain; Secret Service / KWallet on Linux | A Rust keychain crate behind an app command. Keep secrets out of `store`, URLs and other WebViews ([boundaries.md](boundaries.md)). Linux needs a running secret service: define the fallback |
| Biometric or OS re-authentication on Windows/Linux | Windows Hello (`UserConsentVerifier`); polkit / fprintd | Platform code or a community plugin; `biometric` covers macOS only. A prompt does not protect a secret unless the key is bound to it |
| Sign-in (OAuth) | System browser with PKCE and a loopback or custom-scheme redirect | `opener` to launch, `deep-link` to return, `single-instance` so a running app receives the callback on Windows and Linux; validate state and the redirect before use. Not an embedded login WebView |
| Camera and microphone | Engine media capture; AVFoundation / Media Foundation / PipeWire for native capture | WebView `getUserMedia` first: macOS needs the usage-description keys in `Info.plist`, WebView2 and WebKitGTK have their own permission handling. Test per engine on the installed package |
| Location | Windows Geolocation API; CoreLocation; GeoClue | `geolocation` is mobile-only. Engine geolocation or platform code, with the OS permission |
| Bluetooth, serial, USB | OS stacks | Community plugin or Rust crate behind a command |
| Screen capture, system permissions on macOS | ScreenCaptureKit, TCC | Community plugin or platform code; the user grants these in System Settings |
| Native context menu | Tauri core `Menu` popup | Core API, no plugin ([context-menus.md](context-menus.md)) |

## Community candidates

Listed in awesome-tauri with a Tauri v2 tag on 2026-11-16. None was installed, built or reviewed for this skill: evaluate before use. [awesome-tauri plugins].

| Need | Candidate |
|---|---|
| Disable default browser shortcuts | [tauri-plugin-prevent-default](https://github.com/ferreira-tb/tauri-plugin-prevent-default) |
| macOS panel windows, status-bar popover | [tauri-nspanel](https://github.com/ahkohd/tauri-nspanel), [tauri-nspopover-plugin](https://github.com/freethinkel/tauri-nspopover-plugin) |
| Check and request macOS permissions | [tauri-plugin-macos-permissions](https://github.com/ayangweb/tauri-plugin-macos-permissions) |
| macOS drag-out of files | [tauri-plugin-dragout](https://github.com/alexqqqqqq777/tauri-plugin-dragout) |
| Clipboard with files, RTF and change monitoring | [tauri-plugin-clipboard](https://github.com/CrossCopy/tauri-plugin-clipboard) |
| Bluetooth LE client | [tauri-plugin-blec](https://github.com/MnlPhlp/tauri-plugin-blec) |
| Serial port | [tauri-plugin-serialplugin](https://github.com/s00d/tauri-plugin-serialplugin) |
| Window and monitor screenshots | [tauri-plugin-screenshots](https://github.com/ayangweb/tauri-plugin-screenshots) |
| In-app purchases (macOS, Windows) | [tauri-plugin-iap](https://github.com/Choochmeque/tauri-plugin-iap) |
| Crash and error reporting | [sentry-tauri](https://github.com/timfish/sentry-tauri) |
| Device info (battery, network, storage) | [tauri-plugin-device-info](https://github.com/edisdev/tauri-plugin-device-info) |

The maintained mobile plugins do not fill desktop gaps: `tauri-plugin-native-camera` is Android-only and `tauri-plugin-google-auth-firebase` returns `UnsupportedPlatform` on desktop, so gate both behind mobile targets in a shared codebase and keep the desktop paths above.

`window-vibrancy` and `window-shadows` are Tauri 1 plugins: in Tauri 2 the effects are in core ([frame.md](frame.md)).
