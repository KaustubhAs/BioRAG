#!/bin/bash

echo "🏥 Starting Biomedical Assistant UI..."
echo ""
echo "The web interface will open in your browser."
echo "Press Ctrl+C to stop the server."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    exit 1
fi

# Run the UI
python3 run_ui.py 