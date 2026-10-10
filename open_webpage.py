"""
open_webpage.py
===============
Helper script to immediately launch 'index.html' in your default web browser.

Usage:
    python open_webpage.py
    
Or simply double-click 'index.html' directly in Windows File Explorer!
"""

import os
import webbrowser

def main():
    html_path = os.path.abspath("index.html")
    if not os.path.exists(html_path):
        print("Error: 'index.html' not found. Please run 'python build_index_html.py' first.")
        return

    print("=" * 60)
    print("🌐 Launching Network Load Statistical Analyzer...")
    print(f"File Path: {html_path}")
    print("Zero server commands required. Opening in your default browser...")
    print("=" * 60)
    
    webbrowser.open(f"file://{html_path}")

if __name__ == "__main__":
    main()
