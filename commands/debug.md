---
description: Debug a running Tauri 2 app through the tauri MCP server (logs, DOM, IPC, screenshots), then fix the cause.
argument-hint: <symptom>
---

Debug this symptom in the running Tauri 2 app: `$ARGUMENTS`. Work from evidence the `tauri` MCP server returns, not from a guess.

1. **Check the link.** The server's tools must be available (tools named `mcp__plugin_tauri-app-builder_tauri__<tool>`; search deferred tools with ToolSearch first). If none exist, ask the user to open `/mcp` and check that `plugin:tauri-app-builder:tauri` is connected, then stop. The app must be running in dev with the bridge registered. If the bridge is missing, run the `/tauri-app-builder:bridge` procedure first. Start a session with `driver_session`.
2. **Capture the state before touching anything.** Call `webview_screenshot`, `read_logs` (console; add Android logcat for a device, found with `list_devices`) and `webview_dom_snapshot`. Start `ipc_monitor` and keep it running through the reproduction.
3. **Reproduce the symptom** with `webview_interact`, `webview_keyboard` and `webview_wait_for`. Then read `ipc_get_captured` and `read_logs` again. Quote the first error line and the IPC call that failed.
4. **Name the cause and match it to a reference.** For Android or iOS symptoms read the `tauri-native-mobile` skill's `references/debugging-mobile.md`. For a blank window, a crashed WebView or an engine error page read `references/recovery.md` of `tauri-native-desktop`; for selection, cursor, bounce or startup flash read `references/web-layer.md`.
5. **Fix the root cause in the source**, once, where the shared code lives. Let dev hot reload apply it, then repeat steps 2 and 3 and show the screenshot, log and IPC trace that changed.
6. **Stop the session** with `driver_session` and report: symptom, evidence, cause, fix, and what you could not observe through the webview (native frame, OS windows, installer behavior).

Read-only tools first. Ask before `webview_execute_js` changes page state, and before `ipc_execute_command` or `ipc_emit_event`: those run real commands in the user's app. Never run them against production data.
