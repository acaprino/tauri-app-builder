---
name: tauri-native-desktop
description: "Use when building, auditing or improving Tauri 2 desktop behavior on Windows, macOS or Linux: windows and dialogs, frame, system services, native notifications, packaging/updates, sidecars, keyboard/accessibility, browser context menus, startup flash and WebView lifecycle. Not for web-only styling or mobile apps."
---

# Tauri Native Desktop

Act as a desktop integration engineer. Optimize the observable behavior on the chosen operating system while preserving the project's architecture and permissions. Visual resemblance does not replace correct focus, keyboard, accessibility and lifecycle.

## Set the scope and completion bar

For a whole-app audit or a request to make the app native, read [baseline.md](references/baseline.md) and classify every section of [acceptance.md](references/acceptance.md). A narrow request covers its affected surfaces and shared dependencies; it does not authorize an unrelated redesign. Keep a coverage record: surface/window → expected behavior → implementation → evidence → remaining work. Record a reason for each not-applicable or deferred item; an untested item stays untested. Existing audit documents are evidence to recheck, not a reason to skip a failing behavior.

## Identify the required level

Always distinguish four levels, starting from the lightest one that fits the task:

- **In-window surface (default for application UI)**: side panels, detail drawers/inspectors, split views, in-page `<dialog>` modals and `popover` layers inside the main `WebviewWindow`. Keeps spatial context, zero window-spawn latency and parity with a shared web frontend.
- **Native OS control or service**: file/folder picker, simple OS message box, native menu bar, native context menu, system tray and system notifications. Use system APIs directly or through a verified plugin.
- **Separate `WebviewWindow` with web content**: a distinct OS window managed by the window manager (the form inside stays HTML/CSS). Reserve this for surfaces that genuinely need independent multi-window/side-by-side placement, launch while main is hidden, or must exceed a compact host frame—**never** for routine item-detail sheets or side drawers.
- **Fully native interface**: AppKit, WinUI/Win32 or GTK widgets; requires a platform-specific integration or a different toolkit choice. Tauri does not turn HTML components into these controls.

Making an app behave natively does **not** mean turning in-page panels, drawers or forms into separate OS windows. If native toolkit widgets are needed, state the cost and verify the integration before promising it.

## Procedure

1. **Gather the context.** Read local instructions, manifests and lockfiles. Identify shipped platforms, Tauri/plugin/WebView versions, windows, any shared web frontend, authentication, application state and ACLs. Read [guide.md](references/guide.md) and compare the resolved tauri version with its minimum-version matrix before proposing an API; Tauri 3.x is not covered. If the project already holds an audit or a native-rules document from an earlier pass, take it as the baseline: check each reference in scope against it and report the differences. Ask for missing context only when it changes the solution.
2. **Classify the surfaces.** Inventory side drawers, dialogs, panels, menus and notices. Record which levels fit each surface and why:
   - **Never turn side drawers or lateral detail sheets into separate OS windows.** A right/left drawer or inspector that opens over or beside a list/workspace (keeping the parent view visible or dimmed behind it) stays an in-window panel on desktop too; flag any existing blocking OS window used for a drawer/item sheet as UX over-extraction.
   - **Default routine application UI to in-window.** This includes in-page modals (`<dialog>.showModal()`), confirmations, toolbars, popovers, tooltips and dropdowns.
   - Use **OS controls or services** for file/folder pickers, native menus/tray, standard OS message alerts and system notifications when the workflow calls for them.
   - Choose a **separate `WebviewWindow`** only when explicitly requested or objectively required by multi-monitor/side-by-side reference, launch while main is hidden, an independent multi-window workspace, or a host window too compact to fit the form. Default secondary windows to **non-modal**.
