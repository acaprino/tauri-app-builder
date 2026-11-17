# External windows and dialogs: relationship, modality, close

Part of the tauri-native-desktop references: versions, scope and limits are in [guide.md](guide.md). Bracketed names are sources; their URLs are in [sources.md](sources.md).

## Gate: when NOT to open a separate OS window

Before creating a `WebviewWindow`, verify the surface actually belongs outside the main window ([guide.md](guide.md)):

- **Never extract side drawers or lateral detail panels into separate OS windows.** A drawer/sheet/inspector anchored to the side of the viewport (leaving the parent list or workspace visible or dimmed behind it) must stay an in-window panel on desktop too. Turning a lateral drawer into a blocking OS window adds a duplicate title bar, destroys master-detail context and pays WebView startup/IPC synchronization on every item click.
- **Do not assume dialogs should become OS windows either.** Making an app native does **not** imply converting all in-page modals into separate `WebviewWindow`s. Keep `<dialog>.showModal()` and existing in-page forms inside the main window unless the user explicitly asks to detach a specific dialog, or a concrete constraint requires leaving the main window's bounds (side-by-side/multi-monitor reference, quick entry while main is hidden, or a compact tray/utility host too small for the form). When detaching a dialog (such as Settings) is a design option rather than an explicit request, ask the user before extracting it.
- **Default external windows to non-modal.** Apply OS input blocking (`set_enabled(false)`, GTK `set_modal(true)`, AppKit sheet) only when concurrent interaction with the owner window would invalidate an in-flight transaction.

Observed Rust API:

```rust
pub fn parent(self, parent: &WebviewWindow<R>) -> Result<Self>
```

| Platform | Meaning of `parent` | Modality |
|---|---|---|
| Windows | Window owner, with z-order and lifecycle relationship | Input blocking is separate |
| Linux | Only `transient_for` | GTK `set_modal(true)` is a separate operation |
| macOS | AppKit child window | Not equivalent to a document-modal sheet |

