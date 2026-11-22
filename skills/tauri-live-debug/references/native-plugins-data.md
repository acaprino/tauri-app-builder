# Native plugin data (shared by both skills)

Shared reference for `tauri-native-desktop` and `tauri-native-mobile`. Each skill's `references/native-plugins.md` says which plugin to choose for a need and what to read next; this file holds the data both rely on, so it is stated once.

Observed 2026-11-16. Levels and notes are copied from each plugin's `[package.metadata.platforms.support]` in the official plugins-workspace `v2` branch. They are the maintainers' declaration, not a test: compare the versions with the project's lockfile and verify every command you use on the installed app. No plugin listed here was built or run for these skills.

## Official plugins

Crate name is `tauri-plugin-<name>`; the JS package is `@tauri-apps/plugin-<name>`. `full`, `partial` and `none` are the declared support levels.

| Plugin | Version | Windows | macOS | Linux | Android | iOS | Declared notes |
|---|---|---|---|---|---|---|---|
| `autostart` | 2.7.0 | full | full | full | none | none | — |
| `barcode-scanner` | 2.5.3 | none | none | none | full | full | — |
| `biometric` | 2.5.0 | none | full | none | full | full | — |
| `cli` | 2.5.0 | full | full | full | none | none | — |
| `clipboard-manager` | 2.5.0 | full | full | full | partial | partial | Android/iOS: Only plain-text content support |
| `deep-link` | 2.6.3 | full | partial | full | partial | partial | macOS/Android/iOS: Deep links must be registered in config. Dynamic registration at runtime is not supported. |
| `dialog` | 2.8.4 | full | full | full | partial | partial | Android/iOS: Does not support folder picker |
| `fs` | 2.7.1 | full | full | full | partial | partial | Windows: Apps installed via MSI or NSIS in `perMachine` and `both` mode require admin permissions for write access in `$RESOURCES` folder; macOS/Linux: No write access to `$RESOURCES` folder; Android/iOS: Access is restricted to Application folder by default |
| `geolocation` | 2.5.0 | none | none | none | full | full | — |
| `global-shortcut` | 2.4.1 | full | full | full | none | none | — |
| `haptics` | 2.4.2 | none | none | none | full | full | — |
| `http` | 2.9.0 | full | full | full | full | full | — |
| `localhost` | 2.4.0 | full | full | full | none | none | — |
| `log` | 2.10.2 | full | full | full | full | full | — |
| `nfc` | 2.4.2 | none | none | none | full | full | — |
| `notification` | 2.8.1 | full | full | full | full | full | Windows: Only works for installed apps. Shows powershell name & icon in development. |
| `opener` | 2.7.3 | full | full | full | partial | partial | Android/iOS: Only allows to open URLs via `open` |
| `os` | 2.4.0 | full | full | full | full | full | — |
| `persisted-scope` | 2.4.3 | full | full | full | full | full | — |
| `positioner` | 2.4.0 | full | full | full | none | none | — |
| `process` | 2.4.0 | full | full | full | none | none | — |
| `shell` | 2.6.0 | full | full | full | partial | partial | Android/iOS: Only allows to open URLs via `open` |
| `single-instance` | 2.5.5 | full | full | full | none | none | — |
| `sql` | 2.6.0 | full | full | full | full | full | — |
| `store` | 2.5.1 | full | full | full | full | full | — |
| `stronghold` | 2.4.0 | full | full | full | full | full | — |
| `torch` | 2.0.0 | none | none | none | full | full | — |
| `updater` | 2.14.1 | full | full | full | none | none | — |
| `upload` | 2.5.0 | full | full | full | full | full | — |
| `websocket` | 2.5.1 | full | full | full | full | full | — |
| `window-state` | 2.5.1 | full | full | full | none | none | — |

The repository README marks several of these `?` on platforms where the manifest declares a level; the manifest is the more specific statement.

