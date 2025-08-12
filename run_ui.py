#!/usr/bin/env python3
"""
Biomedical Assistant - Streamlit UI Launcher
Run this script to start the web interface
"""

import subprocess
import sys
import os


def main():
    """Launch the Streamlit UI."""
    print("🏥 Starting Biomedical Assistant UI...")
    print("The web interface will open in your browser.")
    print("Press Ctrl+C to stop the server.")

    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the Streamlit app
    app_path = os.path.join(script_dir, "app", "streamlit_app.py")

    try:
        # Run Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port", "8501", "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Biomedical Assistant UI stopped.")
    except Exception as e:
        print(f"❌ Error starting UI: {e}")
        print("Make sure you have installed the requirements:")
        print("pip install -r requirements.txt")


if __name__ == "__main__":
    main()
