import subprocess
import gui  # Your existing gui.py

def start_xvfb():
    subprocess.Popen(["Xvfb", ":99", "-screen", "0", "1024x768x24"])
    print("✅ Xvfb started (virtual display running).")

def stop_xvfb():
    subprocess.run(["pkill", "Xvfb"])
    print("✅ Xvfb stopped.")

if __name__ == "__main__":

    start_xvfb()
    
    subprocess.run(["python", "start_session.py"], check=True)

    gui.run_gui()  # This calls your existing GUI's entry point

    subprocess.run(["python", "end_session.py"], check=True)

    stop_xvfb()
    
    print("✅ All done - data saved to GitHub.")
