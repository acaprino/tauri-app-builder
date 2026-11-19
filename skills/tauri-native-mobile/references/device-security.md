# Biometric unlock and protected credentials

Biometric prompt success establishes a local user-presence/authentication result under a selected policy. It is not a backend login, account identifier or authorization for another account. Use the official Tauri biometric plugin only for the operations it exposes; inspect availability, enrolled methods, device-credential fallback, cancellation and lockout in the installed version. [Tauri biometrics](https://v2.tauri.app/plugin/biometric/).

The current Tauri permission table also lists `biometric_cipher`, excluded from `biometric:default`; it requires `biometric:allow-biometric-cipher`. Check the pinned native implementation and available JS/Rust bindings before choosing it. A permission-table entry alone does not establish a public JS function, cryptographic policy or identical platform behavior.

For protecting a secret, require enforcement at the secret/key operation rather than a separate JS boolean followed by plaintext access. On Android, Keystore protects cryptographic keys; it is not a generic raw-token database. A native design can encrypt stored credentials with an authentication-bound key and use BiometricPrompt/CryptoObject where appropriate. Decide authentication strength, allowed credential fallback and invalidation policy. [Android biometrics](https://developer.android.com/identity/sign-in/biometric-auth), [Keystore](https://developer.android.com/privacy-and-security/keystore).

On iOS, choose Keychain accessibility and access-control flags for the actual foreground/background use case. Face ID requires its purpose string. A keychain access operation can enforce user presence/biometrics; merely displaying a prompt does not encrypt an unrelated file. [Apple protected Keychain access](https://developer.apple.com/documentation/localauthentication/accessing-keychain-items-with-face-id-or-touch-id).

JSON Store, localStorage and ordinary SQLite are not encrypted credential vaults. Verify any proposed secure-storage plugin's platform support, key lifecycle and backup semantics. Persist account-scoped secret references, not tokens in logs, URL parameters or notification bodies. Prefer performing sensitive native operations without returning reusable secrets into JS when the architecture permits it.

Define background access, backup/restore, reinstall, changed biometric enrollment, removed device lock, key invalidation and recovery explicitly. A restored ciphertext without its key must produce a recoverable sign-in flow, not silent data loss or an authorization bypass. Logout invalidates sessions and removes relevant protected credentials while preserving independent unsynced data according to the product's retention policy.

## Stronghold

Do not choose `tauri-plugin-stronghold` for new work. A Tauri maintainer wrote in September 2023 that it "is no longer recommended and will be deprecated and therefore removed in v3" and that it does not use the keychain ([discussion 7846](https://github.com/orgs/tauri-apps/discussions/7846)). The plugin's own pages carry no notice and v3 alpha releases exist, so treat the removal as announced, not done. It is an app-managed encrypted file, not the Keystore or the Keychain: an app that already uses it should plan a move to keys held by the OS.

## Passwords and passkeys the user already saved

This is a different need from protecting the app's own secrets. On Android the system service is [Credential Manager](https://developer.android.com/identity/sign-in/credential-manager), "the recommended Jetpack API for credential exchange": one bottom sheet for passkeys, passwords and Sign in with Google, backed by the user's credential provider, "including password managers such as Google Password Manager".

- **No official Tauri plugin.** It needs Kotlin in a plugin or in the app's Android project. `tauri-plugin-google-auth-firebase` uses Credential Manager for Google sign-in only ([native Google auth](google-auth-native.md)); passwords and passkeys are separate requests.
- **Associate the app with the website.** Passkeys and shared passwords need a [Digital Asset Links](https://developer.android.com/identity/credential-manager/prerequisites) file on a site the product owns, naming the app's package and signing certificate. A debug build signed with another key does not match: test with the release signature.
- **Passkeys from the page.** `androidx.webkit` 1.12.0 and later supports Credential Manager in a WebView once the app calls `setWebAuthenticationSupport` after checking `WebViewFeature.WEB_AUTHENTICATION`; conditional mediation is not supported ([Credential Manager in WebView](https://developer.android.com/identity/sign-in/credential-manager-webview)). Whether Tauri's Android WebView can be configured this way without patching the generated project is **unverified**.
- **Autofill.** An autofill service can offer the passwords saved for the product's website once app and site are associated with the `delegate_permission/common.get_login_creds` relation ([autofill](https://developer.android.com/identity/autofill/autofill-optimize)). That page describes native views; behavior on HTML fields inside the WebView, and the `autocomplete` values it needs, were not verified. Test on a device with the user's real provider.
- **A server is required for passkeys.** They are registered with and verified by the product's backend. For unlocking local data, use the biometric path above.
- **Cancellation is a result.** The user closing the sheet, having no saved credential, or having no provider are three outcomes, each with a working fallback sign-in.

iOS has its own services (Keychain password autofill with associated domains, passkeys through AuthenticationServices). They were not researched for this file.

Test no hardware/enrollment, cancel, temporary/permanent lockout, allowed fallback, app background during prompt, account switch, enrollment changes and backup restoration. A JS-only success mock cannot validate cryptographic access control.
