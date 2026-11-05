#!/usr/bin/env python3
"""
Tulu Transliterator Launcher
Runs the local Web Transliterator application in your default browser,
matching the functionality of https://aatana.org/transliterate/
"""

import sys
import os
import http.server
import socketserver
import webbrowser
import socket

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web") if os.path.isdir(os.path.join(BASE_DIR, "web")) else os.path.join(BASE_DIR, "kannada_tigalari_converter", "web")

def find_free_port(start_port):
    port = start_port
    while port < start_port + 100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
        port += 1
    return start_port

def main():
    if not os.path.exists(WEB_DIR):
        print(f"Error: Web directory not found at {WEB_DIR}")
        sys.exit(1)

    port = find_free_port(PORT)
    os.chdir(WEB_DIR)
    handler = http.server.SimpleHTTPRequestHandler

    print("=" * 65)
    print("  🌺 Tulu Transliterator (Unicode 16.0 & Phonetic Aatana Style)")
    print("=" * 65)
    print(f"  Web Server URL : http://localhost:{port}/index.html")
    print("  Embedded Font  : Mallige Unicode v2 (Tulu-Tigalari script)")
    print("  Controls       : Press Ctrl+C in terminal to stop.")
    print("=" * 65)

    webbrowser.open(f"http://localhost:{port}/index.html")

    with socketserver.TCPServer(("", port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    main()
