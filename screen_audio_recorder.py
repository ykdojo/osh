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

def list_audio_devices():
    """List all available audio input devices"""
    print("Available audio input devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:  # Only input devices
            print(f"[{i}] {device['name']} (Inputs: {device['max_input_channels']})")
    return devices

def list_screen_devices():
    """List available avfoundation devices (screens)."""
    try:
        # This command lists available devices on macOS
        result = subprocess.run(
            ['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', ''],
            stderr=subprocess.PIPE,
            text=True
        )
        print(result.stderr)
        return result.stderr
    except Exception as e:
        print(f"Error listing devices: {str(e)}")
        return None

def record_audio(output_file, duration, fs=44100):
    """
    Record high-quality audio from default microphone
    
    Args:
        output_file (str): Path to save the recording
        duration (int): Recording duration in seconds
        fs (int): Sample rate in Hz
    
    Returns:
        str: Path to saved audio file or None if failed
    """
    # List available devices
    list_audio_devices()
    
    # Use default device
    device_info = sd.query_devices(kind='input')
    print(f"Using audio device: {device_info['name']}")
    
    # Calculate total frames
    frames = int(duration * fs)
    
    # Create empty array for recording
    recording = np.zeros((frames, device_info['max_input_channels']), dtype='float32')
    
    print(f"Starting {duration} second audio recording...")
    
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
    
    print(f"Audio recording complete: {elapsed:.2f} seconds")
    
    # Save to file
    try:
        print(f"Saving audio to {output_file}...")
        sf.write(output_file, recording, fs)
        print(f"Audio saved to {output_file}")
        return output_file
    except Exception as e:
        print(f"Error saving audio file: {str(e)}")
        return None

def record_screen(output_file, duration, framerate=30, resolution='1280x720'):
    """
    Record screen only (no audio) using ffmpeg
    
    Args:
        output_file (str): Path to save the recording
        duration (int): Recording duration in seconds
        framerate (int): Frame rate for recording
        resolution (str): Video resolution in format 'WIDTHxHEIGHT'
    
    Returns:
        str: Path to saved video file or None if failed
    """
    # List available screen devices
    devices_info = list_screen_devices()
    
    # Default to screen index 3 (macOS "Capture screen 0")
    screen_index = 3
    
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
        
        output_stream.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        print(f"Screen recording completed and saved to {output_file}")
        return output_file
        
    except Exception as e:
        print(f"Error during screen recording: {str(e)}")
        return None

def combine_audio_video(video_file, audio_file, output_file):
    """
    Combine separate video and audio files into a single output file
    
    Args:
        video_file (str): Path to video file
        audio_file (str): Path to audio file
        output_file (str): Path to output combined file
    
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
        print(f"Running ffmpeg command: {' '.join(ffmpeg.compile(output))}")
        
        output.run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        print(f"Combined file saved to: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"Error combining audio and video: {str(e)}")
        return None

def record_screen_and_audio(output_file='combined_recording.mp4', duration=10):
    """
    Record high-quality screen and audio separately, then combine them
    
    Args:
        output_file (str): Final output file path
        duration (int): Recording duration in seconds
    
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
        
        # Prepare ffmpeg command for screen recording
        screen_cmd = ffmpeg.compile(
            ffmpeg.output(
                ffmpeg.input(
                    "3",  # Screen index 
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
        
        # Start screen recording in background
        screen_process = subprocess.Popen(screen_cmd)
        
        # Immediately start audio recording
        audio_file = record_audio(temp_audio_path, duration)
        
        # Wait for screen recording to finish if it hasn't already
        screen_process.wait()
        
        if not os.path.exists(temp_video_path) or not audio_file:
            print("Error: Screen or audio recording failed")
            return None
        
        print("\n3. Combining video and audio...")
        result = combine_audio_video(temp_video_path, audio_file, output_file)
        
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
    # Record screen and audio for 10 seconds
    record_screen_and_audio(duration=10)