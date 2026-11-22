---
description: Run the acceptance checks the tauri MCP server can observe in a running Tauri 2 app and record what stays unverified.
argument-hint: [area: frame | keyboard | dialogs | web-layer | all]
---

Verify the area `$ARGUMENTS` (default: all) of the running Tauri 2 app against the `tauri-native-desktop` skill. Read its `references/acceptance.md` and the reference file of each section in scope.

1. **Check the link.** The `tauri` MCP server's tools must be available (tools named `mcp__plugin_tauri-app-builder_tauri__<tool>`; search deferred tools with ToolSearch first). If none exist, ask the user to open `/mcp` and check that `plugin:tauri-app-builder:tauri` is connected, then stop. The app must be running in dev with the bridge registered (`/tauri-app-builder:bridge` sets it up). Start a session with `driver_session`.
2. **Split the checklist in two.** The server acts on the webview: DOM and accessibility snapshot (`webview_dom_snapshot`), computed styles (read with `webview_execute_js` and `getComputedStyle`, no state change), keyboard and pointer input (`webview_keyboard`, `webview_interact`), screenshots, console logs, IPC traffic, and window list and resize (`manage_window`). Mark each check as observable through it or not. The native frame, OS dialogs, tray, notifications after exit, installers and the task switcher are not observable this way: keep them as `not verified here` with the manual step that covers them.
3. **Run each observable check** and record it: check, tool called, observed result, pass or fail. Include the evidence (screenshot file, log line or snapshot node).
4. **Report in the coverage-record shape the skill asks for**: surface or window, expected behavior, implementation, evidence, remaining work. Say which platform and WebView the run used; a result on Windows does not carry over to macOS or Linux.

Observe only. Do not edit code in this command; list the failures and offer `/tauri-app-builder:debug` for each one.
