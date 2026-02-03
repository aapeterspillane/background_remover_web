"""Sidecar entry point for Tauri desktop app."""

import os
import signal
import socket
import sys


def find_available_port() -> int:
    """Find an available port by binding to port 0."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def setup_bundled_model_path():
    """Set up the model path for PyInstaller bundled executable."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        bundle_dir = sys._MEIPASS
        model_dir = os.path.join(bundle_dir, 'u2net_models')

        print(f"DEBUG: Bundle dir: {bundle_dir}", flush=True)
        print(f"DEBUG: Model dir: {model_dir}", flush=True)
        print(f"DEBUG: Model dir exists: {os.path.exists(model_dir)}", flush=True)

        if os.path.exists(model_dir):
            # List contents of model dir
            contents = os.listdir(model_dir)
            print(f"DEBUG: Model dir contents: {contents}", flush=True)
            os.environ['U2NET_HOME'] = model_dir
            print(f"DEBUG: Set U2NET_HOME to: {model_dir}", flush=True)
        else:
            print(f"DEBUG: Model dir does not exist!", flush=True)
            # List bundle dir contents to see what's there
            if os.path.exists(bundle_dir):
                print(f"DEBUG: Bundle dir contents: {os.listdir(bundle_dir)[:20]}...", flush=True)


def main():
    """Main entry point for the sidecar."""
    import uvicorn

    # Set up bundled model path if running as frozen executable
    setup_bundled_model_path()

    # Mark as running in sidecar mode
    os.environ['SIDECAR_MODE'] = '1'

    # Find available port
    port = find_available_port()

    # Print port for Tauri to parse (must be before any other output)
    print(f"PORT:{port}", flush=True)

    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print("Shutting down sidecar...", flush=True)
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Start uvicorn server
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )


if __name__ == "__main__":
    main()
