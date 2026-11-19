# Native feature menu

Part of the tauri-native-desktop references: versions, scope and limits are in [guide.md](guide.md).

The list of optional native integrations to offer the user in phase 3 of the [procedure](../SKILL.md#work-in-phases). Everything here changes what the product does, adds something the user sees, or adds a dependency or a permission, so none of it is added without being chosen. The changes that need no choice are the standard ones in [baseline.md](baseline.md#standard-changes).

## How to present it

- Show one prompt for the whole menu, after the assessment and the baseline, with **Manual** and **Auto** as in [Confirm product choices](../SKILL.md#confirm-product-choices).
- Group the items as below. For each one give its current state in the app (present, partial, absent), one line on what the user gets and one on what it costs or adds.
- Leave out items that do not apply to the shipped systems, and items the user or the product requirements already decided. Say that they were left out and why.
- An item that is already present is offered as "review" only when the assessment found a defect in it.
- Do not ask about a feature only to look thorough: an app with no accounts is not asked about the credential store. State the reason in one line instead.
- Record every answer, including "no". A "no" means the feature stays absent and is not proposed again in the same task.

## Window and app behavior

| Feature | Ask | What the user gets | Cost, or what it adds | Recommend in Auto when | Read |
|---|---|---|---|---|---|
| Dialog placement | For each dialog in scope: inside the main window, a separate OS window, or a standard OS alert? | In-window keeps context and is instant; a separate window can sit beside the main one or on another monitor | A separate window brings its own lifecycle, focus, modality and data path | In-window, unless the dialog must be used side by side with the main window or opens while main is hidden | [dialogs.md](dialogs.md) |
| Title bar | System title bar or a custom one? | Custom frees the top strip for the app's own controls and branding | A custom bar must rebuild dragging, the system menu, Snap Layouts on Windows and the window buttons | System, unless the design needs the strip | [frame.md](frame.md) |
| Close button | Quit the app, or hide it to the tray? | Hide keeps background work and alerts running | A tray icon, a Quit path, a one-time notice | Hide only when the app does work the user expects to continue unattended | [background-presence.md](background-presence.md) |
| Tray icon | Should the app have an icon in the system tray? | A way back to a hidden window, quick actions, status at a glance | Tray menu to design; on Linux the menu is the only reliable interaction | With close to tray, or when the app shows a status worth a glance | [background-presence.md](background-presence.md) |
| Start at login | Start when the user signs in? With the window, or in the tray? | The app is running without being opened | A setting in the app, a startup entry in the OS, the autostart plugin | Only with unattended work, and always off until the user turns it on | [background-presence.md](background-presence.md) |
| Second launch | Starting the app again: bring the running window forward, or allow several instances? | One window to find; links and files open in the running app | The single-instance plugin, registered first | One instance, unless the product is multi-document by process | [os-integration.md](os-integration.md) |
| Window size and position | Reopen where the user left the window? | The window comes back on the same monitor at the same size | The window-state plugin; handling of a disconnected monitor | Yes for a main window the user resizes | [os-integration.md](os-integration.md) |
| Menu bar | A native menu bar with the app's commands? | Commands discoverable by menu and by keyboard; expected on macOS | Menu structure per platform; predefined items differ per OS | Yes on macOS; on Windows and Linux only when the app has many commands | [os-integration.md](os-integration.md), [frame.md](frame.md) |
| Window material | Mica, acrylic or vibrancy behind the interface? | The window picks up the system's translucent material | A transparent window, a readable opaque fallback, per-OS support | No, unless the design asks for it | [frame.md](frame.md) |
| Context menus | App commands on right click: a native OS menu, or a menu drawn by the app? | Native follows the system's look and keyboard behavior; app-drawn can hold richer content | One rule for the whole product; the engine's own menu is removed either way in the baseline | Native for plain command lists | [context-menus.md](context-menus.md) |

## System services

| Feature | Ask | What the user gets | Cost, or what it adds | Recommend in Auto when | Read |
|---|---|---|---|---|---|
| System notifications | Which events should reach the user as an OS notification, and which stay in the app? | Alerts while the window is unfocused or hidden | The notification plugin, OS permission, an installed-app identity on Windows; delivery depends on the close behavior | For events that matter while the user is elsewhere | [notifications.md](notifications.md) |
| Taskbar and dock status | An unread badge, a progress bar on the taskbar button, an attention flash? | Status without opening the window | Per-OS APIs; on Windows the badge is an overlay icon to draw | A count the user tracks, or long operations | [os-integration.md](os-integration.md) |
| Links into the app | Should a link (`myapp://…` or a web link) open the app at a given place? | Sign-in callbacks, shared links, launching from email or chat | The deep-link plugin, a registered scheme, validation of every incoming URL | When sign-in or sharing needs it | [os-integration.md](os-integration.md) |
| Global shortcuts | A key combination that works while another app has focus? | Summon the app or trigger one action from anywhere | The global-shortcut plugin; conflicts with other apps; a setting to change or disable it | Rarely: only for a quick-capture or summon action | [native-plugins.md](native-plugins.md) |
| In-app updates | Should the app update itself? | New versions without a manual download | The updater plugin, a signing key, a place to host the artifacts, a restart the user understands | Yes for an app distributed outside a store | [packaging-updates.md](packaging-updates.md) |
| Files from the OS | Native open and save dialogs, opening a file in its default app, showing it in the file manager? | The system's pickers and the user's own apps | The dialog and opener plugins, scoped paths | Whenever the app reads or writes user files | [os-integration.md](os-integration.md), [native-plugins.md](native-plugins.md) |

## Accounts and device

| Feature | Ask | What the user gets | Cost, or what it adds | Recommend in Auto when | Read |
|---|---|---|---|---|---|
| Credentials in the OS store | Keep passwords and tokens in Windows Credential Manager, the macOS Keychain or the Linux secret service? | Secrets protected by the user's OS account, not in a file of the app | No official plugin: a Rust keychain crate behind an app command; a fallback where Linux has no secret service | Whenever the app stores a token or a password | [native-plugins.md](native-plugins.md), [boundaries.md](boundaries.md) |
| Unlock with the OS | Ask for Windows Hello, Touch ID or the account password before sensitive actions? | Re-authentication with what the user already uses for the device | Official plugin on macOS only; platform code on Windows and Linux | For apps that show sensitive data on a shared machine | [native-plugins.md](native-plugins.md) |
| Sign-in in the system browser | Sign in through the user's browser instead of a form or an embedded page? | The user's saved passwords, passkeys and existing sessions | Opener, deep link or loopback redirect, single instance; state validation | For any OAuth or SSO sign-in | [native-plugins.md](native-plugins.md) |
| Device access | Camera, microphone, location, Bluetooth, serial or USB? | The hardware the workflow needs | Engine permissions that differ per OS, or platform code; usage descriptions on macOS | Only when a workflow needs the device | [native-plugins.md](native-plugins.md) |

## After the answers

Chosen features become the scope of phase 4. Read each feature's reference before defining its contract, and tell the user what changes in the app and in the project before implementing, as [background-presence.md](background-presence.md#what-changes-and-where) does for tray and start at login. Features that depend on each other are decided together: notifications and tray depend on the close behavior, links into the app and sign-in depend on the second-launch behavior.
