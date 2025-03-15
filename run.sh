#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Install portaudio with Homebrew if needed
# brew install portaudio

# Remind user about requirements
echo "Reminder: Install requirements with 'pip install -r requirements.txt' if needed"

# Run the menu system
echo "Starting menu system..."
python menu_system.py