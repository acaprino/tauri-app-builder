# Biometric unlock and protected credentials

Biometric prompt success establishes a local user-presence/authentication result under a selected policy. It is not a backend login, account identifier or authorization for another account. Use the official Tauri biometric plugin only for the operations it exposes; inspect availability, enrolled methods, device-credential fallback, cancellation and lockout in the installed version. [Tauri biometrics](https://v2.tauri.app/plugin/biometric/).

The current Tauri permission table also lists `biometric_cipher`, excluded from `biometric:default`; it requires `biometric:allow-biometric-cipher`. Check the pinned native implementation and available JS/Rust bindings before choosing it. A permission-table entry alone does not establish a public JS function, cryptographic policy or identical platform behavior.

For protecting a secret, require enforcement at the secret/key operation rather than a separate JS boolean followed by plaintext access. On Android, Keystore protects cryptographic keys; it is not a generic raw-token database. A native design can encrypt stored credentials with an authentication-bound key and use BiometricPrompt/CryptoObject where appropriate. Decide authentication strength, allowed credential fallback and invalidation policy. [Android biometrics](https://developer.android.com/identity/sign-in/biometric-auth), [Keystore](https://developer.android.com/privacy-and-security/keystore).

On iOS, choose Keychain accessibility and access-control flags for the actual foreground/background use case. Face ID requires its purpose string. A keychain access operation can enforce user presence/biometrics; merely displaying a prompt does not encrypt an unrelated file. [Apple protected Keychain access](https://developer.apple.com/documentation/localauthentication/accessing-keychain-items-with-face-id-or-touch-id).

JSON Store, localStorage and ordinary SQLite are not encrypted credential vaults. Verify any proposed secure-storage plugin's platform support, key lifecycle and backup semantics. Persist account-scoped secret references, not tokens in logs, URL parameters or notification bodies. Prefer performing sensitive native operations without returning reusable secrets into JS when the architecture permits it.

Define background access, backup/restore, reinstall, changed biometric enrollment, removed device lock, key invalidation and recovery explicitly. A restored ciphertext without its key must produce a recoverable sign-in flow, not silent data loss or an authorization bypass. Logout invalidates sessions and removes relevant protected credentials while preserving independent unsynced data according to the product's retention policy.

Test no hardware/enrollment, cancel, temporary/permanent lockout, allowed fallback, app background during prompt, account switch, enrollment changes and backup restoration. A JS-only success mock cannot validate cryptographic access control.
