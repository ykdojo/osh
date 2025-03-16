#!/usr/bin/env python3
"""
Combined screen/audio recorder with Gemini AI video processing
Records screen with audio, then processes with Gemini for transcription
"""

import os
import sys
import time
from dotenv import load_dotenv

# Import the screen and audio recording functionality
from screen_audio_recorder import record_screen_and_audio

# Import Gemini video processing functionality
from test_gemini_video import generate

def record_and_process(
    output_file='combined_recording.mp4', 
    duration=7, 
    verbose=False, 
    screen_index=None,
    manual_interrupt_key='q',
    skip_transcription=False
):
    """
    Record screen and audio, then process the video with Gemini for transcription
    
    Args:
        output_file (str): Final output file path
        duration (int): Recording duration in seconds for screen recording
        verbose (bool): Whether to show detailed output logs
        screen_index (int, optional): Screen index to capture, if None will use default
        manual_interrupt_key (str, optional): Key to press to manually stop recording
        skip_transcription (bool): If True, skip the Gemini transcription step
        
    Returns:
        tuple: (video_path, transcription_text) or (video_path, None) if skipped
    """
    # Step 1: Record screen and audio
    print("=== Step 1: Recording Screen and Audio ===")
    video_path = record_screen_and_audio(
        output_file=output_file,
        duration=duration,
        verbose=verbose,
        screen_index=screen_index,
        manual_interrupt_key=manual_interrupt_key
    )
    
    if not video_path:
        print("Recording failed. Cannot proceed to transcription.")
        return None, None
        
    # Step 2: Process with Gemini (if not skipped)
    if not skip_transcription:
        print("\n=== Step 2: Processing Video with Gemini AI ===")
        # Generate function now returns the transcription text
        transcription = generate(video_path)
        return video_path, transcription
    else:
        print("\n=== Transcription step skipped as requested ===")
        return video_path, None

if __name__ == "__main__":
    import argparse
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if Gemini API key is available
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in environment variables")
        print("Transcription will not work without API key in .env file")
    
    parser = argparse.ArgumentParser(description="Screen and audio recorder with Gemini transcription")
    parser.add_argument("-d", "--duration", type=int, default=7, help="Recording duration in seconds")
    parser.add_argument("-o", "--output", type=str, default="combined_recording.mp4", help="Output file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed logs during recording")
    parser.add_argument("-s", "--screen", type=int, help="Screen index to capture (run with -l to see available screens)")
    parser.add_argument("-l", "--list", action="store_true", help="List available screen and audio devices")
    parser.add_argument("-k", "--key", type=str, default="q", help="Key to press to manually stop recording (defaults to 'q')")
    parser.add_argument("--no-manual-interrupt", action="store_true", help="Disable manual interrupt capability")
    parser.add_argument("--skip-transcription", action="store_true", help="Skip Gemini transcription step")
    
    args = parser.parse_args()
    
    # If listing devices is requested, use the function from screen_audio_recorder
    if args.list:
        # Import the listing functions directly
        from recorders.utils import list_screen_devices, list_audio_devices
        
        print("=== Available Screen Devices ===")
        screens = list_screen_devices(print_output=False)
        for index, name in sorted(screens.items()):
            print(f"[{index}] {name}")
            
        print("\n=== Available Audio Devices ===")
        list_audio_devices()
        exit(0)
    
    # Set manual interrupt key if not disabled
    manual_interrupt_key = None if args.no_manual_interrupt else args.key
    
    # Record and process
    record_and_process(
        output_file=args.output, 
        duration=args.duration, 
        verbose=args.verbose,
        screen_index=args.screen,
        manual_interrupt_key=manual_interrupt_key,
        skip_transcription=args.skip_transcription
    )