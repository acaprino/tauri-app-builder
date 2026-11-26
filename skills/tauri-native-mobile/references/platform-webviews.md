# WebView compatibility

Android uses Android System WebView; iOS uses WKWebView tied to the OS. Shared desktop targets add WebView2 and WebKitGTK. Record the engine on the affected device rather than infer all features from the OS name.

Pick build syntax targets for the supported engines. Syntax lowering does not polyfill `structuredClone`, `crypto.randomUUID`, media APIs or CSS features. Feature-detect APIs before use and provide bounded fallback or an understandable update requirement. A parse-floor message must itself parse before the main bundle.

Safe-area and keyboard behavior depend on the WebView version (an Android WebView reports the bars to the page from M136 and handles the keyboard from M139); the versions and the rules are in [Android insets and keyboard](insets-keyboard.md). Do not equate 'Safari 15.4' with 'macOS 15', call SharedArrayBuffer Chromium-only, or retain unverified MediaRecorder/OffscreenCanvas OS floors. Capabilities can depend on security context, isolation and exact engine release.

Put required polyfills or a minimal compatibility screen before code that depends on unsupported APIs. Supply plain-color fallbacks for unsupported `color-mix()` tokens when those engines remain supported. Use the same device matrix for behavior and visual checks.

Sources: [Tauri WebView versions](https://v2.tauri.app/reference/webview-versions/).
