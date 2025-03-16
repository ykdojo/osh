#!/usr/bin/env python3
"""
Test script for using video with Gemini 2.0 Flash Thinking
"""

import os
import sys
import base64
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

def generate(video_file_path=None):
    """
    Process a video with Gemini
    
    Args:
        video_file_path (str, optional): Path to the video file to process
        
    Returns:
        str: The transcription text if successful, None otherwise
    """
    
    # Configure Gemini client - use GEMINI_API_KEY from .env file
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        print("Please make sure you have a .env file with your GEMINI_API_KEY")
        return None
    
    # Use default file if none provided
    if not video_file_path:
        video_file_path = os.path.join(os.path.dirname(__file__), "combined_recording.mp4")
        print(f"No video file specified, using default: {video_file_path}")
    
    # Check if the video file exists
    if not os.path.exists(video_file_path):
        print(f"Error: Video file '{video_file_path}' not found.")
        return None
    
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Read the video file
        print(f"Reading video file: {video_file_path}")
        with open(video_file_path, "rb") as f:
            video_data = f.read()
        
        # Initialize the model
        model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
        
        # Create parts for the generation
        video_part = {"mime_type": "video/mp4", "data": video_data}
        
        # Transcription prompt
        transcription_prompt = """
        Transcribe the speech in this video word for word, using the video content as context.
        
        If the user gives a clear instruction in the video (rather than just speaking normally),
        follow that instruction. Use your judgment to determine what is an instruction versus
        content to transcribe.
        """
        
        print("Sending request to Gemini 2.0 Flash Thinking...")
        
        # Stream the response
        print("\n--- Gemini Response ---")
        response = model.generate_content([transcription_prompt, video_part])
        print(response.text)
        
        print("\n--- End of Response ---")
        
        # Return the transcription text
        return response.text
            
    except Exception as e:
        print(f"Error during video processing: {str(e)}")
        return None

if __name__ == "__main__":
    # Use command line argument if provided
    if len(sys.argv) > 1:
        video_file_path = sys.argv[1]
        generate(video_file_path)
    else:
        generate()