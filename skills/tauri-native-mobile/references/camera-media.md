# Camera, microphone and video

Select still capture, embedded preview, barcode scan, video, audio or gallery explicitly. An Android still-camera plugin does not establish video or iOS support.

## Capture ownership

Verify installed ACL: tauri-plugin-native-camera uses `native-camera:allow-take-picture`; an existing but empty default set grants no command. Tauri Kotlin permission completion uses `@PermissionCallback`; activity image results use `@ActivityCallback`.

Keep one application-wide owner. Reject concurrent requests as busy or coalesce them with only the first caller owning UI effects. Carry request IDs across native and JS boundaries. Native ownership lasts until the activity settles or cancellation is acknowledged. A JS timeout cannot release a single native slot and permit another capture: Promise.race does not cancel native work. Ignore stale UI generations while still cleaning resources. See the [ownership contract](../examples/capture-owner.ts).

Distinguish ok, cancelled, unavailable and error. Cancellation must not open a gallery or show an error toast. Offer fallback for unavailable capability; invoke a browser picker synchronously from a fresh user gesture, not after an awaited native failure.

Use narrow FileProvider cache paths and URI grants required by the recipient. Read access to one URI does not grant neighboring files. Align authority, manifest and paths. Clean temporary output after settlement and stale files on startup. Handle empty output, decode errors, all EXIF rotations/reflections, final dimension limits and memory pressure. Sampled decoding alone may not enforce the final maximum dimensions.

## Audio lifecycle

Check WebView permission/origin integration, MediaRecorder and isTypeSupported. Guard pending start as well as active recording. Increment a generation on cancel/unmount; if permission resolves later, stop every track of the stale stream immediately. See [late-stream acquisition](../examples/audio-acquisition.ts).

Attach recorder handlers before start. On normal stop, await final dataavailable and stop before assembling output. On cancel discard chunks. Stop tracks and timers on every terminal path, including encoder error and interrupted start. Bind cleanup to the recorder instance so an old stop callback cannot clear a newer recording. Choose product-specific duration/size limits and show interruption honestly.

## Video and iOS

For Android native video, evaluate CameraX VideoCapture against the SDK/device matrix and packaged libraries. Implement recording state, audio permission, output ownership, interruption and finalization independently from still capture. For iOS use a capture controller or AVFoundation with usage descriptions, main-thread presentation, permission handling and interrupted-session cleanup. Saving to the photo library is a separate authorization decision.

Test first grant, denial/settings, cancel, repeated taps across screens, timeout/late result, unmount during permission prompt, process death, mirrored/large images, unsupported codecs and final output validity. These examples do not certify native behavior.

Sources: [FileProvider](https://developer.android.com/reference/androidx/core/content/FileProvider), [CameraX video](https://developer.android.com/media/camera/camerax/video-capture), [Apple capture authorization](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media).

