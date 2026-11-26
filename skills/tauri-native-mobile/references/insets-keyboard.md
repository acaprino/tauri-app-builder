# Android insets and keyboard

The one place for the Android rules on system bars, the cutout and the keyboard: guidelines, code, checks and references. Other pages point here.

Status: platform statements were read on the pages in [References](#references), consulted 2026-11-26. No code on this page was compiled or run for this skill, and nothing was observed on a phone. Each check says whether its command comes from documentation.

## 1. What the platform does

| Fact | Source |
|---|---|
| The WebView is the activity's content view, so it fills the window. | `wry` Android source, 0.53.5 and 0.57.1 (`setContentView`) |
| The generated `MainActivity` calls `enableEdgeToEdge()`, and the generated manifest sets no `windowSoftInputMode`. The page is drawn under the status bar, the navigation bar and the cutout unless someone pays the insets. Read both files in your project: another CLI version may differ. | Tauri CLI Android template, 2.12.4 |
| Edge-to-edge is also enforced by Android 15 once the app targets SDK 35, and an app that targets SDK 36 cannot opt out. | [Android edge-to-edge], [Android 16 behavior changes] |
| A WebView reports the bars and the cutout to the page as `env(safe-area-inset-*)` from M136 when it fills the window, and from M144 in any position, for the part of it the bars overlap. The page lists no support before M136; read here as: the values are 0 there. | [Android WebView insets] |
| The keyboard: before M139 the WebView does not react to it. From M139 it shrinks the visual viewport only; the layout viewport, and anything fixed to its bottom, stays behind the keyboard. | [Android WebView insets] |
| Below Android 11 the keyboard inset of `WindowInsetsCompat` needs the `adjustResize` soft input mode. It can be set in the manifest or with `Window.setSoftInputMode`. | [Android keyboard guide], [Window reference] |
| An insets listener set on a view is called instead of that view's own `onApplyWindowInsets`. | [View reference] |

The WebView version is the user's, not the app's: a phone can run any of these. Unverified, because not read on a page: that the system never resizes an edge-to-edge window for the keyboard, and that `devicePixelRatio` always equals the display density.

## 2. Guidelines

1. **One owner per inset.** Top, bottom, left, right and keyboard each have exactly one owner, native or web. Two owners of one edge is a defect even when the numbers happen to look right on one phone.
2. **Choose the design by one question: does the page paint behind the bars?**
   - No: **design A, native pads the page.** A listener on the content view pads it by the bars, the cutout and the keyboard. The page never sees an inset and behaves the same on every WebView version. This is the default.
   - Yes (a header color under the status bar, a bottom bar to the screen edge): **design B, the page pays the bars.** Native measures the bars and sends them as CSS variables; the keyboard is still paid natively.
3. **Layout padding uses `systemBars()` and `displayCutout()`, plus `ime()` for the keyboard.** `tappableElement()` adds nothing to the bars (the reference says it may be smaller than the system window insets). `mandatorySystemGestures()` and `systemGestures()` say where the system takes a swipe first, while taps still reach the app: use them to move a swipeable control, not to pad the page.
4. **Assign, never accumulate.** Each dispatch replaces the stored value. `max(old, new)` keeps an inset that has really shrunk (a navigation bar that moves to the side in landscape, a split-screen pane, a taskbar that goes away). If a dispatch reports 0 for a moment during an animation, read the bars with `getInsetsIgnoringVisibility`; that call cannot be used for `ime()`.
5. **A provisional value ends at the first measurement.** A constant or system dimension used before the first dispatch is replaced by the first real value, larger or smaller. It is never a floor.
6. **Zero, do not consume.** After padding by some types, pass the insets on with those types set to `Insets.NONE`. [Android WebView insets] prefers this to `WindowInsetsCompat.CONSUMED`: a WebView that stops receiving insets keeps the last ones it was given.
7. **The keyboard is paid once, natively.** With the content view padded by `ime()` the layout viewport has already shrunk. On Android the page does not subtract a keyboard height, add it to an offset or run a `visualViewport` workaround. In design B the bottom variable is the bar minus the keyboard, never below 0.
8. **An inset is paid by the container pinned to that edge, not by its children.** Before making a container pay, search for children that already do.
9. **The listener goes on the content view** (`android.R.id.content`, the WebView's parent). On the decor view it replaces the decor view's own handling, and another library that sets a listener there removes yours without a sign.
10. **Insets are pixels.** For CSS divide by the display density and round up.
11. **React to dispatches.** A change of the insets reaches the listener as a new dispatch. Do not tie a reset to `onConfigurationChanged` alone: a 180-degree rotation is commonly reported not to call it (not checked for this skill).

## 3. Code

### Code for design A

Not built or run for this skill. A listener of the same shape that consumed the insets ran on Android 14 and 15 emulators in one project; the zeroing variant below has not run anywhere.

`InsetsOwner.kt`, in the app's package:

```kotlin
package com.example.app // the app's own package

import android.app.Activity
import android.view.View
import android.view.WindowManager
import androidx.core.graphics.Insets
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat

/** The one owner of the system insets: the page sits between the bars and above the keyboard. */
object InsetsOwner {
    fun install(activity: Activity) {
        // Below Android 11 the keyboard inset is reported only in this mode. Deprecated from API 30,
        // where the listener below is what the platform asks for. Same effect as the manifest attribute.
        @Suppress("DEPRECATION")
        activity.window.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)

        val content = activity.findViewById<View>(android.R.id.content)
        ViewCompat.setOnApplyWindowInsetsListener(content) { view, insets ->
            val paid = WindowInsetsCompat.Type.systemBars() or
                WindowInsetsCompat.Type.displayCutout() or
                WindowInsetsCompat.Type.ime()
            val room = insets.getInsets(paid)
            view.setPadding(room.left, room.top, room.right, room.bottom)
            // Zeroed, not consumed: the WebView keeps getting updates and is told nothing is left to pay.
            WindowInsetsCompat.Builder(insets).setInsets(paid, Insets.NONE).build()
        }
        ViewCompat.requestApplyInsets(content)
    }
}
```

Call it from the generated `MainActivity`, after `super.onCreate`. The content view exists before the WebView does, so the listener is there from the first dispatch, and a recreated activity installs it again:

```kotlin
class MainActivity : TauriActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    enableEdgeToEdge()
    super.onCreate(savedInstanceState)
    InsetsOwner.install(this)
  }
}
```

**Keeping it across a regenerated `gen/android`.** Choose one:

- The project tracks `gen/android` in git: both edits are ordinary tracked changes. Review the diff after every `tauri android init`.
- The project generates `gen/android` on each build: keep `InsetsOwner.kt` outside it (for example `src-tauri/android/`) and run a step after `tauri android init` that copies the file into the package folder and adds the call. It must fail when the template changed, not guess:

```js
// install-insets.mjs <gen/android/app> <package>   (not run for this skill)
import { copyFileSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const [app, pkg] = process.argv.slice(2)
const dir = join(app, 'src/main/java', ...pkg.split('.'))
const main = join(dir, 'MainActivity.kt')
const anchor = 'super.onCreate(savedInstanceState)'
let source = readFileSync(main, 'utf8')
if (!source.includes('InsetsOwner.install(this)')) {
  if (source.split(anchor).length !== 2) throw new Error('MainActivity.kt has no single super.onCreate call')
  source = source.replace(anchor, `${anchor}\n    InsetsOwner.install(this)`)
  writeFileSync(main, source)
}
copyFileSync(new URL('./InsetsOwner.kt', import.meta.url), join(dir, 'InsetsOwner.kt'))
```

The copied file's `package` line must name the app's package.

**The page.** No bridge and no JavaScript. Keep `viewport-fit=cover` for iOS; on Android it changes nothing here, because the WebView is told every inset is 0.

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
```

```css
html, body { height: 100%; margin: 0; }
.app { height: 100%; }                      /* not 100vh: the page is as tall as the WebView */
.bottom-bar { padding-bottom: env(safe-area-inset-bottom, 0px); }  /* iOS pays here; Android reads 0 */
```

`env()` stays the owner on iOS and reads 0 on Android, so one stylesheet serves both. The strip behind the bars shows the window background: set it from native (`window.setBackgroundDrawable`) to the theme's color, and the bar icons to light or dark with `WindowInsetsControllerCompat`.

**The manifest instead of the code line.** `adjustResize` can also be an attribute of the main activity in `gen/android/app/src/main/AndroidManifest.xml`; then drop the `setSoftInputMode` call. In a regenerated project the same post-init step must add it, so the code line is the simpler choice there.

```xml
<activity
    android:name=".MainActivity"
    android:windowSoftInputMode="adjustResize"
    ... >
```

### Code for design B

Not built or run. Use it only when the page paints behind the bars. Native pads for the keyboard alone and sends the bars to the page.

The page: variables with an `env()` default (iOS, and Android before native has spoken), used everywhere instead of `env()`.

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
```

```css
:root {
  --safe-top: env(safe-area-inset-top, 0px);
  --safe-right: env(safe-area-inset-right, 0px);
  --safe-bottom: env(safe-area-inset-bottom, 0px);
  --safe-left: env(safe-area-inset-left, 0px);
}
.header { padding-top: var(--safe-top); }
.bottom-bar { padding-bottom: var(--safe-bottom); }   /* 0 while the keyboard is up */
```

Native: the listener of design A with two changes, and the post. Only numbers go into the script text.

```kotlin
// Inside InsetsOwner; `webView` is the app's WebView (for example from onWebViewCreate).
private var last = ""

fun install(activity: Activity, webView: WebView) {
    val content = activity.findViewById<View>(android.R.id.content)
    ViewCompat.setOnApplyWindowInsetsListener(content) { view, insets ->
        val bars = insets.getInsets(WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout())
        val ime = insets.getInsets(WindowInsetsCompat.Type.ime())
        view.setPadding(0, 0, 0, ime.bottom)                    // the keyboard, paid here
        val density = view.resources.displayMetrics.density
        fun css(px: Int) = kotlin.math.ceil(px / density - 0.01f).toInt()
        // The bottom is the bar minus the keyboard: 0 while the keyboard covers the bar.
        last = "(function(s){s.setProperty('--safe-top','${css(bars.top)}px');" +
            "s.setProperty('--safe-right','${css(bars.right)}px');" +
            "s.setProperty('--safe-bottom','${css(maxOf(0, bars.bottom - ime.bottom))}px');" +
            "s.setProperty('--safe-left','${css(bars.left)}px')})(document.documentElement.style)"
        post(webView)
        WindowInsetsCompat.Builder(insets).setInsets(WindowInsetsCompat.Type.ime(), Insets.NONE).build()
    }
    ViewCompat.requestApplyInsets(content)
}

/** Also call this when the page says it has loaded: a post made before the document exists is lost. */
fun post(webView: WebView) {
    if (last.isNotEmpty()) webView.post { webView.evaluateJavascript(last, null) }
}
```

Deliberately not given: the call by which the page says it has loaded (a Tauri command or plugin method that ends in `InsetsOwner.post`), because it depends on how the project already reaches native code; and an origin check, which a page that can navigate to another site needs before `post`. Without the first, a reloaded page keeps the `env()` defaults until the next inset change. `maxOf` here subtracts the keyboard; it is not a running maximum.

## 4. Checks

### Static checks

Run from the project root with ripgrep (its regex syntax; not run for this skill). A hit is a place to read, not a verdict: the comment says when it is wrong.

```text
# Running maximum: wrong when an inset value is combined with its previous value.
rg -n "maxOf\(|Math\.max\(|coerceAtLeast" -g "*.kt" -g "*.java" src-tauri

# Consumed insets: wrong when a parent of the WebView pads and returns CONSUMED.
rg -n "WindowInsetsCompat\.CONSUMED|consumeSystemWindowInsets" src-tauri

# Native owners: wrong when more than one place pads, or edge-to-edge is on and none does.
rg -n "setOnApplyWindowInsetsListener|fitsSystemWindows|setDecorFitsSystemWindows|enableEdgeToEdge" src-tauri

# Listener on the decor view: wrong when the insets listener is set on it.
rg -n "decorView" -g "*.kt" src-tauri

# Gesture types as padding: wrong when they are in the mask used for page padding.
rg -n "mandatorySystemGestures|tappableElement|systemGestures" src-tauri

# Fixed sizes: wrong when a system dimension or a constant outlives the first measurement.
rg -n "status_bar_height|navigation_bar_height|getIdentifier\(" src-tauri

# Keyboard mode: wrong when neither sets adjustResize and Android 10 or lower is supported.
rg -n "windowSoftInputMode|setSoftInputMode" src-tauri

# Web owners. Design A: wrong when Android-only code pays an inset or the keyboard.
# Design B: wrong when env() is used directly, or the keyboard height is subtracted.
rg -n "safe-area-inset|--safe-area|visualViewport|keyboard" src index.html

# Paid twice: wrong when a container pinned to an edge and one of its descendants both pay that edge.
rg -n "safe-area-inset-(top|bottom)|--safe-area-(top|bottom)" src
```

ripgrep skips git-ignored files, and a generated `gen/android` is often ignored: an empty result there proves nothing. For such a project run the native searches on the folder the Kotlin is kept in, and again on the generated project after a build with `--no-ignore -g '!target' -g '!build'`. Read the keyboard mode in the merged manifest of the built APK (`aapt2 dump xmltree <apk> --file AndroidManifest.xml`; command not checked in documentation).

### Review checklist

Each line passes or fails on what can be seen.

- [ ] One listener pads, and it is on the content view.
- [ ] The listener returns the insets with the paid types set to `Insets.NONE`.
- [ ] No inset value depends on its previous value; no constant survives the first dispatch.
- [ ] `adjustResize` is set, in the manifest or in code.
- [ ] Design A: with the app open, the page probe below reads `0px` on all four sides.
- [ ] Keyboard up: the three heights below are equal and smaller than before; a control fixed to the bottom touches the keyboard with no bar-sized gap. Keyboard down: all three return.
- [ ] Cold start in landscape with three-button navigation: no empty band on an edge that has no bar.
- [ ] Rotation, split screen and a cutout: the page follows each change without a restart.
- [ ] The WebView version of every run is recorded, and one run is on M139 or later.

### Page-side commands

Run in the WebView inspector (`chrome://inspect`) or through the DevTools socket.

```js
// 1. The WebView version and the three heights.
({ webview: navigator.userAgent.match(/Chrome\/[\d.]+/)?.[0],
   inner: innerHeight,
   client: document.documentElement.clientHeight,
   visual: Math.round(visualViewport.height * visualViewport.scale),
   screen: screen.height, ratio: devicePixelRatio })
```

Expected: `inner`, `client` and `visual` are equal, keyboard up or down. With the keyboard up they are smaller by about the keyboard's height. `visual` smaller than `inner` means the WebView also shrank the visual viewport: the keyboard reached it as an inset. Design A: `screen - inner` is larger than 0 (the bars).

```js
// 2. The insets the WebView tells the page. Set through the CSSOM, which a CSP without inline styles allows.
(() => {
  const probe = document.createElement('div')
  probe.style.setProperty('position', 'fixed')
  probe.style.setProperty('margin-top', 'env(no-such-inset, 7px)')
  probe.style.setProperty('padding', 'env(safe-area-inset-top, 0px) env(safe-area-inset-right, 0px) env(safe-area-inset-bottom, 0px) env(safe-area-inset-left, 0px)')
  document.body.append(probe)
  const style = getComputedStyle(probe)
  const seen = { control: style.marginTop, top: style.paddingTop, right: style.paddingRight, bottom: style.paddingBottom, left: style.paddingLeft }
  probe.remove()
  return seen
})()
```

Expected: `control` is `7px` (the probe reads `env()` at all; that an unknown name falls back is the reading of the CSS specification, not observed). Design A: the four sides are `0px`, before the keyboard, with it and after it. A side that is not 0 is an inset paid twice. On a WebView before M136 they are 0 whatever the native code does, so this check proves the design only on M136 or later.

### Device and emulator procedure

For each state: set it, then run both page-side commands and take a screenshot (`adb shell screencap /sdcard/s.png`, documented in [adb]).

| State | How to set it | Documented? | Expected |
|---|---|---|---|
| WebView version | `adb shell dumpsys webviewupdate` | `dumpsys` is documented in [adb]; the service name is not | Recorded with the result |
| Cutout | Developer options, Drawing, "Simulate a display with a cutout" | Yes, [display cutout] | Content clear of the cutout in portrait and in landscape, where it is on a side |
| Cutout, by command | `adb shell cmd overlay enable com.android.internal.display.cutout.emulation.tall` | No | Same |
| Landscape | Emulator console `rotate` | Yes, [emulator console] | Insets move to the new edges; no band stays |
| Landscape, by command | `adb shell settings put system accelerometer_rotation 0` then `adb shell settings put system user_rotation 1` | No | Same |
| Three-button navigation | `adb shell cmd overlay enable com.android.internal.systemui.navbar.threebutton` | No | Bottom inset equals the button bar; in landscape on a phone the bar is on a side and the bottom inset is 0 |
| Gesture navigation | `adb shell cmd overlay enable com.android.internal.systemui.navbar.gestural` | No | A smaller bottom inset, never 0 padding under a visible handle |
| Keyboard up | `adb shell settings put secure show_ime_with_hard_keyboard 1`, then tap a field: `adb shell input tap <x> <y>` | No; seen working in one project's emulator job | The three heights equal and smaller |
| Keyboard down | `adb shell input keyevent 4` | Key code 4 is Back in the [KeyEvent reference]; the `input` command is not documented there | The three heights return |
| WebView bounds | `adb shell uiautomator dump /sdcard/ui.xml`, read the `android.webkit.WebView` node's `bounds` | No; seen working in one project's emulator job | Design A: inside the bars, bottom at the keyboard's top when it is up. Design B: the whole window, bottom at the keyboard's top when it is up |
| Font scale | Settings, Accessibility, "Display size and text", Font size | Yes, [Android 14 features] | The insets and the three heights do not change |
| Font scale, by command | `adb shell settings put system font_scale 1.3` | No | Same |
| Split screen | Open a second app beside this one | No command known | The pane's own insets; no phantom bar on the inner edge |

Commands marked "No" are widely used but were not found on the documentation pages consulted: check their output on the system image you use. Changing a setting changes the device: use a test device and put each setting back.

What stays unobservable on an emulator: a manufacturer's own inset dispatch (keep a real-device lane for Samsung and others), the WebView versions real users have (an image without Play services keeps the WebView it shipped with, often older than M136), and how the page looks while the keyboard animates. Record these as pending, not as passed.

## References

Consulted 2026-11-26.

- [Android WebView insets]: milestones M136, M139 and M144, overlap logic, zeroing against consuming. Page dated 2026-10-28.
- [Android edge-to-edge]: enforcement at target SDK 35, the inset types for layout, system gesture insets.
- [Android 16 behavior changes]: no opt-out at target SDK 36.
- [Android keyboard guide]: `adjustResize` for the keyboard inset through AndroidX.
- [WindowInsets reference] and [WindowInsets.Type reference]: tappable-element and mandatory-gesture insets, `getInsetsIgnoringVisibility` and its IME exception.
- [View reference]: a listener replaces the view's own `onApplyWindowInsets`.
- [Window reference]: `setSoftInputMode` overrides the mode from the theme.
- [display cutout]: the Developer options switch for a simulated cutout.
- [emulator console]: `rotate`.
- [adb]: `screencap`, `dumpsys`.
- [KeyEvent reference]: `KEYCODE_BACK`.
- [Android 14 features]: the font size setting.
- `wry` crate Android source 0.53.5 and 0.57.1, and the Tauri CLI Android template at tag `tauri-cli-v2.12.4`: read in the published source.

[Android WebView insets]: https://developer.android.com/develop/ui/views/layout/webapps/understand-window-insets
[Android edge-to-edge]: https://developer.android.com/develop/ui/views/layout/edge-to-edge
[Android 16 behavior changes]: https://developer.android.com/about/versions/16/behavior-changes-16
[Android keyboard guide]: https://developer.android.com/develop/ui/views/layout/sw-keyboard
[WindowInsets reference]: https://developer.android.com/reference/android/view/WindowInsets
[WindowInsets.Type reference]: https://developer.android.com/reference/android/view/WindowInsets.Type
[View reference]: https://developer.android.com/reference/android/view/View
[Window reference]: https://developer.android.com/reference/android/view/Window
[display cutout]: https://developer.android.com/develop/ui/views/layout/display-cutout
[emulator console]: https://developer.android.com/studio/run/emulator-console
[adb]: https://developer.android.com/tools/adb
[KeyEvent reference]: https://developer.android.com/reference/android/view/KeyEvent
[Android 14 features]: https://developer.android.com/about/versions/14/features
