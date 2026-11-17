# Desktop acceptance checklist

Use only the rows relevant to the supported platforms. Record each outcome as **observed**, **automated test**, **static inspection**, **to test** or **not applicable**. Do not treat the presence of code as proof of OS behavior. This checklist proposes checks; the reasons are in the topic files listed in the skill's SKILL.md, the source URLs in [sources.md](sources.md).

## Test sheet

Project/commit: … · OS/build/desktop: … · Tauri/plugins/runtime (resolved in the lockfile, compared with the minimum-version matrix in [guide.md](guide.md)): … · WebView2 Runtime/WebKit version: … · Installed package: … · Monitor/scale/text size: … · Date: …

For a whole-app request, classify every section using [baseline.md](baseline.md). Each applicable check records pass/fail, evidence type, window labels and remaining work; not-applicable and deferred checks record a reason. A failed or untested check cannot become a pass because the code exists.

## Windows and dialogs

- [ ] Surface classification fits the workflow: side drawers and lateral detail sheets **never** open as separate OS windows, and ordinary dialogs stay in-page (`<dialog>` / overlay) unless external window management was explicitly requested or required by multi-monitor use, hidden-main launch or a compact host frame.
- [ ] When an external OS window is intentionally in scope, it is a real system window and can extend past the main window's edges; non-modal is used unless owner input would corrupt an active operation.
- [ ] Owner/transient/child relationship appropriate to the target; when OS modality is required, input blocking is demonstrated with mouse and keyboard on the main window.
- [ ] GTK work runs on its main thread, including async creation paths; modality blocks exactly the intended windows, leaving unrelated windows usable when required.
- [ ] Cancel, X, Escape, confirm and error have defined outcomes; the result is applied exactly once.
- [ ] A transactional form's terminal confirmation closes the OS window, restores the owner's usability and returns focus; disappearing fields alone do not count, and no empty host remains. Editor Save and Settings Apply keep the window open when the product contract requires it; they do not accidentally run terminal cleanup.
- [ ] Save rejected or network down: window still open with readable draft and error, retry possible, no false confirmation.
- [ ] X, Alt+F4, Escape/IME, Cancel, owner close and app exit go through the appropriate close contract; late/duplicate events do not duplicate results or cleanup. Also test reopening after each path.
- [ ] With a JS close listener registered, X, Alt+F4 and the app's close command reach the same finalizer. Tauri-managed windows use their desktop close adapter; any retained browser-popup `window.close()` belongs only to the browser path and is tested separately.
- [ ] Creation/load failure, network loss, dialog destruction and shutdown do not leave the main window disabled.
- [ ] With a JS close listener installed, a failed/hung handler, denied terminal command or crashed renderer reaches native supervision: recoverable drafts retained, unavoidable loss reported, owned modality released exactly once, reopening possible.
- [ ] Reopening, nested dialogs, tray and second instance reactivate the relevant window; no orphan windows.
- [ ] With a React frontend, StrictMode's repeated mount does not create two OS windows for one dialog: a cancellable deferred open or other verified coordination avoids duplicate resources and races with destruction.
- [ ] In-page dialogs, side drawers and popovers: Escape closes them, focus returns to the invoker, the background is inert while a modal or blocking drawer is open, and parent list context stays intact; submenus stay open during diagonal pointer movement.
- [ ] Each control type follows one rule across the product (for example all context menus native, or all custom).

## Frame and monitors

- [ ] Single title bar, drag, double click, resize, minimize/maximize and close work; double click on a drag region respects `maximizable: false`.
- [ ] Windows: system menu, Alt+Space, Win+Z and Snap Layouts on hovering maximize verified separately; the minimum window width fits the snap zones.
- [ ] Cold start and opening of every secondary window, in light and dark theme: no white frame or frame of a color other than the theme background (record at 60 fps if needed).
- [ ] Hidden-until-ready startup has a bounded failure path: with the first document unavailable, the user gets a usable app-owned recovery surface and no indefinitely hidden window or exposed engine error page. Test the oldest shipped WebView Runtime separately from Cargo versions.
- [ ] With a system material enabled: turning off transparency effects, battery saver, inactive window and high contrast leave readable, opaque content.
- [ ] macOS: traffic lights, full screen, app menu with Window and Help menus, Cmd+W/Cmd+Q and reopen from the Dock verified according to the chosen policy; `hiddenTitle`, tabbing, first-mouse click and link preview behave as decided.
- [ ] Linux: shipped compositors/sessions tested; file picker and dependencies work in the package.
- [ ] Linux Wayland (GNOME and KDE where shipped): correct icon, app name and window grouping in the dock/taskbar.
- [ ] Dialog and footer reachable at 100/150/200% scale, enlarged text and a removed monitor; sizes adapted to the work area.
- [ ] Windows text size 150% with 150% scale: no clipped content, actions reachable. Zoom to 200% works: through app commands when engine zoom is off, which is Tauri's default (`zoom_hotkeys_enabled` is `false`).
- [ ] A dialog taller or wider than the main window does not clip: long content scrolls and all actions are reachable by mouse and keyboard.

