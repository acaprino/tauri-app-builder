# Credentials, saved passwords and passkeys

Part of the tauri-native-desktop references: versions, scope and limits are in [guide.md](guide.md). Bracketed names are sources; their URLs are in [sources.md](sources.md).

"Integrate with the system's password wallet" covers three different things. Decide which one the product needs before choosing an API; each is an item of the [native feature menu](native-features.md) and is added only when chosen.

| Need | What it is | Windows | macOS | Linux |
|---|---|---|---|---|
| Keep the app's own secrets | Tokens and passwords the app itself must store | Credential Manager | Keychain | Secret Service, KWallet |
| Use the passwords the user already saved | Fill a sign-in from the user's password manager | No OS API hands them to an app | Not researched | Not researched |
| Sign in with a passkey | Public-key sign-in unlocked by the device | Windows Hello through the WebAuthn API | Not researched | Not researched |

Sources were read on 2026-11-19. Nothing in this file was built or run for this skill.

## Keep the app's own secrets

There is no official Tauri plugin for the OS credential store. The path is a Rust crate behind an app command.

- **Crate.** `keyring` 4.2.0 is built on `keyring-core` and ships a store per system, among them `windows-native`, `apple-native`, the Secret Service stores for Linux and `android-native`. Check the features and the store selected for each target in your lockfile. [keyring crate].
- **Windows.** `CredWrite` "creates a new credential or modifies an existing credential in the user's credential set", tied to the user's logon session. The user sees the entry in Control Panel > Credential Manager > Windows Credentials. It belongs to the Windows account, so another Windows user on the same machine does not get it, and it does not follow the user to another machine unless the account roams. [CredWrite].
- **Linux.** A secret service may not be running (minimal desktops, headless sessions). Define the fallback: ask again at each start, or refuse to remember, rather than writing the secret to a file.
- **Shape of the command.** The frontend asks for an operation ("sign in", "call the API") and the native side reads the secret and uses it. Do not return the stored secret to JavaScript when the native side can use it directly. Name each entry by service and account, validate both, and expose the command only to the windows that need it ([boundaries.md](boundaries.md)).
- **What is not a credential store.** `store` writes plain JSON. `localStorage`, cookies and IndexedDB live in the WebView profile, readable by anything running in that origin.
- **Sign-out and uninstall.** Sign-out deletes the entry. Whether the uninstaller removes entries left behind is **unverified**: check on the installed package.

### Stronghold

Do not choose `tauri-plugin-stronghold` for new work. A Tauri maintainer wrote in September 2023 that "stronghold is no longer recommended and will be deprecated and therefore removed in v3", and that it "does not use the keychain". The plugin's page and README carry no such notice and v3 alpha releases of the plugin exist, so treat the removal as announced, not as done: an app that already uses it keeps working on Tauri 2 and should plan a move to the OS store. It was always an app-managed encrypted file unlocked by a password the app must itself keep somewhere, which is the problem the OS store solves. [Stronghold deprecation], [Stronghold plugin].

### Community plugin

`tauri-plugin-keyring-store` (0.3.2 on crates.io, third party) wraps `keyring-core` with a Stronghold-like API and lists Credential Manager on Windows and the Android Keystore among its backends. It was not installed, built or reviewed for this skill: read its native source, permissions and release history before use, and prefer the plain crate behind your own command when the app needs two or three operations. [keyring-store plugin].

## Use the passwords the user already saved

On Windows no OS service gives a desktop app the passwords the user saved in a browser or a password manager. Credential Manager returns only what the app itself wrote.

- **WebView2's own password saving** stores passwords in the WebView's profile, not in a system wallet. It is off by default and wry does not turn it on ([web-layer.md](web-layer.md)). Turning it on makes the app a small browser with its own password list: a product decision, rarely the right one.
- **Sign in through the system browser** when the goal is "the user should not retype the password". The browser has their password manager, passkeys and existing sessions; the app receives the result through a deep link or a loopback redirect ([native-plugins.md](native-plugins.md)). This is the route that reuses saved passwords on desktop.

## Sign in with a passkey

Windows has a platform API for passkeys. "Windows 11 users can create and use a passkey with Windows Hello, a plugin passkey provider, an external FIDO2 security key, or their mobile device", and "passkeys on Windows work in any browsers or apps that support them". Native management arrived with Windows 11 22H2; plugin passkey managers let a third-party manager hold the passkeys. [Windows passkeys].

- **Native call.** `WebAuthNAuthenticatorGetAssertion` and its companions in `webauthn.h` take "the handle for the window that will be used to display the UI": pass the app window's `HWND`, so the Windows Hello prompt is owned by the app. No official Tauri plugin wraps them; it is platform code behind an app command. [WebAuthn API].
- **From the page.** Whether `navigator.credentials` works inside WebView2 for the app's origin, and with which relying-party ID, is **unverified** here. Test on the shipped runtime before designing around it; a Tauri app's page origin is not the website's origin, and passkeys are bound to a relying party.
- **A server is required.** A passkey is registered with, and verified by, the product's backend. Without one there is nothing to sign in to: for unlocking local data use [OS re-authentication](native-plugins.md) instead.
- **Consent.** From Windows 11 24H2 "users are prompted for privacy consent before applications can access passkeys", and can block an app in Settings > Privacy & security > Passkey access. Handle the declined case with another sign-in method. [Windows passkeys].
- **Through the system browser.** Signing in in the browser gets passkeys with no native code. Prefer it unless the product needs the prompt inside the app.

## What to tell the user

Before they choose, say in plain words:

- where the secret will live and where they can see or delete it (on Windows: Credential Manager);
- that it is tied to their OS account on that machine;
- what happens when the store is unavailable, and on sign-out;
- for passkeys, that the product's server must support them, and what the fallback sign-in is.

## Acceptance

- [ ] No token or password in `store`, `localStorage`, a settings file, a URL or a log.
- [ ] After sign-in the entry appears in the OS credential store under the app's name; after sign-out it is gone.
- [ ] A second OS user on the same machine cannot read it; the app behaves sensibly when the store is locked or missing.
- [ ] The secret never reaches a window that does not need it.
- [ ] Passkey sign-in: the prompt is owned by the app window; cancel, no passkey, declined consent and no Windows Hello each lead to a working fallback.
