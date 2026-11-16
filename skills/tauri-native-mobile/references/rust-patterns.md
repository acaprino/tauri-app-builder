# Rust/mobile boundary

Keep the common builder and mobile entry in the library entry point with `#[cfg_attr(mobile, tauri::mobile_entry_point)]`; modules can live in separate files. Gate dependencies and registration by the platforms actually supported, using Android-only gates for Android-only integrations.

Managed state must meet the API's thread-safety requirements. Do not hold a synchronous mutex across an await; choose lock type by access pattern, keeping critical sections small. CPU/IO blocking work belongs on an appropriate worker, not simply inside an async function.

Commands can return plain serializable values or `Result`; async commands do not universally require `Result`. IPC errors must serialize; deriving Serialize or an explicit mapping are both valid. Prefer stable error codes at the boundary over UI parsing of an arbitrary formatted error.

Handle a failed Channel send as a lifecycle signal when appropriate; don't blindly ignore it while producing indefinitely. Release long-lived tasks through an explicit cancellation/subscription contract.

Choose release optimization from measured size/performance needs, and preserve matching symbols. Cargo build scripts run on the host; use target environment metadata rather than host `cfg!` when choosing target behavior in a build script.

Sources: [calling Rust](https://v2.tauri.app/develop/calling-rust/), [Cargo scripts](https://doc.rust-lang.org/cargo/reference/build-scripts.html).
