#!/usr/bin/env python3
"""
Test script for automatically detecting and using selected text,
then sending it to an LLM (to be implemented).
The script:
1. Saves the original clipboard content
2. Simulates Cmd+C to copy the current selection
3. Reads the selection from clipboard
4. Performs operations (will send to LLM later)
5. Restores the original clipboard content
"""

import time
import platform
import subprocess
import traceback
from pynput.keyboard import Controller, Key

# Import existing clipboard handler
from clipboard_handler import ClipboardHandler

def get_clipboard_text():
    """Get text from clipboard using pbpaste on macOS"""
    try:
        if platform.system() == 'Darwin':  # macOS
            result = subprocess.run(['pbpaste'], capture_output=True, text=True)
            return result.stdout
        else:
            # For other platforms, you'd need different approaches
            print("Currently only supporting macOS")
            return None
    except Exception as e:
        print(f"Error getting clipboard content: {e}")
        return None

def copy_current_selection():
    """Send Cmd+C to copy the current selection"""
    keyboard = Controller()
    
    # Send Cmd+C to copy selection
    keyboard.press(Key.cmd)
    keyboard.press('c')
    keyboard.release('c')
    keyboard.release(Key.cmd)
    
    # Small delay to ensure copy completes
    time.sleep(0.1)

def main():
    """Main function to automatically get selection and test operations"""
    print("\n=== Clipboard LLM Integration Test ===")
    
    # Countdown to give user time to select text
    print("\nSelect text with your mouse (but don't copy it)")
    print("Starting in:")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    print("Starting now!\n")
    
    # Step 1: Save current clipboard
    print("\n1. Saving current clipboard content...")
    clipboard = ClipboardHandler(verbose=True)
    clipboard.save_clipboard_content()
    
    original_content = get_clipboard_text()
    print(f"Original clipboard content: {repr(original_content)}")
    
    # Step 2: Simulate Cmd+C to copy the current selection
    print("\n2. Auto-copying current selection (Cmd+C)...")
    copy_current_selection()
    
    # Step 3: Get the newly copied selection
    print("\n3. Reading selection from clipboard...")
    selection_content = get_clipboard_text()
    print(f"Selected text: {repr(selection_content)}")
    
    # Step 4: Simulate doing something with the selection
    print("\n4. Simulating operation on selected text...")
    if selection_content:
        print(f"Selected text has {len(selection_content)} characters")
        print(f"First 50 chars: {repr(selection_content[:50])}")
        # Here's where we'd send to an LLM in the future
    else:
        print("No text was selected")
    
    # Step 5: Restore original clipboard
    print("\n5. Restoring original clipboard content...")
    clipboard.restore_clipboard_content()
    
    # Verify restoration
    time.sleep(0.5)  # Short delay to ensure clipboard updates
    restored_content = get_clipboard_text()
    print(f"Restored clipboard: {repr(restored_content)}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    main()