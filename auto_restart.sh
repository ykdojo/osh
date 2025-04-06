#!/bin/bash

# This script automatically restarts run_with_env.sh when it exits due to errors
# Only Ctrl+C will completely terminate the process

echo "=== Auto-restart wrapper started ==="
echo "Press Ctrl+C to exit completely"

while true; do
    echo "Starting run_with_env.sh..."
    bash run_with_env.sh
    
    EXIT_CODE=$?
    
    # If exit was due to Ctrl+C (exit code 130), exit the wrapper too
    if [ $EXIT_CODE -eq 130 ]; then
        echo "Detected Ctrl+C. Exiting wrapper."
        exit 130
    fi
    
    echo "Script exited with code $EXIT_CODE. Restarting in 3 seconds..."
    sleep 3
done