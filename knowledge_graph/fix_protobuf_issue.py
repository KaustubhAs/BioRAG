#!/usr/bin/env python3
"""
Fix script for protobuf compatibility issue
Run this script to resolve the transformers/protobuf conflict
"""

import subprocess
import sys
import os

def main():
    """Fix the protobuf compatibility issue."""
    print("🔧 Fixing protobuf compatibility issue...")
    print("This will downgrade protobuf to a compatible version.")
    print()
    
    try:
        # Uninstall current protobuf
        print("1. Uninstalling current protobuf...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "protobuf", "-y"], check=True)
        
        # Install compatible protobuf version
        print("2. Installing compatible protobuf version...")
        subprocess.run([sys.executable, "-m", "pip", "install", "protobuf==3.20.3"], check=True)
        
        # Reinstall transformers with compatible version
        print("3. Reinstalling transformers...")
        subprocess.run([sys.executable, "-m", "pip", "install", "transformers==4.35.2"], check=True)
        
        # Reinstall sentence-transformers
        print("4. Reinstalling sentence-transformers...")
        subprocess.run([sys.executable, "-m", "pip", "install", "sentence-transformers==2.2.2"], check=True)
        
        print()
        print("✅ Protobuf issue fixed successfully!")
        print("You can now run the Biomedical Assistant UI.")
        print()
        print("To start the UI:")
        print("  python run_ui.py")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during installation: {e}")
        print("Please try running the commands manually:")
        print("  pip uninstall protobuf -y")
        print("  pip install protobuf==3.20.3")
        print("  pip install transformers==4.35.2")
        print("  pip install sentence-transformers==2.2.2")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 