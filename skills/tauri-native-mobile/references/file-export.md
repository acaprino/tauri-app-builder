# Native file export and downloads

A successful HTTP response, Blob creation or click on `<a download>` does not prove that a file was saved. A `blob:` URL belongs to the WebView document; handing it to Android DownloadManager does not transfer its bytes. A download listener alone does not fix that boundary.

Expose an application-owned adapter with outcomes `saved`, `cancelled`, `failed` and, if supported separately, `shared`. Success requires the destination writer to finish and close successfully. Opening a share sheet is not evidence of saving. In a browser, say “Download started” if actual completion cannot be observed.

## Android save flow

1. Fetch the account export through the authenticated session. Check HTTP status and expected archive response; reject JSON/HTML error bodies. Bind the job to account/session generation and do not resume it under another identity.
2. Select a bounded transfer design. For small files, pass bytes through an explicitly size-limited native command. For large ZIPs, stream into private native cache using a trusted authenticated request or a chunked bridge with backpressure; avoid base64 and several whole-file copies. Never log tokens or account data.
3. Launch `ACTION_CREATE_DOCUMENT` with `CATEGORY_OPENABLE`, MIME `application/zip` and a sanitized suggested filename. Handle activity-result cancellation as cancellation. The returned `content://` URI is a provider resource, not a filesystem path.
4. On an I/O worker, use `ContentResolver.openOutputStream(uri)` and copy the bytes. Handle null streams, short/failed writes and close failures. Resolve the JS promise as saved only after successful completion; report the actual filename/provider where available. This confirms provider acceptance, not remote cloud synchronization.
5. Clean private temporary files on success/cancel/failure and stale jobs on startup. For partial destination files, attempt provider-supported cleanup and report when it cannot be done. On process death, restore a durable job or mark it interrupted; never manufacture a completion toast.

Storage Access Framework grants access to the user-selected URI without broad storage permission. Do not request `MANAGE_EXTERNAL_STORAGE` for account export. Preserve URI grants only if later access is necessary and supported. Custom native plugin callbacks must settle exactly one matching request and reject concurrent picker launches or queue them explicitly.

Check the installed Tauri dialog/file-system platform support and URI handling before using their APIs. A desktop `save()` plus path writer is not automatically an Android implementation. If the installed plugins cannot create and write a document URI, implement a narrow Android plugin with capability-scoped commands. Never fall back silently to an invisible anchor in Tauri.

## iOS and sharing

Use a document export picker for a staged local file, with its completion/cancellation delegate and cleanup lifecycle. If offering sharing instead, use the native share controller and label its result accurately. Account for sandbox and security-scoped resource rules when applicable. Gate Android, iOS, desktop and browser adapters explicitly.

## UI and verification

Use `preparing → choosing destination → writing → saved`, with separate cancelled/failed/interrupted states. Keep a single job owner, provide progress for large transfers and protect against repeated taps. A picker cancel is not a failed server export. Retrying should not duplicate account jobs unnecessarily.

Test an installed release build: inspect the chosen destination, reopen the ZIP and verify expected archive entries/bytes. Cover empty/small/large exports, cloud document provider, duplicate filename, no space, provider failure, picker cancel, background/activity recreation, logout and process death. This guide covers technical delivery; an archive alone does not establish legal compliance.

Sources: [Android documents and files](https://developer.android.com/training/data-storage/shared/documents-files), [Tauri file system](https://v2.tauri.app/plugin/file-system/), [Tauri dialog](https://v2.tauri.app/plugin/dialog/), [Apple document picker](https://developer.apple.com/documentation/uikit/uidocumentpickerviewcontroller).
