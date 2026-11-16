# Native plugin map (Android and iOS)

Which plugin gives a native capability on mobile, and where no official plugin exists. Support levels and notes are copied from each plugin's `[package.metadata.platforms.support]` in the official plugins-workspace `v2` branch, observed 2026-11-16. They are the maintainers' declaration, not a device test: recheck the installed version, and verify each command you use.

## Selection order

1. **Official plugin** with `full` or `partial` support on the target OS. Read the note: `partial` often removes the method you wanted.
2. **Maintained native plugin** from the section below, where it covers the need and the target OS.
3. **Community plugin**, after reading its native source, permissions, last release and open issues. Treat it as third-party code with native privileges.
4. **Own plugin or narrow native bridge** (Kotlin/Swift) when nothing fits. Scaffold with the installed CLI's `tauri plugin new` and its Android/iOS options; check `tauri plugin --help` for the exact flags.

A WebView API (`getUserMedia`, `navigator.geolocation`, Web Notifications) is a fallback, not the native path: it follows the WebView's own permission model and usually has no background behavior.

For every plugin, check the five pieces in [plugin integration](plugins-core.md): JS package, Rust crate, registration, native module, capability/scope.

## Official plugins that run on mobile

| Need | Plugin (crate `tauri-plugin-…`) | Android | iOS | Mobile limit / note | Read next |
|---|---|---|---|---|---|
| Biometric prompt (fingerprint, face) | `biometric` 2.5.0 | full | full | A prompt alone does not protect a secret | [device security](device-security.md) |
| Location, tracking | `geolocation` 2.5.0 | full | full | Background and geofencing need extra native work | [geolocation](geolocation.md) |
| QR / barcode scan with the camera | `barcode-scanner` 2.5.3 | full | full | Scanning only: not photo or video capture | [camera and media](camera-media.md) |
| NFC tag read/write | `nfc` 2.4.2 | full | full | Tags, not card emulation | [NFC and Bluetooth](nfc-bluetooth.md) |
| Local notifications | `notification` 2.8.1 | full | full | Remote push is not included | [notifications and alarms](notifications-alarms.md), [push](push-background.md) |
| Haptic feedback | `haptics` 2.4.2 | full | full | Android vibration is not standardized across devices | — |
| Flashlight | `torch` 2.0.0 | full | full | — | — |
| App links / custom schemes (login callbacks) | `deep-link` 2.6.3 | partial | partial | Links must be registered in config; no runtime registration | [mobile auth and links](authentication-mobile.md) |
| Open an external URL | `opener` 2.7.3 | partial | partial | Only URLs via `open`; no file open or reveal | [plugin integration](plugins-core.md) |
| File/message dialogs | `dialog` 2.8.4 | partial | partial | No folder picker | [file export](file-export.md) |
| File access | `fs` 2.7.1 | partial | partial | Restricted to the application folder by default | [file export](file-export.md) |
| Clipboard | `clipboard-manager` 2.5.0 | partial | partial | Plain text only | — |
| Key-value settings | `store` 2.5.1 | full | full | Not encrypted: no credentials | [plugin integration](plugins-core.md) |
| Encrypted vault | `stronghold` 2.4.0 | full | full | App-managed vault, not the OS Keychain/Keystore | [device security](device-security.md) |
| SQLite and other SQL | `sql` 2.6.0 | full | full | Migrations must match the plugin version | [plugin integration](plugins-core.md) |
| HTTP from Rust | `http` 2.9.0 | full | full | Scope the allowed URLs | [plugin integration](plugins-core.md) |
| Upload/download to disk | `upload` 2.5.0 | full | full | — | — |
| WebSocket from Rust | `websocket` 2.5.1 | full | full | — | — |
| Logging | `log` 2.10.2 | full | full | — | [debugging](debugging-mobile.md) |
| OS, version, arch | `os` 2.4.0 | full | full | — | [frontend](frontend-patterns.md) |
| Persist runtime fs scopes | `persisted-scope` 2.4.3 | full | full | Register after `fs` | — |
| Shell | `shell` 2.6.0 | partial | partial | Only URLs via `open`; no child processes | [shell](shell-plugin.md) |

Declared `none` on Android and iOS: `autostart`, `cli`, `global-shortcut`, `localhost`, `positioner`, `process`, `single-instance`, `updater`, `window-state`. Store updates replace `updater` on mobile.

## Maintained native plugins

Native plugins already built for needs the official catalog does not cover. Use them before writing a new bridge. Facts below come from each repository's README, manifest, permission files and file tree on 2026-11-16; none was built or run for this skill.

