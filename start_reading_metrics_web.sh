#!/bin/bash

# Script to launch the reading metrics web dashboard
# This starts the web server on port 5051

# Determine the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate the virtual environment if it exists
if [ -f "./venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source ./venv/bin/activate
elif [ -f "./activate_env.sh" ]; then
    echo "Activating environment..."
    source ./activate_env.sh
fi

# Function to open browser based on the operating system
open_browser() {
    url=$1
    case "$(uname -s)" in
        Darwin*)  # macOS
            open "$url"
            ;;
        Linux*)   # Linux
            if command -v xdg-open > /dev/null; then
                xdg-open "$url"
            elif command -v gnome-open > /dev/null; then
                gnome-open "$url"
            else
                echo "Could not detect the web browser to use."
            fi
            ;;
        CYGWIN*|MINGW*|MSYS*)  # Windows
            start "$url"
            ;;
        *)
            echo "Unknown operating system. Please open $url manually."
            ;;
    esac
}

# Launch the reading metrics web dashboard
echo "Starting reading metrics web dashboard on http://127.0.0.1:5051/"
echo "Press Ctrl+C to stop the server"

# Open the browser after a minimal delay to ensure the server has started
(sleep 0.5 && open_browser "http://127.0.0.1:5051/reading") &

# Start the server
python reading_metrics_web.py -p 5051

# Deactivate virtual environment on exit
if type deactivate &>/dev/null; then
    deactivate
fi