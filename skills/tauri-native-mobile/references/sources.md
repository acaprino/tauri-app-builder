# Fonti e aggiornamenti

Consultazione: 2026-11-15. Le fonti online cambiano: questa è una revisione datata, non un pin di toolchain o un'autorizzazione a installare automaticamente versioni nuove.

## Verifiche primarie effettuate

| Fonte | Decisione supportata |
|---|---|
| [Cargo build scripts](https://doc.rust-lang.org/cargo/reference/build-scripts.html#change-detection) | Una directory indicata in rerun-if-changed viene scandita per modifiche; il presupposto del vecchio walker era falso |
| [Firebase Google Android](https://firebase.google.com/docs/auth/android/google-signin) | Credential Manager e server/Web client ID; exchange Firebase nativo |
| [Tauri OS JS](https://v2.tauri.app/reference/javascript/os/) | `platform(): Platform`, sincrono |
| [Tauri Store](https://v2.tauri.app/plugin/store/) | `load`, autoSave e save; correzione API |
| [Tauri deep linking](https://v2.tauri.app/plugin/deep-linking/) e [JS API](https://v2.tauri.app/reference/javascript/deep-link/) | Configurazione per versione, startup getCurrent e listener onOpenUrl |
| [Tauri capabilities](https://v2.tauri.app/security/capabilities/) | ACL per finestra/piattaforma, separate dal consenso OS |
| [Android runtime permissions](https://developer.android.com/training/permissions/requesting) | Stato e percorso di richiesta/recupero |
| [Android FileProvider](https://developer.android.com/reference/androidx/core/content/FileProvider) | Grant URI e condivisione contenuti, non intera directory implicita |
| [Android minimal permissions](https://developer.android.com/privacy-and-security/minimize-permission-requests) | Picker come alternativa ad accesso media ampio |
| [Android verified links](https://developer.android.com/training/app-links/verify-applinks) | Associazioni e verifica del dominio |
| [Android edge-to-edge](https://developer.android.com/develop/ui/views/layout/edge-to-edge) | Gestione insets nell'host native |
| [Apple authorization request](https://developer.apple.com/documentation/signinwithapplerestapi/request-an-authorization-to-the-sign-in-with-apple-server) | form_post con scope name/email |
| [Firebase Apple iOS](https://firebase.google.com/docs/auth/ios/apple) | Nonce SHA-256 nella richiesta e raw nonce per Firebase |
| [Tauri CLI](https://v2.tauri.app/reference/cli/) | Build Android release di default e opzioni distinte |
| [Android 16 KB](https://developer.android.com/guide/practices/page-sizes) | ELF + ZIP + prebuilt + verifica runtime; pagina corrente con data 2027-02-01 per blocco update |
| [Google target API](https://support.google.com/googleplay/android-developer/answer/11926878) | API 36 per nuove app/update phone/tablet dal 2026-08-31; eccezioni per altre categorie |
| [Google billing security](https://developer.android.com/google/play/billing/security) | Verifica backend e ownership/idempotenza |
| [Tauri App Store](https://v2.tauri.app/distribute/app-store/) | Catena di distribuzione iOS |
| [Apple upcoming requirements](https://developer.apple.com/news/upcoming-requirements/) | Requisiti da ricontrollare alla submission, non tabella congelata |
| [WebKit inspection](https://webkit.org/blog/13936/enabling-the-inspection-of-web-content-in-apps/) | Inspectability configurabile, non proprietà universale debug/release |
| [Xcode 14 release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-14-release-notes) | Push remoto supportato da alcune configurazioni simulator |
| [Tauri updater](https://v2.tauri.app/plugin/updater/) | true / v1Compatible, non v2Compatible; target e arch separati |

Alcune verifiche hanno usato estratti indicizzati delle stesse fonti ufficiali (Apple REST, Xcode, target API, Store); non sono copie archiviate integrali delle pagine. Non è stato eseguito un crawler di tutti gli URL, né verificata la disponibilità di tutti i servizi provider.

## Documentazione da consultare durante l'implementazione

[RFC 8252](https://www.rfc-editor.org/rfc/rfc8252), [RFC 7636](https://www.rfc-editor.org/rfc/rfc7636), [Tauri prerequisites](https://v2.tauri.app/start/prerequisites/), [Tauri Vite](https://v2.tauri.app/start/frontend/vite/), [Tauri IPC](https://v2.tauri.app/develop/calling-rust/), [Tauri plugin catalog](https://v2.tauri.app/plugin/), [Play subscriptions](https://developer.android.com/google/play/billing/lifecycle/subscriptions), [App Store Server API](https://developer.apple.com/documentation/appstoreserverapi). Questi link sono percorsi di approfondimento, non attestazioni di build/API eseguite oggi.

## Package evidence

[Generic example hashes](../audit/source-manifest.json), [verification limits](../audit/REVIEW.md), [version inventory](../audit/versions-2026-11-16.json). No private checkout is required. See [scheduling](notifications-alarms.md), [file export](file-export.md) and [versions](version-maintenance.md) for additional sources. Reviewed 2026-11-16; recheck requirements before implementation or submission.

## Expanded capability research

Official Tauri, Android, Apple and Firebase documentation reviewed 2026-11-16. Sources are attached to each decision in [location](geolocation.md), [NFC/BLE](nfc-bluetooth.md), [push/background/offline](push-background.md), [biometric credentials](device-security.md) and the [migration inventory](migration-inventory.md). These are documented integration boundaries; no radio, sensor, provider or device runtime was exercised.
