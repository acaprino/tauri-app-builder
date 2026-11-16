# Context menus: remove browser UI, keep app actions

Read this when removing browser behavior or changing a desktop WebView's bootstrap. The target is the engine's default menu inside web content, including Edge/WebView2 on Windows. The OS title-bar menu (right-click on the frame, Alt+Space) and app-owned menus are separate and stay functional.

## Establish the failure

Record the failing window label, route, build mode and target (blank area, selected text, link, image, input, textarea, contenteditable or embedded frame). Inspect every WebView creation path: config-created main, Rust builders, frontend-created windows and windows rebuilt after a crash. A React-root listener or a one-time loop over existing windows does not cover all those paths. If different projects use different skill installations, inspect the loaded SKILL.md path and its references before assuming they received the same instructions.

## Windows: choose one implementation

For a request to remove the Edge menu, use **replacement** unless the product explicitly requires a filtered engine editing menu:

- **Replacement:** set `AreDefaultContextMenusEnabled` to `false` on each WebView2 instance, through Tauri's `with_webview` and `controller().CoreWebView2()?.Settings()?`. The setting defaults to `TRUE`; disabling DevTools or browser accelerators does not disable this menu. Inside the native callback, the Rust setter is `settings.SetAreDefaultContextMenusEnabled(false)?`. Check and report COM failures with the WebView label; successful scheduling of `with_webview` alone does not prove the setting was applied. Supply app-owned editing actions for text and selectable content, using a native popup or an accessible equivalent.
- **Filtered engine menu:** keep the setting `true` and handle `ContextMenuRequested`, allowing only the agreed editing actions for the target. Filter by the item's unlocalized `Name`; use that event's `CommandId` to report a selection, not as a hard-coded identity. Hide the menu where no permitted actions remain. Letting every input or text selection use the untouched engine menu is not filtering. [Menu item contract](https://learn.microsoft.com/en-us/microsoft-edge/webview2/reference/win32/icorewebview2contextmenuitem)

These implementations are alternatives: setting `AreDefaultContextMenusEnabled` to `false` also prevents `ContextMenuRequested` from firing. A replacement therefore needs an app/DOM invocation path. See Microsoft's [settings reference](https://learn.microsoft.com/en-us/microsoft-edge/webview2/reference/win32/icorewebview2settings) and [context-menu API](https://learn.microsoft.com/en-us/microsoft-edge/webview2/how-to/context-menus).

Apply the policy at creation, including dynamically created WebViews. A shared plugin's [on_webview_ready](https://docs.rs/tauri/2.12.5/tauri/plugin/struct.Builder.html#method.on_webview_ready) receives `tauri::Webview`, not `WebviewWindow`; adapt the helper type accordingly and register before relevant WebViews exist. This covers creation but does not guarantee execution before the initial navigation. Inspect Rust and JS builders as well as config entries. Microsoft documents that settings changed after `NavigationStarting` take effect on the next top-level navigation: check the first visible document, not only the page after reload. Bridge any initial gap with the document-start guard below; avoid an unconditional reload that can lose application state.

## Document guard and editing

For replacement, install the context-menu guard through the shared desktop initialization path at document start on every relevant document/frame. In Tauri 2.12.5 use a registered plugin's `js_init_script_on_all_frames` or a builder's `initialization_script_for_all_frames`; evaluating JS after page load is a different timing path. The guard calls `preventDefault()` on `contextmenu`, including editable targets and selected text. Keep the native Windows setting as the engine-level policy; the document guard also serves the other shipped engines, whose behavior must be tested separately. Scope it to the desktop app so a shared browser frontend keeps its intended behavior.

Integrate the guard with the app's context-menu dispatcher: preserve propagation and check whether a menu library skips events whose `defaultPrevented` is already true. Blanket `stopPropagation()` or `stopImmediatePropagation()` can break the replacement. A listener in the main document does not automatically handle an iframe's document; use the supported per-frame initialization path or an explicit policy for embedded content. Do not combine unconditional DOM prevention with the filtered-engine implementation, which needs the engine event.

Keep text selection, IME and editing shortcuts. Provide Cut/Copy/Paste/Select All and Undo/Redo where supported, with correct enabled states, keyboard invocation and focus restoration. A blanket editable-target exemption lets the browser menu back in; suppressing all menus without an accessible editing replacement is also incomplete. Apply the chosen browser-menu policy in development and release; a development-only exception requires an explicit product choice.

## Evidence required

Use the context-menu section of [acceptance.md](acceptance.md). Inspecting the setter or testing DOM `defaultPrevented` proves only that layer. Confirm absence of the Edge menu in the real Tauri app, on its first document, secondary windows and rebuilt WebViews; report runtime checks not performed as **to test**. Updating this skill does not update projects or executables that used an earlier version: reapply the change and rebuild the affected app before claiming its menu is fixed.
