# Mobile migration capability inventory

Use this when auditing an existing web app for mobile migration. Inventory actual user actions and browser dependencies before selecting plugins. This is a discovery map, not a requirement to add every permission or feature.

For each used capability record: Android/iOS/web adapter, supported OS/hardware, installed command support, ACL, native declarations, user authorization, foreground/background owner, persistence, cancellation/error result, observable completion and release-device test. Mark unimplemented and unsupported explicitly. Hardware absent, permission denied, service disabled, busy, cancelled, timed out and operation failed are not interchangeable.

## Detailed integration references

| User action | Integration boundary |
|---|---|
| Find nearby places, follow a journey, enter an area | [Position, tracking and geofences](geolocation.md); map tiles/geocoding are separate |
| Scan/write a tag, connect an accessory | [NFC and Bluetooth](nfc-bluetooth.md); tag reading is not payment/card emulation |
| Unlock private data | [Biometrics and protected credentials](device-security.md); local authentication is not server authorization |
| Receive a server message, sync while away | [Push, background and offline](push-background.md); native ownership and durable jobs |
| Remind at a chosen time, snooze an alarm | [Notifications and alarms](notifications-alarms.md); preserve exact timing requirements |
| Capture/record media | [Camera and media](camera-media.md); still, video, audio and gallery differ |
| Export/download/share a file | [Native export](file-export.md); provider write completion differs from share-sheet launch |
| Open a callback or content link | [Links](authentication-mobile.md); cold/warm delivery and authorized routing |

## Additional capability decisions

**Photos and document import.** Prefer a system picker for selected files rather than blanket library access. content:// URIs and security-scoped resources are not ordinary persistent paths. Stage a bounded local copy or retain an allowed grant if upload will outlive the picker/activity; handle grant loss, cloud-only content, MIME/size validation and unavailable providers. Receiving a shared file may require Android intent handling or an iOS share extension, independently of outgoing sharing. [Android photo picker](https://developer.android.com/training/data-storage/shared/photo-picker).

**Contacts and calendars.** Selecting one contact or opening an event editor differs from reading/synchronizing a full database. Respect limited contact access, partial results and revocation; don't translate an empty allowed subset into “no contacts on device.” For calendar integration select system UI versus direct storage APIs, write-only versus full access where supported, and maintain event IDs/timezones without duplicate creation. Opening an editor is not confirmation of a saved event. [Apple Contacts UI](https://developer.apple.com/documentation/ContactsUI), [EventKit access](https://developer.apple.com/documentation/eventkit/accessing-the-event-store), [Android calendar intents](https://developer.android.com/guide/components/intents-common#Calendar).

**Health, activity and sensors.** Health Connect and HealthKit require dedicated native integrations and granular data-type authorization. Check availability, units/timezones, provenance, duplicate samples, change/deletion synchronization and retention. HealthKit deliberately does not reveal whether read access was denied; absent results cannot establish permission or absence of data. Raw motion/step sensors are a separate capability: check hardware, permission for the selected sensor, sampling rate, coordinate frame and lifecycle/battery cost. [Health Connect](https://developer.android.com/health-and-fitness/health-connect/get-started), [HealthKit authorization](https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data).

**QR/barcodes, haptics and clipboard.** Check the official plugin catalog's command-level support. A scanner owns the camera/preview and must release it on cancel and restore UI; deduplicate results and validate scanned URLs. Haptic feedback can be unavailable or disabled and must not be the only success cue. Clipboard read/write behavior varies by platform and foreground state; avoid automatic copying of secrets or background polling. [Tauri scanner](https://v2.tauri.app/plugin/barcode-scanner/), [plugin catalog](https://v2.tauri.app/plugin/).

**Local network and accessories.** Printer discovery, LAN devices, Bonjour and Wi-Fi configuration are separate from internet HTTP. iOS local-network access needs the relevant purpose description and Bonjour service declarations where used. Diagnose denied LAN access separately from TLS/CORS and service discovery failure. USB, printing, casting, widgets and wearable integrations need explicit native/plugin research when present; don't manufacture APIs from their desktop equivalents. [Apple local-network privacy](https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy).

**Navigation and accessibility.** Test Android system/predictive Back with modal, keyboard, WebView and app-route ownership; one gesture must not pop two stacks. Test TalkBack/VoiceOver focus across native dialogs and WebView, text scaling, touch targets, reduced motion, keyboard overlap, rotation and resume after process recreation. HTML appearance alone does not establish native accessibility. [Android predictive Back](https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture), [insets](plugins-mobile.md).

**Android Back contract.** Tauri's default sends Back to the WebView's history and, with none left, closes the activity: a wrapped web app leaves at the first press on its first page. Recommended default (a product choice, not an Android rule): Back closes what is on top (sheet, dialog, panel, sub-page); at the root it shows "press back again to exit" and only a second press within about two seconds leaves. On Android implement it with `onBackButtonPress()` from `@tauri-apps/api/app` (2.9.0 and later; registering "takes over the default behavior", payload `canGoBack`); on the web and in a PWA keep history entries and `popstate`. The code below was not built or run on a device.

```ts
import { onBackButtonPress } from '@tauri-apps/api/app';
import { PluginListener } from '@tauri-apps/api/core';

const KEY = 'app-back-listener';

async function listenForBack(): Promise<void> {
  // A reload runs no cleanup: remove the listener the previous document left.
  const stale = localStorage.getItem(KEY);
  if (stale !== null) await new PluginListener('app', 'back-button', Number(stale)).unregister().catch(() => {});
  const listener = await onBackButtonPress(({ canGoBack }) => {
    if (canGoBack) return window.history.back(); // closes what is on top
    showExitHint(); // "Press back again to exit"
    // For two seconds the next press is Android's own; then take Back again.
    void listener.unregister().then(() => {
      localStorage.removeItem(KEY);
      setTimeout(() => void listenForBack().catch(reportBackFailure), 2000);
    });
  });
  localStorage.setItem(KEY, String(listener.channelId));
}

listenForBack().catch(reportBackFailure);
```

- **Each overlay owns one history entry**, so `canGoBack` is true while something is open and `history.back()` closes it. Closing it another way removes its entry, and that `popstate` must not close a second thing. A router that navigates with `replace` rewrites `history.state`: merge into the state instead of overwriting it, and do not rely on a marker surviving.
- **No root sentinel on Android.** A web build needs a spare history entry to catch Back at the root; with the handler above it would keep `canGoBack` true forever. Dropping it has a cost: a registration that fails silently means Back leaves at once, so report the failure.
- **A listener outlives the page.** Read in Tauri's Android source (2.9.5 and 2.12.5): a plugin listener stays until `remove_listener`, and a page reload removes nothing, so the orphaned channel still counts as a handler and Back does nothing at all. Store the listener's `channelId` and remove it before registering, as above.
- **Capability.** `core:app:default`, part of `core:default`, allows registering and removing listeners; a narrower capability needs `core:app:allow-register-listener` and `core:app:allow-remove-listener`.
- **Leave by letting Android handle the press.** Calling `exit()` instead is avoided here as a precaution: its effect on a running foreground service was not checked.
- **Not observed:** how the predictive-back preview looks when the first press at the root is intercepted.

For capabilities without a first-party implementation covering the required command, inspect a maintained community plugin or implement a narrow native bridge. Check source, licensing, release activity, platform lifecycle and a working device example; package popularity is not compatibility evidence. Use [version maintenance](version-maintenance.md) and [device verification](testing.md) for the final acceptance decision.
