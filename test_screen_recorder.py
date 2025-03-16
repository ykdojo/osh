# Make sure to activate virtual environment before running:
# source venv/bin/activate (or venv\Scripts\activate on Windows)
# If ffmpeg-python is not installed, run: pip install ffmpeg-python

import ffmpeg
import subprocess
import time
import os

def list_devices():
    """List available avfoundation devices (screens and audio devices)."""
    try:
        # This command lists available devices on macOS
        result = subprocess.run(
            ['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', ''],
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stderr
    except Exception as e:
        return f"Error listing devices: {str(e)}"

def record_screen_and_audio(output_file='screen_recording.mp4', duration=10):
    """Record screen and audio for the specified duration."""
    # First, list devices to show which ones we're using
    devices_info = list_devices()
    print("Available devices:")
    print(devices_info)
    
    # Based on output, screens are index 3 and 4, audio inputs are 0, 1, 2
    # Using "Capture screen 0" which is index 3 and "Shure Digital" which is index 0
    screen_index = 3  # Capture screen 0
    audio_index = 0   # Shure Digital
    
    print(f"Using screen index: {screen_index}, audio index: {audio_index}")
    
    try:
        # Create a stream object using avfoundation
        input_stream = ffmpeg.input(
            f"{screen_index}:{audio_index}", 
            f='avfoundation',
            framerate=30,
            video_size='1280x720',
            capture_cursor=1,
            pix_fmt='uyvy422',  # Common format for avfoundation
            t=duration
        )
        
        # Output to file
        output_stream = ffmpeg.output(
            input_stream, 
            output_file,
            vcodec='h264',
            acodec='aac',
            preset='ultrafast',
            crf=28
        )
        
        print(f"Starting screen and audio recording for {duration} seconds...")
        # Show the ffmpeg command
        print(f"Running ffmpeg command: {' '.join(ffmpeg.compile(output_stream))}")
        output_stream.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        print(f"Recording completed and saved to {output_file}")
        
    except Exception as e:
        print(f"Error during recording: {str(e)}")

if __name__ == "__main__":
    # Record screen and audio for 10 seconds
    record_screen_and_audio()