## Keyboard and accessibility

- [ ] Initial focus, Tab/Shift+Tab and return on close verified; no unintended trap. Focus indication remains visible for keyboard navigation, text input and user preferences; `:focus-visible` does not imply every mouse-focused control must hide its ring.
- [ ] Useful editing and context menu present; selection and copy of the necessary data available.
- [ ] Ctrl/Cmd+A outside fields does not select the interface; content text can be selected and copied. Windows desktop chrome uses the arrow cursor; content links, other platforms and the shared browser path follow their agreed policy. Inspect app CSS, component-library styles and utility classes.
- [ ] F5, Ctrl+R, Ctrl+P, Ctrl+F, F12, Alt+Arrow, mouse back/forward buttons, middle click and Ctrl+click on links, and a file dropped outside a drop zone: none reloads, navigates or opens browser features; every disabled shortcut the product needs has an app command.
- [ ] Enter/Escape do not break IME or multiline input; with a Japanese or Chinese IME on macOS and Windows, confirming a candidate with Enter does not submit the form or message; shortcuts follow the target's conventions.
- [ ] On shipped Linux sessions, IME is tested independently; system-preference portal updates, absent backend/keys and unset/unknown values use the agreed defaults.
- [ ] Shortcuts work with the non-US keyboard layouts the product supports; the shortcut list shown to users matches the real bindings.
- [ ] Labels, roles, values, errors and color/icon pickers readable with the system screen reader; state not conveyed by color alone.
- [ ] Light/dark, contrast themes/forced colors, reduced motion and zoom tested separately; focus rings and separators stay visible in forced colors.
- [ ] Changing system accent and theme with the app open updates the interface without restart, on every shipped platform (if the product follows the system accent).

## Context menus

- [ ] Right-click on blank areas, app chrome, selected text, links/images and input/textarea/contenteditable: no default browser menu; only the agreed app actions or filtered editing menu. OS frame right-click and Alt+Space still work.
- [ ] Same result in main and every secondary/dynamically created WebView, on the first visible document, after reload, reopen and crash recovery; test embedded frames where present.
- [ ] Shift+F10 and the Menu key on Windows follow the same policy; Cut/Copy/Paste/Select All, supported Undo/Redo, text selection, IME and replacement-menu focus work.
- [ ] Windows: the native callback's outcome is recorded per WebView, with COM failures visible; replacement uses `AreDefaultContextMenusEnabled=false`, filtering uses `true` with a verified handler. Neither devtools settings nor DOM-only tests count as this check.
- [ ] Development and installed release tested separately; shared browser frontend preserves its intended behavior. Record OS/runtime, window labels and untested cases. An older executable is rebuilt before testing the change.

## Bounce and scrolling

- [ ] Explicit decision for list, panel and viewport: OS feedback kept or bounce suppressed; spring animations evaluated separately.
- [ ] Trackpad and wheel tested at the top/bottom edges and on the relevant axes: no unintended movement of the app structure or empty background.
- [ ] A nested list at its edge does not drag the underlying surface when it must be isolated; ordinary scrolling keeps working.
- [ ] `contain` and `none` tested on the shipped WebView, without inferring the outcome from the CSS alone (WKWebView short pages included).
- [ ] Web frontend: intended gestures preserved; reduced motion removes non-essential elastic animations without removing understandable feedback.
- [ ] Scrollbars follow theme and high contrast; their appearance does not shift the layout where that matters.

## Boundaries and state

