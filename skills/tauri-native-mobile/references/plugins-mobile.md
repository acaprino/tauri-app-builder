# Mobile plugins, insets and keyboard

Select plugins by documented support of the installed version, including individual commands. Android-only camera/auth code needs `target_os = "android"` gates, not a generic mobile gate. Separate capabilities by platform where it clarifies support; it is not mandatory to put them in a file literally named `mobile.json`.

## Insets and keyboard

On Android the page is drawn under the system bars and the keyboard unless one owner pays each inset, and what the WebView does by itself depends on its version. The rules, the code for the recommended design, the static and device checks and the sources are in [Android insets and keyboard](insets-keyboard.md). In short: one owner per inset, native padding of the content view by default, values assigned at every dispatch and never accumulated, insets passed on as zero instead of consumed, and the keyboard paid once, natively.

On iOS `env(safe-area-inset-*)` with `viewport-fit=cover` is the owner; keep the same one-owner rule in CSS. iOS keyboard behavior was not reviewed for this skill.

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
