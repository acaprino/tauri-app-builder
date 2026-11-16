# OAuth and identity architecture

Select the provider-supported flow for the platform and OAuth client type. Android Google/Firebase may use [native Credential Manager](google-auth-native.md). Generic OAuth native apps normally use an external user agent and Authorization Code with PKCE. Do not embed Google sign-in in the app WebView or embed confidential client secrets in a mobile binary. [Native-app OAuth](https://www.rfc-editor.org/rfc/rfc8252), [PKCE](https://www.rfc-editor.org/rfc/rfc7636).

Use a cryptographically random, opaque state bound to a pending local/server transaction. Keep state, OIDC nonce and PKCE verifier as distinct fields with distinct checks. Persist the pending transaction across process death using appropriate protected storage; merely echoing nonce/timestamp in a callback is not proof that this device initiated it. Validate exact callback scheme/host/path, issuer/client, expiry, state, nonce where applicable and one-time consumption. Serialize duplicate callbacks and clear only the matching transaction.

Prefer verified HTTPS App Links/Universal Links where supported. Private-use schemes have interception risks and depend on provider/client support. A hosted redirect bridge is conditional, not universally required. If used, allowlist its return destination; never accept an arbitrary `continueUri` from untrusted state. Do not forward access/ID tokens in URLs. Exchange an authorization code through the supported provider flow; a Web OAuth client may need a confidential backend and cannot be turned into a public native client merely by adding PKCE.

Navigation redirects are not CORS. Cross-origin JS token exchange is; troubleshoot redirect URI matching, browser navigation policy and endpoint CORS separately.

Tauri Store is a JSON persistence plugin, not a credential vault. Current JS creation uses `load`/`Store.load`, not a public `new Store` constructor. Auto-save is configurable; `await save()` gives an explicit flush point, not encryption. Prefer platform credential storage or the provider SDK for credentials.

Token refresh is different from login, identity reconciliation and reauthentication. Route backend authorization through the authoritative session source. Never infer a successful native login from a stale Firebase JS `currentUser`.

See [mobile callback lifecycle](authentication-mobile.md) and [dated sources](sources.md).
