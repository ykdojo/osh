#!/usr/bin/env python3
import time
import sys
import platform
import traceback
from pynput.keyboard import Controller, Key, Listener

# Check if we're on macOS
is_macos = platform.system() == 'Darwin'
print(f"Running on: {platform.system()} {platform.release()}")

# For debugging key events
key_events = []

def on_press(key):
    """Monitor key presses for debugging"""
    try:
        key_events.append(f"Press: {key}")
    except:
        pass

def on_release(key):
    """Monitor key releases for debugging"""
    try:
        key_events.append(f"Release: {key}")
    except:
        pass

def test_permission():
    """Test if we have accessibility permissions by trying to press and release a harmless key."""
    try:
        print("Initializing keyboard controller...")
        keyboard = Controller()
        
        # Try to press and immediately release a modifier key that won't have any effect
        print("Testing with Alt key press/release...")
        keyboard.press(Key.alt)
        time.sleep(0.1)
        keyboard.release(Key.alt)
        return True
    except Exception as e:
        print(f"Permission test failed: {e}")
        traceback.print_exc()
        return False

def type_text(text):
    """Type the given text at the current cursor position all at once after a wait."""
    try:
        keyboard = Controller()
        
        # Give user time to position cursor where they want the text
        print("\nPositioning cursor in 3 seconds...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        print("Now typing...")
        
        # Print what we're going to type for debugging
        print(f"About to type: '{text}'")
        
        # Type the entire text by writing it to the clipboard and pasting it
        # This approach avoids potential issues with the keyboard.type() method
        try:
            import pyperclip
            # Save original clipboard content
            original_clipboard = pyperclip.paste()
            
            # Copy our text to clipboard
            pyperclip.copy(text)
            
            # Paste using keyboard shortcut
            with keyboard.pressed(Key.ctrl if not is_macos else Key.cmd):
                keyboard.press('v')
                keyboard.release('v')
                
            # Wait a moment before restoring clipboard
            time.sleep(0.5)
            
            # Restore original clipboard content
            pyperclip.copy(original_clipboard)
            
        except ImportError:
            print("pyperclip module not found. Falling back to manual typing.")
            # Manual typing as fallback - no delays between characters
            for char in text:
                keyboard.press(char)
                keyboard.release(char)
        
        # Print debug info about registered keystrokes
        if key_events:
            print("\nDebug - Recorded key events:")
            for event in key_events[-10:]:  # Show last 10 events
                print(f"  {event}")
        
        return True
    except Exception as e:
        print(f"Error while typing: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # First check if we have permission
    print("Testing accessibility permissions...")
    permission_ok = test_permission()
    
    if not permission_ok:
        print("\nERROR: Missing accessibility permissions!")
        print("Please go to System Settings > Privacy & Security > Accessibility")
        print("Add and enable your terminal application (Terminal, iTerm2, or VS Code)")
        sys.exit(1)
    
    print("Accessibility permissions seem OK")
    
    # Start key listener for debugging
    print("Starting key event listener for debugging...")
    listener = Listener(on_press=on_press, on_release=on_release)
    listener.start()
    
    # Text to type (can be modified as needed)
    text_to_type = "Hello, this is a test of programmatic typing!"
    
    # Execute typing
    print("\nPreparing to type text. Please click where you want to type...")
    success = type_text(text_to_type)
    
    if success:
        print("\nText typing completed successfully.")
    else:
        print("\nFailed to type text.")
    
    # Additional troubleshooting info for macOS
    if is_macos:
        print("\nMacOS Troubleshooting:")
        print("1. Ensure terminal has Accessibility permission in System Settings")
        print("2. Try running the script with 'sudo' for full permissions")
        print("3. Make sure the target application allows keyboard input")
    
    # Stop the key listener
    listener.stop()
    time.sleep(0.5)  # Give time for listener to stop cleanly