| Need | Plugin | Android | iOS | Desktop |
|---|---|---|---|---|
| Photo capture with the system camera app | [tauri-plugin-native-camera](https://github.com/acaprino/tauri-plugin-native-camera) 0.1.0 (fork) | yes | no | no |
| Native Google sign-in with a Firebase session | [tauri-plugin-google-auth-firebase](https://github.com/acaprino/tauri-plugin-google-auth-firebase) 0.1.0 | yes, API 24+ | no native module | every command returns `UnsupportedPlatform` |
| In-app purchases and subscriptions | [tauri-plugin-iap](https://github.com/Choochmeque/tauri-plugin-iap) 0.9.0 (upstream, vendored) | Play Billing v8 | StoreKit 2, iOS 15+ | macOS 13+, Windows Store |

**tauri-plugin-native-camera.** Launches `ACTION_IMAGE_CAPTURE`, so the device's own camera app takes the photo. `takePicture()` from `tauri-plugin-native-camera-api` returns base64 JPEG with width and height, EXIF rotation applied and the long side capped at 2048 px. Grant `native-camera:allow-take-picture`: the `default` set is empty and authorizes nothing. Depend on the fork by git or path, under `cfg(target_os = "android")`: it annotates the permission result with `@PermissionCallback` and drops the `FLAG_GRANT_READ_URI_PERMISSION` over-grant, and the crates.io 0.1.0 release is the upstream package without those commits. Photos only: video, gallery pick and iOS still need another path. Contract and failure cases in [camera and media](camera-media.md) and [permissions](permissions.md).

**tauri-plugin-google-auth-firebase.** Credential Manager shows the system bottom sheet, then the Firebase Android SDK signs in; the WebView receives a flat user object and a Firebase ID token, with no Firebase JS SDK at runtime. Four commands: `signInWithGoogle`, `signOut`, `getCurrentUser`, `getIdToken`. Grant `google-auth-firebase:default`. Register behind `#[cfg(mobile)]` and depend by git or path. The host app applies the `google-services` Gradle plugin and supplies `google-services.json`; the server client ID is the Web OAuth client, and debug, release and Play App Signing SHA-1 fingerprints must all be registered. `USER_CANCELLED` is not an error to retry. iOS needs GoogleSignIn-iOS or another route. Details in [native Google auth](google-auth-native.md).

**tauri-plugin-iap.** Third-party plugin kept as a vendored copy. JS package `@choochmeque/tauri-plugin-iap-api`. Purchase verification and entitlement stay on the backend: [IAP](iap.md).

## Needs with no official plugin

Do not promise these from the official catalog. Check the maintained plugins above first; otherwise each needs a community plugin or a native bridge, with its own manifest/entitlement and runtime permission.

| Need | Native API to reach | Notes | Read next |
|---|---|---|---|
| Photo/video capture, gallery pick | CameraX / Photo Picker; AVFoundation / PHPicker | Android photos: `tauri-plugin-native-camera` above. Video, gallery and iOS remain open; `barcode-scanner` does not capture media | [camera and media](camera-media.md) |
| Microphone recording | MediaRecorder / AVAudioSession | WebView capture depends on WebView permission handling | [camera and media](camera-media.md) |
| Credentials in OS secure storage | Android Keystore; iOS Keychain | `store` is plaintext; biometric-bound keys need native key setup | [device security](device-security.md) |
| Google sign-in | Credential Manager; GoogleSignIn-iOS | Android: `tauri-plugin-google-auth-firebase` above. iOS remains open; external-browser OAuth is the alternative | [native Google auth](google-auth-native.md) |
| Apple sign-in, OAuth session | AuthenticationServices (`ASWebAuthenticationSession`); Custom Tabs | `opener` is not an auth-session API | [auth architecture](authentication.md) |
| Remote push | FCM; APNs | `notification` schedules local notifications only | [push and background work](push-background.md) |
| Background jobs, offline sync | WorkManager; BGTaskScheduler | — | [push and background work](push-background.md) |
| Exact alarms | AlarmManager; UNCalendarNotificationTrigger | — | [notifications and alarms](notifications-alarms.md) |
| Bluetooth LE | BluetoothLeScanner/Gatt; CoreBluetooth | — | [NFC and Bluetooth](nfc-bluetooth.md) |
| In-app purchases | Play Billing; StoreKit | `tauri-plugin-iap` above; backend verification still required | [IAP](iap.md) |
| Share sheet, save to user-chosen location | Sharesheet / SAF; UIActivityViewController / document picker | `fs` stays in the app folder | [file export](file-export.md) |
| Contacts, calendar, health, sensors | Platform frameworks | — | [migration inventory](migration-inventory.md) |

## Community candidates

Listed in awesome-tauri with a Tauri v2 tag on 2026-11-16. None was installed, built or reviewed for this skill: evaluate before use.

| Need | Candidate |
|---|---|
| Android file access beyond the app folder | [tauri-plugin-android-fs](https://github.com/aiueo13/tauri-plugin-android-fs) |
| iOS auth session with keychain access | [tauri-plugin-auth](https://github.com/inKibra/tauri-plugins/tree/main/packages/tauri-plugin-auth) |
| Bluetooth LE client | [tauri-plugin-blec](https://github.com/MnlPhlp/tauri-plugin-blec) |
| In-app review prompt | [tauri-plugin-in-app-review](https://github.com/Gbyte-Group/tauri-plugin-in-app-review) |
| iOS Photos library | [tauri-plugin-ios-photos](https://github.com/Gbyte-Group/tauri-plugin-ios-photos) |
| Share sheet (send) | [tauri-plugin-sharesheet](https://github.com/buildyourwebapp/tauri-plugin-sharesheet) |
| Share target (receive) | [tauri-plugin-mobile-sharetarget](https://github.com/IT-ess/tauri-plugin-mobile-sharetarget) |
| View/share files | [tauri-plugin-view](https://github.com/ecmel/tauri-plugin-view) |
| Keep screen on | [tauri-plugin-keep-screen-on](https://gitlab.com/cristofa/tauri-plugin-keep-screen-on) |
| Battery optimization exemption (Android) | [tauri-plugin-android-battery-optimization](https://github.com/NeoHuncho/tauri-plugin-android-battery-optimization) |
| Home-screen widgets | [tauri-plugin-widgets](https://github.com/s00d/tauri-plugin-widgets) |
| Device info (battery, network, storage) | [tauri-plugin-device-info](https://github.com/edisdev/tauri-plugin-device-info) |

Sources: [official plugins table](https://github.com/tauri-apps/plugins-workspace/blob/v2/README.md), [plugin manifests](https://github.com/tauri-apps/plugins-workspace/tree/v2/plugins), [plugin catalog](https://v2.tauri.app/plugin/), [awesome-tauri plugins](https://github.com/tauri-apps/awesome-tauri#plugins). The official README marks several desktop-first plugins `?` on mobile where the manifests declare a level; the manifest is the more specific statement.
