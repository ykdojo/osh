#!/usr/bin/env python3
"""
High-quality screen and audio recorder
Records screen with ffmpeg and audio with sounddevice separately,
then combines them for optimal quality
"""

import ffmpeg
import subprocess
import sounddevice as sd
import soundfile as sf
import numpy as np
import time
import os
import tempfile

# Import utility functions from recorders module
from recorders.utils import list_audio_devices, list_screen_devices

def record_audio(output_file, duration, fs=44100, verbose=False):
    """
    Record high-quality audio from default microphone
    
    Args:
        output_file (str): Path to save the recording
        duration (int): Recording duration in seconds
        fs (int): Sample rate in Hz
        verbose (bool): Whether to show detailed output logs
    
    Returns:
        str: Path to saved audio file or None if failed
    """
    # List available devices if verbose
    if verbose:
        list_audio_devices()
    
    # Use default device
    device_info = sd.query_devices(kind='input')
    print(f"Using audio device: {device_info['name']}")
    
    # Calculate total frames
    frames = int(duration * fs)
    
    # Create empty array for recording
    recording = np.zeros((frames, device_info['max_input_channels']), dtype='float32')
    
    print(f"Recording audio for {duration} seconds...")
    
    # Start recording
    with sd.InputStream(samplerate=fs, device=None, channels=device_info['max_input_channels'], callback=None) as stream:
        start_time = time.time()
        stream.start()
        
        # Read chunks of audio
        chunk_size = 1024
        offset = 0
        
        while offset < frames:
            # Calculate remaining frames
            remaining = frames - offset
            this_chunk = min(chunk_size, remaining)
            
            # Read audio chunk
            chunk, overflowed = stream.read(this_chunk)
            if overflowed:
                print("Warning: Audio buffer overflowed")
            
            # Store chunk in recording array
            if offset + len(chunk) <= frames:
                recording[offset:offset+len(chunk)] = chunk
                
            offset += len(chunk)
            
            # Check if duration reached
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break
                
        stream.stop()
    
    if verbose:
        print(f"Audio recording complete: {elapsed:.2f} seconds")
    
    # Save to file
    try:
        if verbose:
            print(f"Saving audio to {output_file}...")
        sf.write(output_file, recording, fs)
        if verbose:
            print(f"Audio saved to {output_file}")
        return output_file
    except Exception as e:
        print(f"Error saving audio file: {str(e)}")
        return None

def record_screen(output_file, duration, framerate=30, resolution='1280x720', screen_index=None):
    """
    Record screen only (no audio) using ffmpeg
    
    Args:
        output_file (str): Path to save the recording
        duration (int): Recording duration in seconds
        framerate (int): Frame rate for recording
        resolution (str): Video resolution in format 'WIDTHxHEIGHT'
        screen_index (int, optional): Screen index to capture, if None will list available screens
    
    Returns:
        str: Path to saved video file or None if failed
    """
    # List available screen devices
    devices_info = list_screen_devices()
    
    # If no screen index provided, prompt user to select or use default
    if screen_index is None:
        # Default to screen index 4 (macOS "Capture screen 1")
        screen_index = 4
        print("No screen index specified. Using default screen index 4.")
    
    print(f"Using screen index: {screen_index}")
    
    try:
        # Create input stream for screen only (no audio)
        input_stream = ffmpeg.input(
            f"{screen_index}", 
            f='avfoundation',
            framerate=framerate,
            video_size=resolution,
            capture_cursor=1,
            pix_fmt='uyvy422',
            t=duration
        )
        
        # Output to file (video only, no audio)
        output_stream = ffmpeg.output(
            input_stream, 
            output_file,
            vcodec='h264',
            preset='ultrafast',
            crf=22  # Lower CRF for better quality
        )
        
        print(f"Starting screen recording for {duration} seconds...")
        print(f"Running ffmpeg command: {' '.join(ffmpeg.compile(output_stream))}")
        
        output_stream.run(capture_stdout=True, capture_stderr=True, overwrite_output=True, quiet=True)
        print(f"Screen recording completed and saved to {output_file}")
        return output_file
        
    except Exception as e:
        print(f"Error during screen recording: {str(e)}")
        return None

