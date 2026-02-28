#!/usr/bin/env python3
"""
Biomedical Assistant - Streamlit UI Launcher (run from repo root: python app/run_ui.py)
"""

import subprocess
import sys
import os


def main():
    """Launch the Streamlit UI."""
    print("Starting Biomedical Assistant UI...")
    print("The web interface will open in your browser.")
    print("Press Ctrl+C to stop the server.")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "streamlit_app.py")
    project_root = os.path.dirname(script_dir)

    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", app_path,
             "--server.port", "8501", "--server.address", "localhost"],
            cwd=project_root
        )
    except KeyboardInterrupt:
        print("\nBiomedical Assistant UI stopped.")
    except Exception as e:
        print(f"Error starting UI: {e}")
        print("Make sure you have installed the requirements:")
        print("  pip install -r requirements.txt")


if __name__ == "__main__":
    main()
