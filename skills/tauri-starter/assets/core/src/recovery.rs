//! WebView2 recovery on Windows. A renderer that dies is reloaded a bounded number of times, a browser
//! process that dies restarts the app, and everything else is only logged. WebView2 calls its handlers on
//! the UI thread, so the handler copies what it needs and returns; the work runs from another thread.
//! Not covered: failed navigations, an unresponsive renderer, frames, and windows other than "main".
//! A restart loses in-memory state, so an app with unsaved work must persist it before relying on this.

use std::{
    sync::{Arc, Mutex},
    time::{Duration, Instant},
};

use tauri::{AppHandle, Manager, WebviewWindow};
use webview2_com::{
    Microsoft::Web::WebView2::Win32::{
        COREWEBVIEW2_PROCESS_FAILED_KIND, COREWEBVIEW2_PROCESS_FAILED_KIND_BROWSER_PROCESS_EXITED,
        COREWEBVIEW2_PROCESS_FAILED_KIND_RENDER_PROCESS_EXITED,
    },
    ProcessFailedEventHandler,
};

const MAX_RELOADS: usize = 3;
const RELOAD_WINDOW: Duration = Duration::from_secs(60);
const DEFER: Duration = Duration::from_millis(300);

#[derive(Debug, PartialEq, Eq)]
enum Action {
    Reload,
    Restart,
    Ignore,
}

fn decide(kind: COREWEBVIEW2_PROCESS_FAILED_KIND) -> Action {
    if kind == COREWEBVIEW2_PROCESS_FAILED_KIND_RENDER_PROCESS_EXITED {
        Action::Reload
    } else if kind == COREWEBVIEW2_PROCESS_FAILED_KIND_BROWSER_PROCESS_EXITED {
        Action::Restart
    } else {
        Action::Ignore
    }
}

/// At most MAX_RELOADS reloads per RELOAD_WINDOW, so a page that crashes at once does not reload forever.
#[derive(Default)]
struct ReloadBudget {
    recent: Vec<Instant>,
}

impl ReloadBudget {
    fn allow(&mut self, now: Instant) -> bool {
        self.recent.retain(|at| now.saturating_duration_since(*at) < RELOAD_WINDOW);
        if self.recent.len() < MAX_RELOADS {
            self.recent.push(now);
            true
        } else {
            false
        }
    }
}

/// Registers the ProcessFailed handler on the window's WebView2. Call it once, right after the window exists.
pub fn install(window: &WebviewWindow) {
    let app = window.app_handle().clone();
    let target = window.clone();
    let budget = Arc::new(Mutex::new(ReloadBudget::default()));
    let installed = window.with_webview(move |webview| {
        // Safety: COM calls on the UI thread that owns the controller.
        unsafe {
            let core = match webview.controller().CoreWebView2() {
                Ok(core) => core,
                Err(error) => {
                    log::error!("webview recovery not installed: {error}");
                    return;
                }
            };
            let handler = ProcessFailedEventHandler::create(Box::new(move |_sender, args| {
                let mut kind = COREWEBVIEW2_PROCESS_FAILED_KIND::default();
                if args.is_some_and(|args| args.ProcessFailedKind(&mut kind).is_ok()) {
                    respond(&app, &target, &budget, kind);
                }
                Ok(())
            }));
            let mut token = Default::default();
            if let Err(error) = core.add_ProcessFailed(&handler, &mut token) {
                log::error!("webview recovery not installed: {error}");
            }
        }
    });
    if let Err(error) = installed {
        log::error!("webview recovery not installed: {error}");
    }
}

fn respond(app: &AppHandle, window: &WebviewWindow, budget: &Arc<Mutex<ReloadBudget>>, kind: COREWEBVIEW2_PROCESS_FAILED_KIND) {
    match decide(kind) {
        Action::Ignore => log::warn!("a WebView2 process failed (kind {}); no recovery for this kind", kind.0),
        Action::Restart => {
            let app = app.clone();
            let label = window.label().to_string();
            std::thread::spawn(move || {
                std::thread::sleep(DEFER);
                // A normal exit also ends the browser process: restart only while the window still exists.
                if app.get_webview_window(&label).is_some() {
                    log::error!("the WebView2 browser process exited, restarting the app");
                    app.request_restart();
                }
            });
        }
        Action::Reload => {
            let allowed = budget.lock().map(|mut budget| budget.allow(Instant::now())).unwrap_or(false);
            if !allowed {
                log::error!("the page crashed again and the reload limit is reached; the engine's error page stays");
                return;
            }
            log::warn!("the page process exited, reloading");
            let window = window.clone();
            std::thread::spawn(move || {
                std::thread::sleep(DEFER);
                let _ = window.with_webview(|webview| unsafe {
                    if let Ok(core) = webview.controller().CoreWebView2() {
                        let _ = core.Reload();
                    }
                });
            });
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::{Duration, Instant};
    use webview2_com::Microsoft::Web::WebView2::Win32::{
        COREWEBVIEW2_PROCESS_FAILED_KIND_BROWSER_PROCESS_EXITED, COREWEBVIEW2_PROCESS_FAILED_KIND_GPU_PROCESS_EXITED,
        COREWEBVIEW2_PROCESS_FAILED_KIND_RENDER_PROCESS_EXITED, COREWEBVIEW2_PROCESS_FAILED_KIND_RENDER_PROCESS_UNRESPONSIVE,
    };

    #[test]
    fn a_dead_renderer_is_reloaded() {
        assert_eq!(decide(COREWEBVIEW2_PROCESS_FAILED_KIND_RENDER_PROCESS_EXITED), Action::Reload);
    }

    #[test]
    fn a_dead_browser_process_restarts_the_app() {
        assert_eq!(decide(COREWEBVIEW2_PROCESS_FAILED_KIND_BROWSER_PROCESS_EXITED), Action::Restart);
    }

    #[test]
    fn an_unresponsive_renderer_and_other_failures_are_only_logged() {
        assert_eq!(decide(COREWEBVIEW2_PROCESS_FAILED_KIND_RENDER_PROCESS_UNRESPONSIVE), Action::Ignore);
        assert_eq!(decide(COREWEBVIEW2_PROCESS_FAILED_KIND_GPU_PROCESS_EXITED), Action::Ignore);
    }

    #[test]
    fn three_reloads_are_allowed_per_minute_and_the_fourth_is_refused() {
        let mut budget = ReloadBudget::default();
        let t0 = Instant::now();
        assert!(budget.allow(t0));
        assert!(budget.allow(t0 + Duration::from_secs(1)));
        assert!(budget.allow(t0 + Duration::from_secs(2)));
        assert!(!budget.allow(t0 + Duration::from_secs(3)));
    }

    #[test]
    fn the_budget_recovers_after_the_window() {
        let mut budget = ReloadBudget::default();
        let t0 = Instant::now();
        for i in 0..3 {
            assert!(budget.allow(t0 + Duration::from_secs(i)));
        }
        assert!(!budget.allow(t0 + Duration::from_secs(30)));
        assert!(budget.allow(t0 + Duration::from_secs(61)));
    }
}
