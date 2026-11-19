# Whole-app desktop baseline

Use this for a whole-app native audit or implementation. For a narrow change, apply the affected rows and the shared bootstrap/lifecycle dependencies only. It holds the standard changes to apply and a coverage contract for the audit; it is not a requirement to add optional features.

## Inventory before implementation

Record shipped platforms, resolved dependencies, package/build mode, every initial and dynamic WebView, routes, custom frame, embedded content and the shared browser frontend if any. Identify existing desktop adapters and product choices. A version number or a previous audit does not prove a behavior works in the current package.

Classify every area below as applicable, not applicable with a reason, or deferred with the reason and next check. For applicable work, record the acceptance result separately as observed, automated test, static inspection or to test. A failing result remains a finding even when it is outside the authorized fix scope.

| Area | Essential behaviors to inspect | Read |
|---|---|---|
| Startup and frame | Correct app identity and theme from first frame; visible startup failure instead of an indefinitely hidden window; OS frame or complete replacement; dragging, resizing, system menu, Snap where shipped, DPI and monitor restore | [frame.md](frame.md), [recovery.md](recovery.md) |
| Browser UI and editing | Engine context menu absent under the chosen policy; shortcuts, links, dropped files, new windows and browser dialogs handled by the app; chrome selection/cursor separated from useful content; the content never drags as a whole on overscroll; text editing, scrolling and accessible zoom retained | [web-layer.md](web-layer.md), [context-menus.md](context-menus.md), [keyboard-accessibility.md](keyboard-accessibility.md) |
| Windows and state | Surface restraint (contextual detail drawers/inspectors kept in-window rather than extracted into blocking OS windows); every actual secondary WebView shares the relevant bootstrap; initial data and caller privileges; non-modal default and modality only where required; non-terminal Save/Apply distinguished from confirmation/closure; cancel, Escape/IME, X, owner close, crash and reopen without lost drafts or orphan hosts | [dialogs.md](dialogs.md), [boundaries.md](boundaries.md) |
| Keyboard and accessibility | Focus entry/return, keyboard-only paths and menus, semantic names/states, system reader, enlarged text/zoom, contrast and reduced motion; app commands preserve editing and composition | [keyboard-accessibility.md](keyboard-accessibility.md) |
| OS services and delivery | Native file/message dialogs where required; notifications if the app sends desktop alerts; close/hide/quit/reopen, tray/second instance/deep links where present; embedded release frontend and actual installed-package verification | [os-integration.md](os-integration.md), [background-presence.md](background-presence.md), [notifications.md](notifications.md), [recovery.md](recovery.md) |

## Standard changes

Phase 2 of the [procedure](../SKILL.md#work-in-phases). These make the app stop behaving like a web page and do not change what the product does. When changes were requested, apply every missing one, in every WebView, without asking about each. Features the user must choose are in [native-features.md](native-features.md).

| # | Standard change | Read |
|---|---|---|
| 1 | The first frame is the app's theme: no white flash, on the main window and on every secondary one | [frame.md](frame.md) |
| 2 | A hidden-until-ready window always appears: bounded timeout and a usable failure surface | [frame.md](frame.md), [recovery.md](recovery.md) |
| 3 | Interface text does not select and shows the arrow cursor; fields and content to read or copy stay selectable | [web-layer.md](web-layer.md) |
| 4 | The content never drags as a whole on overscroll, and a gap never shows a color other than the theme | [web-layer.md](web-layer.md) |
| 5 | Browser shortcuts and gestures are off (reload, print, find, developer tools in release, back and forward); each one the product needs has an app command, zoom included | [keyboard-accessibility.md](keyboard-accessibility.md), [web-layer.md](web-layer.md) |
| 6 | The engine's context menu is gone or filtered in every WebView; editing commands keep working | [context-menus.md](context-menus.md) |
| 7 | Links, dropped files and new-window requests never navigate the app away or open a browser window inside it | [web-layer.md](web-layer.md) |
| 8 | The engine's error page is never shown; a crashed WebView recovers with a retry limit | [recovery.md](recovery.md) |
| 9 | File pickers and OS message boxes the app already opens have the app's window as owner | [dialogs.md](dialogs.md), [os-integration.md](os-integration.md) |
| 10 | Every WebView, not only main, runs the same bootstrap | [web-layer.md](web-layer.md) |
| 11 | The release build loads its embedded frontend, never the development URL | [recovery.md](recovery.md) |

What is not standard: anything that adds a visible feature, changes what a control does, replaces the frame, or adds a plugin for a new capability. Keyboard and accessibility defects found in phase 1 are fixed here when the fix does not change the design (focus return, missing names and states); the others are reported for the user to decide.

## Prevent partial completion

Use [acceptance.md](acceptance.md) to turn each applicable area into observable checks. Test first launch, secondary windows, rebuild/recovery and packaged release separately when they exercise different initialization paths. Preserve the intended browser behavior when the same frontend also ships on the web.

For each failed behavior, find its owning adapter before adding local exceptions. Fixing main alone does not cover a Settings WebView; a component listener does not establish engine configuration. Add a durable check when it catches a real failure mode, and record native manual checks that automation cannot establish. Do not require brittle tests that only search for a particular implementation spelling.

Completion means the requested surfaces have implementation evidence and recorded acceptance outcomes, with failures and unexecuted checks visible. An unavailable OS is a verification gap, not a pass. Feature choices such as tray, effects, autostart or desktop notifications remain absent when the product does not need them.
