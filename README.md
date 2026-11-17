# tauri-app-builder

A Claude Code plugin with two skills for building, auditing and shipping Tauri 2 apps that behave natively.

| Skill | Use it for |
|---|---|
| `tauri-native-desktop` | Windows, macOS and Linux: windows and dialogs, frame, system services, notifications, installers/updates, sidecars, keyboard and accessibility, context menus, startup flash, WebView lifecycle and recovery |
| `tauri-native-mobile` | Android and iOS: permissions, camera and microphone, sign-in, deep links, insets, location, NFC/BLE, biometrics, push and background work, file export, builds and store delivery |

Each skill has its own native plugin map: which plugin covers a capability on its platforms and which capabilities have no official plugin. The canonical data lives in [`shared/native-plugins.md`](shared/native-plugins.md) (31 official plugins on all five platforms, maintained plugins and community candidates) and is mirrored in each skill's `references/native-plugins-data.md` so either skill can also be installed standalone.

## Install

```
/plugin marketplace add acaprino/tauri-app-builder
/plugin install tauri-app-builder@tauri-app-builder
```

## Limits

The skills are documentation and decision guides. Plugin support levels are copied from the official plugin manifests on the date stated in each file; no plugin was built or run, and no feature was exercised on a device. Recheck versions against your lockfile and verify on the installed app.

## Validate the plugin and skill bundles

```
python scripts/validate_plugin.py
python -m unittest discover -s scripts -p "test_*.py"
cd skills/tauri-native-mobile
python scripts/validate_bundle.py
python -m unittest discover -s scripts -p "test_*.py"
```

After editing `shared/native-plugins.md`, run `python scripts/validate_plugin.py --sync-shared` to update both standalone skill copies.

## License

MIT. See [LICENSE](LICENSE).
