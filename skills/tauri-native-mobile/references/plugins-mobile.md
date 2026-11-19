# Mobile plugins, insets and keyboard

Select plugins by documented support of the installed version, including individual commands. Android-only camera/auth code needs `target_os = "android"` gates, not a generic mobile gate. Separate capabilities by platform where it clarifies support; it is not mandatory to put them in a file literally named `mobile.json`.

## Insets

Do not assume Android `env(safe-area-inset-*)` is permanently unsupported or use fixed 48/24px padding. Results depend on WebView version, native edge-to-edge setup, viewport metadata and the embedding layout. Measure on the supported device matrix. If a native fallback is necessary, use WindowInsets for system bars/cutout and convert native pixels to the CSS coordinate system used by the WebView.

Give each inset one owner. The page container, header and bottom navigation must not each pay the same padding. Treat IME height separately from navigation-bar padding; don't retain the keyboard inset as a permanent safe area. Handle rotation, three-button/gesture navigation, resumed activity and a document created after the first native inset event.

If a native inset bridge is needed, validate its message origin and replay the latest measurements after the WebView signals readiness. Test OEM-specific inset dispatch, double-counted header padding and keyboard-driven viewport shrink independently. A fixed CSS constant cannot correct all three failure modes.

## Overscroll and pull to refresh

A web page in a WebView reacts to a pull past its edge: iOS rubber-bands the whole document and Android stretches or glows it. When the app's header, tabs and content slide together and a strip of background shows, the app reads as a web page. Users often report it as "pull to refresh", although nothing reloads.

Lock the root by default, in the stylesheet every screen loads:

```css
html {
  height: 100%;
  overflow: hidden;           /* screens scroll inside their own container */
  overscroll-behavior: none;  /* html is the viewport-defining element */
}
body {
  height: 100%;
  margin: 0;
  overflow: hidden;
  overscroll-behavior: none;
}
```

- Put `overscroll-behavior` on `html`, the viewport-defining element, and repeat it on `body`. A value only on the app's shell element does not reach the viewport.
- Each screen scrolls in its own container. Whether that container keeps the platform's edge feedback is a per-screen choice; `overscroll-behavior: contain` keeps it from pulling the screen behind it.
- `overscroll-behavior` needs a WebKit from iOS 16 or later. For an older supported iOS, or if the document still bounces on a device, turn the bounce off on the WKWebView's scroll view from native code. That path was not built for this skill.
- Paint `html`, `body` and the native view behind the WebView in the theme's background color, so a gap is never white.
- If a list should refresh on pull, build that as a gesture of that list with its own indicator. Do not get it by letting the document move.
- Apply the lock even when no device was available to see the effect, and record the device check as pending. Then test at every edge, from a list at its end and on a screen shorter than the viewport, on the oldest supported OS versions.

## Capability-specific checks

Use the [migration inventory](migration-inventory.md) to discover missing native adapters. Follow [geolocation](geolocation.md) for location/geofences, [NFC and Bluetooth](nfc-bluetooth.md) for peripherals, [device security](device-security.md) for biometric/key access, and [push/background work](push-background.md) for remote delivery and offline jobs. For local notifications, exact reminders and alarms use [notifications and alarms](notifications-alarms.md). A foreground success or permission grant alone does not establish any background delivery guarantee.

Sources: [plugin catalog](https://v2.tauri.app/plugin/), [Android edge-to-edge](https://developer.android.com/develop/ui/views/layout/edge-to-edge), [MDN overscroll-behavior](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/overscroll-behavior).
