#!/usr/bin/env python3
import argparse
import asyncio
import traceback
import os
import sys

import pyaudio
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Please install the required packages: pip install google-generativeai python-dotenv")
    sys.exit(1)

# Audio constants
FORMAT = pyaudio.paInt16
CHANNELS = 1
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

# Model settings
MODEL = "models/gemini-2.0-flash-exp"

class GeminiTTS:
    def __init__(self, api_key=None):
        # Load environment variables from .env file
        load_dotenv()
        
        # Try to get API key from argument, environment variable, or .env file
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            print("Gemini API key not found. Please add it to .env file or provide via --api-key")
            print("Check .env.sample for the expected format")
            sys.exit(1)
        
        # Configure the Gemini API
        self.client = genai.Client(
            http_options={"api_version": "v1alpha"}, 
            api_key=self.api_key
        )
        
        # Configure TTS settings
        self.config = types.LiveConnectConfig(
            response_modalities=["audio"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
                )
            ),
        )
        
        # Create PyAudio instance
        self.pya = pyaudio.PyAudio()
        
        # Create audio queue for playback
        self.audio_in_queue = None
        
        # Test text for TTS conversion
        self.test_text = "This is a test of Gemini's text to speech capabilities. If you can hear this, the implementation is working correctly. The quick brown fox jumps over the lazy dog. Testing, testing, one, two, three."

    async def receive_audio(self, session):
        """Background task to read from websocket and write audio chunks to the queue"""
        while True:
            turn = session.receive()
            async for response in turn:
                if data := response.data:
                    self.audio_in_queue.put_nowait(data)
                    continue
                if text := response.text:
                    print(text, end="")
                    
            # If model is interrupted, clear the queue
            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()

    async def play_audio(self):
        """Play audio from the queue"""
        try:
            # Initialize audio playback stream
            stream = await asyncio.to_thread(
                self.pya.open,
                format=FORMAT,
                channels=CHANNELS,
                rate=RECEIVE_SAMPLE_RATE,
                output=True,
            )
            
            while True:
                # Get audio data from queue
                bytestream = await self.audio_in_queue.get()
                
                # Play the audio
                await asyncio.to_thread(stream.write, bytestream)
                
        except Exception as e:
            print(f"Error playing audio: {e}")
            traceback.print_exception(type(e), e, e.__traceback__)

    async def run(self):
        """Run the TTS system with the test text"""
        try:
            async with (
                self.client.aio.live.connect(model=MODEL, config=self.config) as session,
                asyncio.TaskGroup() as tg,
            ):
                # Initialize audio queue
                self.audio_in_queue = asyncio.Queue()
                
                # Start audio receive and playback tasks
                tg.create_task(self.receive_audio(session))
                tg.create_task(self.play_audio())
                
                # Send the test text to Gemini for TTS conversion with specific prompt
                print(f"Sending test text to Gemini: '{self.test_text}'")
                prompt = f"Please read the following text out loud, exactly as written without any commentary or response: {self.test_text}"
                await session.send(input=prompt, end_of_turn=True)
                
                # Wait for user to quit
                while True:
                    cmd = await asyncio.to_thread(input, "\nPress q to quit: ")
                    if cmd.lower() == 'q':
                        break
                
        except asyncio.CancelledError:
            print("Operation cancelled")
        except Exception as e:
            print(f"Error in TTS process: {e}")
            traceback.print_exception(type(e), e, e.__traceback__)
        finally:
            # Clean up resources
            self.pya.terminate()

def main():
    parser = argparse.ArgumentParser(description="Test Gemini Text-to-Speech")
    parser.add_argument("--api-key", type=str, help="Gemini API Key (or set in .env file)")
    args = parser.parse_args()
    
    # Create and run the TTS system
    tts = GeminiTTS(api_key=args.api_key)
    asyncio.run(tts.run())

if __name__ == "__main__":
    main()