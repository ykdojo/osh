#!/usr/bin/env python3
"""
Clipboard to LLM with TTS

A simple tool that reads the current clipboard content when 
triggered by the keyboard shortcut Shift+Alt+A (Å).
It then converts the clipboard text to speech using Gemini TTS.

Usage:
- Copy text to your clipboard
- Press Shift+Alt+A
- The script will display the clipboard content and play it using TTS
"""

import time
import subprocess
import asyncio
import os
import threading
from pynput.keyboard import Controller, Key, Listener, KeyCode

# Import Gemini TTS functionality
from gemini_tts_test import GeminiTTS

def get_clipboard_text():
    """Get text from clipboard using pbpaste on macOS"""
    try:
        result = subprocess.run(['pbpaste'], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Error getting clipboard content: {e}")
        return None

def play_tts(text):
    """Play text using TTS in a separate thread"""
    if not text:
        return
    
    async def tts_task():
        try:
            # Create TTS instance with text from clipboard and 1.2x speed
            tts = GeminiTTS(speed_factor=1.1)
            # Override the test text with our clipboard content
            tts.test_text = text
            # Play once and exit
            await tts.run(repeat_count=1, interval=0)
        except Exception as e:
            print(f"Error playing TTS: {e}")
    
    # Run the async task in a new thread to not block main thread
    def run_async_task():
        asyncio.run(tts_task())
    
    # Start in a separate thread so we don't block keyboard listener
    tts_thread = threading.Thread(target=run_async_task)
    tts_thread.daemon = True  # Thread will exit when main program exits
    tts_thread.start()
    
    return tts_thread

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
            
            # Play the clipboard content using TTS
            print("Playing clipboard content using TTS...")
            play_tts(clipboard_content)
        else:
            print("Clipboard is empty")
            
    # Exit on Ctrl+C (correct check for macOS)
    if key == Key.ctrl_l and hasattr(key, 'vk'):
        return False
        
    return True

def main():
    """Run the clipboard monitor with TTS"""
    print("=== Clipboard to TTS ===")
    print("1. Copy text to your clipboard (Cmd+C)")
    print("2. Press Shift+Alt+A (Å) to read the clipboard and play it using TTS")
    print("3. Press Ctrl+C to exit")
    
    # Start the keyboard listener
    with Listener(on_press=on_press) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("\nExiting...")

if __name__ == "__main__":
    main()