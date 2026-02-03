use std::sync::Mutex;
use tauri::Manager;
use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::{CommandChild, CommandEvent};

struct BackendPort(Mutex<Option<u16>>);
struct BackendChild(Mutex<Option<CommandChild>>);

#[tauri::command]
fn get_backend_port(state: tauri::State<BackendPort>) -> Option<u16> {
    state.0.lock().unwrap().clone()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .manage(BackendPort(Mutex::new(None)))
        .manage(BackendChild(Mutex::new(None)))
        .setup(|app| {
            let app_handle = app.handle().clone();

            // Spawn the backend sidecar
            let sidecar_command = app.shell().sidecar("backend").unwrap();
            let (mut rx, child) = sidecar_command.spawn().expect("Failed to spawn sidecar");

            // Store child handle so we can kill it on exit
            let state = app.state::<BackendChild>();
            *state.0.lock().unwrap() = Some(child);

            // Listen for output from sidecar to get the port
            let handle = app_handle.clone();
            tauri::async_runtime::spawn(async move {
                while let Some(event) = rx.recv().await {
                    match event {
                        CommandEvent::Stdout(line) => {
                            let line_str = String::from_utf8_lossy(&line);
                            if line_str.starts_with("PORT:") {
                                if let Ok(port) = line_str.trim_start_matches("PORT:").trim().parse::<u16>() {
                                    let state = handle.state::<BackendPort>();
                                    *state.0.lock().unwrap() = Some(port);
                                    println!("Backend started on port: {}", port);
                                }
                            } else {
                                println!("Backend: {}", line_str);
                            }
                        }
                        CommandEvent::Stderr(line) => {
                            eprintln!("Backend error: {}", String::from_utf8_lossy(&line));
                        }
                        CommandEvent::Error(error) => {
                            eprintln!("Backend command error: {}", error);
                        }
                        CommandEvent::Terminated(status) => {
                            println!("Backend terminated with status: {:?}", status);
                        }
                        _ => {}
                    }
                }
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_backend_port])
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|app, event| {
            if let tauri::RunEvent::Exit = event {
                // Kill the backend sidecar on app exit
                let child = app.state::<BackendChild>().0.lock().unwrap().take();
                if let Some(child) = child {
                    let _ = child.kill();
                    println!("Backend sidecar killed");
                }
            }
        });
}
