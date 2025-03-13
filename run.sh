#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Install portaudio with Homebrew if needed
brew install portaudio

# Install requirements
pip install -r requirements.txt

# Run the application
python app.py