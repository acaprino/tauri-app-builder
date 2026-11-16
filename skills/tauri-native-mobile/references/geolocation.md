# Geolocation, background tracking and geofencing

Choose one-shot position, a visible-screen watch, an ongoing user-visible journey, background tracking or geofencing. These have different permissions and native lifecycles. Maps, geocoding and routing are separate services; a location plugin does not provide them.

## Foreground position

The official Tauri geolocation plugin exposes permission checks/requests, getCurrentPosition, watchPosition and clearWatch. Check the installed declarations and native configuration. Watch registration is asynchronous: if the owner closes before the watch ID arrives, clear the newly returned ID immediately. Suppress stale callbacks by generation, report callback errors and clear active watches when their feature ends. A component unmount alone does not unregister native work. [Tauri API](https://v2.tauri.app/reference/javascript/geolocation/).

Treat denied permission, disabled location service, timeout, approximate/reduced accuracy and unavailable position as separate states. Record position timestamp and accuracy; a cached coordinate is not a fresh fix. Set maximumAge, timeout and accuracy according to the feature. Never convert missing latitude/longitude to zero, or treat nullable heading/speed as measured zero. Ask for precision only when it changes the result; offer manual location entry where useful.

Android foreground access uses coarse and, when needed, fine location; Android 12+ users can still choose approximate access. High-accuracy options cannot override that choice. Inspect current target-specific rules, including session-based location access, when upgrading the target SDK. iOS needs usage descriptions and authorization appropriate to the actual feature; reduced accuracy is not denial. [Android location access](https://developer.android.com/develop/sensors-and-location/location/permissions), [Tauri setup](https://v2.tauri.app/plugin/geolocation/).

## Background is a separate implementation

Do not infer background survival from a working JS watcher. Identify a native owner, its persistence and relaunch behavior before promising updates with the screen locked or the WebView suspended.

On Android, a user-started journey may use a location foreground service with the required service type, permissions and visible notification. Check current launch restrictions; foreground service does not mean unrestricted background startup. Truly background access/geofencing may require ACCESS_BACKGROUND_LOCATION. Request foreground access first, then the separately justified background access; Android 11+ background grants use settings. Approximate foreground access remains approximate in the background. [Background permission](https://developer.android.com/develop/sensors-and-location/location/permissions/background).

On iOS, select the Core Location service and authorization appropriate to the deployment target. Configure Location updates background mode when needed; newer APIs include CLBackgroundActivitySession and CLServiceSession, with availability gates. Own sessions natively and persist enough state to recover supported relaunches. Do not request Always access merely because a foreground watch exists. [Core Location background updates](https://developer.apple.com/documentation/corelocation/handling-location-updates-in-the-background).

Geofences use OS monitoring, not distance calculations on a suspended JS timer. Persist IDs, owner, center/radius, transition/dwell rules and registration state. Respect platform capacity and service availability; re-register on documented reset/reboot paths and remove obsolete/account-owned fences. Events can be delayed and duplicated: deduplicate and re-authorize resulting actions. A fence crossing is not an exact alarm or a proof of physical presence. [Android geofencing](https://developer.android.com/develop/sensors-and-location/location/geofencing).

Test fresh/one-time grant, approximate mode, disabled service, no GPS fix, stale coordinates, watch-register/unmount race, lock screen, battery saver, restart/reboot, permission revoke, logout and fence transitions on hardware. Record observed update latency and battery cost, not merely the permission result.
