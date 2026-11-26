# Sources and updates

Consulted 2026-11-15. Online sources change: this is a dated review, not a toolchain pin or permission to install new versions automatically.

## Primary checks performed

| Source | Decision it supports |
|---|---|
| [Cargo build scripts](https://doc.rust-lang.org/cargo/reference/build-scripts.html#change-detection) | A directory named in rerun-if-changed is scanned for changes; the old walker's premise was false |
| [Firebase Google Android](https://firebase.google.com/docs/auth/android/google-signin) | Credential Manager and server/Web client ID; native Firebase exchange |
| [Tauri OS JS](https://v2.tauri.app/reference/javascript/os/) | `platform(): Platform`, synchronous |
| [Tauri Store](https://v2.tauri.app/plugin/store/) | `load`, autoSave and save; API correction |
| [Tauri deep linking](https://v2.tauri.app/plugin/deep-linking/) and [JS API](https://v2.tauri.app/reference/javascript/deep-link/) | Configuration per version, startup getCurrent and the onOpenUrl listener |
| [Tauri capabilities](https://v2.tauri.app/security/capabilities/) | ACL per window/platform, separate from OS consent |
| [Android runtime permissions](https://developer.android.com/training/permissions/requesting) | State and the request/recovery path |
| [Android FileProvider](https://developer.android.com/reference/androidx/core/content/FileProvider) | URI grants and content sharing, not an implicit whole directory |
| [Android minimal permissions](https://developer.android.com/privacy-and-security/minimize-permission-requests) | Picker as the alternative to broad media access |
| [Android verified links](https://developer.android.com/training/app-links/verify-applinks) | Associations and domain verification |
| [Android edge-to-edge](https://developer.android.com/develop/ui/views/layout/edge-to-edge) | Inset handling in the native host |
| [Apple authorization request](https://developer.apple.com/documentation/signinwithapplerestapi/request-an-authorization-to-the-sign-in-with-apple-server) | form_post with name/email scope |
| [Firebase Apple iOS](https://firebase.google.com/docs/auth/ios/apple) | SHA-256 nonce in the request and raw nonce for Firebase |
| [Tauri CLI](https://v2.tauri.app/reference/cli/) | Android release build by default, with distinct options |
| [Android 16 KB](https://developer.android.com/guide/practices/page-sizes) | ELF + ZIP + prebuilt + runtime check; the current page gives 2027-02-01 for blocking updates |
| [Google target API](https://support.google.com/googleplay/android-developer/answer/11926878) | API 36 for new apps and phone/tablet updates from 2026-08-31; exceptions for other categories |
| [Google billing security](https://developer.android.com/google/play/billing/security) | Backend verification and ownership/idempotency |
| [Tauri App Store](https://v2.tauri.app/distribute/app-store/) | iOS distribution chain |
| [Apple upcoming requirements](https://developer.apple.com/news/upcoming-requirements/) | Requirements to recheck at submission, not a frozen table |
| [WebKit inspection](https://webkit.org/blog/13936/enabling-the-inspection-of-web-content-in-apps/) | Inspectability is configurable, not a universal debug/release property |
| [Xcode 14 release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-14-release-notes) | Remote push supported by some simulator configurations |
| [Tauri updater](https://v2.tauri.app/plugin/updater/) | true / v1Compatible, not v2Compatible; target and arch are separate |
| [Android Auto Backup](https://developer.android.com/identity/data/autobackup) | `allowBackup` defaults to true; on API 31+ both extraction-rule sections are needed |
| [Android network security configuration](https://developer.android.com/privacy-and-security/security-config) | Target 24+ trusts system CAs only; cleartext off from target 28 |
| [Android foreground service types](https://developer.android.com/develop/background-work/services/fgs/service-types) and [timeouts](https://developer.android.com/develop/background-work/services/fgs/timeout) | `specialUse` property and review; `dataSync` 6 hours in 24 and no start from boot on Android 15 |
| [Android zipalign](https://developer.android.com/tools/zipalign) | `-P 16` for 16 KB; `-p` is 4 KiB and deprecated |
| [Tauri icons](https://v2.tauri.app/develop/icons/) and the CLI reference | Default icon is Tauri's; `tauri icon` writes Android icons into the generated project; manifest keys for adaptive layers |
| [Tauri configuration](https://v2.tauri.app/reference/config/) | `bundle.android` has four fields, none for compile or target SDK; default version code formula |
| [Tauri Android signing](https://v2.tauri.app/distribute/sign/android/) | `keystore.properties` written in CI, signing config in the Gradle file |
| [Tauri app API](https://v2.tauri.app/reference/javascript/api/namespaceapp/) and the `tauri` crate's Android source (2.9.5, 2.12.5) | `onBackButtonPress` since 2.9.0 takes over the default; a listener stays until removed; `core:app:default` allows register and remove |
| [Android WebView insets](https://developer.android.com/develop/ui/views/layout/webapps/understand-window-insets) (page dated 2026-10-28) | `env(safe-area-inset-*)` for bars and cutout added in WebView M136 (M144 for a WebView that does not fill the window); keyboard by visual viewport from M139; zero the insets a parent paid instead of consuming them |
| [Android 16 behavior changes](https://developer.android.com/about/versions/16/behavior-changes-16) | No opt-out from edge-to-edge when targeting SDK 36 |
| [Android keyboard guide](https://developer.android.com/develop/ui/views/layout/sw-keyboard) | `adjustResize` for the keyboard inset through AndroidX on older Android |
| [WindowInsets](https://developer.android.com/reference/android/view/WindowInsets), [WindowInsets.Type](https://developer.android.com/reference/android/view/WindowInsets.Type) and [View](https://developer.android.com/reference/android/view/View) references | Tappable-element and mandatory-gesture insets are not layout insets; `getInsetsIgnoringVisibility` and its IME exception; a listener replaces the view's own handling |
| [Window](https://developer.android.com/reference/android/view/Window), [display cutout](https://developer.android.com/develop/ui/views/layout/display-cutout), [emulator console](https://developer.android.com/studio/run/emulator-console), [adb](https://developer.android.com/tools/adb), [KeyEvent](https://developer.android.com/reference/android/view/KeyEvent), [Android 14 features](https://developer.android.com/about/versions/14/features) | `setSoftInputMode`; which test steps of the insets page are documented (simulated cutout, `rotate`, `screencap`, `dumpsys`, Back key code, font size setting) and which adb shortcuts are not |
| `wry` crate Android source (0.53.5, 0.57.1) | The WebView is set as the activity's content view |
| Tauri CLI Android template at tag `tauri-cli-v2.12.4` (`MainActivity.kt`, `AndroidManifest.xml`) | The generated activity calls `enableEdgeToEdge()`; the manifest sets no `windowSoftInputMode` |

The eight rows from Auto Backup down were consulted 2026-11-25, and the seven rows from Android WebView insets down on 2026-11-26. They support [Android insets and keyboard](insets-keyboard.md).

Some checks used indexed excerpts of the same official sources (Apple REST, Xcode, target API, Store); they are not full archived copies of the pages. No crawler was run over every URL, and the availability of every provider service was not checked.

## Documentation to consult during implementation

[RFC 8252](https://www.rfc-editor.org/rfc/rfc8252), [RFC 7636](https://www.rfc-editor.org/rfc/rfc7636), [Tauri prerequisites](https://v2.tauri.app/start/prerequisites/), [Tauri Vite](https://v2.tauri.app/start/frontend/vite/), [Tauri IPC](https://v2.tauri.app/develop/calling-rust/), [Tauri plugin catalog](https://v2.tauri.app/plugin/), [Play subscriptions](https://developer.android.com/google/play/billing/lifecycle/subscriptions), [App Store Server API](https://developer.apple.com/documentation/appstoreserverapi). These links are further reading, not attestations of builds or APIs run today.

## Package evidence

[Generic example hashes](../audit/source-manifest.json), [verification limits](../audit/REVIEW.md), [version inventory](../audit/versions-2026-11-16.json). No private checkout is required. See [scheduling](notifications-alarms.md), [file export](file-export.md) and [versions](version-maintenance.md) for additional sources. Reviewed 2026-11-16; recheck requirements before implementation or submission.

## Expanded capability research

Official Tauri, Android, Apple and Firebase documentation reviewed 2026-11-16. Sources are attached to each decision in [location](geolocation.md), [NFC/BLE](nfc-bluetooth.md), [push/background/offline](push-background.md), [biometric credentials](device-security.md) and the [migration inventory](migration-inventory.md). These are documented integration boundaries; no radio, sensor, provider or device runtime was exercised.
