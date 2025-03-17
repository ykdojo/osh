#!/bin/bash

# Source the virtual environment directly
source "$(dirname "$0")/venv/bin/activate"

# Remind user about requirements
echo "Reminder: Install requirements with 'pip install -r requirements.txt' if needed"

# Check for portaudio
if command -v brew &> /dev/null && ! brew list portaudio &> /dev/null; then
    echo "portaudio not found, but may be needed for PyAudio. Install with 'brew install portaudio' if you encounter issues."
fi

# Run the terminal video voice recorder
echo "Starting terminal video voice recorder..."
python terminal_video_voice_recorder.py