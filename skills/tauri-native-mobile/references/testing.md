# Mobile verification matrix

Record device/OS/WebView, installed package/version/signature, build revision and artifact digest alongside each result. Mark tests as executed, historical evidence, or pending. Browser automation cannot exercise a native account picker by DOM selectors.

| Area | Required relevant cases |
|---|---|
| Camera | Fresh grant, denial, permanent denial/settings, cancellation, repeated tap, late callback, process restart, large/rotated image |
| Microphone/video | Grant after screen close, MIME support, track cleanup, background interruption |
| Location | Approximate/precise, disabled service, stale fix, watch/unmount race, foreground/background, lock screen, geofence duplicate/reset, permission revoke |
| NFC | No hardware/off, session cancel, incompatible/read-only/full tag, removal mid-write, duplicate scan, protocol/platform differences |
| BLE | Scan/connect grants, radio toggle, accessory reboot, stale connection callback, packet framing, reconnect limit, suspend/restore |
| Biometrics/keys | No enrollment, cancel/lockout/fallback, changed enrollment, key invalidation, locked device, backup/restore, account switch |
| Push/background/offline | Token refresh, account detach, foreground/background/tap routing, duplicates, missing push, worker expiration, offline restart, idempotent retry/conflict |
| Other device APIs | Picker grant lifetime, limited contacts, calendar editor cancel, partial health access, LAN denial, predictive Back, TalkBack/VoiceOver and text scaling |
| Back | Overlay on overlay, root with one press, two presses, and one press then a wait, overlay opened during the exit window, router navigation with an overlay open, Back after a page reload, return from another app |
| Install defaults | Launcher and notification icon are the app's own, backup and device transfer as decided (restore on a second device), target SDK equals the tested system image, server with a private CA or plain HTTP as decided |
| Google | Registered/unregistered signature, account picker cancel, no account, offline, native/JS switch, refresh, logout, reauth |
| Export | Picker cancel, failed write/close, large ZIP, cloud provider, low disk, process death, inspect destination bytes and archive entries, no false completion |
| Scheduling | Exact access denied/revoked, notifications disabled, idle, app closed, reboot, force-stop distinction, DST/timezone, duplicate reconciliation, edit/delete/snooze, logout, iOS supported/unsupported OS |
| Links | Cold and warm launch, duplicate callback, verified/unverified host, Play signing, wrong path, installed old APK |
| Layout | The WebView version of the run, then the checklist and device procedure in [Android insets and keyboard](insets-keyboard.md#4-checks): Samsung/other OEM, rotation, cold start in landscape and in split screen, cutout, keyboard open/close, gestures/three-button nav, dialog scroll, pull past every edge (the screen never slides as a whole, no background strip) |
| Build | Fresh clone/submodules, clean native generation, selected ABI, packaged assets, no dev server, same-key update |
| Distribution | Play-generated APK, 16 KB environment, purchase pending/restore/revoke, iOS entitlements/hardware |

Useful read-only commands: `adb devices -l`, `adb shell dumpsys package <package>`, `adb shell dumpsys webviewupdate`, `adb shell pm get-app-links <package>`. Use `adb -s <serial>` with multiple devices. Installing, force-stopping, revoking permission and opening a test link change device state: use the intended test device and preserve user data.

`adb reverse` can make a device's localhost reach a host port; LAN access is another route. Don't universally prescribe IPv6, localhost avoidance or a full emulator reset. Inspect the connection first.

For first-request tests, don't pre-grant the permission. Reset only the test app's relevant state when needed. Keep a real-device lane for OEM behavior even when emulator checks pass.

Sources: [ADB](https://developer.android.com/tools/adb), [Android App Links](https://developer.android.com/training/app-links/verify-applinks).