- [ ] New window identified by allowed type/label/route; credentials absent from URLs.
- [ ] Negative test of privileged commands from the secondary window, checking the app command manifest and combined capabilities.
- [ ] Result correlated to the session/caller, applied through the authoritative data owner.
- [ ] Minimal/targeted events, handshake and re-read cover late listeners, reopening and errors.
- [ ] Event API grants and payload/caller authorization checked separately; a window claimed to lack credentials cannot read them through shared cookies, localStorage, IndexedDB or its opener/profile.
- [ ] A trusted popup portal receives the full WebView bootstrap and intended native features. Opener/child close, reload and crash are tested separately; React ownership, target document, IPC caller identity and cleanup follow the documented contract.
- [ ] Listeners, sessions and menu resources released after repeated cycles; no duplicated notification streams.

## WebView failures

- [ ] In a disposable instance, ending its positively identified renderer follows bounded recovery and restores persisted drafts; an out-of-process frame failure follows its frame policy. A browser-process exit rebuilds the affected group or offers a restart after native state is persisted. Never terminate unrelated WebView/Edge processes. On Windows this needs app code; on macOS Tauri reloads by default, or runs the app's hook. See "Testing recovery on Windows without Task Manager" in [recovery.md](recovery.md).
- [ ] Dev server stopped, network offline and a link to an unreachable local address: no engine error page; the app's own recovery surface or the system browser appears instead.
- [ ] Repeated forced crashes: recovery stops after the retry limit and shows the app's error surface (on macOS only with the app's own hook: the default reload has no limit); no reload loop.
- [ ] App-handled reload works independently of the page. A live page with dirty state reloads only after durable save or explicit discard; save failure, cancellation and a save slower than the timeout retain the draft. A confirmed renderer crash restores the persisted draft where supported.
- [ ] A recovery surface shown as a native dialog is owned by the main window and blocks it while open; answering it gives the main window back.
- [ ] After a restart triggered by recovery the new process opens its window: single-instance and every lock the app owns are free.
- [ ] A navigation the app refuses (for example `location.href = 'about:blank'` in the page) leaves the page in place and raises no recovery surface.
- [ ] A normal close and exit raise no recovery surface.
- [ ] Partial native-handler installation, repeated bootstrap, rebuilt WebViews and stale callbacks do not duplicate recovery; event registrations are removed through their owning UI-thread lifecycle.
- [ ] The release package loads the embedded frontend: the page URL is the app's custom-protocol origin, not `devUrl`, with the dev server not running.

## Notifications (when the product sends desktop alerts)

- [ ] The existing notification flow uses the chosen native adapter for desktop events and retains appropriate in-app/web feedback; no duplicate alerts for one event. The official Tauri plugin was evaluated before custom OS code.
- [ ] Rust plugin initialization, compatible JS bindings when used, and caller-scoped permissions verified; permission denied, OS suppression/Do Not Disturb and the app's preference leave an accessible in-app status without repeated prompts.
- [ ] Installed Windows package shows the intended app identity and icon; development behavior is recorded separately. A successful send/permission response is not used as proof of a visible banner.
- [ ] Click/actions while visible, notification-center click, app hidden and process exited have separate recorded outcomes; unsupported activation is explicit. Listener registration precedes sending, duplicate events do not repeat business actions, focus returns only as intended.
- [ ] For new notifications after process exit, the event producer and sender have an explicit lifetime contract; exit before job completion/delivery is tested separately from clicking an existing notification after exit. If delivery requires a running app, that limit and any catch-up on restart are explicit. Scheduling, grouping, cancellation and richer actions are used only where supported by the resolved backend.

## Installed app

- [ ] Package name/icon and associations correct; second launch and deep link verified where planned.
- [ ] Linux with `enableGTKAppId` enabled: a second launch forwards its arguments to the running instance instead of failing silently.
- [ ] Window close, hide and exit are distinguishable and consistent with the product; on macOS an explicit Quit exits even when closing the last window keeps the app alive.
- [ ] Taskbar/dock: badge or overlay icon, attention request and progress bar appear and clear as designed; jump list tasks reach the running instance.
- [ ] Signing/update/restart verified if the updater is in scope.
- [ ] Startup, scrolling and interaction latency and memory measured if relevant; child processes launched at startup start reliably on the installed package; DOM tests and desktop tests reported separately.
