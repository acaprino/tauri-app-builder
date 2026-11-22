---
description: Connect a Tauri 2 project to this plugin's tauri MCP server by adding the debug-only MCP bridge crate.
argument-hint: [project path]
---

Set up `tauri-plugin-mcp-bridge` in the Tauri 2 project at `$ARGUMENTS` (default: the current directory). The `tauri` MCP server of this plugin can only drive an app that registers the bridge.

1. **Check the versions first.** Read `src-tauri/Cargo.toml`, `Cargo.lock`, `tauri.conf.json` and the capability files. The bridge needs the resolved `tauri` to be 2.12.2 or a later 2.12 patch, and Rust 1.90 or later. If the project is outside that range, stop and report the resolved versions. Do not upgrade Tauri unasked.
2. **Take the exact steps from the server.** Call the `get_setup_instructions` tool of the `tauri` MCP server and follow it for the crate version, the registration and any capability permission. If the server's tools are not available (names `mcp__plugin_tauri-app-builder_tauri__<tool>`; search deferred tools first), ask the user to open `/mcp` and check that `plugin:tauri-app-builder:tauri` is connected, then stop.
3. **Register it for debug builds only.** Put the plugin behind `#[cfg(debug_assertions)]` so a release build never contains it. On desktop bind it to `127.0.0.1` with `Builder::new().bind_address("127.0.0.1").build()`: the default is `0.0.0.0`, which exposes script execution and IPC to the local network. How a phone or emulator reaches the bridge was not verified: if the target is a device, say so and ask before choosing the bind.
4. **Name the two other required settings.** `app.withGlobalTauri: true` in `tauri.conf.json` (the server cannot talk to the webview without it; it exposes `window.__TAURI__` to page scripts) and the `mcp-bridge:default` permission in the capability file. Ask before setting `withGlobalTauri`, and prefer a dev-only way to set it (check `tauri dev --help` for `--config`) so release config stays unchanged.
5. **Show the diff before applying it.** Change only `Cargo.toml`, the builder registration, `tauri.conf.json` and the capability file.
6. **Prove the connection.** Ask the user to restart `tauri dev`, then call `driver_session` to start a session and `manage_window` with `action: "list"`. Report what answered. If nothing did, say so and give the first failing step. Do not claim the bridge works from the diff alone.

Finish with the files changed, the resolved versions and whether step 6 ran.
