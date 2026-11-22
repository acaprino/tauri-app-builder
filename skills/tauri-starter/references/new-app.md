# New app: from an empty directory to a running window

Use this path when there is no web app yet. It writes the shared `src-tauri` core and a minimal frontend (plain HTML and TypeScript with Vite, no framework). For an existing web app use `adapt-web-app.md`.

## Before you start

Check, and stop at the first missing item (name it to the user):

```text
rustc --version        Rust 1.90 or newer (the floor declared by the tauri crates)
node --version         Node 20.19 or newer, or 22.12 or newer (the floor of the template's Vite 8)
```

Both floors come from the packages' own metadata; the starter was run only with Rust 1.99.1 and Node 24.14.1.

On Windows the Visual Studio Build Tools with the C++ workload and the WebView2 runtime are also needed. Android steps have their own check in `android.md`.

## Steps

1. **Decide three values.** The product name (shown in the title bar; Tauri refuses `/ \ : * ? " < > |` in it, so the script does too), the identifier (reverse-DNS such as `com.example.notes`, letters, digits, hyphens and dots) and the crate name (lowercase kebab-case such as `notes`). Pick the target directory.
2. **Instantiate.** Run the skill's script. `<skill-dir>` is this skill's own directory.

   ```text
   node <skill-dir>/scripts/instantiate.mjs --mode new --target <dir> --name "<Product Name>" --id <identifier> --crate <crate-name>
   ```

   Expected: one line of JSON listing the files written, exit code 0. Exit 3 means something would have been overwritten and nothing was written; exit 2 is an invalid value; exit 4 is a placeholder left in the template. Never work around an exit code by deleting the user's files.
3. **Install.** In the target directory run `npm install`. This also installs the Tauri CLI for this project; always run it as `npm run tauri -- <command>`.
4. **Run.** `npm run tauri -- dev`. The first build compiles the Tauri crates and takes several minutes. Expected: a window titled with the product name opens and shows "Running on windows".
5. **Check the page.** "Open tauri.app (granted)" shows `opener: allowed` and opens the system browser. "Save window state (not granted)" shows `window-state denied` followed by the ACL message: the capability files work as intended. The "External link" opens the system browser and the window stays on the app: that is the navigation guard. Move and resize the window, close it and run step 4 again: it reopens where you left it. Start the executable a second time while it runs: the first window comes to the front and no second process stays.
6. **Check the packaged build.** `npm run tauri -- build --no-bundle`, then start `src-tauri/target/release/<crate-name>.exe` without the dev server. Expected: the same page. Installers are not part of this check.

## After the start

The core and the page are a baseline, not a product. Continue with `tauri-native-desktop` for desktop behavior and `tauri-native-mobile` for Android, and see `wiring.md` for what each part of the core is for and where to add to it.
