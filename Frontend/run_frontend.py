"""Lightweight HTTP Server for the AdaptiveStudy AI Frontend."""

import http.server
import os
import socketserver
import sys
import webbrowser

# Ensure UTF-8 or safe console encoding on Windows
if sys.platform == "win32":
    try:
        if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DEFAULT_PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class CustomHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Enable CORS headers so browser permits local development
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def log_message(self, format, *args):
        try:
            sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")
        except Exception:
            pass


def find_available_port_server(start_port=3000, max_attempts=10):
    socketserver.TCPServer.allow_reuse_address = True
    for port in range(start_port, start_port + max_attempts):
        try:
            httpd = socketserver.TCPServer(("127.0.0.1", port), CustomHTTPHandler)
            return httpd, port
        except OSError:
            continue
    for port in range(start_port, start_port + max_attempts):
        try:
            httpd = socketserver.TCPServer(("", port), CustomHTTPHandler)
            return httpd, port
        except OSError:
            continue
    raise RuntimeError(f"Could not bind to any port in range {start_port}-{start_port + max_attempts}")


if __name__ == "__main__":
    try:
        httpd, active_port = find_available_port_server(DEFAULT_PORT)
    except Exception as e:
        print(f"[ERROR] Error starting server: {e}")
        sys.exit(1)

    url = f"http://localhost:{active_port}"
    print("=" * 65)
    print("  AdaptiveStudy AI Frontend is LIVE!")
    print(f"  URL:     {url}")
    print(f"  Folder:  {DIRECTORY}")
    print("=" * 65)
    print("  Press Ctrl+C to stop the server.\n")

    # Automatically open browser
    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[STOPPED] Frontend server stopped cleanly.")
    finally:
        httpd.server_close()
