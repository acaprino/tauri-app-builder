# Mobile CI

Build Android on a supported SDK host and iOS on macOS with the chosen Xcode. Pin toolchain versions and lockfiles; cache by OS, architecture, toolchain and dependency/build inputs. A cached frontend or native output must still be invalidated when its inputs change.

Initialize pinned submodules and any generated JS bindings before the app install/build. Resolve native plugin modules from the dependency graph used by Cargo, not a stale absolute registry path. Custom Gradle tasks must declare producing dependencies, including generated Kotlin before Kotlin compilation.

Restore signing material through the CI's protected secret mechanism and a temporary location. Base64 is transport encoding, not encryption. Keep API upload authorization distinct from Android/iOS code signing. Limit upload operations to the intended application/track. Tauri's documented Android signing is a `keystore.properties` file in `gen/android`, written by the CI job from secrets, plus a signing config in `app/build.gradle.kts`; a project regenerated on every run has no such edit and must sign after Gradle instead. Then align before signing (`zipalign -P 16`; `-p` aligns to 4 KiB and is deprecated), sign, verify the signature, and check the signed file again with `zipalign -c -P 16 -v 4`. Fail the job before building when a secret is missing: never publish an unsigned artifact. [Tauri Android signing](https://v2.tauri.app/distribute/sign/android/), [zipalign](https://developer.android.com/tools/zipalign).

Archive checksum, revision, build version, ABI list, signature identity and symbols with each artifact. Test the produced native artifact. Check whether the deployment pipeline actually builds Android or iOS: a green web deploy does not ship manifest or native plugin fixes.

An emulator job can test the debug artifact (pattern seen in one project, not run for this skill): install the APK, drive the page through the WebView's DevTools socket forwarded with adb, point the app at a fake of the backend on the runner, and keep screenshots, logcat and the received requests as artifacts. Do not pre-grant runtime permissions. A release build has no DevTools socket: there, check that the minified app installs, starts, stays up and logs no missing class. The emulator's ABI is not the phone's, and an emulator does not replace the real-device lane.

When publishing association files or web auth handlers, verify hidden directories such as `.well-known` survive artifact transfer. Configure artifact-upload inclusion explicitly when its defaults exclude hidden files. Test the deployed route's content, not merely a repository file.

See [general CI](ci-cd.md), [builds](build-deploy-mobile.md), [release matrix](testing.md).
