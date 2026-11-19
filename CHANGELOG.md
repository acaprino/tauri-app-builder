# Changelog

One section per released version of the plugin. The release workflow publishes the section that matches `version` in `.claude-plugin/plugin.json` as the GitHub Release notes.

## 1.6.0

### Desktop skill

- The window's content never moves as a whole: locking the root of every WebView against overscroll is now a default, on Windows too, where a precision touchpad or a touchscreen makes the whole view slide and uncover the background.
- The lock is applied without waiting to observe the effect on a device; an audit can no longer defer it as "to be observed first".
- Explains why a full-height shell with hidden overflow does not prevent it, and that it is not WebView2's pull to refresh.
- New acceptance checks for the locked root.

### Mobile skill

- New section on overscroll and pull to refresh: lock the root, scroll inside each screen's container, match the background, and build pull to refresh as a gesture of the list that needs it.

## 1.5.0

### Desktop skill

- Asks the user whether the main window's close button quits the app or hides it to the tray, and whether the app starts at login (with its window or in the tray).
- Before the choice, explains how start at login works on each OS, which setting the app gains and where, and where the user can turn it off in the OS.
- Lists the project files each choice changes, to show the user before implementing.
- Both questions are open in every whole-app pass and in any task that adds background work, a tray icon or notifications.

### Repository

- Releases are published by a GitHub Actions workflow from the plugin version and this changelog.
- The README describes what each skill covers, when to use it and how it works.

## 1.4.0

### Desktop skill

- New reference for apps that keep running with their window closed: tray icon, close to tray, one restore path and start at login are decided together.
- Start at login with the official autostart plugin: what each OS writes, off until the user turns it on, the OS as the source of truth, and a launch argument to start in the tray.
- Explains why a windowed app cannot be a Windows service and what to use instead: a separate headless service binary, a Task Scheduler task, or a signed-in session with a startup entry.
- New acceptance checks for tray and start at login.

## 1.3.0

### Desktop skill

- Present unresolved product choices for dialog placement, the title bar, the main window's close action, and notification delivery together.
- In **Manual**, apply the user's explicit choices. In **Auto**, recommend an option for each open choice and wait for approval before implementing.
- Explain the effects on main window interaction, native window controls, running work, and notification delivery. Check that notification delivery works with the chosen close behavior.

## 1.2.0

- Hardened the standalone skill bundles, the boundaries between surfaces and the plugin validation.

## 1.1.0

- The desktop and mobile skills share one native plugin data file, mirrored into each skill so either works standalone.

## 1.0.0

- Initial release: the `tauri-native-desktop` and `tauri-native-mobile` skills.
