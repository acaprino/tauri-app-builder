# Mobile plugins, insets and keyboard

Select plugins by documented support of the installed version, including individual commands. Android-only camera/auth code needs `target_os = "android"` gates, not a generic mobile gate. Separate capabilities by platform where it clarifies support; it is not mandatory to put them in a file literally named `mobile.json`.

## Insets

Do not assume Android `env(safe-area-inset-*)` is permanently unsupported or use fixed 48/24px padding. Results depend on WebView version, native edge-to-edge setup, viewport metadata and the embedding layout. Measure on the supported device matrix. If a native fallback is necessary, use WindowInsets for system bars/cutout and convert native pixels to the CSS coordinate system used by the WebView.

Give each inset one owner. The page container, header and bottom navigation must not each pay the same padding. Treat IME height separately from navigation-bar padding; don't retain the keyboard inset as a permanent safe area. Handle rotation, three-button/gesture navigation, resumed activity and a document created after the first native inset event.

If a native inset bridge is needed, validate its message origin and replay the latest measurements after the WebView signals readiness. Test OEM-specific inset dispatch, double-counted header padding and keyboard-driven viewport shrink independently. A fixed CSS constant cannot correct all three failure modes.

## Capability-specific checks

Use the [migration inventory](migration-inventory.md) to discover missing native adapters. Follow [geolocation](geolocation.md) for location/geofences, [NFC and Bluetooth](nfc-bluetooth.md) for peripherals, [device security](device-security.md) for biometric/key access, and [push/background work](push-background.md) for remote delivery and offline jobs. For local notifications, exact reminders and alarms use [notifications and alarms](notifications-alarms.md). A foreground success or permission grant alone does not establish any background delivery guarantee.

Sources: [plugin catalog](https://v2.tauri.app/plugin/), [Android edge-to-edge](https://developer.android.com/develop/ui/views/layout/edge-to-edge).
