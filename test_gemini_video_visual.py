#!/usr/bin/env python3
"""
Test script for Gemini 2.0 Flash Thinking to analyze video visual content only
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

def analyze_visual_content(video_file_path=None):
    """
    Analyze the visual content of a video using Gemini 2.0 Flash Thinking,
    ignoring any audio/speech content.
    
    Args:
        video_file_path (str): Path to the video file to analyze
    """
    
    # Configure Gemini client - use GEMINI_API_KEY from .env file
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        print("Please make sure you have a .env file with your GEMINI_API_KEY")
        return
    
    # Use default file if none provided
    if not video_file_path:
        video_file_path = os.path.join(os.path.dirname(__file__), "combined_recording.mp4")
        print(f"No video file specified, using default: {video_file_path}")
    
    # Check if the video file exists
    if not os.path.exists(video_file_path):
        print(f"Error: Video file '{video_file_path}' not found.")
        return
    
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
        
        # Visual analysis prompt that explicitly asks to ignore audio content
        visual_analysis_prompt = """
        Analyze ONLY the visual content of this video. 
        
        Describe in detail what you can see, including:
        - The visual elements and content displayed on the screen
        - Any UI elements, windows, or applications visible
        - Any text visible on screen
        - Any actions or movements happening visually
        
        IMPORTANT: Completely IGNORE any audio or speech content. Focus solely on what can be seen.
        """
        
        print("Sending request to Gemini 2.0 Flash Thinking...")
        
        # Generate the response
        print("\n--- Gemini Visual Analysis ---")
        response = model.generate_content([visual_analysis_prompt, video_part])
        print(response.text)
        
        print("\n--- End of Analysis ---")
            
    except Exception as e:
        print(f"Error during video analysis: {str(e)}")

if __name__ == "__main__":
    # Use command line argument if provided
    if len(sys.argv) > 1:
        video_file_path = sys.argv[1]
        analyze_visual_content(video_file_path)
    else:
        analyze_visual_content()