#!/bin/bash

# Script to launch both typing and reading metrics web dashboards in parallel
# This starts the typing metrics server on port 5050 and reading metrics on port 5051

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

# Start typing metrics web dashboard in background
start_typing_dashboard() {
    echo "Starting typing metrics web dashboard on http://127.0.0.1:5050/"
    python typing_metrics_web.py &
    typing_pid=$!
    sleep 0.5
    open_browser "http://127.0.0.1:5050/"
    echo "Typing metrics dashboard started with PID: $typing_pid"
    return $typing_pid
}

# Start reading metrics web dashboard in background
start_reading_dashboard() {
    echo "Starting reading metrics web dashboard on http://127.0.0.1:5051/reading"
    python reading_metrics_web.py -p 5051 &
    reading_pid=$!
    # Don't automatically open the reading dashboard in browser
    echo "Reading metrics dashboard started with PID: $reading_pid"
    return $reading_pid
}

# Start both dashboards
echo "Launching both dashboards..."
start_typing_dashboard
typing_pid=$?
start_reading_dashboard
reading_pid=$?

echo "Both dashboards are running"
echo "Press Ctrl+C to stop all servers"

# Wait for user to press Ctrl+C
trap "kill $typing_pid $reading_pid 2>/dev/null; echo 'Shutting down dashboards...'" INT TERM
wait

# Deactivate virtual environment on exit
if type deactivate &>/dev/null; then
    deactivate
fi