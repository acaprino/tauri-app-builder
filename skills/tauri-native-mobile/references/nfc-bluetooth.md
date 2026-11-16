# NFC and Bluetooth peripherals

## NFC: define the operation

Tag reading/writing, protocol-specific commands, card emulation and payments are different capabilities. The official Tauri NFC plugin covers tag scanning and NDEF writing. Check isAvailable before opening a session; false can mean absent hardware or disabled/unavailable configuration. Its documented iOS setup currently requires iOS 14+, NFC capability and NFCReaderUsageDescription; check signing entitlements and any protocol-specific declarations. A technology enum shared by the API does not guarantee support on every device. [Tauri NFC setup](https://v2.tauri.app/plugin/nfc/).

Own one scan/write session, deduplicate repeated discoveries and distinguish cancel, timeout, unsupported tag and tag lost. With keepSessionAlive, a following write targets the scanned tag; without it, write scans again. Check the installed API's termination behavior; do not invent a cancel method. A UI timeout is not proof the native session ended. [Tauri NFC API](https://v2.tauri.app/reference/javascript/nfc/).

Before writing, check format, capacity and writable state. Await write completion and read back when feasible before claiming verified success. Removal mid-write may leave partial data. Retry only after re-identifying the intended tag and checking whether repeating the operation is safe; a failed callback does not prove no bytes were written. Never make tags read-only implicitly. Treat NDEF text/URLs as untrusted input; don't automatically execute deep links or grant account access based on tag UID. A UID alone is not a secret or an authentication proof.

iOS background tag reading is system-mediated delivery of suitable tag content after user interaction, not an always-running app scanner. Foreground Core NFC sessions and supported background URL delivery need separate tests. [Apple background tag reading](https://developer.apple.com/documentation/CoreNFC/adding-support-for-background-tag-reading).

Android HCE uses a separate native service/protocol integration. Apple contactless transaction capabilities have separate eligibility, entitlement, territory, hardware and OS requirements. Neither follows from installing a tag plugin; verify the current platform program before promising payment/card support. [Android HCE](https://developer.android.com/develop/connectivity/nfc/hce), [Apple NFC and SE](https://developer.apple.com/support/nfc-se-platform/).

Test no NFC, NFC off, session cancel/timeout, multiple tags, unsupported technology, read-only/full tag, removal during write and repeated scan on the actual Android/iPhone hardware.

## Bluetooth/BLE: discovery is not connection

Choose BLE central/GATT, peripheral advertising, Bluetooth Classic or a specific accessory SDK. Verify a maintained plugin's native implementation and supported roles; browser Web Bluetooth is not evidence of Android WebView/WKWebView support. Do not invent a first-party Tauri BLE API.

For Android 12+ targets, request BLUETOOTH_SCAN, CONNECT or ADVERTISE only for the used roles. Older Android scan rules differ. neverForLocation is a real assertion and can filter some beacons; do not add it if deriving location. Check hardware, adapter state and permission independently. [Android Bluetooth permissions](https://developer.android.com/develop/connectivity/bluetooth/bt-permissions).

On iOS, configure NSBluetoothAlwaysUsageDescription (and any legacy key required by the deployment target) and observe Core Bluetooth authorization/power states before scanning. Background modes and state restoration require native ownership; a JS listener does not provide them. [Bluetooth purpose string](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription), [Core Bluetooth background lifecycle](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/CoreBluetoothBackgroundProcessingForIOSApps/PerformingTasksWhileYourAppIsInTheBackground.html).

Model scan -> connect -> discover services -> subscribe -> exchange -> disconnect. Bound scan duration, filter services, serialize GATT operations where required, handle MTU/chunking/backpressure, unsubscribe and close resources. Match callbacks to connection generations and use bounded reconnect/backoff. Do not use a MAC address as a universal cross-platform stable identity. Pairing, bonding and application authentication are separate. A successful transport write does not prove the accessory applied the command; define acknowledgments.

Background reconnection needs an OS-supported design, such as Android companion-device/foreground mechanisms or iOS Core Bluetooth restoration, with its limits documented. [Android background BLE](https://developer.android.com/develop/connectivity/bluetooth/ble/background).

Test radio toggles, denied permission, out-of-range, accessory reboot, stale callbacks, repeated connect, packet boundaries, app suspend/kill and real peripheral firmware. Emulator-only checks cannot establish radio behavior.
