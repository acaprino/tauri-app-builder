# iOS distribution

Use macOS/full Xcode and the project's selected deployment target. Read CLI/Xcode export-method help; preserve signing configuration when regenerating projects. The bundle identifier, certificate/private key, provisioning profile and enabled capabilities must agree. Automatic signing can be used with correctly configured CI; manual signing is not universally mandatory.

Confirm marketing/build versions in the archive, not only config files. Add purpose strings only for APIs actually accessing protected resources. A system picker is not equivalent to direct Photos-library access. Validate camera, microphone, location and biometrics on supported hardware when present.

Upload through a supported Xcode Organizer, Transporter or documented CLI workflow. Keep archive/dSYM and the uploaded build identity. App Store Connect API credentials do not replace distribution signing material. Before submission consult current Apple SDK/upload minimums, screenshot specifications, privacy manifests/required-reason APIs, third-party SDK declarations, account deletion and sign-in requirements applicable to the app. Do not hardcode stale screenshot sizes or promise fixed App Review turnaround times.

Simulator testing is useful but does not establish hardware/device parity. Remote push is supported in some simulator configurations (Xcode 14 added iOS 16 support on suitable macOS 13 Macs); 'never supported on simulator' is obsolete. Validate the intended APNs/device environment separately.

Sources: [Tauri App Store distribution](https://v2.tauri.app/distribute/app-store/), [Apple upcoming requirements](https://developer.apple.com/news/upcoming-requirements/), [Xcode 14 notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-14-release-notes). No iOS build or device verification was performed in this review.
