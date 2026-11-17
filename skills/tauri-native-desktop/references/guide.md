# Guide: making a Tauri app as native as possible

Overview, minimum versions, proof and limits. The topic files are listed in the skill's SKILL.md. Bracketed names are sources; their URLs are in [sources.md](sources.md).

Reference snapshot: tauri 2.12.5, tauri-runtime-wry 2.12.3, wry 0.57.2, tauri-plugin-notification 2.8.1 and tauri-plugin-dialog 2.8.4 (depends on rfd 0.17). The original research dated 2026-11-14 was reviewed on 2026-11-15. These are examined versions, not an instruction to upgrade every project or a claim about the latest release. Tauri 3.x is not covered. This is a decision base, not an adapter tested on every platform. Compare the actual lockfile and shipped WebView Runtime before using an API. Illustrative excerpts need project integration and runtime verification even when their signatures have been type-checked. [crates.io tauri], [crates.io wry], [tauri-runtime-wry 2.12.3 Cargo.toml].

## Minimum versions

Many useful APIs are recent. Compare the tauri version resolved in the lockfile with this matrix before proposing an API. Source: [tauri CHANGELOG].

| Feature | Minimum tauri | Note |
|---|---|---|
| `WindowConfig::default().focus` is `true` | 2.10.0 | Bug fix: earlier versions returned `false`, so windows built from the default config opened unfocused |
| `set_simple_fullscreen` on `WebviewWindow` | 2.10.0 | macOS |
| `general_autofill_enabled` | 2.11.0 | Does not disable password or credit card autofill |
| Remote custom-command ACL and local-origin security fixes | 2.11.1 | Earlier 2.x behavior differs; inspect the security changes before relying on current remote/local privilege boundaries |
| `data-tauri-drag-region="deep"` | 2.11.0 | Opt out with `="false"` |
| Bring All to Front menu item; `dbus` feature for the Linux theme | 2.11.0 | `dbus` enabled by default |
| `Builder::on_web_content_process_terminate` | 2.11.0 | macOS/iOS; with no hook the runtime reloads the webview by itself |
| Double click on a drag region respects `maximizable: false` | 2.11.3 | Earlier versions maximized anyway |
| Liquid Glass effects, `no_redirection_bitmap`, `set_fullscreen_on_monitor`, `activate_ignoring_other_apps`, icons from exe resources | 2.12.0 | Windows 7 no longer supported |
| `asset://` files loaded asynchronously | 2.12.0 | A slow path no longer blocks every window |
| macOS transparency and fullscreen without `macOSPrivateApi` | 2.12.1 | The flag "is no longer required" for them |

## Choose what native means

| Goal | Solution | Limit |
|---|---|---|
| Inspect or edit a selected item in context (detail sheet, right-hand drawer, inspector, quick modal) | In-window panel, split view, `<dialog>` or `popover` inside the main `WebviewWindow` | Cannot extend past the main window's frame; preserves list context, instant open and shared web parity |
| Open/save files, pick folders, show standard OS messages, native menus/tray | OS controls through `tauri` core or `tauri-plugin-dialog` | They do not build arbitrary custom forms |
| Detach a workspace/Settings window, work side by side, or exceed a compact host frame | A separate `WebviewWindow` (non-modal by default) with a defined relationship to main | Adds OS window chrome, WebView startup/memory cost and cross-context state sync; fields stay HTML/CSS |
| Have fields, pickers and layout from the native toolkit | AppKit/GTK/WinUI integration or evaluating another toolkit | Platform-specific work, not a CSS property |

The distinction follows the [dialog plugin] catalog and the [WebviewWindowBuilder] contract. More OS windows do not make an app more native: never extract side drawers or lateral detail panels (such as a task or record sheet over a dimmed list) into separate OS windows, and do not assume ordinary in-page dialogs should become `WebviewWindow`s either. Turning a lateral drawer or routine dialog into a blocking OS window adds a duplicate title bar, breaks spatial context and slows down interaction. Keep side drawers, tooltips, dropdowns and in-page `<dialog>` modals inside the main window unless the user explicitly asks to detach a specific dialog or a multi-window/sizing constraint requires an external `WebviewWindow`.

