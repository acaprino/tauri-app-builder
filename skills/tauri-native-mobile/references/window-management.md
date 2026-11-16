# Window boundaries in shared projects

Tray/global-shortcut and desktop window-chrome patterns are not mobile navigation patterns. Check the current Tauri/platform support before making blanket statements about mobile multi-window capabilities.

On desktop, use Tauri's documented drag-region/dragging mechanism and permission, not Electron's CSS alone. Keep window labels unique, scope capabilities to the intended windows and handle concurrent create/focus attempts. Preventing close and hiding a window are separate actions; define restore and quit behavior explicitly.

On mobile, activity/process lifecycle, Back, keyboard and screen transitions need their own state model. See [insets](plugins-mobile.md) and [testing](testing.md).

Source: [Tauri window customization](https://v2.tauri.app/learn/window-customization/).
