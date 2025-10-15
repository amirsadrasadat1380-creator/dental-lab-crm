import subprocess
import os
import sys
import webbrowser
import time
import threading

def launch_streamlit():
    """Launch the Streamlit app in a separate process."""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Change to the script's directory (important for relative paths)
        os.chdir(script_dir)
        
        # Launch Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app-V1.py",
            "--server.port", "8501",  # Optional: specify a port
            "--server.headless", "false"  # Open browser automatically
        ])
    except Exception as e:
        print(f"Error launching app: {e}")

def open_browser():
    """Open the app in the default browser after a short delay."""
    time.sleep(3)  # Wait for Streamlit to start
    webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    print("🚀 Launching CRM Lab...")
    print("Browser will open shortly. Keep this window open while using the app.")
    
    # Launch Streamlit in a background thread
    app_thread = threading.Thread(target=launch_streamlit)
    app_thread.daemon = True  # Dies when main program dies
    app_thread.start()
    
    # Open browser in main thread
    open_browser()
    
    # Keep the launcher alive while Streamlit runs
    try:
        # Don't join the thread - let it run independently
        app_thread.join(timeout=0.1)  # Check every 0.1 seconds
        while app_thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        # The subprocess will be killed when this script exits