For in-page surfaces, prefer semantic browser primitives when the shipped engines support them: `<dialog>.showModal()` for modal dialogs and `popover` for non-modal layers. Define focus entry/return, Escape and light-dismiss behavior explicitly. Feature-detect newer dialog attributes, anchor positioning and interest/hover triggers against the project's oldest WebView, and retain a tested fallback where needed. CSS or a JavaScript popup inside the page does not become an OS window. A stable cross-engine behavior matters more than adopting every recent primitive. [MDN dialog], [BCD dialog], [Chrome anchor positioning], [Chrome popover hint].

**Proposed order:** window behavior → keyboard/focus → OS services → accessibility → appearance → effects. The priority comes from the risk of an app that looks desktop but is hard to use; it is not an order prescribed by the framework. What the user notices in the first second and on every click (startup flash, cursor, selection, browser behaviors: [frame.md](frame.md) and [web-layer.md](web-layer.md)) usually comes before dialog refinements.

Mature hybrid products do not get the native feel by replacing HTML with OS controls: they avoid web-page tells, keep the OS where it is irreplaceable and invest in keyboard and speed. 1Password 8 put "every feasible piece" of logic in a Rust core, stopping short of the UI, yet still needed per-platform implementations of some components. A review of a Tauri v2 Mac app credits speed, "no needless animations" and a clear line between content and chrome. Speed and restraint weigh as much as widget imitation; measure them (Proving the result, below). [1Password 8, the story so far], [Tolaria review].

## Proving the result

Use [the acceptance checklist](acceptance.md), recording OS, runtime version, package type and tests. Renderer tests do not prove the behavior of the frame, OS windows or task switcher. The current WebDriver guide separates direct `tauri-driver` on Windows/Linux from `@wdio/tauri-service` with the `tauri-plugin-wdio-webdriver` plugin, which also covers macOS; the CrabNebula fork's macOS support requires a paid key; with msedgedriver the version must match the WebView2 Runtime. Recheck support in the chosen toolchain. [Tauri WebDriver], [WebView2 WebDriver].

Measure cold start, scrolling, interaction latency, cold open and reopen of the dialog, memory with multiple WebViews and release after repeated closes if they are project risks. This research does not prove any universal number of cheap windows. Native and hybrid apps can both be slow: the result needs measurements of the product. Measure WebKit rendering on the macOS/Linux targets you ship (one project moved from Tauri to Electron over WebKit rendering and sidecar startup on Windows), and treat any child process launched at startup as a reliability risk to test on the installed package. [Moving OpenCode Desktop to Electron].

## Limits of this guide

Primary-source research and architectural synthesis; no cross-platform adapter compiled or tested. Orchestration examples are proposals and snippets are illustrative, except the ones marked as compiled, which name the versions they were built against. `latest` pages and GitHub branches move; recheck them before changing a new project. No guarantee about compositors, screen readers, IME or notification activation after process exit without tests on the actual package.

Not verified: Tauri 3.0 alpha changelogs; how the default macOS reload behaves under repeated crashes; the WebKitGTK `web-process-terminated` signal through `with_webview`; whether WebView2's Window Controls Overlay became stable after 1.0.4314.35; `overscroll-behavior` and `prefers-color-scheme` in WebKitGTK 2.50+; whether `AccentColor` gives the real accent in WebView2 Runtime 150+; `popover="hint"`, interest invokers, `closedby` and anchor positioning in WebKitGTK; the portal `modal` option on real backends. Apple HIG values such as default font sizes or tooltip delays were not researched: do not state them as facts. Client- vs server-side decorations on GNOME/KDE, Flatpak and AppImage packaging and the Dock menu were not studied.
