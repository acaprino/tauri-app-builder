# Google sign-in and Firebase identity

Select Android, iOS and web explicitly. An isTauri check alone cannot select an Android-only plugin on iOS. A failed native import or token lookup must not authorize use of a stale JS account.

## Android

Use Credential Manager with registered package and signing certificates: debug, local release and store app signing may differ. Supply the server/Web OAuth client ID where the ID-token request requires it. Initialize Rust registration, Gradle module and JS bindings coherently; a local vendor may need bindings built before installation. Optional JS fields must match Kotlin serialization defaults.

Use GetGoogleIdOption for the authorized-account route. On NoCredentialException, offer explicit user-triggered GetSignInWithGoogleOption button flow. Cancellation is cancellation, not an automatic second picker. Parse the Google credential and exchange it through native Firebase. Return the adopted identity through the app facade. Normalize cancellation, no credential, interruption, invalid token, network and provider errors without logging tokens.

A release build can remove what code reaches only by name. A plugin that reads the Web client ID with `Resources.getIdentifier("default_web_client_id", "string", …)` leaves no reference the resource shrinker can see: the string that `google-services.json` generates is in the debug APK and may be missing from the minified one, and the sign-in then fails before Credential Manager is asked, with no account sheet and no Google error. Seen in an app whose Gradle project is generated on each build; an app with the same plugin, `isMinifyEnabled` and no resource shrinking kept the string. Pass the Web client ID explicitly as `serverClientId`, or keep the resource (`tools:keep` in `res/raw/keep.xml`). The same holds for classes loaded by name under R8.

Verify on the release artifact, not the debug one: list the resource in the built APK (`aapt2 dump resources`), then press the button on a device or an emulator image that has Google services and read logcat for `executeGetCredential` from the app's package. Its absence means the call never left the app, so signing certificates and OAuth clients are not the cause. An image without Google services, or a test that only starts the app, proves nothing about sign-in. Show or log the plugin's error code: one generic message hides which stage failed.

## iOS

Configure GoogleSignIn SDK, iOS client ID, reversed-client-ID URL scheme and Firebase; configure server client ID when required by the backend flow. Present from the active view controller on the main thread. Forward Google callback URLs to the SDK and coordinate that handler with ordinary app links. Exchange the credential through Firebase Auth on iOS. Implement restore/refresh, cancellation, account selection and logout separately; Android bindings and web popups provide no iOS parity.

## Identity boundary

Expose one authoritative current-user, token, sign-in, sign-out and reauthentication contract. Check account UID and session generation before and after async token acquisition. Verify token subject through the appropriate trusted boundary. Never send a request for one account using another account's token.

Logout first invalidates outstanding operations and persists a signed-out barrier against automatic restoration. Attempt every SDK cleanup even when one fails; Android cleanup includes Credential Manager credential-state clearing. Keep failures retryable. Clear the barrier only after explicit successful sign-in. Destructive reauthentication must confirm the same UID. Preserve unsynced data according to an explicit retention policy.

Web Firebase callbacks such as /__/auth/handler must bypass service-worker navigation fallback. Returning an app shell there can break authentication. Scope service-worker registration by runtime policy. Separate environments need coherent package/client/signature registrations; never copy another app's keys.

Test no accounts, picker cancel, no authorized account, offline, wrong signature, process death, stale JS identity, token-refresh/logout races, account switch and same-account reauthentication independently on both native platforms.

Sources: [Firebase Android](https://firebase.google.com/docs/auth/android/google-signin), [Android resource shrinking](https://developer.android.com/build/shrink-code#shrink-resources), [Google iOS](https://developers.google.com/identity/sign-in/ios/sign-in), [Firebase iOS](https://firebase.google.com/docs/auth/ios/google-signin).