3. **Confirm product choices.** Use [Manual or Auto](#confirm-product-choices) for the unresolved behaviors listed there when they are in scope for implementation. For report-only work, include recommendations in the report.
4. **Define the desktop contract.** Read the reference files for the surfaces in scope (table below) and the matching sections of [the checklist](references/acceptance.md). Define owner, modality, sizing, focus, closing, result and authoritative state. Verify against the actual versions: `parent`, `owner`, `transient_for`, sheets and modality are not synonyms.
5. **Deliver the authorized scope.** In an audit, deliver evidence and priorities. When changes are requested, implement verifiable increments that reuse the existing domain and transport. Define the least privileges for new windows and test the caller. Keep the browser path when the product requires it. Before setting an engine switch, check its default in the resolved versions. Add meaningful regression checks for changed behavior and shared initialization paths; scope chrome cursor rules to chrome, composition guards to submitting handlers, and desktop lifecycle rules to Tauri-managed windows.
6. **Verify in the real app.** Run the relevant automated checks and tests in the installed app on the declared platforms. Distinguish inspected code, build, automated tests and observed behavior. Report the tests that still need a different environment.

### Confirm product choices

Carry forward decisions already established by the user or by explicit product requirements. For the choices below, confirm any that implementation needs to make. A repair to an established behavior uses that behavior as its requirement.

- **Dialog placement.** For each new dialog or existing dialog whose placement is being reviewed, compare opening it in the main window, in a separate window, or as a standard OS alert where applicable. Explain whether the main window stays usable. [Dialogs](references/dialogs.md)
- **Title bar.** Compare the system title bar with a custom title bar. Explain how dragging, system menus and controls such as Windows Snap Layouts would work. [Frame](references/frame.md)
- **Main window close.** Compare closing the window, quitting the app and hiding to the tray where supported. Explain what happens to running work and how the user reopens or quits the app. [OS integration](references/os-integration.md)
- **Notification delivery.** For each affected event, compare in-app feedback with a system notification where appropriate. Explain what happens while the app is focused, unfocused, hidden or exited. Check that delivery can work with the chosen close behavior. [Notifications](references/notifications.md)

For each open choice, show the current behavior if one exists, the feasible options and their effect on the user. Offer **Manual** and **Auto** in one prompt for all open choices in scope. Honor a mode the user has already selected for the task.

- **Manual.** Let the user choose each open behavior. Their explicit choices approve those behaviors.
- **Auto.** Recommend one option per open choice using the defaults and the app's actual workflow. Give a short reason for each. Let the user approve the proposal or amend individual choices. Wait for explicit approval of the resulting proposal before implementing those behaviors.

Use the confirmed behaviors when defining the desktop contract.

## References

Read the files the work in scope needs, not all of them. [native-plugins-data.md](references/native-plugins-data.md) holds the official plugin support matrix for all five platforms, the maintained plugins and the community candidates (kept in sync with the plugin's `shared/native-plugins.md` so this skill also works standalone); the `tauri-native-mobile` skill owns Android and iOS work. Each file holds the reasons, the version facts and the illustrative code for its topic.

| Work in scope | File |
|---|---|
| Versions covered, minimum-version matrix, choosing the level, proving the result, limits | [guide.md](references/guide.md) |
| Whole-app native audit or implementation: essential coverage and completion criteria | [baseline.md](references/baseline.md) |
| Title bar, decorations, Snap Layouts, startup flash, drag regions, Mica/vibrancy/Liquid Glass | [frame.md](references/frame.md) |
| Existing or proposed separate OS windows, including owner/parent, modality, close lifecycle and React StrictMode | [dialogs.md](references/dialogs.md) |
| What a new window may call and read: capabilities, credentials, events, relay or broker | [boundaries.md](references/boundaries.md) |
| Bootstrap of every WebView, WebView2 switches, selection and cursors, bounce, scrollbars | [web-layer.md](references/web-layer.md) |
| Removing browser behavior, Edge right-click menu, editing menus or WebView bootstrap changes | [context-menus.md](references/context-menus.md) |
| Zoom, text size, screen readers, forced colors, system accent, IME, command registry | [keyboard-accessibility.md](references/keyboard-accessibility.md) |
| Menu, tray, single instance, deep link, badge, progress, exit and reopen, notifications, Linux file dialogs | [os-integration.md](references/os-integration.md) |
| Installers (NSIS/MSI/DMG/Linux), signing/notarization, updater artifacts and keys, sidecars/shell, CI | [packaging-updates.md](references/packaging-updates.md) |
| Which plugin or core API covers a capability: credentials, sign-in, biometrics, camera, disk access, location, clipboard, updates; gaps with no official plugin | [native-plugins.md](references/native-plugins.md), [native-plugins-data.md](references/native-plugins-data.md) |
| App sends desktop notifications, background alerts or completed-job notices | [notifications.md](references/notifications.md) |
| Engine error page, WebView process crash, release build that loads the dev URL | [recovery.md](references/recovery.md) |
| Acceptance checks to run and record | [acceptance.md](references/acceptance.md) |
| URL of a source named in brackets in the files above | [sources.md](references/sources.md) |

## Key decisions

- **Frame.** Recommend the OS frame when native behavior is the priority. On Windows 11, `decorations: false` with HTML buttons loses Snap Layouts on hovering maximize unless dedicated Win32 code is added. If a custom bar is chosen, budget that work and verify Win+Z and the other system features it replaces.
- **First frame.** Every window, main and secondary, opens on the theme background: no white flash.
- **Chrome and content.** Chrome is not selectable, not draggable and uses the arrow cursor; content (documents, fields, code, data to copy) stays selectable.
- **In-window vs external window.** Side drawers, lateral detail sheets and inspectors **must** stay inside the main window (preserving the visible/dimmed list behind them and instant switching). Even for ordinary dialogs, extracting them into separate OS windows is **not** automatic: in-page `<dialog>.showModal()` is valid desktop UI, so never bulk-convert dialogs into `WebviewWindow`s unless requested or required by multi-window/side-by-side use, hidden-main entry or a compact host frame.
- **Modality.** Default secondary windows to non-modal. Reserve OS-level modal blocking (`set_enabled(false)` / GTK `set_modal` / AppKit sheet) for short, high-consequence decisions where interacting with the owner window would corrupt an active operation—never for drawers, routine item sheets or browsing. A modal dialog gives the main window back on confirm, cancel, X, error and destruction. `always_on_top` is not modality.
- **Lifecycle.** An OS window brings its whole lifecycle: opening, readiness, confirm/save, cancel, Escape, X/Alt+F4, owner close, error and shutdown. A terminal confirmation of a transactional form closes the OS window, not just the form inside it: an empty window is a defect. Editor Save and Settings Apply follow the product's contract and keep the window open when intended. A failed save keeps the draft, the message and the retry. On terminal closure, verify release of modality, focus return and single cleanup. One close decider per window (Rust or JS); `window.close()`, `close()`, `destroy()` and unmounting the form's component are different paths.
- **Sizing.** Side drawers and most dialogs fit inside the main window; only a surface that genuinely must extend past a compact main window's frame needs an external OS window. With small windows, enlarged text and long content the body scrolls and the actions stay reachable.
- **State and credentials.** Another WebView is a separate JavaScript context. Use the service/host that is already authoritative, a reliable initial read and targeted invalidation events; no second backend, no secrets in URLs. If only main has access to credentials, define the secondary window's authenticated path before implementing it.
- **Bootstrap.** Every new WebView gets the relevant desktop bootstrap, not only main. An external window need not block the main one: a Settings window can be non-modal and reusable.
- **Context menus.** When removing browser behavior, suppress the default engine menu in every WebView, including editable targets and selected text; retain app-owned actions and accessible editing. Read [context-menus.md](references/context-menus.md) for replacement versus filtering, first-navigation timing and verification. Native-looking Edge menus are still browser UI; the OS frame's system menu is separate.
- **Browser commands and zoom.** Remove irrelevant browser commands; keep editing, useful selection and IME; replace every intercepted shortcut the product needs with an app command. Engine zoom is off by default in Tauri, so accessible zoom is the app's job. With more than a few shortcuts, derive bindings, menus and the shortcut list from one command registry.
- **Failures.** Never leave the user on the engine's error page: an app-owned recovery surface, recovery from WebView process failures with a retry limit, and an app-handled reload.
- **Bounce.** Decide per surface and platform, keeping scrolling and motion preferences; overscroll/rubber-banding and elastic animations are separate choices.
- **Optional features.** Mica/vibrancy, tray, autostart, global shortcuts and updater are product choices. Effects require the appropriate transparent-window configuration and a readable fallback; an always-opaque HTML root can hide an active material.
- **Notifications.** If the app sends desktop alerts, evaluate the official Tauri notification plugin as the native adapter, including Windows toasts. Read [notifications.md](references/notifications.md) for setup, scoped permissions, delivery limits and installed-app checks. Inline validation and local feedback keep their in-app role.
- **Native capabilities.** Before adding a capability (credentials, sign-in, biometrics, camera, disk, location), read [native-plugins.md](references/native-plugins.md): prefer core, then an official plugin supported on every shipped OS, and state plainly when the service has no official plugin.
- **Speed and restraint** weigh as much as widget imitation: no decorative animations, quiet chrome, local interactions without spinners; measure startup, scrolling and latency on the shipped platforms.

## Delivery

Show the achieved behavior or the top-priority defect first. Include files and lines, platform/version, checks and limits. For an audit use `surface → current state → solution → acceptance test`. Report coverage and deferred/untested behavior; compilation and DOM tests do not prove OS behavior. Updating a skill does not update projects that used it: identify any application work still required. One concrete final action if work remains for the user.

The references reflect research done on 2026-11-14 and reviewed on 2026-11-15 (tauri 2.12.5). Recheck the needed APIs for every new project, especially modality, notifications and permissions. The skill provides expertise: on its own it does not authorize changes, installs or releases.
