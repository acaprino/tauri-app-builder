# Plugin integration

Choose the plugin from the [native plugin map](native-plugins.md). For each feature check five matching pieces: JS package, Rust crate, registration, native platform module and exact capability/scope. Use the installed plugin's command support table; a plugin supporting Android does not imply that all its desktop methods work there.

Use opener for external URLs where supported; don't assume it always selects Custom Tabs or provides an OAuth authentication-session API. Native Google sign-in is a separate integration. Scope opened URLs and validate untrusted destinations.

Store persists JSON and supports configurable auto-save. Use the installed API (`load`/`Store.load`) and an explicit save when a flush is required. It is not encrypted credential storage. Filesystem permissions still require an appropriate path scope; AppData is not the only usable iOS sandbox directory. Resolve platform paths rather than copying Windows absolute paths.

Native HTTP avoids browser CORS enforcement but still needs authentication, TLS, URL validation and plugin scopes. Do not replace a broken backend origin policy with unrestricted native HTTP access by default. SQL migrations, notification configuration and log targets must match the actual plugin version.

Split capability files by target OS (`src-tauri/capabilities/mobile.json` for shared mobile plugins; `src-tauri/capabilities/android.json` for Android-only plugins so `tauri-build` does not reject missing ACL manifests on iOS):

```json
{
  "identifier": "mobile-shared",
  "description": "Shared Android and iOS permissions for main window",
  "platforms": ["android", "iOS"],
  "windows": ["main"],
  "permissions": ["biometric:allow-authenticate"]
}
```

```json
{
  "identifier": "android-camera",
  "description": "Android-only camera permission for main window",
  "platforms": ["android"],
  "windows": ["main"],
  "permissions": ["native-camera:allow-take-picture"]
}
```

```rust
// src-tauri/src/lib.rs — gate mobile-only plugins behind target cfg
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let builder = tauri::Builder::default();
    #[cfg(mobile)]
    let builder = builder.plugin(tauri_plugin_biometric::init());
    #[cfg(target_os = "android")]
    let builder = builder.plugin(tauri_plugin_native_camera::init());
    builder.run(tauri::generate_context!()).expect("error while running tauri application");
}
```

Sources: [catalog](https://v2.tauri.app/plugin/), [Store](https://v2.tauri.app/plugin/store/), [capabilities](https://v2.tauri.app/security/capabilities/).
