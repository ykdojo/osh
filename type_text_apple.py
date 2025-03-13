#!/usr/bin/env python3
import subprocess
import time
import sys

def type_text_with_applescript(text):
    """Use AppleScript to type text at the current cursor position."""
    # Escape double quotes in the text
    escaped_text = text.replace('"', '\\"')
    
    # AppleScript command to type text at the current cursor position
    applescript = f'''
    tell application "System Events"
        keystroke "{escaped_text}"
    end tell
    '''
    
    # Give user time to position cursor
    print("Positioning cursor in 5 seconds...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    print("Now typing...")
    
    try:
        # Execute the AppleScript
        result = subprocess.run(['osascript', '-e', applescript], 
                               capture_output=True, text=True, check=True)
        print("AppleScript executed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"AppleScript error: {e}")
        print(f"Error output: {e.stderr}")
        print("\nERROR: This likely means your terminal needs Accessibility permissions.")
        print("Please go to System Settings > Privacy & Security > Accessibility")
        print("Add and enable your terminal application (Terminal, iTerm2, or VS Code)")
        return False

if __name__ == "__main__":
    # Text to type (can be modified as needed)
    text_to_type = "Hello, this is a test of programmatic typing!"
    
    print("This script uses AppleScript to type text at the current cursor position.")
    print("Make sure your terminal has Accessibility permissions.")
    
    # Execute typing
    success = type_text_with_applescript(text_to_type)
    
    if success:
        print("Text typing completed successfully.")
    else:
        print("Failed to type text. See error messages above.")