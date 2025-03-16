#!/usr/bin/env python3
"""
Simple audio recorder using sounddevice
Records 7 seconds of audio and saves to a file
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
import time
import os

def list_audio_devices():
    """List all available audio input devices"""
    print("Available audio input devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:  # Only input devices
            print(f"[{i}] {device['name']} (Inputs: {device['max_input_channels']})")
    return devices

def record_audio(output_file='audio_recording.wav', duration=7, fs=44100):
    """
    Record audio from default microphone for specified duration
    
    Args:
        output_file (str): Path to save the recording
        duration (int): Recording duration in seconds
        fs (int): Sample rate in Hz
    """
    # List available devices
    devices = list_audio_devices()
    
    # Use default device (device=None)
    device_info = sd.query_devices(kind='input')
    print(f"Using device: {device_info['name']}")
    
    # Calculate total frames based on duration and sample rate
    frames = int(duration * fs)
    
    # Create empty array to store recording
    recording = np.zeros((frames, device_info['max_input_channels']), dtype='float32')
    
    print(f"Starting {duration} second recording...")
    print("Recording...")
    
    # Start recording
    with sd.InputStream(samplerate=fs, device=None, channels=device_info['max_input_channels'], callback=None) as stream:
        start_time = time.time()
        stream.start()
        
        # Read chunks of audio until we reach desired duration
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
            
            # Print progress
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break
                
        stream.stop()
    
    print(f"Recording complete: {elapsed:.2f} seconds")
    
    # Save to file
    try:
        print(f"Saving to {output_file}...")
        sf.write(output_file, recording, fs)
        print(f"Audio saved to {output_file}")
        
        # Show file info
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # Size in MB
        print(f"File size: {file_size:.2f} MB")
        
        return output_file
    except Exception as e:
        print(f"Error saving audio file: {str(e)}")
        return None

if __name__ == "__main__":
    # Record 7 seconds of audio
    output_file = record_audio()
    
    print(f"\nRecorded file: {output_file}")
    print("You can play this file with any audio player")