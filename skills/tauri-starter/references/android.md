# Android: check the toolchain, then build and run

Use this after the app exists (`new-app.md` or `adapt-web-app.md`). Every step below was run on an Android 16 emulator on Windows; what was not run is marked.

## 1. Check the toolchain, and stop if anything is missing

```text
node <skill-dir>/scripts/check-android.mjs
```

Expected: `{"ok":true,"missing":[]}` and exit code 0. On exit code 1 tell the user each name in `missing` and stop. This skill never installs the toolchain; `tauri-native-mobile` describes the setup. The names mean:

- `JDK`: `java -version` fails.
- `ANDROID_HOME`: not set, or not a directory. With it set, `SDK platform`, `SDK build-tools` and `adb` name what its folders lack.
- `NDK_HOME`: not set or not a directory. Use NDK r28 or newer (16 KB page size, see `tauri-native-mobile`).
- `Rust target ...`: `aarch64-linux-android` (phones) and `x86_64-linux-android` (emulators) must be installed with rustup.

## 2. Things that bite

- Keep the project and `CARGO_HOME` on the same volume: plugin sources on another volume can break the Kotlin build (see `tauri-native-mobile`).
- On Windows, Developer Mode must be on for the symlinks Tauri creates.
- `android init` installs all four Android Rust targets with rustup, which writes into `RUSTUP_HOME`. On a small system disk run it with `--skip-targets-install` and install only the two targets above.
- Record the versions you actually used (CLI, crates, JDK, Gradle, AGP, SDK platform, NDK); a newer release is not a tested combination.

## 3. Generate the Android project and build an APK

```text
npm run tauri -- android init --skip-targets-install
npm run tauri -- android build --apk --debug --target x86_64
```

`init` writes `src-tauri/gen/android`; run it after the identifier is final and review a diff before regenerating. The generated project takes its compile and target SDK from Tauri's template (37 here) and Gradle installs a missing SDK platform itself once the SDK licence is accepted. The first build takes several minutes. Expected: `src-tauri/gen/android/app/build/outputs/apk/universal/debug/app-universal-debug.apk`. The file name says universal but it holds only the ABI you asked for: check with `aapt2 dump badging <apk>` (the `native-code` line). Use `--target aarch64` for a phone.

## 4. Install and run

```text
adb install -r <apk>
adb shell monkey -p <identifier> -c android.intent.category.LAUNCHER 1
```

Expected: the page shows "Running on android", below the status bar. Observed on the emulator:

- The page origin is `http://tauri.localhost/`.
- "Open tauri.app (granted)" shows `opener: allowed` and starts the browser. "Save window state (not granted)" is refused with `Plugin not found`, because that plugin is desktop-only and is not compiled in on Android.
- The external link stays out of the webview: the page keeps its URL and the log shows the guard's line.
- A script created at run time is blocked by the CSP (`Tauri/Console` in logcat).
- The Rust log plugin writes to logcat under the library name (`adb logcat`).
- Back at the first page closes the app.

To drive the page from the computer, forward the WebView's DevTools socket: find `webview_devtools_remote_<pid>` in `adb shell cat /proc/net/unix`, then `adb forward tcp:<port> localabstract:<that name>`. This is the same view as `chrome://inspect`.

## 5. Not verified

- Live development with `npm run tauri -- android dev` and Vite on `TAURI_DEV_HOST`: Gradle finished but the CLI never installed or started the app from a non-interactive shell, in two tries of seven minutes each. Try it from a terminal you can watch before relying on it.
- A physical phone, and the `aarch64` build.

## 6. Emulator notes

Hardware acceleration must be usable (`emulator -accel-check`). On Windows the windowed emulator hung twice on a crash-report dialog; `emulator -avd <name> -no-window -gpu swiftshader_indirect` was stable, and screenshots and input still work through adb.
