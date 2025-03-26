#!/usr/bin/env python3
"""
Clipboard handler for preserving and restoring clipboard content,
including both text and images.
"""

import time
import platform
import traceback
from pynput.keyboard import Controller, Key
import copykitten

# Check if we're on macOS
is_macos = platform.system() == 'Darwin'

class ClipboardHandler:
    """
    Handles saving and restoring clipboard content,
    including support for both text and images.
    """
    
    def __init__(self, verbose=False):
        """Initialize the clipboard handler"""
        self.verbose = verbose
        self.original_text = None
        self.original_image = None
        self.has_text = False
        self.has_image = False
        
    def save_clipboard_content(self):
        """
        Save the current clipboard content (both text and image if available)
        """
        if self.verbose:
            print("Saving clipboard content...")
        
        # Try to get text content
        try:
            self.original_text = copykitten.paste()
            if self.original_text:
                self.has_text = True
                if self.verbose:
                    print(f"Saved clipboard text: '{self.original_text[:50]}...' (truncated)" 
                           if len(self.original_text) > 50 
                           else f"Saved clipboard text: '{self.original_text}'")
        except Exception as e:
            if self.verbose:
                print(f"No text in clipboard: {e}")
            self.original_text = None
            self.has_text = False
        
        # Try to get image content
        try:
            self.original_image = copykitten.paste_image()
            if self.original_image:
                self.has_image = True
                if self.verbose:
                    print(f"Saved clipboard image (data size: {len(self.original_image)} bytes)")
        except Exception as e:
            if self.verbose:
                print(f"No image in clipboard: {e}")
            self.original_image = None
            self.has_image = False
            
        # Summary
        if self.verbose:
            if not self.has_text and not self.has_image:
                print("Clipboard appears to be empty")
            elif self.has_text and self.has_image:
                print("Clipboard contains both text and image")
            elif self.has_text:
                print("Clipboard contains only text")
            else:
                print("Clipboard contains only an image")
    
    def restore_clipboard_content(self):
        """
        Restore the original clipboard content
        """
        if self.verbose:
            print("Restoring clipboard content...")
        
        # First check if we have an image to restore
        if self.has_image and self.original_image:
            try:
                if self.verbose:
                    print("Attempting to restore image content...")
                # There's no direct way to restore image with copykitten without
                # dimensions and format, so we'll try using the stored binary data
                
                # On macOS, we might need a system-level command if copykitten fails
                if is_macos:
                    self._restore_macos_image()
                else:
                    # On other platforms, best effort with copykitten
                    copykitten.copy(self.original_text if self.has_text else "")
            except Exception as e:
                if self.verbose:
                    print(f"Failed to restore image: {e}")
        
        # If we only have text, or if image restore failed, restore text
        elif self.has_text and self.original_text:
            try:
                if self.verbose:
                    print("Restoring text content...")
                copykitten.copy(self.original_text)
            except Exception as e:
                if self.verbose:
                    print(f"Failed to restore text: {e}")
        
        # If we have nothing, clear the clipboard
        else:
            try:
                if self.verbose:
                    print("Clearing clipboard...")
                copykitten.clear()
            except Exception as e:
                if self.verbose:
                    print(f"Failed to clear clipboard: {e}")
    
    def _restore_macos_image(self):
        """
        Special handling for macOS image clipboard restoration.
        On macOS, for image restoration we need to use a different approach.
        For this prototype, we'll just restore text and note the limitation.
        """
        if self.verbose:
            print("Note: Image restoration on macOS limited to text content only.")
        
        # Fall back to restoring text if we have it
        if self.has_text and self.original_text:
            copykitten.copy(self.original_text)
        else:
            copykitten.clear()

def type_text_with_clipboard(text, countdown=False, verbose=False):
    """
    Type the given text at the current cursor position using clipboard.
    Preserves original clipboard content (text only).
    
    Args:
        text (str): The text to type
        countdown (bool): Whether to show a countdown before typing (default: False)
        verbose (bool): Whether to print debug information (default: False)
    """
    try:
        keyboard = Controller()
        
        # Create clipboard handler and save original content
        clipboard = ClipboardHandler(verbose=verbose)
        clipboard.save_clipboard_content()
        
        # Give user time to position cursor if countdown is enabled
        if countdown:
            if verbose:
                print("\nPositioning cursor in 3 seconds...")
            for i in range(3, 0, -1):
                if verbose:
                    print(f"{i}...")
                time.sleep(1)
        
        if verbose:
            print("Now pasting text via clipboard...")
            print(f"About to paste: '{text}'")
        
        # Copy text to clipboard
        copykitten.copy(text)
        
        # Paste using keyboard shortcut
        if is_macos:
            keyboard.press(Key.cmd)
            keyboard.press('v')
            keyboard.release('v')
            keyboard.release(Key.cmd)
        else:
            keyboard.press(Key.ctrl)
            keyboard.press('v')
            keyboard.release('v')
            keyboard.release(Key.ctrl)
        
        # Small delay to ensure paste completes
        time.sleep(0.1)
        
        # Restore original clipboard content
        clipboard.restore_clipboard_content()
        
        return True
    except Exception as e:
        if verbose:
            print(f"Error while pasting: {e}")
            traceback.print_exc()
        return False

# Test the module if run directly
if __name__ == "__main__":
    print(f"Running on: {platform.system()} {platform.release()}")
    
    # Test the clipboard handler
    clipboard = ClipboardHandler(verbose=True)
    
    # First save the current clipboard
    print("\n=== Testing Clipboard Save ===")
    clipboard.save_clipboard_content()
    
    # Test typing text with clipboard
    print("\n=== Testing Text Pasting ===")
    type_text_with_clipboard(
        "This is a test of the clipboard handler.\nIt preserves your original clipboard content!",
        countdown=True,
        verbose=True
    )
    
    print("\nTest completed.")