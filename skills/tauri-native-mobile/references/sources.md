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

Some checks used indexed excerpts of the same official sources (Apple REST, Xcode, target API, Store); they are not full archived copies of the pages. No crawler was run over every URL, and the availability of every provider service was not checked.

## Documentation to consult during implementation

[RFC 8252](https://www.rfc-editor.org/rfc/rfc8252), [RFC 7636](https://www.rfc-editor.org/rfc/rfc7636), [Tauri prerequisites](https://v2.tauri.app/start/prerequisites/), [Tauri Vite](https://v2.tauri.app/start/frontend/vite/), [Tauri IPC](https://v2.tauri.app/develop/calling-rust/), [Tauri plugin catalog](https://v2.tauri.app/plugin/), [Play subscriptions](https://developer.android.com/google/play/billing/lifecycle/subscriptions), [App Store Server API](https://developer.apple.com/documentation/appstoreserverapi). These links are further reading, not attestations of builds or APIs run today.

## Package evidence

[Generic example hashes](../audit/source-manifest.json), [verification limits](../audit/REVIEW.md), [version inventory](../audit/versions-2026-11-16.json). No private checkout is required. See [scheduling](notifications-alarms.md), [file export](file-export.md) and [versions](version-maintenance.md) for additional sources. Reviewed 2026-11-16; recheck requirements before implementation or submission.

## Expanded capability research

Official Tauri, Android, Apple and Firebase documentation reviewed 2026-11-16. Sources are attached to each decision in [location](geolocation.md), [NFC/BLE](nfc-bluetooth.md), [push/background/offline](push-background.md), [biometric credentials](device-security.md) and the [migration inventory](migration-inventory.md). These are documented integration boundaries; no radio, sensor, provider or device runtime was exercised.
