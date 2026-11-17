# Packaging, installers, updates and sidecars

Part of the tauri-native-desktop references: versions, scope and limits are in [guide.md](guide.md). Bracketed names are sources; their URLs are in [sources.md](sources.md).

## Installers and OS identity

Build and verify the actual installer format shipped to users on each platform; `cargo build` or `tauri dev` does not exercise installer permissions, file associations, toast identity or notarization. [Distribute overview].

- **Windows.** NSIS builds a `.exe` setup installer (not a `.nsis` user artifact); WiX builds `.msi`. Do not manually pin an obsolete WiX toolset unless the resolved bundler requires it. With `installMode` set to `perMachine` or `both`, `$RESOURCES` is read-only to a standard user (`fs` plugin manifest note in [native-plugins.md](native-plugins.md)); store mutable user data in `app_data_dir` / `app_local_data_dir`. Windows notifications and taskbar jump lists depend on the installed app's shortcut and AUMID ([notifications.md](notifications.md), [os-integration.md](os-integration.md)). [Windows installer].
- **macOS.** Ship a signed and notarized `.app` / `.dmg` with matching bundle identifier, `Info.plist` usage descriptions (camera, microphone, location when used) and only the entitlements actually needed. Gatekeeper behavior differs from an unsigned local build: verify first launch from a downloaded artifact. [macOS signing].
- **Linux.** Match the `.desktop` entry, icon, `StartupWMClass` (X11) and `app.enableGTKAppId` (Wayland) as covered in [frame.md](frame.md). For `.deb`, `.rpm`, AppImage or Flatpak, verify WebKitGTK and portal runtime dependencies (`xdg-desktop-portal`) on clean target sessions. [Linux packaging].

## In-app updates

Use `tauri-plugin-updater` for desktop self-update when the product distributes outside an OS store. Set `bundle.createUpdaterArtifacts` to `true` in Tauri 2; use `"v1Compatible"` only while migrating an existing Tauri v1 install base (`"v2Compatible"` is not a valid setting). [Updater].

Keep **OS code signing** (Authenticode, Developer ID/notarization) separate from **updater artifact signing** (minisign keypair). Every update requires a valid updater signature verified against the public key embedded in `tauri.conf.json`. Never regenerate the updater private key to "fix" a signature mismatch without a dual-signed transition plan, or installed releases will reject future updates. Before restarting into an update, persist user state and release app-owned locks ([recovery.md](recovery.md)). Test upgrading from the previous installed version, not only fresh installs. [Updater].

## Sidecars and scoped shell execution

Prefer in-process Rust crates over child processes where practical: every helper launched at startup adds failure modes (antivirus quarantine, missing runtime DLLs, orphaned children and cold-start latency). When a binary sidecar is required, package it through `bundle.externalBin` with the exact target-triple filename suffix (`name-<target-triple>[.exe]`) and verify it inside the installed bundle. [Sidecar], [Shell plugin].

Scope `tauri-plugin-shell` capabilities narrowly per window, executable and fixed argument shape. A regex validator such as `.*` grants arbitrary argument injection rather than meaningful protection; keep executable paths separate from shell command strings, bound execution time, drain `stdout`/`stderr` so pipes cannot deadlock, and terminate owned children on window close or `RunEvent::Exit`. [Shell plugin].

## Release pipeline checks

Build each desktop bundle on its native target OS runner (or a verified signing pipeline), keep debug symbols alongside the release artifacts, and ensure downstream release/updater jobs publish the exact binary that passed verification. A green frontend or `cargo check` job does not validate bundler scripts, installer elevation, signing or WebView startup on the packaged app. [GitHub Actions].
