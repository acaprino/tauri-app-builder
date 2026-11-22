use tauri::Url;

#[tauri::command]
fn platform_name() -> &'static str {
    std::env::consts::OS
}

fn same_origin(a: &Url, b: &Url) -> bool {
    a.scheme() == b.scheme() && a.host_str() == b.host_str() && a.port_or_known_default() == b.port_or_known_default()
}

// The packaged app origin: tauri://localhost, or http(s)://tauri.localhost on Windows and Android.
fn is_app_url(url: &Url) -> bool {
    match url.scheme() {
        "tauri" => url.host_str() == Some("localhost"),
        "http" | "https" => url.host_str() == Some("tauri.localhost") && url.port().is_none(),
        _ => false,
    }
}

// Only the app's own origin may load in the webview; web links open in the system browser instead.
fn navigation_guard<R: tauri::Runtime>() -> tauri::plugin::TauriPlugin<R> {
    tauri::plugin::Builder::new("navigation-guard")
        .on_navigation(|webview, url| {
            let dev_origin = cfg!(debug_assertions)
                && webview.app_handle().config().build.dev_url.as_ref().is_some_and(|dev| same_origin(dev, url));
            if is_app_url(url) || dev_origin {
                return true;
            }
            if matches!(url.scheme(), "http" | "https") {
                let _ = tauri_plugin_opener::open_url(url.as_str(), None::<&str>);
            }
            false
        })
        .build()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let builder = tauri::Builder::default();

    // Desktop only: a second launch focuses the first window, and the window keeps its size and place.
    #[cfg(desktop)]
    let builder = builder
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            use tauri::Manager;
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.unminimize();
                let _ = window.set_focus();
            }
        }))
        .plugin(tauri_plugin_window_state::Builder::default().build());

    builder
        .plugin(tauri_plugin_log::Builder::default().level(log::LevelFilter::Info).build())
        .plugin(tauri_plugin_opener::init())
        .plugin(navigation_guard())
        .invoke_handler(tauri::generate_handler![platform_name])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
