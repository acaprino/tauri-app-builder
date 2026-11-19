# Background presence: tray, close to tray, start at login

Part of the tauri-native-desktop references: versions, scope and limits are in [guide.md](guide.md). Bracketed names are sources; their URLs are in [sources.md](sources.md).

An app that keeps working with its window closed (alerts, sync, monitoring) needs four pieces that are decided together: a tray icon, a close button that hides, one restore path and, optionally, start at login. Each is a product choice: confirm it through [Manual or Auto](../SKILL.md#confirm-product-choices). An app with no background work closes and quits normally.

Sources were read on 2026-11-19: `tauri-plugin-autostart` 2.7.0, `auto-launch` 0.6.0 and tauri 2.12.5. No code in this file was built or run for this skill.

## Choose the mechanism

| Need | Mechanism | Note |
|---|---|---|
| Window gone, process alive, user can bring it back | Tray icon in Tauri core plus close-to-tray | `tray-icon` feature of the `tauri` crate, no plugin |
| App opens when the user signs in | `autostart` plugin | Per-user entry, no admin rights |
| App starts at sign-in straight into the tray | `autostart` plugin with a launch argument | The argument tells startup to skip showing the window |
| Start elevated at sign-in without a UAC prompt | Windows Task Scheduler task created by the installer | No Tauri API; platform code |
| Work that runs before sign-in, with no user signed in, or across sign-out | Separate headless service binary, with the app as its client | No official plugin; see below |
| Background work that drives another desktop app's UI | Not a service: a signed-in desktop session plus a startup entry | See below |

## Tray and close to tray

Rules that make the behavior hold together:

- **One restore function.** Tray click, tray menu, second launch and notification click all call the same `show` → `unminimize` → `set_focus` sequence. Separate copies drift: one forgets `unminimize` and the window "opens" off screen.
- **Quit stays reachable.** Once the close button hides, the tray menu needs a Quit item and so does the menu bar (File > Exit). Both go through `app.exit(0)`, so shutdown cleanup runs on `RunEvent::Exit`. Without them the only way out is the task manager.
- **Linux.** `TrayIconEvent` is not emitted and `show_menu_on_left_click` is unsupported, so a click handler alone leaves no way back: the menu needs a Show item. The icon may not appear without a menu. [tray source]
- **macOS.** Staying alive without windows is the platform norm and reopening comes from the Dock (`RunEvent::Reopen`); a menu-bar extra is an addition, not the reopen path ([os-integration.md](os-integration.md)).
- **Hidden startup.** With a hidden-until-ready main window ([frame.md](frame.md)), the "first paint, now show" step runs once per process. A later page reload must not pull a hidden window out of the tray, and a tray-start launch skips the step entirely.
- **Recovery.** Put Reload in the tray menu when the page can end up blank or dead: the tray is native and still works then ([recovery.md](recovery.md)).
- **Tell the user once.** The first time the window hides, say that the app is still running and where to find it. A window that vanishes while the process continues reads as a crash or as hidden activity.
- **Notifications.** Close to tray keeps the process alive, so alerts still arrive; a click on one calls the restore function ([notifications.md](notifications.md)).

```rust
// Illustrative, compile against your lockfile. Cargo: tauri = { features = ["tray-icon"] }
pub(crate) fn restore_main_window(app: &tauri::AppHandle) {
    if let Some(window) = app.get_webview_window("main") {
        let _ = window.show();
        let _ = window.unminimize();
        let _ = window.set_focus();
    }
}

// in setup()
let show = MenuItem::with_id(app, "show", "Show", true, None::<&str>)?;
let quit = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
TrayIconBuilder::new()
    .icon(app.default_window_icon().cloned().expect("bundle icon"))
    .menu(&Menu::with_items(app, &[&show, &quit])?)
    .show_menu_on_left_click(false)
    .on_tray_icon_event(|tray, event| {
        if let TrayIconEvent::Click { button: MouseButton::Left, .. } = event {
            restore_main_window(tray.app_handle());
        }
    })
    .on_menu_event(|app, event| match event.id.as_ref() {
        "show" => restore_main_window(app),
        "quit" => app.exit(0),
        _ => {}
    })
    .build(app)?;

// on the builder
.on_window_event(|window, event| {
    if window.label() != "main" { return; }
    if let tauri::WindowEvent::CloseRequested { api, .. } = event {
        api.prevent_close();
        let _ = window.hide();
    }
})
```

Register `single-instance` first and have its callback call the restore function: starting the app again while it sits in the tray must bring the window back, not start a second process ([os-integration.md](os-integration.md)).

### Windows: pause the hidden WebView

Hiding or minimizing the host window does not tell WebView2 that it is off screen. Microsoft's reference says a WebView2 child window "does not get window messages when the top window is minimized or restored" and that developers "should set the IsVisible property of the WebView to FALSE when the app window is minimized and back to TRUE when the app window is restored", with CPU and memory benefits while hidden. [ICoreWebView2Controller]

Whether wry already does this for your version is **unverified** here: measure before adding code. Hide the window to the tray, then check the WebView2 processes' CPU and whether `document.visibilityState` reads `hidden`. If the page keeps rendering, call `hide()` on each webview of the window when it is hidden or minimized and `show()` in the restore function; minimize and restore arrive as `WindowEvent::Resized`, so check `is_minimized()` there. Timers and animations that must stop while hidden also key off `visibilitychange` in the frontend.

## Start at login

The `autostart` plugin registers the running executable with the OS. [Autostart], [autostart lib.rs]

| OS | What `enable()` writes | Note |
|---|---|---|
| Windows | A value under `SOFTWARE\Microsoft\Windows\CurrentVersion\Run`, named after the app | Machine-wide when the process may write there, otherwise per-user. `is_enabled()` also reads the Task Manager startup switch, so it returns `false` when the user turned the entry off there. [auto-launch windows.rs] |
| macOS | A Launch Agent plist in `~/Library/LaunchAgents` (default), or a login item added through AppleScript | Choose with `macos_launcher`; the AppleScript mode talks to System Events |
| Linux | `~/.config/autostart/<app name>.desktop` | Uses the AppImage path when the app runs as an AppImage. Flatpak and Snap are not covered by the examined source. [auto-launch linux.rs] |

```rust
// Illustrative, compile against your lockfile.
.plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| restore_main_window(app)))
.plugin(
    tauri_plugin_autostart::Builder::new()
        .arg("--autostart") // lets startup tell a login launch from a user launch
        .build(),
)
```

Decisions:

- **Off until the user turns it on.** Offer a visible setting, or ask once after the first successful sign-in. Enabling it silently at install adds a startup entry the user did not ask for.
- **The OS is the source of truth.** Read the state with `is_enabled()` every time the setting is shown. A copy in the app's own settings goes stale when the user disables the entry in Task Manager or System Settings.
- **Who may change it.** The plugin's default permission set grants `allow-enable`, `allow-disable` and `allow-is-enabled` to the WebView. The narrower option is to grant none and expose app commands that call `app.autolaunch()` through `tauri_plugin_autostart::ManagerExt`; the frontend then reaches autostart only through commands the app defines. [autostart permissions]
- **Login launch into the tray.** With close to tray, a launch carrying the autostart argument stays hidden: skip the first-show step and leave the tray icon as the entry point. A normal launch shows the window. Without a tray, a login launch shows the window like any other.
- **The registered path is the current executable.** Enabling from a development build registers the debug binary, and a portable copy registers wherever it sits. Hide the setting in development builds, and call `enable()` again after an update only if the install path can change.
- **Uninstall.** Whether the installer removes the startup entry is **unverified**: check on the installed package and add an uninstall hook if it stays behind ([packaging-updates.md](packaging-updates.md)).

## Windows services

There is no official plugin for running a Tauri app as a Windows service, and a windowed app should not be one: "Services cannot directly interact with a user as of Windows Vista". A service runs outside the user's desktop session, so it has no window, no tray icon and no toasts. [Interactive services]

- **Work that must run without a signed-in user** (collection, sync, device control): a separate headless binary registered as a service by the installer, for example with the `windows-service` crate. The Tauri app is its client over a local channel such as a named pipe. Restrict who can connect to the pipe and validate every request: the service usually runs with more rights than the app ([boundaries.md](boundaries.md)).
- **Elevated start at sign-in:** a Task Scheduler task set to run with highest privileges, created by the installer. A `Run` entry cannot elevate without a prompt. [Task Scheduler]
- **Work that drives another desktop app's UI** (a trading terminal, a legacy client): it needs an interactive desktop, so a service cannot host it. The working arrangement is automatic sign-in of a dedicated account, a startup entry that launches the work, then locking the workstation. Automatic sign-in stores that account's credential on the machine: use it only on a dedicated, physically controlled host.

Launch daemons on macOS and system units on Linux follow the same split: headless binary, installer-registered, app as client. None of these paths was built or tested for this skill.
