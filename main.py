import subprocess
import gui  # Your existing gui.py

if __name__ == "__main__":
    subprocess.run(["python", "start_session.py"], check=True)

    gui.run_gui()  # This calls your existing GUI's entry point

    subprocess.run(["python", "end_session.py"], check=True)
    print("✅ All done - data saved to GitHub.")