`stronghold`: do not choose it for new work. A Tauri maintainer wrote in September 2023 that it "is no longer recommended and will be deprecated and therefore removed in v3" ([discussion 7846](https://github.com/orgs/tauri-apps/discussions/7846)). The plugin's own pages carry no notice and v3 alpha releases exist, so the removal is announced, not done. For secrets use the OS credential store: each skill's credentials reference says how.

## Maintained plugins

Native plugins built for needs the official catalog does not cover. Integration details are in the mobile skill's `references/native-plugins.md`.

| Plugin | Covers | Android | iOS | Desktop |
|---|---|---|---|---|
| [tauri-plugin-native-camera](https://github.com/acaprino/tauri-plugin-native-camera) 0.1.0 (fork, fixes on `main`) | Photo capture with the system camera app | yes | no | no |
| [tauri-plugin-google-auth-firebase](https://github.com/acaprino/tauri-plugin-google-auth-firebase) 0.1.0 | Native Google sign-in with a Firebase session | yes, API 24+ | no native module | every command returns `UnsupportedPlatform` |
| [tauri-plugin-iap](https://github.com/Choochmeque/tauri-plugin-iap) 0.9.0 (third party) | In-app purchases and subscriptions | Play Billing | StoreKit 2, iOS 15+ | macOS 13+, Windows Store |

Consume them as git dependencies pinned by full commit; for Google sign-in pin the crate and the JS package to the same commit.

## Community candidates

Listed in awesome-tauri with a Tauri v2 tag on 2026-11-16. None was installed, built or reviewed: read the native source, permissions, last release and open issues before use, and treat each as third-party code with native privileges.

| Need | Candidate | Where |
|---|---|---|
| Android file access beyond the app folder | [tauri-plugin-android-fs](https://github.com/aiueo13/tauri-plugin-android-fs) | mobile |
| iOS auth session with keychain access | [tauri-plugin-auth](https://github.com/inKibra/tauri-plugins/tree/main/packages/tauri-plugin-auth) | mobile |
| In-app review prompt | [tauri-plugin-in-app-review](https://github.com/Gbyte-Group/tauri-plugin-in-app-review) | mobile |
| iOS Photos library | [tauri-plugin-ios-photos](https://github.com/Gbyte-Group/tauri-plugin-ios-photos) | mobile |
| Share sheet (send) | [tauri-plugin-sharesheet](https://github.com/buildyourwebapp/tauri-plugin-sharesheet) | mobile |
| Share target (receive) | [tauri-plugin-mobile-sharetarget](https://github.com/IT-ess/tauri-plugin-mobile-sharetarget) | mobile |
| View/share files | [tauri-plugin-view](https://github.com/ecmel/tauri-plugin-view) | mobile |
| Keep screen on | [tauri-plugin-keep-screen-on](https://gitlab.com/cristofa/tauri-plugin-keep-screen-on) | mobile |
| Battery optimization exemption | [tauri-plugin-android-battery-optimization](https://github.com/NeoHuncho/tauri-plugin-android-battery-optimization) | mobile |
| Home-screen widgets | [tauri-plugin-widgets](https://github.com/s00d/tauri-plugin-widgets) | mobile, desktop |
| Bluetooth LE client | [tauri-plugin-blec](https://github.com/MnlPhlp/tauri-plugin-blec) | mobile, desktop |
| Device info (battery, network, storage) | [tauri-plugin-device-info](https://github.com/edisdev/tauri-plugin-device-info) | mobile, desktop |
| Disable default browser shortcuts | [tauri-plugin-prevent-default](https://github.com/ferreira-tb/tauri-plugin-prevent-default) | desktop |
| macOS panel windows, status-bar popover | [tauri-nspanel](https://github.com/ahkohd/tauri-nspanel), [tauri-nspopover-plugin](https://github.com/freethinkel/tauri-nspopover-plugin) | desktop |
| Check and request macOS permissions | [tauri-plugin-macos-permissions](https://github.com/ayangweb/tauri-plugin-macos-permissions) | desktop |
| macOS drag-out of files | [tauri-plugin-dragout](https://github.com/alexqqqqqq777/tauri-plugin-dragout) | desktop |
| Clipboard with files, RTF and change monitoring | [tauri-plugin-clipboard](https://github.com/CrossCopy/tauri-plugin-clipboard) | desktop |
| Serial port | [tauri-plugin-serialplugin](https://github.com/s00d/tauri-plugin-serialplugin) | desktop |
| Window and monitor screenshots | [tauri-plugin-screenshots](https://github.com/ayangweb/tauri-plugin-screenshots) | desktop |
| Crash and error reporting | [sentry-tauri](https://github.com/timfish/sentry-tauri) | desktop |

## Sources

- Official plugins table: https://github.com/tauri-apps/plugins-workspace/blob/v2/README.md
- Plugin manifests: https://github.com/tauri-apps/plugins-workspace/tree/v2/plugins
- Plugin catalog: https://v2.tauri.app/plugin/
- awesome-tauri plugins: https://github.com/tauri-apps/awesome-tauri#plugins
