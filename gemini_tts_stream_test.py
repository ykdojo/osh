#!/usr/bin/env python3
import base64
import os
import mimetypes
import wave
import struct
import argparse
from dotenv import load_dotenv

try:
    import pyaudio
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


def save_wav_file(file_name, audio_data, sample_rate=SAMPLE_RATE, channels=CHANNELS):
    """Save audio data as a proper WAV file with headers"""
    with wave.open(file_name, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)  # 2 bytes for 16-bit audio
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data)
    print(f"Saved WAV file: {file_name}")


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


def generate(play_directly=False):
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Gemini API key not found. Please add it to .env file")
        import sys
        sys.exit(1)
    
    # Initialize client
    client = genai.Client(
        api_key=api_key,
    )
    
    # Create a sample text file for upload
    with open("sample_input.txt", "w") as f:
        f.write("Hello, this is a test file for Gemini TTS.")
    
    try:
        # Upload the sample file
        files = [
            client.files.upload(file="sample_input.txt"),
        ]
        
        # Model configuration
        model = "gemini-2.0-flash-exp-image-generation"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="""Say with a cheerful, upbeat intonation: Have a wonderful day!"""),
                ],
            ),
            types.Content(
                role="model",
                parts=[
                    types.Part.from_uri(
                        file_uri=files[0].uri,
                        mime_type=files[0].mime_type,
                    ),
                ],
            ),
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="""Generate a cheerful greeting with enthusiasm!"""),
                ],
            ),
        ]
        
        # Configure TTS settings
        generate_content_config = types.GenerateContentConfig(
            response_modalities=[
                "audio",
            ],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
                )
            ),
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_CIVIC_INTEGRITY",
                    threshold="OFF",  # Off
                ),
            ],
            response_mime_type="text/plain",
        )

        print("Generating TTS content with Gemini...")
        
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
                
                print(f"Received audio data of mime type: {inline_data.mime_type}")
                
                if play_directly:
                    # Play the audio directly
                    play_audio(audio_data)
                else:
                    # Save as proper WAV file with headers
                    file_name = "gemini_tts_output.wav"
                    save_wav_file(file_name, audio_data)
            else:
                print(chunk.text)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up the sample file
        if os.path.exists("sample_input.txt"):
            os.remove("sample_input.txt")


def main():
    parser = argparse.ArgumentParser(description="Test Gemini TTS with proper audio handling")
    parser.add_argument("--play", action="store_true", help="Play audio directly instead of saving to file")
    args = parser.parse_args()
    
    generate(play_directly=args.play)


if __name__ == "__main__":
    main()