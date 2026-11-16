# Google Play delivery

Reviewed 2026-11-15. The current Play target-API page states API 36 for new phone/tablet apps and updates from 2026-08-31, with platform-specific exceptions. Recheck the app's Play Console eligibility before each submission. [Target API policy](https://support.google.com/googleplay/android-developer/answer/11926878).

The retrieved Android 16 KB guide now states 2027-02-01 for blocking incompatible updates; the backup's 2026-05-31 blanket deadline is superseded by that page. Recheck applicability/Console notices instead of treating this date as a permanent grace period. Technical compatibility still matters today. [Page sizes](https://developer.android.com/guide/practices/page-sizes).

Before release: build a signed AAB; inspect its final package/versionCode and merged manifest; test generated APKs; preserve matching symbols; verify required account access, listing assets, privacy/data declarations and any account-specific testing requirements in Console. Review timing and internal-track review exemptions are not guaranteed.

Use the app's version source of truth and confirm a monotonically valid versionCode in the artifact. A semver formula is not a substitute for inspecting custom Gradle logic. Keep signing credentials out of shared skill examples. The existing application's key-management policy remains project-specific.

Inspect **merged** permissions, including plugin contributions, before removing anything. Verify both runtime denial UX and the resource actually used. Don't force-grant notifications as release acceptance evidence.

For Google login, register the certificate used by the Play-delivered APK. For verified links, publish matching SHA-256 association data, including the relevant Play signing key; upload-key fingerprints alone may not work. Verify `.well-known` survives the build→artifact→hosting chain.

Sources: [Tauri Play distribution](https://v2.tauri.app/distribute/google-play/), [Play signing](https://support.google.com/googleplay/android-developer/answer/9842756), [build checks](build-deploy-mobile.md).
