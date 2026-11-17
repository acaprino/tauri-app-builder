# IPC streams

Use commands for request/response, events for notifications and Channels when the installed Tauri API fits ordered streaming. Measure payload size, frequency, latency, queue growth and device load. Avoid unbenchmarked rules of thumb such as fixed event latencies or arbitrary 100 messages/second cutoffs.

Use bounded producer queues, explicit cancellation and an intentional overflow policy. Latest-value coalescing is suitable for replaceable display state, not financial events or durable operations. Handle broadcast lag distinctly from stream closure.

Raw binary responses need an agreed format, bounds/version/endian checks and a matching decoder. A Rust rkyv archive containing vectors is not a flat Float64Array; zero-copy Rust deserialization does not give JavaScript a decoder automatically. Validate the actual serialization API/version.

UI teardown must stop the producer or unsubscribe, not merely replace a JS callback. Worker transfer should use the actual transferable buffer representation; stop pending work when the owning view closes.

Source: [Tauri calling Rust and Channels](https://v2.tauri.app/develop/calling-rust/).
