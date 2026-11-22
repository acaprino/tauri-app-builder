---
name: tauri-live-debug
description: "Use when debugging, inspecting or checking a running Tauri 2 app through the plugin's tauri MCP server: a blank or wrong window, console errors, denied or failing IPC calls, a UI that does not match the code, a screen to build and check live, or a request to look at, click through or screenshot the app. Not for static code review, for an app that is not running, or for native frame and OS-window checks."
---

# Tauri live debug

Act as a debugging engineer who works from what the running app shows. The `tauri` MCP server of this plugin reads and drives the webview of a Tauri 2 app in dev. Use it when a symptom needs runtime evidence; answer from the code when it does not.

## Decide

- **Use the server** for a blank or wrong screen, a console error, an IPC call that fails or is denied, a layout or state that differs from the code, a flow to click through, or a screen being built that should be checked in the live window.
- **Do not use it** for a question the code or the docs answer, for an app that is not running, or for what the webview cannot show: the native frame, OS dialogs, tray, notifications after exit, installers and the task switcher. Those stay with the `tauri-native-desktop` and `tauri-native-mobile` skills and checks on the installed package.

## Check the link

1. The server's tools are available: tools named `mcp__plugin_tauri-app-builder_tauri__<tool>` (search deferred tools with ToolSearch first). If none exist, ask the user to open `/mcp` and check that `plugin:tauri-app-builder:tauri` is connected, then stop; do not guess its output.
2. The app runs in dev (`tauri dev`) and registers `tauri-plugin-mcp-bridge` in debug builds. If it does not, offer `/tauri-app-builder:bridge`, which adds it after showing the diff. The bridge needs `app.withGlobalTauri: true` and the `mcp-bridge:default` capability; both stay in the release config unless the project keeps them in a dev-only config, so keep them out of release builds.
3. Start a session with the session tool (`driver_session`) and confirm with its status action before anything else.

## Work from evidence

1. **Baseline first.** Screenshot, console log (`read_logs`) and DOM snapshot before touching the app. Start IPC monitoring if the symptom involves a command.
2. **Reproduce** with input and wait tools, then read the log and the captured IPC again. Quote the first error line, the failing command and what the screen showed.
3. **Name the cause from that evidence**, then take the matching reference from the sibling skills (table below).
4. **Fix the root cause once, in the source**, let dev hot reload apply it, and repeat the same observations. A fix counts when the earlier screenshot, log or IPC trace changed.
5. **Stop the session** and report: symptom, evidence, cause, fix, and what the webview could not show.

## Tools

The `/mcp` view lists 19 tools. Names below are the upstream tool ids from its README, with the `/mcp` title in brackets.

| Need | Tool | Marked read-only in `/mcp` |
|---|---|---|
| Session start, status, stop | `driver_session` [Manage Tauri Session] | No |
| Setup steps for the bridge | `get_setup_instructions` | Yes |
| Screenshot, DOM and accessibility tree | `webview_screenshot`, `webview_dom_snapshot` | Yes |
| Find an element, wait for a condition | `webview_find_element`, `webview_wait_for` | Yes |
| Console, Android and system logs | `read_logs` | Yes |
| Start or stop IPC monitoring | `ipc_monitor` | No |
| Read captured IPC, backend state, devices | `ipc_get_captured`, `ipc_get_backend_state`, `list_devices` | Yes |
| Click, scroll, type | `webview_interact`, `webview_keyboard` | No |
| Run script, call a command, emit an event | `webview_execute_js`, `ipc_execute_command`, `ipc_emit_event` | No |
| Windows: list, resize | `manage_window` | No |
| Element picked by the user | `webview_select_element`, `webview_get_pointed_element` | Yes |

Read-only tools first. Ask before `webview_execute_js` changes page state and before `ipc_execute_command` or `ipc_emit_event`: those run real code in the user's app. Never run them against production data.

## Symptom to reference

| Symptom | Read |
|---|---|
| Android or iOS: white screen, old UI, IPC denied, permission without result, ANR | `tauri-native-mobile`, `references/debugging-mobile.md` |
| Blank window, WebView crash, engine error page, release build loading the dev URL | `tauri-native-desktop`, `references/recovery.md` |
| Selection, cursor, bounce, scrollbars, startup flash | `tauri-native-desktop`, `references/web-layer.md` |
| IPC denied in a new window, credentials or events crossing windows | `tauri-native-desktop`, `references/boundaries.md` |
| Checks to run and record on a finished screen | `tauri-native-desktop`, `references/acceptance.md` |

## Limits

The server acts on the webview. The bridge binds `0.0.0.0` by default; on desktop use `Builder::new().bind_address("127.0.0.1").build()`. How the server reaches a bridge on a phone or emulator was not read or tested; confirm it on the device. The skill reflects the server at version 0.13.2, checked on 2026-11-22: the connected server listed 19 tools and 3 prompts, and no app was driven. Recheck tool names against the installed server before relying on a parameter.

Commands that run these procedures: `/tauri-app-builder:debug`, `/tauri-app-builder:build`, `/tauri-app-builder:verify`, `/tauri-app-builder:bridge`.
