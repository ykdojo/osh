#!/usr/bin/env python3
"""
Audio transcription module for Gemini 2.0 Flash Thinking
Processes audio files and returns transcribed text with minimal debug output
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

def transcribe_audio(audio_file_path=None, verbose=False):
    """
    Process an audio file with Gemini and transcribe its content
    
    Args:
        audio_file_path (str, optional): Path to the audio file to process
        verbose (bool): Whether to show detailed output logs
        
    Returns:
        str: The transcription text if successful, None otherwise
    """
    
    # Configure Gemini client - use GEMINI_API_KEY from .env file
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        if verbose:
            print("Error: GEMINI_API_KEY not found in environment variables")
            print("Please make sure you have a .env file with your GEMINI_API_KEY")
        return None
    
    # Use default file if none provided
    if not audio_file_path:
        audio_file_path = os.path.join(os.path.dirname(__file__), "audio_recording.wav")
        if verbose:
            print(f"No audio file specified, using default: {audio_file_path}")
    
    # Check if the audio file exists
    if not os.path.exists(audio_file_path):
        if verbose:
            print(f"Error: Audio file '{audio_file_path}' not found.")
        return None
    
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Read the audio file
        if verbose:
            print(f"Reading audio file: {audio_file_path}")
        with open(audio_file_path, "rb") as f:
            audio_data = f.read()
        
        # Determine mime type based on file extension
        file_ext = os.path.splitext(audio_file_path)[1].lower()
        if file_ext == '.wav':
            mime_type = "audio/wav"
        elif file_ext == '.mp3':
            mime_type = "audio/mpeg"
        elif file_ext == '.ogg':
            mime_type = "audio/ogg"
        elif file_ext == '.flac':
            mime_type = "audio/flac"
        else:
            # Default to wav if unknown
            mime_type = "audio/wav"
            if verbose:
                print(f"Warning: Unknown audio format '{file_ext}', defaulting to {mime_type}")
        
        # Initialize the model
        # Old model: flash-thinking experimental model
        # model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
        # New model: standard flash model
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Create parts for the generation
        audio_part = {"mime_type": mime_type, "data": audio_data}
        
        # Transcription prompt
        transcription_prompt = """
        Create a polished, professional transcription of this audio recording, completely removing all speech disfluencies.
        
        IMPORTANT: 
        - If there is any audio, attempt to transcribe it even if it seems like background noise
        - Only if there is absolutely no audio at all (complete silence), return exactly "NO_AUDIO"
        - If you've confirmed there is audio but cannot detect any speech, return "NO_AUDIBLE_SPEECH"
        
        Critical instructions:
        - You MUST remove ALL filler words (um, uh, like, you know, sort of, kind of, etc.)
        - You MUST remove ALL repetitions, stutters, false starts, and self-corrections
        - You MUST eliminate ALL verbal crutches and speech disfluencies
        - You MUST convert hesitant, rambling speech into clear, articulate sentences
        - You MUST NOT include phrases like "Here's the transcript:" or any other headers
        - You MUST NOT add timestamps or speaker attributions 
        - You MUST NOT include any introductory or concluding remarks
        - You MUST begin immediately with the transcribed content
        - For longer speech, use appropriate paragraph breaks for readability
        - Preserve all technical terms, names, and specialized vocabulary accurately
        - ALWAYS maintain the exact capitalization of proper names and terms (e.g., "Claude Code" with both capital Cs)
        - Preserve the original meaning while substantially improving speech clarity
        - For numbered lists or bullet points, format them properly with one item per line and preserve their numbering
        
        Your goal is to produce a transcript that reads as if it were written text rather than spoken words.
        Make it concise, clear, and professional - as if it had been carefully edited for publication.
        """
        
        if verbose:
            print("Sending request to Gemini 2.0 Flash Thinking...")
            print("\n--- Gemini Response ---")
        
        # Generate the response
        response = model.generate_content([transcription_prompt, audio_part])
        
        if verbose:
            print(response.text)
            print("\n--- End of Response ---")
        
        # Return the transcription text with whitespace stripped
        return response.text.strip()
            
    except Exception as e:
        if verbose:
            print(f"Error during audio processing: {str(e)}")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Transcribe audio using Gemini AI")
    parser.add_argument("-f", "--file", type=str, help="Path to audio file to transcribe")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output")
    
    args = parser.parse_args()
    
    result = transcribe_audio(
        audio_file_path=args.file, 
        verbose=args.verbose
    )
    
    if result:
        if not args.verbose:
            print(result)  # Only print result directly in non-verbose mode
    else:
        print("Transcription failed or returned no results.")