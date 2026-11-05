#!/usr/bin/env python3
"""
Tulu Transliterator & ASR Speech Studio Launcher
Runs the local Web Transliterator & Speech Studio with Apple M4 MPS acceleration.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from kannada_tigalari_converter.cli import launch_web

def main():
    port = 8080
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    launch_web(port=port)

if __name__ == "__main__":
    main()
