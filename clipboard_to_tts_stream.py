#!/usr/bin/env python3
"""
Clipboard to TTS Stream

A simple tool that reads the current clipboard content when 
triggered by the keyboard shortcut Shift+Alt+A (Å).
It then converts the clipboard text to speech using Gemini TTS streaming.

Usage:
- Copy text to your clipboard
- Press Shift+Alt+A
- The script will display the clipboard content and play it using streaming TTS
"""

import time
import subprocess
import threading
import os
from pynput.keyboard import Controller, Key, Listener, KeyCode

# Core imports for audio
import pyaudio
import base64
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Please install the required packages: pip install google-generativeai python-dotenv pyaudio")
    import sys
    sys.exit(1)

# Audio constants
SAMPLE_RATE = 24000
CHANNELS = 1
FORMAT = pyaudio.paInt16  # 16-bit audio format

def get_clipboard_text():
    """Get text from clipboard using pbpaste on macOS"""
    try:
        result = subprocess.run(['pbpaste'], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Error getting clipboard content: {e}")
        return None

def play_audio(audio_data, sample_rate=SAMPLE_RATE, channels=CHANNELS):
    """Play audio data directly without saving to file"""
    p = pyaudio.PyAudio()
    
    # Open stream
    stream = p.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=sample_rate,
        output=True
    )
    
    # Play audio
    print("Playing audio...")
    stream.write(audio_data)
    
    # Cleanup
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Audio playback complete")

def generate_and_play_tts(text):
    """Generate and play TTS for the given text"""
    if not text:
        print("No text provided")
        return
    
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Gemini API key not found. Please add it to .env file")
        import sys
        sys.exit(1)
    
    # Initialize client
    client = genai.Client(api_key=api_key)
    
    # Model configuration
    model = "gemini-2.0-flash-exp-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"""Read out loud the following text. No need to say yes, okay, and stuff like that. 
Just focus on reading it out loud by itself with nothing else. 
IMPORTANT: Skip all preambles like 'okay' or 'I'll read this'. ONLY read exactly these words: {text}"""),
            ],
        ),
    ]
    
    # Configure TTS settings
    generate_content_config = types.GenerateContentConfig(
        response_modalities=["audio"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
            )
        ),
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_CIVIC_INTEGRITY",
                threshold="OFF",
            ),
        ],
        response_mime_type="text/plain",
    )

    print("Generating TTS content with Gemini...")
    
    try:
        # Stream the response
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
                continue
                
            if chunk.candidates[0].content.parts[0].inline_data:
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                audio_data = inline_data.data
                
                print(f"Received audio data chunk of mime type: {inline_data.mime_type}")
                
                # Play the audio directly
                play_audio(audio_data)
            elif hasattr(chunk, 'text') and chunk.text:
                print(chunk.text)
                
    except Exception as e:
        print(f"Error: {e}")

def play_tts(text):
    """Play text using TTS in a separate thread"""
    if not text:
        return
    
    # Run in a new thread to not block main thread
    def run_tts_task():
        generate_and_play_tts(text)
    
    # Start in a separate thread so we don't block keyboard listener
    tts_thread = threading.Thread(target=run_tts_task)
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
            print("Playing clipboard content using streaming TTS...")
            play_tts(clipboard_content)
        else:
            print("Clipboard is empty")
            
    # Exit on Ctrl+C (correct check for macOS)
    if key == Key.ctrl_l and hasattr(key, 'vk'):
        return False
        
    return True

def main():
    """Run the clipboard monitor with TTS"""
    print("=== Clipboard to Streaming TTS ===")
    print("1. Copy text to your clipboard (Cmd+C)")
    print("2. Press Shift+Alt+A (Å) to read the clipboard and play it using TTS")
    print("3. Press Ctrl+C to exit")
    
    # Create the keyboard listener (not starting it yet)
    listener = None
    
    try:
        # Start the keyboard listener
        listener = Listener(on_press=on_press)
        listener.start()
        
        # Keep the main thread alive
        while listener.is_alive():
            listener.join(0.1)  # Check every 0.1 seconds if listener is alive
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Ensure listener is stopped even if an exception occurs
        if listener and listener.is_alive():
            print("Cleaning up keyboard listener...")
            listener.stop()
            time.sleep(0.1)  # Give a moment for the listener to stop cleanly

if __name__ == "__main__":
    main()