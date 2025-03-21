#!/usr/bin/env python3
"""
Core recording functions for screen and audio capture
"""

import ffmpeg
import sounddevice as sd
import soundfile as sf
import numpy as np
import time

# Import utility functions from utils module
from recorders.utils import list_audio_devices, list_screen_devices

def record_audio(output_file, fs=44100, verbose=False, stop_event=None, status_callback=None):
    """
    Record high-quality audio from default microphone until stop_event is set
    
    Args:
        output_file (str): Path to save the recording
        fs (int): Sample rate in Hz
        verbose (bool): Whether to show detailed output logs
        stop_event (threading.Event): Event to signal when to stop recording
        status_callback (callable): Optional callback to report status updates
    
    Returns:
        str: Path to saved audio file or None if failed
    """
    # List available devices if verbose
    if verbose:
        list_audio_devices()
    
    # Use default device
    device_info = sd.query_devices(kind='input')
    
    # Get device name and report it
    mic_name = device_info['name']
    if verbose:
        print(f"Using audio device: {mic_name}")
    
    # Report microphone information through the callback if provided
    if status_callback:
        status_callback(f"Using audio device: {mic_name}")
    
    # Maximum buffer size (30 minutes of audio at given sample rate)
    max_frames = int(1800 * fs)
    
    # Create empty array for recording
    recording = np.zeros((max_frames, device_info['max_input_channels']), dtype='float32')
    
    if verbose:
        print("Recording audio until screen recording completes...")
    
    # Start recording
    with sd.InputStream(samplerate=fs, device=None, channels=device_info['max_input_channels'], callback=None) as stream:
        start_time = time.time()
        stream.start()
        
        # Read chunks of audio
        chunk_size = 1024
        offset = 0
        
        while offset < max_frames:
            # Calculate remaining frames
            remaining = max_frames - offset
            this_chunk = min(chunk_size, remaining)
            
            # Read audio chunk
            chunk, overflowed = stream.read(this_chunk)
            if overflowed and verbose:
                print("Warning: Audio buffer overflowed")
            
            # Store chunk in recording array
            if offset + len(chunk) <= max_frames:
                recording[offset:offset+len(chunk)] = chunk
                
            offset += len(chunk)
            
            # Check if we should stop recording
            if stop_event and stop_event.is_set():
                if verbose:
                    print("Audio recording stopped by stop event")
                break
                
        stream.stop()
    
    elapsed = time.time() - start_time
    if verbose:
        print(f"Audio recording complete: {elapsed:.2f} seconds")
    
    # Trim the recording array to actual recorded length
    recording = recording[:offset]
    
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

def record_screen(output_file, duration, framerate=30, resolution='1280x720', screen_index=None, 
              stop_event=None, verbose=False, on_process_start=None):
    """
    Record screen only (no audio) using ffmpeg
    
    Args:
        output_file (str): Path to save the recording
        duration (int): Recording duration in seconds
        framerate (int): Frame rate for recording
        resolution (str): Video resolution in format 'WIDTHxHEIGHT'
        screen_index (int, optional): Screen index to capture, if None will list available screens
        stop_event (threading.Event, optional): Event to signal manual interruption
        verbose (bool, optional): Whether to show detailed output logs
        on_process_start (callable, optional): Callback function to execute when ffmpeg process actually starts
    
    Returns:
        str: Path to saved video file or None if failed
    """
    # List available screen devices
    devices_info = list_screen_devices(print_output=False)
    
    # If no screen index provided, use the last available screen index
    if screen_index is None:
        # Get the highest screen index available (usually the last screen)
        if devices_info:
            screen_index = max(devices_info.keys())
            if verbose:
                print(f"No screen index specified. Using last available screen index {screen_index}.")
        else:
            # Fallback to index 1 if no screens detected
            screen_index = 1
            if verbose:
                print("No screens detected. Falling back to screen index 1.")
    
    if verbose:
        print(f"Using screen index: {screen_index}")
    
    try:
        import subprocess
        import threading
        import signal
        import os
        
        # We can't directly interrupt ffmpeg using stop_event with ffmpeg module,
        # so create a subprocess and manage it manually
        
        # Create input stream for screen only (no audio)
        cmd = [
            'ffmpeg', '-y',
            '-f', 'avfoundation',
            '-framerate', str(framerate),
            '-video_size', resolution,
            '-capture_cursor', '1',
            '-pix_fmt', 'uyvy422',
            '-t', str(duration),
            '-i', f"{screen_index}",
            '-vcodec', 'h264',
            '-preset', 'ultrafast',
            '-crf', '22',
            output_file
        ]
        
        # Add flags to hide ffmpeg output unless verbose is enabled
        if not verbose:
            cmd.insert(2, '-hide_banner')
            cmd.insert(3, '-loglevel')
            cmd.insert(4, 'error')  # Only show errors
            cmd.insert(5, '-nostats')
        
        if verbose:
            print(f"Starting screen recording for up to {duration} seconds...")
            print(f"Running ffmpeg command: {' '.join(cmd)}")
            if stop_event:
                print(f"Press the designated key to stop recording early")
        
        # Start ffmpeg process with appropriate redirection
        if verbose:
            process = subprocess.Popen(cmd)
        else:
            # Make sure we completely suppress all output when not in verbose mode
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        # Give ffmpeg a moment to initialize
        time.sleep(0.5)
        
        # Check if the process has started properly
        if process.poll() is None:  # None means it's still running
            # Process has actually started, trigger the callback
            if on_process_start:
                on_process_start()
        
        # Create a function to monitor stop_event
        if stop_event:
            def monitor_stop_event():
                stop_event.wait()  # Wait until stop_event is set
                if process.poll() is None:  # If process is still running
                    if verbose:
                        print("Manual stop requested, terminating recording...")
                    # Send SIGTERM to gracefully stop ffmpeg
                    if os.name == 'nt':  # Windows
                        process.terminate()
                    else:  # Unix/Mac
                        os.kill(process.pid, signal.SIGTERM)
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=monitor_stop_event)
            monitor_thread.daemon = True
            monitor_thread.start()
        
        # Wait for process to complete
        process.wait()
        
        # Check return code
        if process.returncode != 0 and process.returncode != -15:
            stderr_msg = ""
            if hasattr(process, 'stderr') and process.stderr:
                stderr_msg = process.stderr.read().decode('utf-8')
            if stderr_msg and "Interrupt" not in stderr_msg and "Operation not permitted" not in stderr_msg and verbose:
                print(f"Error during screen recording: {stderr_msg}")
            elif verbose:
                print(f"Error during screen recording (return code: {process.returncode})")
            return None
        
        if verbose:
            print(f"Screen recording completed and saved to {output_file}")
            
        return output_file
        
    except Exception as e:
        if verbose:
            print(f"Error during screen recording: {str(e)}")
        return None