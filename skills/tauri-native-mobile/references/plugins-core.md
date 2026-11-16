# Plugin integration

Choose the plugin from the [native plugin map](native-plugins.md). For each feature check five matching pieces: JS package, Rust crate, registration, native platform module and exact capability/scope. Use the installed plugin's command support table; a plugin supporting Android does not imply that all its desktop methods work there.

Use opener for external URLs where supported; don't assume it always selects Custom Tabs or provides an OAuth authentication-session API. Native Google sign-in is a separate integration. Scope opened URLs and validate untrusted destinations.

Store persists JSON and supports configurable auto-save. Use the installed API (`load`/`Store.load`) and an explicit save when a flush is required. It is not encrypted credential storage. Filesystem permissions still require an appropriate path scope; AppData is not the only usable iOS sandbox directory. Resolve platform paths rather than copying Windows absolute paths.

Native HTTP avoids browser CORS enforcement but still needs authentication, TLS, URL validation and plugin scopes. Do not replace a broken backend origin policy with unrestricted native HTTP access by default. SQL migrations, notification configuration and log targets must match the actual plugin version.

Sources: [catalog](https://v2.tauri.app/plugin/), [Store](https://v2.tauri.app/plugin/store/), [capabilities](https://v2.tauri.app/security/capabilities/).
