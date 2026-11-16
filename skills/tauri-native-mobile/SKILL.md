---
name: tauri-native-mobile
description: Build, debug and review Tauri 2 Android and iOS integrations, including native permissions, camera and microphone capture, Google/Firebase sign-in, deep links, WebView insets, native builds and store delivery. Includes location, NFC/BLE, biometrics, push, background work, exact alarms and native file export; use for native mobile work, not ordinary web-only UI changes.
---

# Tauri native mobile

Standalone, generic reference for migrating web applications to Tauri mobile. Reviewed 2026-11-16. Examples are integration contracts, not a prebuilt plugin or proof of device execution.

## Work from the installed application

Identify target OS, device/WebView version, package ID, signing identity, installed version, source revision and build command. Read the project's actual lockfiles, native source, merged manifest and capabilities before changing them. Preserve existing project decisions; select Android, iOS and web adapters explicitly.

Trace a failing feature through JS invocation → Tauri capability → plugin registration → native manifest/entitlement → runtime permission → callback → UI result. A successful web build does not verify that chain. Separate confirmed defects, historical reports, retired fixes and device checks still needed.

## Read by task

| Task | Local reference |
|---|---|
| Which plugin covers a capability, support per OS, gaps with no official plugin | [native plugin map](references/native-plugins.md) |
| Audit web-to-mobile capability gaps | [migration inventory](references/migration-inventory.md) |
| Location, background journeys and geofencing | [geolocation](references/geolocation.md) |
| NFC tags, card capability boundaries and BLE peripherals | [NFC and Bluetooth](references/nfc-bluetooth.md) |
| Push, background jobs and offline sync | [push and background work](references/push-background.md) |
| Biometric unlock and credential protection | [device security](references/device-security.md) |
| Machine/project setup | [setup](references/setup.md), [mobile toolchain](references/setup-mobile.md) |
| Permission denied, no dialog, no recovery | [permissions](references/permissions.md) |
| Camera, gallery, microphone, cancellation | [camera and media](references/camera-media.md) |
| Android/iOS Google login/Firebase session | [native Google auth](references/google-auth-native.md) |
| Other OAuth, Apple, callback lifecycle | [auth architecture](references/authentication.md), [mobile auth and links](references/authentication-mobile.md) |
| Safe areas, keyboard, old WebViews | [mobile layout](references/plugins-mobile.md), [engine compatibility](references/platform-webviews.md) |
| Wrong UI in APK / missing Rust or Kotlin output | [stale builds](references/mobile-stale-builds.md), [builds](references/build-deploy-mobile.md) |
| Native plugin/JS boundary | [core plugins](references/plugins-core.md), [Rust](references/rust-patterns.md), [frontend](references/frontend-patterns.md) |
| Device investigation | [debugging](references/debugging-mobile.md), [verification matrix](references/testing.md) |
| Purchases | [IAP](references/iap.md) |
| Release | [Android](references/distribution-android.md), [iOS](references/distribution-ios.md), [mobile CI](references/ci-cd-mobile.md) |
| Streaming/performance | [IPC](references/ipc-streaming.md), [rendering](references/high-frequency-ui.md) |
| Shared desktop target (boundaries only; desktop behavior is the `tauri-native-desktop` skill) | [desktop builds](references/build-deploy-desktop.md), [shell](references/shell-plugin.md), [windows](references/window-management.md), [CI](references/ci-cd.md) |
| Notifications, timed reminders, exact alarms, snooze | [scheduling contract](references/notifications-alarms.md) |
| ZIP export, downloads, save/share files | [native file export](references/file-export.md) |
| Dependency updates and compatibility | [version maintenance](references/version-maintenance.md), [sources](references/sources.md) |

## Invariants learned from the review

- Android Google sign-in can be native; external-browser OAuth is not the only option. Keep native Firebase and JS Firebase sessions behind one explicit identity/token boundary.
- Tauri permissions, Android manifest declarations, OS runtime grants and WebView-origin authorization are separate controls. Grant only the command/resource required by the selected implementation.
- User cancellation is not denial, absence of a plugin, or a timeout. A JS timeout does not cancel a native camera request.
- Derive safe-area values from real measurements, with one layout owner. Do not turn a device's pixel values into universal constants.
- Inspect the packaged APK and installed version before blaming caches. Cargo scans watched directories recursively; verify the actual packaging pipeline.
- Check command options against the installed CLI. Pin compatible build dependencies; do not automatically choose the newest SDK/NDK/Gradle combination.
- Prefer the native path for every device capability: official plugin, then a reviewed community plugin, then a narrow Kotlin/Swift bridge. Check the [native plugin map](references/native-plugins.md) before choosing; a WebView API is a fallback.
- Native changes need native evidence. Never mark a device flow verified because TypeScript compiled or a historical commit says it was fixed.

For findings, report symptom, affected platform/version, source evidence, cause, correction and verification status. Recheck time-sensitive store requirements before submission using [sources](references/sources.md).

Run `python scripts/validate_bundle.py` and `python -m unittest discover -s scripts -p "test_*.py"` to check package integrity and validator regressions. These checks do not run mobile features. The [manifest](audit/source-manifest.json) hashes generic examples; [review status](audit/REVIEW.md) states verification limits.

For migrations, inventory each browser-dependent action (downloads, popup login, capture, timers, clipboard and links). Give each a platform adapter, cancellation/error contract and observable completion condition. Never show completion merely because a browser API returned without throwing. Apps may need notifications, exact alarms, or both: preserve each requested delivery contract.

The plugin-wide data file `../../shared/native-plugins.md` (relative to this skill's folder) holds the official plugin support matrix for all five platforms, the maintained plugins and the community candidates; the desktop skill reads the same file.

For a broad migration audit, start with the [capability inventory](references/migration-inventory.md), then load only the references for features the app actually uses. A browser API or foreground callback does not establish native background support.
