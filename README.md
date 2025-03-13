# OSH Project

A Textual-based Python application with Gemini AI integration.

## Features

- Voice recording functionality
- Global keyboard shortcuts (using pynput)
- Text typing automation scripts

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   ./run.sh
   ```

## Automated Typing Scripts

This project includes two scripts for automated typing at the cursor position:

### 1. Python with pynput (`type_text.py`)

Uses the pynput library to simulate keyboard input. For this script to work:

- Grant Accessibility permissions to your terminal application (Terminal, iTerm2, or VS Code)
- System Settings → Privacy & Security → Accessibility → Add your terminal app

### 2. Python with AppleScript (`type_text_apple.py`)

Uses macOS AppleScript to type text. For this script to work:

- Grant Accessibility permissions to your terminal application
- System Settings → Privacy & Security → Accessibility → Add your terminal app

## Important Permission Notes

Both typing automation scripts require explicit permission in macOS security settings. Without these permissions, the scripts will run without errors but will not actually type text in other applications.

To set up permissions:
1. Go to System Settings → Privacy & Security → Accessibility
2. Click the "+" button
3. Navigate to your terminal application (Terminal, iTerm2, VS Code)
4. Make sure the checkbox next to the application is checked
5. Restart your terminal application after granting permissions