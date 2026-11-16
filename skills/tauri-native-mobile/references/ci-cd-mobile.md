# Mobile CI

Build Android on a supported SDK host and iOS on macOS with the chosen Xcode. Pin toolchain versions and lockfiles; cache by OS, architecture, toolchain and dependency/build inputs. A cached frontend or native output must still be invalidated when its inputs change.

Initialize pinned submodules and any generated JS bindings before the app install/build. Resolve native plugin modules from the dependency graph used by Cargo, not a stale absolute registry path. Custom Gradle tasks must declare producing dependencies, including generated Kotlin before Kotlin compilation.

Restore signing material through the CI's protected secret mechanism and a temporary location. Base64 is transport encoding, not encryption. Keep API upload authorization distinct from Android/iOS code signing. Limit upload operations to the intended application/track.

Archive checksum, revision, build version, ABI list, signature identity and symbols with each artifact. Test the produced native artifact. Check whether the deployment pipeline actually builds Android or iOS: a green web deploy does not ship manifest or native plugin fixes.

When publishing association files or web auth handlers, verify hidden directories such as `.well-known` survive artifact transfer. Configure artifact-upload inclusion explicitly when its defaults exclude hidden files. Test the deployed route's content, not merely a repository file.

See [general CI](ci-cd.md), [builds](build-deploy-mobile.md), [release matrix](testing.md).
