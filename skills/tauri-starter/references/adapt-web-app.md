# Adapt a web app: wrap an existing project in Tauri

Use this path when a web project exists. It adds the shared `src-tauri` core to it and leaves the app's own source alone. The browser path must keep working: the project's own dev and build scripts run unchanged afterwards. For a project with no web app yet use `new-app.md`.

## 1. Detect, read-only

Write the result of each point down before changing anything.

1. **Existing Tauri.** A `src-tauri/` folder, a `tauri` crate or `@tauri-apps/cli` means the project is already wrapped. Stop and say so; this is not an adaptation.
2. **Package manager.** The lockfile (`package-lock.json` npm, `pnpm-lock.yaml` pnpm, `yarn.lock` yarn, `bun.lock` or `bun.lockb` bun) and the `packageManager` field. Use that manager for every command; this skill's examples say `npm run tauri -- ...`, so write `pnpm tauri ...`, `yarn tauri ...` or `bun run tauri ...` instead.
3. **Dev server and build.** The `dev` and `build` scripts, the tool's config file, the dev URL and port (the config, else the tool's default: Vite 5173, Next.js and Nuxt 3000, Angular 4200, Astro 4321) and the build output directory (`dist`, `build`, `out`, `.output/public`).
4. **Static output.** Tauri serves files, not a server. Refuse when the app needs a server at run time: Next.js without `output: 'export'`, Nuxt without `generate`, Remix, SvelteKit without the static adapter, Astro with a server adapter, any API route (`app/api`, `pages/api`, `server/`) or cookies set by a server.
5. **Router and base path.** History or hash routing, and any `base`, `basePath`, `homepage` or `publicPath` other than `/`.
6. **Service worker.** `navigator.serviceWorker.register`, a PWA plugin, `sw.js` or workbox.
7. **Remote origins.** Every absolute `http(s)` address other than localhost in the source, the HTML, the config and the `.env*` files: API base URLs (including `VITE_*` and similar variables), CDN scripts and styles, web fonts, sign-in redirects. List each host with the file that uses it.

## 2. Decide

- **Stop and tell the user why:** an existing Tauri project; no static output (point 4).
- **Warn, show the proposed change and ask:** a non-root base path (the Tauri build needs `/`; the Tauri CLI sets `TAURI_ENV_PLATFORM` for the commands it runs, which a config can use to switch the base for that build only); a service worker (the packaged build must not register one, see `tauri-native-mobile` on stale builds: switch it off for the Tauri build or stop); remote origins (below).
- **Remote origins.** Show the list and ask which hosts to allow. Add them only to the matching directive of the CSP in `src-tauri/tauri.conf.json` (`connect-src` for APIs, `script-src`, `style-src` and `font-src` for CDNs and fonts) and never widen the CSP, the navigation guard or the capabilities silently. Tell the user the packaged origin is not the dev server's (`http://tauri.localhost` on Windows and Android), so a backend that expects the web origin needs CORS, cookie and redirect changes made on its side.

## 3. Add the core

```text
node <skill-dir>/scripts/instantiate.mjs --mode adapt --target <project dir> --name "<Product Name>" --id <identifier> --crate <crate-name>
```

It writes only `src-tauri/` and refuses when that folder exists (exit 3, nothing written). The core brings its own `.gitignore` for `target` and `gen/schemas`.

## 4. Wire it to the project

New files and keys go in directly:

- In `src-tauri/tauri.conf.json` set `build.devUrl` to the detected dev URL, `build.frontendDist` to the output directory relative to `src-tauri` (for example `../dist`), and `build.beforeDevCommand` and `build.beforeBuildCommand` to the project's own dev and build scripts run with its package manager.
- In `package.json` add `@tauri-apps/cli` as a dev dependency (use the version in this skill's `assets/web/package.json`) with the project's package manager, and a `"tauri": "tauri"` script if there is none.

Edits to files the project already owns are shown as a diff and applied only after the user approves; without approval stop:

- Dev server host for Android, in the tool's config: read `process.env.TAURI_DEV_HOST` and use it as `server.host` (see the new-app page's `vite.config.ts`).
- The base path and the service worker switch from point 2.

Then run the app with the project's package manager (`tauri dev`), and `android.md` for Android.

## 5. Check

1. The window opens on Windows and shows the app; a packaged build (`tauri build --no-bundle`) opens it without the dev server.
2. With a history router, load a route inside the app directly (reload on it, or open its URL), not only by clicking a link: the page must render the app, not an error. Observed with a React history router: the packaged Windows build and the Android debug APK both rendered the route.
3. The browser path: run the project's original `dev` and `build` scripts. They must behave as before the adaptation, and the build output must list the same files.
4. Remote origins the user allowed load; the ones they did not are blocked.
5. Requests to the app's own origin (for example `fetch('/data.json')` or a translation file) work in a packaged build: the core's policy allows `'self'` in `connect-src`. A `tauri dev` run does not prove it, because the policy is not enforced on the dev server's page.
