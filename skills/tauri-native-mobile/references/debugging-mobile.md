# Mobile debugging

Begin with artifact identity and reproduction. Observe the layer that can explain the symptom; don't turn an old incident's cause into a universal diagnosis.

| Symptom | Investigation |
|---|---|
| White screen | Resource URL/reachability, packaged files, parse/runtime errors, CSP, native startup crash |
| Old UI | [Artifact chain](mobile-stale-builds.md), installed version, service worker, ABI/variant |
| IPC denied | Plugin presence/registration and exact capability before OS permissions |
| Permission accepted, no result | Native callback annotation/dispatch and pending-request owner |
| Login generic error | Normalize native error shape; check client ID/certificate/project and session source |
| All API calls 401 | Token type/issuer/audience and backend verifier/IAM; not automatically a client login bug |
| Link opens browser | Association delivery, installed manifest, signing certificate and domain verification |
| ANR | Main-thread trace, blocking IPC, decode/IO/JS workload; process CPU alone doesn't identify a thread |

Inspect Android WebViews through `chrome://inspect` when debugging is enabled. On iOS, Safari visibility depends on Web Inspector settings and WKWebView inspectability; release and simulator behavior is not an unconditional rule. Since iOS 16.4, `isInspectable` controls opt-in inspection. [WebKit explanation](https://webkit.org/blog/13936/enabling-the-inspection-of-web-content-in-apps/).

When the plugin's `tauri` MCP server is connected and the app registers `tauri-plugin-mcp-bridge` in debug builds, `/tauri-app-builder:debug` uses it for console output, Android logcat, IPC capture and webview screenshots, and the server lists Android devices and iOS simulators (`list_devices`) according to its own README. How the server reaches a bridge on a phone or emulator was not read or tested here, so confirm it on the device. It does not replace native crash traces or the installed-artifact checks.

Collect logcat/native crash traces and WebView console/network separately. Preserve logs before clearing them. Keep matching symbols for native addresses and R8 mappings when minification is used. A Rust abort commonly signals SIGABRT; SIGSEGV is not interchangeable with 'Rust panic'.

`async fn` does not make CPU work nonblocking; offload blocking work and inspect lock ownership. Switching every mutex to an async mutex does not cure a logical deadlock. Avoid modifying process environment unsafely after threads start; Rust 2024 treats `set_var` as unsafe. Prefer deliberate startup/build logging configuration.

Debug CA overrides affect compatible Android networking stacks, not automatically every Rust TLS client. A system proxy may be ignored by a native client or defeated by pinning. Never treat a proxy's silence as proof that no request happened.

See [permissions](permissions.md), [camera](camera-media.md), [native Google auth](google-auth-native.md) and [testing](testing.md).
