import os
import subprocess
import gui

def start_xvfb():
    # Force cleanup lock files (handle stale Xvfb)
    os.system("rm -f /tmp/.X99-lock")

    # Kill any existing Xvfb (best effort)
    os.system("pkill Xvfb")

    # Start fresh Xvfb
    os.system("Xvfb :99 -screen 0 1024x768x24 &")

    # Set DISPLAY for PyQt5
    os.environ["DISPLAY"] = ":99"

def initialize_database_from_github():
    subprocess.run(["python", "start_session.py"], check=True)

if __name__ == "__main__":
    start_xvfb()
    initialize_database_from_github()
    gui.run_gui()
