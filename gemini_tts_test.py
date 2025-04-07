#!/usr/bin/env python3
import argparse
import asyncio
import traceback
import os
import sys

import pyaudio
import websockets
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
    def __init__(self, api_key=None, speed_factor=1.0):
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
        
        # Set speed factor for playback (1.0 = normal speed, 1.25 = 25% faster)
        self.speed_factor = speed_factor
        
        # Test text for TTS conversion
        self.test_text = "This is a test of Gemini's text to speech capabilities. If you can hear this, the implementation is working correctly. The quick brown fox jumps over the lazy dog. Testing, testing, one, two, three."

    async def receive_audio(self, session):
        """Background task to read from websocket and write audio chunks to the queue"""
        try:
            while True:
                turn = session.receive()
                try:
                    async for response in turn:
                        if data := response.data:
                            self.audio_in_queue.put_nowait(data)
                            continue
                        if text := response.text:
                            print(text, end="")
                except websockets.exceptions.ConnectionClosedError as e:
                    reason = getattr(e, 'reason', 'Internal error encountered')
                    print(f"\nConnection error from Gemini API: {reason}")
                    # Make sure to raise an exception that can be caught by the retry logic
                    # Re-raise with enough context to be caught by outer try/except
                    raise RuntimeError(f"Connection error: {reason}") from e
                except Exception as e:
                    print(f"\nError receiving audio from Gemini API: {e}")
                    traceback.print_exc(limit=2)
                    # Re-raise all exceptions so they're caught by retry logic
                    raise RuntimeError(f"API error: {e}") from e
                    
                # If model is interrupted, clear the queue
                while not self.audio_in_queue.empty():
                    self.audio_in_queue.get_nowait()
        except Exception as e:
            print(f"\nFatal error in receive_audio task: {e}")
            traceback.print_exc(limit=2)
            # Re-raise to ensure TaskGroup catches this
            raise

    async def play_audio(self):
        """Play audio from the queue"""
        try:
            # Initialize audio playback stream with adjusted rate for speed control
            adjusted_rate = int(RECEIVE_SAMPLE_RATE * self.speed_factor)
            
            stream = await asyncio.to_thread(
                self.pya.open,
                format=FORMAT,
                channels=CHANNELS,
                rate=adjusted_rate,  # Use adjusted rate for speed control
                output=True,
            )
            
            print(f"Playing audio at {self.speed_factor:.2f}x speed ({adjusted_rate} Hz)")
            
            while True:
                # Get audio data from queue
                bytestream = await self.audio_in_queue.get()
                
                # Play the audio
                await asyncio.to_thread(stream.write, bytestream)
                
        except Exception as e:
            print(f"Error playing audio: {e}")
            traceback.print_exception(type(e), e, e.__traceback__)

    async def run(self, repeat_count=3, interval=5, max_retries=3):
        """Run the TTS system with the test text, repeating playback at specified intervals
        
        Args:
            repeat_count: Number of times to play the audio
            interval: Seconds to wait between playbacks
            max_retries: Maximum number of retries on API errors before giving up
        """
        try:
            # Play the audio multiple times with intervals
            for i in range(repeat_count):
                print(f"\nPlayback {i+1}/{repeat_count}")
                
                # Retry logic for handling API errors
                retry_count = 0
                success = False
                
                while not success and retry_count < max_retries:
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
                            prompt = f"Read out loud the following text. No need to say yes, okay, and stuff like that. Just focus on reading it out loud by itself with nothing else. IMPORTANT: Skip all preambles like 'okay' or 'I'll read this'. ONLY read exactly these words: {self.test_text}"
                            await session.send(input=prompt, end_of_turn=True)
                            
                            # Wait for the audio to finish playing (approximate time)
                            await asyncio.sleep(10)  # Adjust if needed based on text length
                            success = True
                            
                    except Exception as e:
                        retry_count += 1
                        if retry_count >= max_retries:
                            print(f"Failed after {max_retries} attempts. Last error: {e}")
                            print("Exiting due to repeated failures.")
                            # Force exit directly from here
                            os._exit(1)  # This is a hard exit that bypasses normal cleanup
                        else:
                            print(f"Error encountered: {e}. Retrying ({retry_count}/{max_retries})...")
                            await asyncio.sleep(1)  # Brief pause before retry
                
                # Wait for the specified interval before next playback if we're not on the last one
                if i < repeat_count - 1 and success:
                    print(f"Waiting {interval} seconds before next playback...")
                    await asyncio.sleep(interval)
            
            print("\nTest complete. Exiting.")
                
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
    parser.add_argument("--repeat", type=int, default=3, help="Number of times to play the audio")
    parser.add_argument("--interval", type=int, default=5, help="Seconds to wait between playbacks")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed factor (1.0=normal, 1.25=25% faster)")
    args = parser.parse_args()
    
    # Create and run the TTS system
    tts = GeminiTTS(api_key=args.api_key, speed_factor=args.speed)
    try:
        asyncio.run(tts.run(repeat_count=args.repeat, interval=args.interval))
    except RuntimeError as e:
        if "Maximum retry attempts reached" in str(e):
            print("Terminating program due to maximum retry failures.")
            sys.exit(1)
        else:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()