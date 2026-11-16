# Native desktop notifications

Read this when the app already sends, or is being asked to send, desktop alerts: background job completion, incoming messages, reminders or events the user should see while the app is unfocused. Prefer the official `tauri-plugin-notification` and, for JS callers, `@tauri-apps/plugin-notification` as the native adapter on supported desktop platforms, including Windows. Keep field validation and immediate local feedback in the app; choose whether an unfocused event needs a system notification instead of duplicating every in-app toast. [Notification]

## Integrate the existing notification flow

1. Inspect the existing provider and its callers. Choose which events warrant desktop delivery, user opt-in/preferences, privacy of preview text and duplicate suppression. Keep domain decisions in the existing service; change its desktop delivery adapter and preserve the web implementation.
2. Add the official plugin with the project's Tauri CLI/package manager, for example `cargo tauri add notification`. Verify the resolved Rust and JS versions and the toolchain requirement. Confirm `.plugin(tauri_plugin_notification::init())` is registered; a frontend package alone is insufficient. [Notification]
3. For JS callers, grant only the needed notification permissions to the actual caller windows. Basic sending uses `notification:allow-is-permission-granted`, `notification:allow-request-permission` and `notification:allow-notify`; add action/listener permissions only if used. `notification:default` grants the entire plugin set. Rust-side delivery uses `NotificationExt`; frontend capability grants are not required merely to call the plugin from Rust. [Notification permissions], [Notification commands]
4. Follow the plugin permission API before sending and handle denied/unavailable states without repeated prompts. The desktop Rust implementation in 2.8.1 returns `Granted` without querying all OS notification settings: that result does not prove a banner will appear. Account for system notification settings, Do Not Disturb/Focus and the app's own preferences. Keep the event/status available in the app if desktop delivery is suppressed. [Notification desktop 2.8.1]
5. Test the installed package, its app name/icon and the relevant click behavior. A successfully prepared notification is not a delivery receipt; do not mark a business operation complete based on a notification callback. [Notification desktop 2.8.1]

The JS entry points are `isPermissionGranted`, `requestPermission` and `sendNotification`. In 2.8.1 `sendNotification` returns `void` through the plugin's notification wrapper; awaiting it does not acknowledge display. The Rust builder's `.show()` reports preparation errors but dispatches asynchronously. Route errors through the app's logging/status path and verify actual delivery separately. Direct use of the browser `Notification` global is not by itself evidence of native integration: the plugin also supplies a wrapper for it. [Notification JS 2.8.1], [Notification desktop 2.8.1]

## Windows delivery and activation

The official plugin documents installed applications as the supported Windows case; development may show PowerShell branding. Use the normal Tauri installer and app identity first. Verify the shipped installer on Windows before adding custom registry/AUMID registration. A native backend is an alternative only when a verified plugin limitation blocks a product requirement. [Notification]

Distinguish a banner while the process is running, a notification in the notification center, and activation after process exit. A callback in a running app proves neither of the latter cases. A custom Windows integration may require explicit identity and activation registration; follow the chosen notification backend's requirements, not a generic registry recipe. [Toasts from unpackaged apps], [AppNotificationManager.Register]

Sending a **new** notification after process exit is a separate requirement from clicking a previously delivered notification. Identify where the job/event is produced and which still-running component can send its notification. The plugin runs inside the app; installing it does not keep the process alive or create a background agent. A hidden window is different from a terminated process: prefer the existing native job coordinator for background delivery and do not depend on hidden-page timers. If post-exit delivery is required, define an authorized independent sender or supported OS scheduling mechanism and its lifetime; do not silently add a service, tray residency or autostart. Otherwise state the running-process limit and any catch-up on restart. Test exit before completion/delivery separately from exit after delivery. This is the application's lifetime contract, not a capability supplied by the plugin.

## Version-specific limits

Verified against plugin 2.8.1 source and its changelog; recheck the project's lockfile. The guide's mobile-only actions label is stale for this version. [Notification], [Notification changelog 2.8.1]

| Feature | Verified constraint |
|---|---|
| Click/action callbacks | Desktop support entered in 2.6.0. Register the handler/listener before sending; without one, actions are not shown. Rust handlers run on a background thread. |
| Windows click | Documented only while the toast is on screen, not after it moves to the notification center. Cold activation needs its own implementation and test. |
| Desktop options | Title, body, icon, sound and supported action buttons are used; scheduling/grouping options are ignored. A desktop reminder needs a scheduler with an explicit process-lifetime contract. |
| Action fields | Desktop uses action identifier and title; do not infer support for mobile reply fields, authentication or foreground flags. On macOS multiple actions have additional menu limitations. |
| Removing delivered notifications | In this version removal is a no-op on Windows/macOS; Linux/BSD support is restricted to tracked notifications. |

Source for the table: [Notification desktop 2.8.1]. Delivery and callback behavior still require the real OS. Use the notification section of [acceptance.md](acceptance.md), including denied/suppressed delivery and app-hidden/process-exited cases. Source names resolve in [sources.md](sources.md).
