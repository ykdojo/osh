#!/bin/bash

# Script to launch the typing metrics web dashboard
# This starts the web server on port 5050

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

# Launch the typing metrics web dashboard
echo "Starting typing metrics web dashboard on http://127.0.0.1:5050/"
echo "Press Ctrl+C to stop the server"
python typing_metrics_web.py

# Deactivate virtual environment on exit
if type deactivate &>/dev/null; then
    deactivate
fi