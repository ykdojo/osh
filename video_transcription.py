#!/usr/bin/env python3
"""
Video transcription module for Gemini 2.0 Flash Thinking
Processes video files and returns transcribed text with minimal debug output
"""

import os
import sys
import base64
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

def transcribe_video(video_file_path=None, verbose=False):
    """
    Process a video with Gemini and transcribe its content
    
    Args:
        video_file_path (str, optional): Path to the video file to process
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
    if not video_file_path:
        video_file_path = os.path.join(os.path.dirname(__file__), "combined_recording.mp4")
        if verbose:
            print(f"No video file specified, using default: {video_file_path}")
    
    # Check if the video file exists
    if not os.path.exists(video_file_path):
        if verbose:
            print(f"Error: Video file '{video_file_path}' not found.")
        return None
    
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Read the video file
        if verbose:
            print(f"Reading video file: {video_file_path}")
        with open(video_file_path, "rb") as f:
            video_data = f.read()
        
        # Initialize the model
        # Old model: flash-thinking experimental model
        # model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
        # New model: standard flash model
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Create parts for the generation
        video_part = {"mime_type": "video/mp4", "data": video_data}
        
        # Transcription prompt
        transcription_prompt = """
        Transcribe the speech in this video word for word, carefully using the visual content as context.
        
        Focus on accuracy and completeness. Pay special attention to:
        - Any text, file names, or UI elements visible on the screen
        - Names of people, places, companies, or products shown visually
        - Code, commands, or technical content being demonstrated
        - Match your transcription to what's being discussed in the context of what's shown
        
        When the speaker refers to something visible on screen (like "this file," "that function," 
        or "click here"), include the specific name/identifier of what they're referencing.
        
        Always prioritize accurate transcription while incorporating relevant visual context.
        """
        
        if verbose:
            print("Sending request to Gemini 2.0 Flash Thinking...")
            print("\n--- Gemini Response ---")
        
        # Generate the response
        response = model.generate_content([transcription_prompt, video_part])
        
        if verbose:
            print(response.text)
            print("\n--- End of Response ---")
        
        # Return the transcription text
        return response.text
            
    except Exception as e:
        if verbose:
            print(f"Error during video processing: {str(e)}")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Transcribe video using Gemini AI")
    parser.add_argument("-f", "--file", type=str, help="Path to video file to transcribe")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output")
    
    args = parser.parse_args()
    
    result = transcribe_video(
        video_file_path=args.file, 
        verbose=args.verbose
    )
    
    if result:
        if not args.verbose:
            print(result)  # Only print result directly in non-verbose mode
    else:
        print("Transcription failed or returned no results.")