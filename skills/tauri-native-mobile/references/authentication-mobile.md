# Mobile callbacks and deep links

Read [OAuth architecture](authentication.md) and [native Google](google-auth-native.md). A link that launches an app followed by authenticated state recovery is not proof of URL-to-screen routing.

Configure plugin registration, capabilities and native manifest/entitlements together. Use getCurrent() for startup and onOpenUrl() for running-app delivery. Subscribe before consuming startup URLs, deduplicate overlap and serialize routing until navigation/auth readiness. Use an app-level owner; dispose the listener even when async registration completes after unmount.

Parse and validate scheme, exact host, port and allowed path. Reject unexpected userinfo, encoded-path tricks and arbitrary return destinations. Links are untrusted input; authorization stays on the server. Keep bounded pending navigation across login and respect account changes. Deduplicate OAuth by one-time transaction; use a bounded delivery window for ordinary navigation so a later intentional click still works.

Android App Links require intent filters and deployed /.well-known/assetlinks.json with actual package and signing fingerprints, including store signing. Test installed-package verification. Deployment must preserve hidden directories and serve association content without app-shell fallback. Hosting changes cannot add filters to an installed APK. Remove obsolete custom schemes deliberately.

iOS Universal Links require Associated Domains and a valid apple-app-site-association file with correct app identity/path rules. Register provider SDK URL schemes separately and dispatch callbacks to the proper owner. Test cold/warm launch, duplicates, malicious links, signed-out navigation, wrong account, old builds and actual release signing.

For Sign in with Apple, follow the supported native/Firebase flow. Where scoped authorization uses form_post, provide the correct HTTPS receiver. Keep state and nonce distinct; Firebase Apple flows use a hashed nonce in the request and the original nonce for verification. Handle private relay email and first-authorization-only name fields.

Sources: [Tauri links](https://v2.tauri.app/plugin/deep-linking/), [Android verification](https://developer.android.com/training/app-links/verify-applinks), [Apple associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains), [Firebase Apple](https://firebase.google.com/docs/auth/ios/apple).

