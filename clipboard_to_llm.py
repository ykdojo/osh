#!/usr/bin/env python3
"""
Clipboard to LLM

A simple tool that reads the current clipboard content when 
triggered by the keyboard shortcut Shift+Alt+A (Å).

Usage:
- Copy text to your clipboard
- Press Shift+Alt+A
- The script will display the clipboard content
- Later it will send this to an LLM
"""

import time
import subprocess
from pynput.keyboard import Controller, Key, Listener, KeyCode

def get_clipboard_text():
    """Get text from clipboard using pbpaste on macOS"""
    try:
        result = subprocess.run(['pbpaste'], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Error getting clipboard content: {e}")
        return None

def on_press(key):
    """Handle key press events"""
    # Check for special character "Å" which is produced by Shift+Alt+A on Mac
    if hasattr(key, 'char') and key.char == "Å":
        print(f"\nShortcut detected: Shift+Alt+A (Å)")
        
        # Delete the "Å" character
        keyboard = Controller()
        keyboard.press(Key.backspace)
        keyboard.release(Key.backspace)
        
        # Get clipboard content
        clipboard_content = get_clipboard_text()
        
        # Process the clipboard content
        if clipboard_content:
            print("\n=== Clipboard Content ===")
            print(clipboard_content)
            print("=== End of Clipboard Content ===")
            print(f"(Length: {len(clipboard_content)} characters)")
            
            # THIS IS WHERE WE'LL SEND TO LLM IN THE FUTURE
        else:
            print("Clipboard is empty")
            
    # Exit on Ctrl+C (correct check for macOS)
    if key == Key.ctrl_l and hasattr(key, 'vk'):
        return False
        
    return True

def main():
    """Run the clipboard monitor"""
    print("=== Clipboard to LLM ===")
    print("1. Copy text to your clipboard (Cmd+C)")
    print("2. Press Shift+Alt+A (Å) to read the clipboard")
    print("3. Press Ctrl+C to exit")
    
    # Start the keyboard listener
    with Listener(on_press=on_press) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("\nExiting...")

if __name__ == "__main__":
    main()