def combine_audio_video(video_file, audio_file, output_file, verbose=False):
    """
    Combine separate video and audio files into a single output file
    
    Args:
        video_file (str): Path to video file
        audio_file (str): Path to audio file
        output_file (str): Path to output combined file
        verbose (bool): Whether to show detailed output logs
    
    Returns:
        str: Path to combined file or None if failed
    """
    try:
        # Input video stream
        video_stream = ffmpeg.input(video_file)
        
        # Input audio stream
        audio_stream = ffmpeg.input(audio_file)
        
        # Combine streams
        output = ffmpeg.output(
            video_stream, 
            audio_stream, 
            output_file,
            vcodec='copy',  # Copy video without re-encoding
            acodec='aac',   # Convert audio to AAC
            strict='experimental'
        )
        
        print(f"Combining video and audio into {output_file}...")
        if verbose:
            print(f"Running ffmpeg command: {' '.join(ffmpeg.compile(output))}")
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True, quiet=not verbose)
        if verbose:
            print(f"Combined file saved to: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"Error combining audio and video: {str(e)}")
        return None

def record_screen_and_audio(output_file='combined_recording.mp4', duration=7, verbose=False, screen_index=None):
    """
    Record high-quality screen and audio separately, then combine them
    
    Args:
        output_file (str): Final output file path
        duration (int): Recording duration in seconds
        verbose (bool): Whether to show detailed output logs
        screen_index (int, optional): Screen index to capture, if None will use default (3)
    
    Returns:
        str: Path to final combined file or None if failed
    """
    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
        temp_video_path = temp_video.name
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
        temp_audio_path = temp_audio.name
    
    try:
        print("=== Starting High-Quality Recording ===")
        print(f"Recording duration: {duration} seconds")
        print(f"Final output will be saved to: {output_file}")
        
        # Display which screen will be captured, but don't print the full device list
        screen_devices = list_screen_devices(print_output=False)
        screen_to_use = 4 if screen_index is None else screen_index
        screen_name = screen_devices.get(screen_to_use, f"Unknown screen at index {screen_to_use}")
        print(f"Screen to capture: {screen_name}")
        
        # Prepare ffmpeg command for screen recording
        screen_cmd = ffmpeg.compile(
            ffmpeg.output(
                ffmpeg.input(
                    str(4 if screen_index is None else screen_index),  # Use provided screen index or default to 4
                    f='avfoundation',
                    framerate=30,
                    video_size='1280x720',
                    capture_cursor=1,
                    pix_fmt='uyvy422',
                    t=duration
                ),
                temp_video_path,
                vcodec='h264',
                preset='ultrafast',
                crf=22
            )
        )
        
        print("\nStarting recording now...")
        
        # Add -y flag to force overwrite without prompting
        screen_cmd.insert(1, '-y')
        
        # Always suppress ffmpeg banner and warnings, but show progress if verbose
        screen_cmd.extend(['-hide_banner'])
        
        # If not verbose, suppress all ffmpeg output
        if not verbose:
            screen_cmd.extend(['-v', 'quiet', '-nostats'])
            
        # Start screen recording in background
        screen_process = subprocess.Popen(
            screen_cmd,
            stdout=subprocess.DEVNULL if not verbose else None,
            stderr=subprocess.DEVNULL if not verbose else None
        )
        
        # Immediately start audio recording
        audio_file = record_audio(temp_audio_path, duration, verbose=verbose)
        
        # Wait for screen recording to finish if it hasn't already
        screen_process.wait()
        
        if not os.path.exists(temp_video_path) or not audio_file:
            print("Error: Screen or audio recording failed")
            return None
        
        print("\n3. Combining video and audio...")
        result = combine_audio_video(temp_video_path, audio_file, output_file, verbose=verbose)
        
        # Clean up temporary files
        try:
            os.remove(temp_video_path)
            os.remove(temp_audio_path)
        except:
            pass
            
        print("\n=== Recording Process Completed ===")
        if result:
            file_size = os.path.getsize(output_file) / (1024 * 1024)  # Size in MB
            print(f"Final file size: {file_size:.2f} MB")
            print(f"Recording saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"Error in recording process: {str(e)}")
        # Clean up temporary files
        try:
            os.remove(temp_video_path)
            os.remove(temp_audio_path)
        except:
            pass
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="High-quality screen and audio recorder")
    parser.add_argument("-d", "--duration", type=int, default=7, help="Recording duration in seconds")
    parser.add_argument("-o", "--output", type=str, default="combined_recording.mp4", help="Output file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed logs during recording")
    parser.add_argument("-s", "--screen", type=int, help="Screen index to capture (run with -l to see available screens)")
    parser.add_argument("-l", "--list", action="store_true", help="List available screen and audio devices")
    
    args = parser.parse_args()
    
    # List devices if requested
    if args.list:
        print("=== Available Screen Devices ===")
        screens = list_screen_devices(print_output=False)
        for index, name in sorted(screens.items()):
            print(f"[{index}] {name}")
            
        print("\n=== Available Audio Devices ===")
        list_audio_devices()
        exit(0)
    
    # Record screen and audio
    record_screen_and_audio(
        output_file=args.output, 
        duration=args.duration, 
        verbose=args.verbose,
        screen_index=args.screen
    )