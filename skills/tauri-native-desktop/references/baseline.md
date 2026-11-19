# Whole-app desktop baseline

Use this for a whole-app native audit or implementation. For a narrow change, apply the affected rows and the shared bootstrap/lifecycle dependencies only. This is a coverage contract, not a requirement to add optional features.

## Inventory before implementation

Record shipped platforms, resolved dependencies, package/build mode, every initial and dynamic WebView, routes, custom frame, embedded content and the shared browser frontend if any. Identify existing desktop adapters and product choices. A version number or a previous audit does not prove a behavior works in the current package.

Classify every area below as applicable, not applicable with a reason, or deferred with the reason and next check. For applicable work, record the acceptance result separately as observed, automated test, static inspection or to test. A failing result remains a finding even when it is outside the authorized fix scope.

| Area | Essential behaviors to inspect | Read |
|---|---|---|
| Startup and frame | Correct app identity and theme from first frame; visible startup failure instead of an indefinitely hidden window; OS frame or complete replacement; dragging, resizing, system menu, Snap where shipped, DPI and monitor restore | [frame.md](frame.md), [recovery.md](recovery.md) |
| Browser UI and editing | Engine context menu absent under the chosen policy; shortcuts, links, dropped files, new windows and browser dialogs handled by the app; chrome selection/cursor separated from useful content; text editing, scrolling and accessible zoom retained | [web-layer.md](web-layer.md), [context-menus.md](context-menus.md), [keyboard-accessibility.md](keyboard-accessibility.md) |
| Windows and state | Surface restraint (contextual detail drawers/inspectors kept in-window rather than extracted into blocking OS windows); every actual secondary WebView shares the relevant bootstrap; initial data and caller privileges; non-modal default and modality only where required; non-terminal Save/Apply distinguished from confirmation/closure; cancel, Escape/IME, X, owner close, crash and reopen without lost drafts or orphan hosts | [dialogs.md](dialogs.md), [boundaries.md](boundaries.md) |
| Keyboard and accessibility | Focus entry/return, keyboard-only paths and menus, semantic names/states, system reader, enlarged text/zoom, contrast and reduced motion; app commands preserve editing and composition | [keyboard-accessibility.md](keyboard-accessibility.md) |
| OS services and delivery | Native file/message dialogs where required; notifications if the app sends desktop alerts; close/hide/quit/reopen, tray/second instance/deep links where present; embedded release frontend and actual installed-package verification | [os-integration.md](os-integration.md), [background-presence.md](background-presence.md), [notifications.md](notifications.md), [recovery.md](recovery.md) |

## Prevent partial completion

Use [acceptance.md](acceptance.md) to turn each applicable area into observable checks. Test first launch, secondary windows, rebuild/recovery and packaged release separately when they exercise different initialization paths. Preserve the intended browser behavior when the same frontend also ships on the web.

For each failed behavior, find its owning adapter before adding local exceptions. Fixing main alone does not cover a Settings WebView; a component listener does not establish engine configuration. Add a durable check when it catches a real failure mode, and record native manual checks that automation cannot establish. Do not require brittle tests that only search for a particular implementation spelling.

Completion means the requested surfaces have implementation evidence and recorded acceptance outcomes, with failures and unexecuted checks visible. An unavailable OS is a verification gap, not a pass. Feature choices such as tray, effects, autostart or desktop notifications remain absent when the product does not need them.
