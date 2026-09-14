use std::net::TcpStream;
use std::time::{Duration, Instant};

use tauri::{AppHandle, Manager, WebviewUrl, WebviewWindowBuilder};
use tauri_plugin_shell::process::CommandChild;
use tauri_plugin_shell::{process::CommandEvent, ShellExt};

#[allow(dead_code)]
struct BackendSidecar(CommandChild);

const HOST: &str = "127.0.0.1";
const PORT: u16 = 8785;
const SESSIONS_URL: &str = "http://127.0.0.1:8785/sessions/";

fn wait_for_loopback(timeout: Duration) -> bool {
    let deadline = Instant::now() + timeout;
    while Instant::now() < deadline {
        if TcpStream::connect((HOST, PORT)).is_ok() {
            return true;
        }
        std::thread::sleep(Duration::from_millis(50));
    }
    false
}

fn spawn_backend(app: &AppHandle) -> CommandChild {
    let sidecar = app
        .shell()
        .sidecar("sessions-app-sidecar")
        .expect("sessions-app-sidecar must be declared in tauri.conf.json externalBin")
        .args([
            "serve",
            "--host",
            HOST,
            "--port",
            &PORT.to_string(),
        ]);
    let (mut rx, child) = sidecar.spawn().expect("sidecar spawn failed");
    tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
            if let CommandEvent::Terminated(payload) = event {
                log::warn!("sessions-app sidecar exited: {:?}", payload);
                break;
            }
        }
    });
    child
}

fn open_main_window(app: &AppHandle) -> tauri::Result<()> {
    if app.get_webview_window("main").is_some() {
        return Ok(());
    }
    let url = tauri::Url::parse(SESSIONS_URL).expect("sessions shell URL must parse");
    WebviewWindowBuilder::new(app, "main", WebviewUrl::External(url))
        .title("COSMOS Sessions")
        .inner_size(1280.0, 860.0)
        .build()?;
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_single_instance::init(|app, _argv, _cwd| {
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.unminimize();
                let _ = window.show();
                let _ = window.set_focus();
            } else {
                let _ = open_main_window(app);
            }
        }))
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            let handle = app.handle().clone();
            let child = spawn_backend(&handle);
            app.manage(BackendSidecar(child));
            if !wait_for_loopback(Duration::from_secs(15)) {
                log::error!(
                    "sessions-app backend did not bind {HOST}:{PORT} — loopback serve refused or slow start"
                );
            }
            open_main_window(&handle)?;
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
