# Versions and compatibility

Read actual lockfiles. Record declared ranges, resolved versions, native modules, vendor commit and patches separately. A version number does not identify a patched fork. The [dated registry inventory](../audit/versions-2026-11-16.json) is discovery evidence, not a tested compatible toolchain.

Inventory Tauri CLI/API/core/build, plugin JS/Rust/native bindings, Wry, Rust, Node/package manager, frontend tooling, Gradle/AGP/Kotlin/JDK, compile/target/min SDK and NDK. For iOS include macOS/Xcode/SDK/deployment target, Swift, CocoaPods/SPM and provider SDKs. Inspect resolved native dependencies and packaged libraries, not just declarations.

Check official registries/release notes. Separate stable versions from alpha/beta/rc and npm dist-tags. Check Cargo MSRV, Node engines, AGP/Gradle/JDK compatibility, deployment minimums and migration guides. Newest releases are not automatically mutually compatible. Keep plugin bindings aligned as their release contract requires.

Upgrade in reviewable groups: core/bindings, native plugins, auth SDKs, Android toolchain, iOS toolchain, frontend tooling. Preserve lockfiles/vendor patches and rollback. Verify affected installed-device flows after each group. Recheck notification serialization, camera callbacks/ACL and auth identity when crossing versions. A newer release alone is not evidence that an internal-protocol workaround can be removed.

Sources: [Tauri updates](https://v2.tauri.app/develop/updating-dependencies/), [Android Gradle](https://developer.android.com/build/releases/gradle-plugin), [Xcode requirements](https://developer.apple.com/xcode/system-requirements/).


Capability upgrade regressions: location precision/background lifecycle, geofence restoration, NFC session/tag compatibility, Bluetooth permissions and reconnect, push token/tap handling, biometric key invalidation, picker URI lifetime and native Back/accessibility. Recheck support per command, OS version and hardware; general plugin platform support is insufficient.
