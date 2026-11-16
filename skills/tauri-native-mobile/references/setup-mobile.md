# Android and iOS toolchains

Record and pin the compatible combination actually used: Tauri CLI/crates, Rust, JDK, Gradle wrapper, AGP, Kotlin, compile/target/min SDK and NDK. A historical template version is not today's required version. Do not select an NDK by lexicographic 'latest' directory order.

Android needs installed SDK/platform/build tools, NDK, a compatible JDK and Rust targets matching the device/emulator ABIs. Start with `aarch64-linux-android` for arm64 devices and `x86_64-linux-android` only for emulators that need it; add other targets when shipping them. Validate SDK/NDK paths instead of copying machine-specific paths into configuration.

iOS builds require macOS and full Xcode. Match device/simulator targets to the runner architecture, selected Xcode and deployment target. A Windows or Linux build of shared code does not verify iOS compilation or device behavior.

Use `tauri android init` or `ios init` for initial generation when appropriate; inspect a diff before regenerating a tracked/custom native project. A checkout that already tracks native build files may need no reinitialization. Initialize pinned vendor submodules and generate their JS bindings before app dependency installation when those bindings are not included in the checkout.

For live mobile development, bind Vite/HMR to the host selected by `TAURI_DEV_HOST`; verify actual reachability. LAN networking, emulator host aliases and `adb reverse` are alternatives; neither IPv6 nor LAN IP is universally required. Select the route supported by the device and CLI.

If OpenSSL cross-compilation fails, inspect the dependency feature graph first. A supported rustls feature can remove an unnecessary OpenSSL dependency; Perl is relevant only when the selected dependencies build vendored OpenSSL. Windows symlinks require suitable privileges/Developer Mode; cross-volume plugin-source paths can also break Kotlin independently of symlink privileges.

Use [version maintenance](version-maintenance.md) when evaluating updates: a newer registry release is not a tested toolchain combination.

Sources: [mobile prerequisites](https://v2.tauri.app/start/prerequisites/#mobile-targets), [CLI](https://v2.tauri.app/reference/cli/).
