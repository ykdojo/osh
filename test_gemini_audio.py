#!/usr/bin/env python3
"""
Test script for using audio with Gemini 2.0 Flash Thinking
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

def transcribe_audio_data(audio_data):
    """
    Transcribe audio data using Gemini 2.0 Flash Thinking
    
    Args:
        audio_data (bytes): Raw audio data in bytes
        
    Returns:
        str: Transcription text or None if an error occurs
    """
    # Configure Gemini client - use GEMINI_API_KEY from .env file
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        print("Please make sure you have a .env file with your GEMINI_API_KEY")
        return None
    
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Initialize the model - using the same model as in app.py
        model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
        
        # Create parts for the generation
        audio_part = {"mime_type": "audio/mp3", "data": audio_data}
        
        # Define prompt
        prompt = "Transcribe this audio word for word only. No introduction, no description, just the exact transcription of any speech."
        
        # Generate content
        response = model.generate_content([prompt, audio_part])
        
        return response.text
            
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return None

def test_audio_with_gemini(audio_file_path=None):
    """Test audio processing with Gemini 2.0 Flash Thinking"""
    
    # Default to the test.mp3 file if no file is specified
    if audio_file_path is None:
        audio_file_path = os.path.join(os.path.dirname(__file__), "test.mp3")
    
    # Check if the audio file exists
    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file '{audio_file_path}' not found.")
        return
    
    # Read the audio file
    print(f"Reading audio file: {audio_file_path}")
    with open(audio_file_path, "rb") as f:
        audio_data = f.read()
    
    print("Sending request to Gemini 2.0 Flash Thinking...")
    
    # Use the transcription function
    transcription = transcribe_audio_data(audio_data)
    
    # Print response
    if transcription:
        print("\n--- Gemini Response ---")
        print(transcription)

if __name__ == "__main__":
    # Use command line argument if provided, otherwise use default
    audio_file_path = sys.argv[1] if len(sys.argv) > 1 else None
    test_audio_with_gemini(audio_file_path)