---
description: Build or change a screen or flow in a running Tauri 2 app and check every step in the live window through the tauri MCP server.
argument-hint: <what to build>
---

Build this in the running Tauri 2 app: `$ARGUMENTS`. Check each step in the live window, not only in the code.

1. **Check the link.** The `tauri` MCP server's tools must be available (tools named `mcp__plugin_tauri-app-builder_tauri__<tool>`; search deferred tools with ToolSearch first). If none exist, ask the user to open `/mcp` and check that `plugin:tauri-app-builder:tauri` is connected, then stop. The app must be running in dev with the bridge registered (`/tauri-app-builder:bridge` sets it up). Start a session with `driver_session` and take a `webview_screenshot` as the baseline.
2. **Decide the surface level before writing code.** Use the `tauri-native-desktop` skill: side drawers, detail sheets and routine modals stay in-window; a separate `WebviewWindow` needs one of the reasons listed there. For an Android target use `tauri-native-mobile` for insets, permissions and plugins.
3. **Follow the project's own patterns.** Read the neighboring components, the existing commands and the capability files. Reuse them. Add a capability or a plugin only when this feature needs one.
4. **Implement the smallest slice that shows something**, let dev hot reload apply it, and check it: `webview_screenshot`, `webview_dom_snapshot` (labels and roles), `read_logs` for errors. Exercise the flow with `webview_interact`, `webview_keyboard` and `webview_wait_for`, keyboard path and focus included.
5. **Repeat slice by slice.** After each one show what changed on screen. A slice with a console error or a denied IPC call is not done.
6. **Close with the evidence.** List what you observed (screens, flows, logs) and what you could not observe through the webview (native frame, OS windows, notifications, installers). Stop the session with `driver_session`.

Ask before `ipc_execute_command` or `webview_execute_js` changes real state in the app.
