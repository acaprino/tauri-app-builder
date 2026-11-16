# Rendering under frequent updates

Measure on the slowest supported mobile device before choosing a rendering architecture. Subscribe to narrow state slices, batch replaceable display updates, virtualize lists with correct item positioning and stable IDs, and bound retained history.

Canvas/workers can help measured bottlenecks, but require capability detection, accessibility alternatives and lifecycle cleanup. OffscreenCanvas transfer is not freely repeatable across React effect restarts; design initialization and teardown accordingly. Cancel native subscriptions as well as terminating workers.

Treat compiler speedups, row-count capacity and memory limits as measurements of a specific workload and device. Select a JS target compatible with the device floor rather than using `esnext` as a performance shortcut. Every optimization needs before/after evidence and equivalent behavior.

See [IPC](ipc-streaming.md), [WebView compatibility](platform-webviews.md).
