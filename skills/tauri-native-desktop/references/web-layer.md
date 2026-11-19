# Web layer: bootstrap, browser behaviors, chrome, scrolling

Part of the tauri-native-desktop references: versions, scope and limits are in [guide.md](guide.md). Bracketed names are sources; their URLs are in [sources.md](sources.md).

**Bootstrap for every WebView:** apply to windows created after startup the same relevant policies as the main window: theme/initial background ([frame.md](frame.md)), browser switches, navigation guard, context menu, the accelerator policy for release builds, error and failure recovery ([recovery.md](recovery.md)) and listeners. Centralize this adapter to avoid secondary windows initialized differently; verify the related permissions instead of granting a global set. This is an implementation recommendation derived from the window creation lifecycle.

## Browser behaviors to switch off

For context menus, read [context-menus.md](context-menus.md): it defines the engine setting, editing replacement, coverage of every WebView and first-navigation checks. The example below assumes the replacement policy; filtering the engine menu uses a different path.

Tauri 2.12.5 exposes only part of the switches: `zoom_hotkeys_enabled` (default `false`; on Windows it sets `IsZoomControlEnabled` and `IsPinchZoomEnabled`, on macOS/Linux it injects a zoom polyfill that needs `core:webview:allow-set-webview-zoom`), `general_autofill_enabled` (2.11.0; it "does not disable password or credit card autofill"), `disable_drag_drop_handler` or the `dragDropEnabled` key (needed for HTML5 drag and drop on Windows), `browser_extensions_enabled` and `additional_browser_args`, which replaces wry's default flags `--disable-features=msWebOOUI,msPdfOOUI,msSmartScreenProtection` (re-add them if still wanted). [WebviewWindowBuilder].