On Windows `owner(&WebviewWindow)` is explicit; `parent_raw(HWND)` instead creates a `WS_CHILD` window confined to the client area: it is not the choice for an external dialog. The default docs.rs page uses the Linux target and does not show `owner`, `owner_raw` and `parent_raw`: read the Windows target page. Do not invent a `.modal(true)` builder for Tauri 2.12.5: there is no `modal` config key either, and the open issues found (for example [tauri#3326]) concern full-screen transparent overlays, not a generic modal API. [Windows builder], [tauri-utils 2.10.2 config.rs], [tao Linux window], [GTK modal], [AppKit child], [AppKit sheet].

On Linux, retrieve `gtk_window()` and call `set_modal(true)` only on the main thread. When coordinating from an async command or worker, pass a cloned Tauri window handle to `run_on_main_thread` and retrieve the GTK object inside that closure; do not move an extracted GTK object between threads. Handle both scheduling and inner-operation errors, and match the GTK crate to the lockfile. GTK modality blocks other application windows, so `transient_for` alone does not limit the block to the owner. Define the intended scope and test unrelated windows too. [Tauri WebviewWindow], [GTK modal].

For a modal Windows form, `set_enabled(false)` on the main window is a possible part of the adapter; Win32 requires re-enabling the owner before destroying the dialog to keep activation correct. It is a strategy to test, not a portable, already proven recipe. [Tauri WebviewWindow], [EnableWindow].

## Proposed manager contract

The coordinator owns an identified session and a single terminal completion. The following phases describe responsibilities, not a ready-to-copy snippet:

1. Reactivate the existing session or create one with an allowed type/label/route. Create the window in the async context/thread allowed by the version: Tauri documents a Windows deadlock risk in synchronous commands/event handlers.
2. Prepare content, initial data and a readiness handshake. Size to the monitor's work area; keep actions and content reachable with large text. Show and focus the dialog first; disable the main window only once a path that re-enables it exists.
3. If required, apply modality with the platform adapter, specifying which windows it blocks. Ownership, `always_on_top`, an HTML overlay and `inert` in the main page do not by themselves prove native input blocking.
4. Handle confirm/cancel/X/Escape according to the contract; on Windows release the block before the controlled destruction. Cover load failure, API errors, forced close, owner destruction and shutdown. Make cleanup idempotent and for nested dialogs define the release order, or count the blocks so the main window is re-enabled only when the last one ends.
5. Deliver the result exactly once, remove listeners/sessions and restore focus if the original control still exists. If confirmation fails, keep the draft and a readable error instead of closing automatically.

The documented APIs set the constraints; this orchestration is an engineering proposal to validate in the runtime. On macOS a sheet suits a brief, scoped task tied to its context; `beginSheet` presents one sheet per owner window and queues another until the current sheet is dismissed. For long or complex flows Apple suggests a new window or full screen; for repeated input whose effect the user watches (find and replace) a panel. "Document-modal" is AppKit API terminology, not HIG wording. [Apple Sheets], [Modality], [beginSheet].

In Windows handling do not rely only on `Destroyed` for the release: it is already too late for the documented activation order. Intercept `CloseRequested` and converge on the finalizer without `close()` recursion (deduced from the documented `close()` contract); `destroy()` can skip the normal path. Restore only the block owned by the session, respecting any other reasons for disabling. `tauri-runtime-wry` 2.12.3 implements `set_enabled` per platform: Windows calls `EnableWindow` directly, Linux `gtk_window().set_sensitive`, macOS attaches a dummy NSWindow as a sheet, which requires the main thread. It queues requests coming from other threads: a successful `Result<()>` does not prove the OS effect has already happened. Establish the order in the coordinator and test it, without blocking the UI thread while waiting for the form. [WebviewWindow source], [runtime lib.rs], [runtime macOS window], [runtime Windows window], [EnableWindow].

## Full close, not just unmounting the form

For React frontends also cover StrictMode: in development the effects' setup/cleanup cycle is repeated. Do not create and immediately destroy OS windows in that cycle without coordination. A deferred, cancellable open before creating the resource is one possible solution; a test must show a single actual open and the runtime must confirm repeated closing and reopening. Do not disable StrictMode to hide the defect.

For every surface intentionally hosted in its own OS window define an event → result → cleanup → focus table. Separate non-terminal Save/Apply in an editor or Settings window from a transactional form's terminal confirmation; successful non-terminal operations keep the window/session open. Cover successful confirm, rejected confirm, Cancel, Escape, X/Alt+F4, owner close, unexpected destruction and app exit. Confirmation completes only after the authoritative operation succeeds; an error keeps the draft and the message in the form. When the contract calls for closure, unmounting the form's component does not prove the OS host was closed: verify that the window really disappears and the main window becomes usable again, with no empty hosts, blocks or leftover listeners. Late events and repeated closes must converge on the same idempotent completion.

Choose one close decider per window, Rust or JS. The mere presence of a JS `onCloseRequested` listener makes the Rust side always call `prevent_close()` and moves the decision to the frontend, even if a Rust handler exists; the JS wrapper awaits the handler and then calls `destroy()`. [manager/window.rs], [window.ts].

If JS decides normal closes, define native supervision for a hung/crashed renderer, a rejected handler or a denied terminal command. Verify `core:window:allow-destroy` for the wrapper, or route completion through the authorized native coordinator. A missing JS answer must not leave an inaccessible modal window or its owner permanently blocked. The fallback must use the same session finalizer and release only that session's block. A timeout alone does not authorize discarding a live draft: use the product's draft recovery/persistence policy and an app-owned native recovery choice when needed. Test a failed renderer after close-listener registration, X/close during failure, repeated requests and reopening; distinguish restored drafts from data that existed only in the lost renderer. This supervision is a proposed failure path, not a second competing normal close decider. [Core window permissions], [manager/window.rs], [window.ts].

Verify the concrete close path in the shipped runtime. The wry source for WebView2 (0.57.1, unchanged in 0.57.2) registers `WindowCloseRequested` by directly calling `DestroyWindow(hwnd)`: JavaScript `window.close()` bypasses `CloseRequested`. From the frontend close with `getCurrentWindow().close()`, never with `window.close()`. In an adapter based on a same-origin portal (see "Alternative for trusted forms" in [boundaries.md](boundaries.md)), route the unmount to the shell's coordinator and test the real close; do not destroy a controller inside its own COM callback. [wry 0.57.2 source].
