---
name: tauri-starter
description: "Use when starting a new Tauri 2 app, or wrapping an existing web app in Tauri 2, for Windows and Android: it adds one shared src-tauri core with least-privilege capabilities, a minimal web page for new apps and a check of the Android toolchain, then hands over to tauri-native-desktop and tauri-native-mobile. Not for auditing an existing Tauri app or for visual design."
---

# Tauri Starter

Start a Tauri 2 app that runs on Windows and Android from one shared `src-tauri` core, either as a new app or by wrapping an existing web app. After the start, `tauri-native-desktop` owns desktop behavior and `tauri-native-mobile` owns Android behavior. This skill adds no visual layer and no UI framework.

## Pick the path

- **New app**, from an empty directory: [new-app.md](references/new-app.md). The part of the core each file is for: [wiring.md](references/wiring.md).
- **Existing web app**, to wrap in Tauri: `references/adapt-web-app.md`.

Both paths use the same core. The new-app path also adds a minimal frontend with plain HTML and TypeScript; the adapt path leaves the host app's frontend alone and edits its files only after the user approves a shown diff.

## The core

- One `src-tauri` for both platforms: desktop-only dependencies behind `cfg` and target-specific tables, one capability file per platform, a Content Security Policy that is not null.
- Only what runs and is observed: window state, single instance, an opener with a navigation guard, logging. Everything else (updater, tray, notifications, deep links, sign-in) belongs to the two native skills.
- The system title bar stays the default. Title bar, close behavior, dialog placement and notification delivery are the choices `tauri-native-desktop` asks the user to make.
- Pin the Tauri CLI per project as an npm dev dependency and run it with `npm run tauri -- ...`; never rely on a global CLI.

## Before any Android step

Run the toolchain check in [android.md](references/android.md) (`scripts/check-android.mjs`): JDK, SDK platform, build-tools, NDK, the Rust Android targets, `ANDROID_HOME`, `NDK_HOME` and `adb`. When something is missing, name it and stop. This skill never installs the Android toolchain; setup is described in `tauri-native-mobile`. The same page has the build, install and run steps.

## Hand-off

Once the app starts, move to `tauri-native-desktop` for windows, dialogs, frame, notifications and packaging, and to `tauri-native-mobile` for permissions, capture, sign-in, builds and store delivery. Choose plugins from [native-plugins-data.md](references/native-plugins-data.md): check the Windows and Android columns before adding one.
