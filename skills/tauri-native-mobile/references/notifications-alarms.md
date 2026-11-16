# Notifications, reminders and exact alarms

Choose the delivery contract before choosing a plugin. A notification displays information; a schedule determines when it is delivered; an alarm may additionally require interruption, sound, dismiss and snooze. An app may need all three. Never silently replace a requested exact reminder with an inexact notification or a WebView timer.

| Requirement | Android | iOS |
|---|---|---|
| Immediate/local notification | Notification permission, channel and installed notification plugin | UserNotifications authorization and presentation |
| Flexible scheduled notification | OS-backed notification scheduling; expose timing tolerance | Calendar/time-interval local notification; delivery presentation follows system policy |
| Exact timed reminder | Native AlarmManager exact one-shot scheduling with required access | Assess AlarmKit on iOS 26+; ordinary local notifications are not an equivalent alarm guarantee |
| User-visible alarm with snooze | AlarmManager alarm-clock semantics where appropriate, receiver and native action handling | AlarmKit authorization, alarm presentation and actions on supported OS |

## Durable model and ownership

Persist `id`, `revision`, `ownerId`, enabled state, delivery kind, local wall time or absolute instant, timezone policy, recurrence, next occurrence, snooze state and native identifier. Use stable collision-free IDs and namespace them per account/feature. Decide explicitly whether 07:30 follows the user's current timezone or a fixed zone; define DST gaps (skip or shift) and overlaps (first or second occurrence). Compute from calendar rules, not repeated addition of 24 hours.

Use one serialized reconciliation worker. Snapshot desired state, compare only app-owned OS requests, cancel obsolete revisions, schedule missing requests and record successful registrations. Changes arriving during a run mark it dirty and trigger another pass. Handle partial failure and retry idempotently; a cancel-all-then-batch strategy creates a delivery gap. Trigger on changes, startup/resume, permission changes, account switch, timezone/time change and reboot where the platform permits. Account deletion/sign-out must cancel only the relevant owner's pending requests.

Re-arm recurring exact occurrences in the native delivery path; JS may be suspended or dead. Deduplicate delivery/actions by occurrence ID. A snooze is a separate persisted occurrence with its own ID and cancellation relationship, not a JS timeout. Stop/dismiss must settle native sound/session state. Define missed-occurrence policy and expose reconciliation errors.

## Android exact lane

Use `canScheduleExactAlarms()` where required before registration. `SCHEDULE_EXACT_ALARM` is special user access, independent from Android 13+ notification permission and channel settings. `USE_EXACT_ALARM` has restricted eligible use cases and store policy: do not add it just to avoid the access screen. After returning from settings, recheck access. Revocation invalidates scheduled exact work; reconcile after access returns.

Select `setExactAndAllowWhileIdle` for suitable exact work during idle, or `setAlarmClock` for actual user-facing alarm-clock semantics. Follow current quotas and platform guidance; no API promises execution with the device powered off. Android repeating alarms are inexact: calculate and re-arm exact one-shots. Use stable PendingIntent identity (explicit component, action/data or request code), appropriate immutable flags, a native receiver, durable schedule state and reboot restoration. WorkManager is for deferrable work, not exact alarms. Request foreground-service/full-screen capabilities only when the actual alarm design and platform rules require them.

Distinguish process eviction, swiping the task and force-stop. Force-stop suppresses execution until the user reactivates the app; do not promise immunity. Explain blocked permission states in the UI and retain the requested schedule for recovery. An unsupported exact lane must report unavailable or require an explicitly accepted alternative.

## Existing notification-plugin adapters

Prefer documented APIs from the pinned version. A historical Android 2.3.3 workaround invoked Kotlin `plugin:notification|batch`, `get_pending` and `cancel` directly to bypass a Rust date-serialization defect. Its payload used `sourceJson = JSON.stringify(entry)` for persistence, second/millisecond-zero one-shot dates, and Calendar weekday mapping `jsWeekday + 1`. These are version-specific internal protocol details, not a stable public API or an exact-alarm implementation. Before keeping such an adapter, inspect the installed Kotlin parser, persistence, receiver and reboot restoration; before removing it, prove the public path works in a release build. Pin and isolate any workaround with an upgrade regression.

## iOS

Local UserNotifications requests can repeat, but do not turn them into a promise of an audible exact alarm regardless of user settings. For alarm semantics on iOS 26+, use AlarmKit with an availability gate, nonempty `NSAlarmKitUsageDescription`, authorization, stable UUIDs, supported fixed/weekly/countdown schedules and cancel/snooze actions. Observe `alarmUpdates` and reconcile removed alarms. Countdown presentation needs the corresponding widget extension. On older OS versions, explicitly mark the exact alarm feature unavailable unless a separately validated supported implementation exists.

Acceptance: fresh permission, denial/revoke, disabled channels, locked/idle device, app process gone, reboot, force-stop recovery, edit/delete during reconciliation, DST gap/overlap, timezone travel, duplicate receiver delivery, snooze/dismiss and account switch. Record requested and observed delivery times on real devices; documentation review cannot certify timing.

Sources: [Android alarms](https://developer.android.com/develop/background-work/services/alarms), [Tauri notifications](https://v2.tauri.app/plugin/notification/), [AlarmKit scheduling](https://developer.apple.com/documentation/AlarmKit/scheduling-an-alarm-with-alarmkit), [Apple local notifications](https://developer.apple.com/documentation/usernotifications/scheduling-a-notification-locally-from-your-app).
