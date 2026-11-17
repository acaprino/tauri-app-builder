# Desktop companion builds

Retained only for projects sharing a desktop target with mobile; desktop behavior itself belongs to the `tauri-native-desktop` skill in this plugin. Use the installed Tauri bundler's supported installer formats and signing setup. NSIS produces an executable installer, not a `.nsis` end-user artifact. Don't manually install an old WiX toolchain unless the selected Tauri version needs it.

Use current updater configuration; `createUpdaterArtifacts: true` is supported (use `"v1Compatible"` only when migrating from Tauri v1; `"v2Compatible"` is not a valid setting). Preserve signing keys, inspect the actual artifact/signature format and test updates from an installed previous version. Do not regenerate a private key to 'fix' a signature mismatch without a key-transition plan.

Desktop updater recipes do not authorize bypassing mobile store delivery. Keep OS signing, macOS notarization and updater signatures distinct.

Source: [Tauri updater](https://v2.tauri.app/plugin/updater/).
