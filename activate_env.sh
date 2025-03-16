#!/bin/bash

# Check if script is being sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: This script must be sourced, not executed."
    echo "Use: source activate_env.sh"
    exit 1
fi

# Activate the virtual environment
source venv/bin/activate

# Remind user about requirements
echo "Reminder: Install requirements with 'pip install -r requirements.txt' if needed"

# Install portaudio with Homebrew if needed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found, skipping portaudio check"
else
    if ! brew list portaudio &> /dev/null; then
        echo "portaudio not found, but may be needed for PyAudio. Install with 'brew install portaudio' if you encounter issues."
    fi
fi
