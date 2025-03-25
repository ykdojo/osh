#!/usr/bin/env python3
import time
import sys
import platform
import traceback
from pynput.keyboard import Controller, Key, Listener

# Check if we're on macOS
is_macos = platform.system() == 'Darwin'
# Only print system info when running the file directly, not when imported
if __name__ == "__main__":
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

def test_permission(verbose=False):
    """Test if we have accessibility permissions by trying to press and release a harmless key."""
    try:
        if verbose:
            print("Initializing keyboard controller...")
        keyboard = Controller()
        
        # Try to press and immediately release a modifier key that won't have any effect
        if verbose:
            print("Testing with Alt key press/release...")
        keyboard.press(Key.alt)
        time.sleep(0.1)
        keyboard.release(Key.alt)
        return True
    except Exception as e:
        if verbose:
            print(f"Permission test failed: {e}")
            traceback.print_exc()
        return False

def type_text(text, countdown=False, verbose=False):
    """
    Type the given text at the current cursor position character by character.
    
    Args:
        text (str): The text to type
        countdown (bool): Whether to show a countdown before typing (default: False)
        verbose (bool): Whether to print debug information (default: False)
    """
    try:
        keyboard = Controller()
        
        # Give user time to position cursor if countdown is enabled
        if countdown:
            if verbose:
                print("\nPositioning cursor in 3 seconds...")
            for i in range(3, 0, -1):
                if verbose:
                    print(f"{i}...")
                time.sleep(1)
        
        if verbose:
            print("Now typing...")
            print(f"About to type: '{text}'")
        
        # Type directly character by character
        # This avoids clipboard issues with images or other non-text content
        for char in text:
            # Handle special characters
            if char == '\n':
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)
            elif char == '\t':
                keyboard.press(Key.tab)
                keyboard.release(Key.tab)
            else:
                keyboard.press(char)
                keyboard.release(char)
            
            # Small delay to prevent missed keystrokes on some systems
            # Adjust this value if typing is too slow or missing characters
            time.sleep(0.01)
        
        # Print debug info about registered keystrokes if verbose
        if verbose and key_events:
            print("\nDebug - Recorded key events:")
            for event in key_events[-10:]:  # Show last 10 events
                print(f"  {event}")
        
        return True
    except Exception as e:
        if verbose:
            print(f"Error while typing: {e}")
            traceback.print_exc()
        return False

if __name__ == "__main__":
    # When running the script directly, we want verbose output
    verbose_mode = True
    
    print(f"Running on: {platform.system()} {platform.release()}")
    
    # First check if we have permission
    print("Testing accessibility permissions...")
    permission_ok = test_permission(verbose=verbose_mode)
    
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
    text_to_type = "Hello, this is a test of programmatic typing!\nIt handles special characters: !@#$%^&*()\nAnd has\ttabs and\nnewlines too."
    
    # Execute typing
    print("\nPreparing to type text. Please click where you want to type...")
    success = type_text(text_to_type, countdown=True, verbose=verbose_mode)
    
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