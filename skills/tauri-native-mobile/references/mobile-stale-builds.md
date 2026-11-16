# Stale Android builds: follow the artifact

Cargo's `rerun-if-changed` scans a directory for changes. It is not restricted to the directory inode's mtime. Timestamp-based invalidation still has limits, but those must be reproduced rather than assumed. [Cargo build scripts](https://doc.rust-lang.org/cargo/reference/build-scripts.html#change-detection).

Locate the runtime asset loader before adding build checks. When Android assets are served through WebViewAssetLoader, searching the Rust `.so` for frontend chunk names does not establish which HTML/JS was packaged. A standard `build.rs` calling `tauri_build::build()` does not need a recursive walker solely to compensate for a presumed Cargo directory-watch limitation.

## Investigation order

1. Record the exact device/package/version/signature, source revision and artifact checksum. Confirm which APK was installed and which ABI/variant it contains.
2. Distinguish live `devUrl`/HMR from a packaged debug build. A `--debug` build is not necessarily a dev-server session. Check the actual WebView URL and runtime resource loader.
3. Compare Vite output, `build.frontendDist`, Android asset input, merged assets and final APK ZIP entries. Remove obsolete output files when synchronizing; verify HTML references chunks actually packaged.
4. Inspect Gradle task dependencies and outputs. `mustRunAfter` only orders scheduled tasks; it does not schedule a producer. `SKIPPED` in Gradle is not proof of a Cargo dependency bug.
5. Inspect service-worker/cache registrations and which content origin is active. A new APK may still run stale cached web content when a PWA worker was accidentally enabled.
6. For direct Cargo builds, ensure the intended custom-protocol feature, NDK compiler/linker variables, target directory, package/library names, Wry generated-source output and Kotlin task dependencies agree. Prefer the standard Tauri CLI for new integrations; retain custom Gradle orchestration only when the project requires it.
7. Invalidate only the demonstrated stale output, then rebuild and compare. Do not patch generated `RustWebViewClient.kt`, change origin or uninstall the app as a generic fix.

For custom orchestration, make asset synchronization remove obsolete chunks, build native libraries for the selected variant/ABI, resolve plugin paths from locked Cargo metadata and produce Wry's Kotlin sources before Kotlin compilation. Declare these dependencies in the task graph; task names alone provide no correctness guarantee.

See [mobile builds](build-deploy-mobile.md), [mobile CI](ci-cd-mobile.md) and [verification](testing.md).