The builder counterpart of the `dragDropEnabled` key is `disable_drag_drop_handler()`: the config key calls that method (checked in tauri-runtime 2.12.2). The Windows-only builder method `drag_and_drop(false)` is a different, window-level setting and does not free HTML5 drag and drop. A report that the flag "is ignored from the Rust builder" came from calling it instead. [tauri#13761], [tauri-runtime webview.rs].

wry 0.57.2 already turns off two more switches: `IsStatusBarEnabled` is always `false`, and `IsSwipeNavigationEnabled` follows a wry attribute that Tauri 2.12.5 does not expose, so it stays `false`. The remaining WebView2 switches (`AreBrowserAcceleratorKeysEnabled`, `AreDefaultContextMenusEnabled`, `IsBuiltInErrorPageEnabled`) are reachable only through `with_webview` → `controller()`, default to `TRUE` and take effect from the next navigation. `IsPasswordAutosaveEnabled` needs no code: its WebView2 default is `FALSE` and wry (checked in 0.57.1 and 0.57.2) never sets it, so there is no "save password?" prompt to switch off; touch it only if the product wants password saving. State each switch's default before writing code for it: a line that sets a default is not a fix. [ICoreWebView2Settings4]. `AreBrowserAcceleratorKeysEnabled` separates browser accelerators from copy/cut/paste and other editing commands, does not affect the `AcceleratorKeyPressed` event and also disables Ctrl+Plus/Minus, so zoom becomes the app's job. WKWebView and WebKitGTK lack these switches: use JS guards. Decide each switch per product, apply it in the shared bootstrap, keep editing and app shortcuts, and reimplement as app commands what you switch off and the product needs (find, print, zoom, reload). Disabling all context menus indiscriminately also removes useful functions: keep a native editing menu or an accessible equivalent. [CoreWebView2Settings], [WebView2 Settings3], [Settings], [wry 0.57.2 source].

```rust
// Illustrative, compile against your lockfile: check names and signatures against the
// webview2-com and windows versions it resolves (tauri 2.12 uses webview2-com 0.39, windows 0.62).
// The status bar and swipe navigation are already off in wry: no code needed for them.
// `windows::core::Interface` is the `windows_core::Interface` trait: import it from the crate you depend on.
#[cfg(windows)]
fn harden_webview2(win: &tauri::WebviewWindow) -> tauri::Result<()> {
    use webview2_com::Microsoft::Web::WebView2::Win32::*;
    use windows::core::Interface;
    let label = win.label().to_owned();
    win.with_webview(move |wv| {
        let result = (|| -> windows::core::Result<()> {
            unsafe {
                let core = wv.controller().CoreWebView2()?;
                let s = core.Settings()?;
                // Replacement policy: app-owned menus include accessible editing actions.
                s.SetAreDefaultContextMenusEnabled(false)?;
                // Only if the app provides its own error/recovery surface (recovery.md):
                s.SetIsBuiltInErrorPageEnabled(false)?;
                s.cast::<ICoreWebView2Settings3>()?.SetAreBrowserAcceleratorKeysEnabled(false)?;
                // Password autosave is off by default: no line for it.
            }
            Ok(())
        })();
        if let Err(error) = result {
            eprintln!("WebView2 policy failed for '{label}': {error}");
        }
    })
}
```

```js
// Illustrative cross-engine guards (needed on WKWebView/WebKitGTK, useful everywhere).
// Install once per desktop document; real drop zones handle their own accepted drops.
for (const t of ['dragover', 'drop']) window.addEventListener(t, e => {
  const target = e.target instanceof Element ? e.target : null;
  if (!target?.closest('[data-dropzone]')) {
    e.preventDefault();
    if (t === 'dragover' && e.dataTransfer) e.dataTransfer.dropEffect = 'none';
  }
});
document.addEventListener('auxclick', e => {
  if (e.target instanceof Element && e.target.closest('a')) e.preventDefault();
});
```

These guards are not a complete navigation policy: native Back/Forward buttons can bypass DOM cancellation. Enforce allowed destinations and new-window behavior in the shared native navigation adapter, define Ctrl/Cmd-click routing, and verify real input on each runtime. A synthetic `mouseup` test cannot prove native history navigation is blocked.

## Chrome and content

Separate desktop chrome from useful content: chrome uses the platform's intended cursor and avoids accidental text/image dragging; documents, fields, code and data remain selectable. Scope desktop CSS to the desktop entry point. On Windows use the arrow for clickable chrome; content links and other platforms follow their own policy. Preserve focus indicators according to `:focus-visible` and user/engine preferences rather than globally hiding rings after pointer input. Keep `-webkit-user-select` alongside the unprefixed rule for older WKWebViews. [Mouse interactions], [Focus visible], [BCD user-select].

The hand cursor hides in the app's CSS, component-library styles and utility classes such as Tailwind's `cursor-pointer`. Inspect all three within desktop chrome. Links inside rendered content are a separate product choice, and the shared browser frontend keeps its own policy. Preserve `:focus-visible` heuristics for text inputs, keyboard navigation and user preferences; pointer focus does not universally imply an invisible ring. [Focus visible].

```css
/* Desktop stylesheet only; adapt content selectors and theme to the product. */
html { cursor: default; -webkit-user-select: none; user-select: none; }
input, textarea, [contenteditable], .selectable, pre, code {
  -webkit-user-select: text; user-select: text; cursor: auto;
}
img, a { -webkit-user-drag: none; }      /* or draggable="false" in the markup */
:focus-visible { outline: 2px solid Highlight; outline-offset: 2px; }
:focus:not(:focus-visible) { outline: none; }
```

## Bounce, rubber-banding and scroll chaining

**Scroll bounce** is the elastic feedback at the edge; **scroll chaining** hands the scroll over to an ancestor container. Both are distinct from spring animations on buttons/panels. The specification, still a 2019 First Public Working Draft, does not require an OS to have bounce: CSS can limit it where implemented, not add it automatically. [W3C css-overscroll-1], [Editor's draft].

| Value | Handoff to ancestors | Elastic feedback |
|---|---|---|
| `auto` | Default behavior | Depends on system and engine |
| `contain` | Prevented | May remain |
| `none` | Prevented | Suppressed where supported |

Apply the property to the actual scroll container: it is not inherited. Syntax support does not prove trackpad behavior. WebKit's nonoverflowing-container limitation is tracked in WebKit 243452; test the actual container and shipped runtime. The separate short-viewport issue 244232 was fixed in January 2023, so it is not evidence of a current universal WKWebView defect. Keep ordinary scrolling and test short pages without adding blanket wheel/touch interception. [MDN overscroll-behavior], [BCD overscroll-behavior], [WebKit 243452], [WebKit 244232].

### The window's content never moves as a whole

This is a default for every WebView, not a per-surface choice. Pulling past an edge must not slide the whole interface and uncover the background behind it: that is how a web page behaves, and users describe it as "pull to refresh".

It is not a macOS-only concern. Microsoft Edge enabled an overscroll bounce on the page's root scroller "both for touch input and for PTP touchpad input", by default; WebView2 runs the same engine, so expect it there with a precision touchpad or a touchscreen. Chromium also planned the effect for nested scroll containers on platforms that already have one. On macOS, WKWebView rubber-bands the document. [Edge scrolling personality], [blink-dev overscroll PSA].

A shell with `height: 100vh` and `overflow: hidden` does not prevent it: the viewport is still the root scroller, and a panel at its end hands the gesture to it. It is also not the browser's pull to refresh: in WebView2 "swiping down to refresh is off by default" and needs the `--pull-to-refresh` browser argument, and wry already turns swipe navigation off. [ICoreWebView2Settings6].

```css
/* Shared stylesheet of every WebView. */
html {
  height: 100%;
  overflow: hidden;           /* only panels scroll, never the document */
  overscroll-behavior: none;  /* html is the viewport-defining element */
}
body {
  height: 100%;
  margin: 0;
  overflow: hidden;
  overscroll-behavior: none;
}
```

Rules:

- **Put it on `html`.** The specification's own example sets the value "on the viewport defining element"; repeat it on `body`. A value only on the app's shell element does not reach the viewport. [Editor's draft].
- **Apply it without waiting to observe the bounce.** A review on a machine with no precision touchpad or touchscreen, or with no running build, cannot see it. The rule changes nothing for wheel, keyboard or scrollbar scrolling, so record it as applied with the device observation pending. Do not defer it as "to be observed first".
- **Match the background.** `html`, `body` and the native window use the theme's ground color ([frame.md](frame.md)), so a frame that still shows a gap never shows white.
- **A window whose document must scroll** (a long reading view) moves that scrolling into a container inside the locked root.

### Lists and panels

**Proposed policy:** inside the locked root, bounce is a per-surface choice. On macOS keep the system feedback in lists when appropriate. On Windows/Linux follow the runtime's behavior without globally simulating macOS rubber-banding. Use `contain` to isolate nested lists and `none` on the surfaces where you explicitly want to remove the bounce.

```css
/* Illustrative classes: assign them to the project's actual scroll containers. */
.isolated-list {
  overflow: auto;
  overscroll-behavior: contain;
}
.no-bounce-scroll {
  overflow: auto;
  overscroll-behavior: none;
}
```

A shared web frontend that relies on the browser's pull to refresh or swipe navigation loses them under the locked root: scope the lock to the desktop build, or verify those gestures separately. Prefer CSS over global `wheel`/`touchmove` blocks that interfere with scrolling and latency.

For **elastic animations created by the app**, decide where they help feedback; do not make them mandatory to look native. Reduce/remove non-essential ones with `prefers-reduced-motion`. This does not guarantee control over the engine's native bounce. Do not add animation dependencies if scroll handling is enough.

**Scrollbars:** Windows 11 style overlay scrollbars are a stable WebView2 API since Runtime 125, exposed by Tauri as `scroll_bar_style(ScrollBarStyle::FluentOverlay)`, which "must be given the same value for all webviews that target the same data directory". On Windows consider it for all webviews sharing the data folder. Prefer native scrollbars themed by `color-scheme`, `scrollbar-width` and `scrollbar-color` over `::-webkit-scrollbar`; use `scrollbar-gutter: stable` where the scrollbar's appearance shifts the layout. In `forced-colors` `scrollbar-color` reverts to `auto`. [SDK 1.0.2535.41], [WebviewWindowBuilder].
