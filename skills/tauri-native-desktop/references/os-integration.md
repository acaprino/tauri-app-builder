# OS integration and lifecycle

Part of the tauri-native-desktop references: versions, scope and limits are in [guide.md](guide.md). Bracketed names are sources; their URLs are in [sources.md](sources.md).

| Operation | Tauri option | Constraint to verify |
|---|---|---|
| Menu and editing | Menu + predefined items | Platform roles and structure (unsupported items per platform, below), resources released |
| Background presence | Tray | Explicit exit gesture; on Linux `TrayIconEvent` is not emitted (the right-click menu is), the icon may appear only with a menu set, no tooltip |
| Second launch | Single-instance | Plugin registered first; reactivate the relevant dialog; a Tauri restart (`request_restart`) releases its lock, but not the app's own locks ([recovery.md](recovery.md)) |
| External links into the app | Deep-link | Cold start and running app; validate and queue until the UI is ready |
| Window restore | Window-state | Disconnected monitor; exclude temporary dialogs where appropriate |
| Desktop alerts and completed-job notices | Official notification plugin | Installed app, identity, scoped permissions and callbacks; reminders also need a supported scheduler ([notifications.md](notifications.md)) |
| Updates | Updater | Signing required and understandable restart ([packaging-updates.md](packaging-updates.md)) |
| Unread count or status | `set_badge_count` (macOS; Linux with a matching `.desktop`), `set_overlay_icon` (Windows, per window) | On Windows `set_badge_count` is unsupported: the badge is an icon to generate |
| Getting attention | `request_user_attention` | No effect if the app already has focus |
| Long operations | `set_progress_bar` | Per window on Windows (ITaskbarList3), app-wide on macOS and Linux; on Linux only desktops with `libunity` |
| Taskbar tasks, thumbnail buttons | No first-party API: `ICustomDestinationList`, `ITaskbarList3::ThumbBarAddButtons` | At most seven thumbnail buttons, not removable once added; stable AUMID shared with toasts; arguments forwarded to single-instance |

Sources for the options: [Menu], [Tray], [tray source], [Single instance], [Deep linking], [Window state], [Notification], [Updater], [Window, Windows target], [ThumbBarAddButtons]. Install only what the product uses. Global shortcuts need a different justification than shortcuts active while the app has focus.

Predefined menu items are not portable. Linux does not support `undo`, `redo`, `minimize`, `maximize`, `fullscreen`, `hide`, `hide_others`, `show_all`, `close_window`, `quit`, `services` and `bring_all_to_front`; Windows does not support `undo`, `redo`, `fullscreen`, `show_all`, `services` and `bring_all_to_front`. Replace the ones the product needs with custom items. The macOS app menu, with its Window and Help submenu ids, is in [frame.md](frame.md). [predefined menu items].

Confirm an open choice about what the main window’s close button does through [Manual or Auto](../SKILL.md#confirm-product-choices). Explain whether the process stays alive, what happens to background work and how the user reopens or quits the app.

Define separately close window, hide, terminate process and reopen. On macOS there is `RunEvent::Reopen { has_visible_windows }`, visible in the Darwin target documentation; the model of staying alive without windows is a product choice. Its counterpart is `RunEvent::ExitRequested { api, code, .. }`: call `api.prevent_exit()` only when `code` is `None`, so an explicit Quit still works. For menu-bar apps see `set_activation_policy(ActivationPolicy::Accessory)` and `set_dock_visibility`. [RunEvent Darwin], [app.rs].

```rust
// Illustrative, compile against your lockfile.
.run(|_app, event| {
    if let tauri::RunEvent::ExitRequested { api, code, .. } = event {
        if code.is_none() { api.prevent_exit(); } // stay alive without windows; explicit Quit passes
    }
});
```

## Notifications

If the product sends desktop alerts, read [notifications.md](notifications.md) and evaluate the official plugin first, including on Windows. It covers the complete delivery path, capability and OS permission distinctions, installed-app identity, suppression/fallback, callbacks and the version-specific desktop limits. In-app validation does not become an OS notification merely to look native.

## Linux file dialogs

The dialog wrapper's default and `rfd`'s default can differ: the plugin documents `gtk3`, while `rfd` documents `xdg-portal`. Verify resolved features, portal backend and package dependencies; for Flatpak or the KDE file picker use the portal backend. Use the builder's `set_parent` to tie native dialogs to the window. Portal modality is **unverified**: the specification only says "Whether the dialog should be modal. Default is true" and ties the dialog to a window through a `parent_window` handle (`x11:<XID>` or `wayland:<handle>`); without the handle it is not tied to the app's window. Test on GNOME and KDE before stating its effect. [dialog 2.8.4 Cargo.toml], [dialog lib.rs], [rfd source], [FileChooser XML], [window identifiers].

```toml
tauri-plugin-dialog = { version = "2", default-features = false, features = ["xdg-portal"] }
```
