#!/bin/bash

# This script automatically restarts run_with_env.sh when it exits
# Press Ctrl+C twice to exit: once to exit the inner script, once for this wrapper

echo "=== Auto-restart wrapper started ==="
echo "Press Ctrl+C twice to exit completely (once for the script, once for this wrapper)"

while true; do
    echo "Starting run_with_env.sh..."
    bash run_with_env.sh
    
    echo "Script exited. Restarting in 1 second..."
    sleep 1
done