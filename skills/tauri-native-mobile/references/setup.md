# Base setup

Read the project's package manager and lockfiles first. Record Rust/Cargo, Node/package manager and local Tauri CLI versions with `rustc -Vv`, `cargo -V` and the project's `tauri info` command. Tauri crate, CLI and plugin versions are not required to have identical version numbers.

Use a project-local CLI when available. `npm run tauri -- <arguments>` assumes a package script named `tauri`; don't invent that script if the repository uses another command. Preserve the project's generated native tree and custom scripts.

Vite config can read `process.env.TAURI_DEV_HOST` during configuration without exposing every `TAURI_*` variable to client code. `envPrefix` controls client exposure; only expose values the frontend needs. `clearScreen: false` is useful for readable logs, not a correctness requirement.

Keep `frontendDist` relative to the Tauri config and aligned with the actual frontend output. Set an explicit supported JS/CSS engine baseline and separately feature-detect runtime APIs. Continue with [mobile setup](setup-mobile.md).

Sources: [prerequisites](https://v2.tauri.app/start/prerequisites/), [Vite integration](https://v2.tauri.app/start/frontend/vite/).
