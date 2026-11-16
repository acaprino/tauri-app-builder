# Mobile build artifacts

Use the installed CLI's help and repository scripts. Standard examples, when the CLI is installed locally:

```text
npm run tauri -- android build --apk --debug
npm run tauri -- android build --aab
npm run tauri -- ios build
```

`--apk` selects an artifact; it does not mean debug. `android build` defaults to release. The old `--apk true` workaround was a CLI-version issue, not a Windows rule. iOS export options depend on CLI/Xcode versions; use their help rather than copying retired method names.

Android artifact paths vary with architecture, flavors and build type. Inspect actual outputs, signature, application ID, versionCode and packaged assets. Do not label a per-ABI build 'universal'. AAB is for distribution and cannot be installed with `adb install` directly; test APKs generated from the bundle as well as direct APK builds.

## 16 KB compatibility

Check both ELF segment alignment of **every** native library and ZIP alignment of packaged uncompressed libraries. A Rust linker flag cannot fix an incompatible prebuilt CameraX library: update or rebuild the dependency that supplies it, then inspect the packaged result.

The current Android guide recommends AGP 8.5.1+ and NDK r28+ with compatible prebuilts. It also requires testing native code's page-size assumptions. NDK choice alone does not prove a Rust/custom-linker binary or a third-party `.so` is compatible. Inspect with the guide's ELF tooling, `zipalign -c -P 16 -v 4 <apk>` and bundletool configuration, then run on a 16 KB environment. [Android page-size guidance](https://developer.android.com/guide/practices/page-sizes).

## Signing and installation

Keep debug, local release, upload and store signing identities distinct. Prefer in-place `adb install -r` with a compatible signature/version when preserving app state matters. Signature mismatch or a deliberate downgrade may need a separate test device or an explicitly chosen reset; uninstall deletes app data and is not a routine repair.

For iOS, the certificate/private key, provisioning profile, entitlements and app identity must agree. An App Store Connect API key authenticates service operations; it is not itself the code-signing identity.

Keep symbols and build metadata with release artifacts. Verify [stale-build](mobile-stale-builds.md) boundaries and [release testing](testing.md) before upload. Neither this review nor a web build establishes that a new APK is installed.
