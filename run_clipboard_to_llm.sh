#!/bin/bash

# Source the environment activation script
source "$(dirname "$0")/activate_env.sh"

# Run the clipboard to LLM script
echo "Starting Clipboard to LLM with TTS..."
echo "Press Shift+Alt+A (Å) to read clipboard content with TTS"
echo "Press Ctrl+C to exit"
python clipboard_to_llm.py