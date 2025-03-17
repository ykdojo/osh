#!/usr/bin/env python3
"""
High-quality audio recorder
Records audio with sounddevice for optimal quality
"""

import os
import time
import tempfile
import threading

# Import utility functions and core recording functions
from recorders.utils import list_audio_devices
from recorders.recorder import record_audio


def record_audio_only(output_file='audio_recording.wav', duration=10, verbose=False, manual_stop_event=None):
    """
    Record high-quality audio using threading with ability to stop manually
    
    Args:
        output_file (str): Final output file path
        duration (int): Maximum recording duration in seconds 
        verbose (bool): Whether to show detailed output logs
        manual_stop_event (threading.Event, optional): Event to trigger manual stopping from outside
    
    Returns:
        str: Path to recorded audio file or None if failed
    """
    # Create a default manual stop event if none is provided
    if manual_stop_event is None:
        manual_stop_event = threading.Event()
    
    # Create event to stop recording after duration
    duration_stop_event = threading.Event()
    
    # Combine both events - will stop when either is triggered
    stop_event = threading.Event()
    
    try:
        if verbose:
            print("=== Starting High-Quality Audio Recording ===")
            print(f"Maximum recording duration: {duration} seconds")
            if manual_stop_event:
                print("Recording can be stopped early using external control")
            print(f"Final output will be saved to: {output_file}")
        
        # Create timer thread to stop after duration
        def duration_timer():
            time.sleep(duration)
            duration_stop_event.set()
            
        timer_thread = threading.Thread(target=duration_timer)
        timer_thread.daemon = True
        timer_thread.start()
        
        # Thread to monitor both stop events
        def monitor_events():
            while not stop_event.is_set():
                if manual_stop_event.is_set() or duration_stop_event.is_set():
                    stop_event.set()
                    if verbose and manual_stop_event.is_set():
                        print("Manual stop requested")
                    elif verbose and duration_stop_event.is_set():
                        print(f"Maximum duration of {duration} seconds reached")
                    break
                time.sleep(0.1)
                
        monitor_thread = threading.Thread(target=monitor_events)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        if verbose:
            print("\nStarting recording now...")
        
        # Start audio recording
        result = record_audio(output_file, verbose=verbose, stop_event=stop_event)
        
        if verbose:
            print("\n=== Recording Process Completed ===")
            if result:
                file_size = os.path.getsize(output_file) / (1024 * 1024)  # Size in MB
                print(f"Final file size: {file_size:.2f} MB")
                print(f"Recording saved to: {output_file}")
        
        return result
        
    except Exception as e:
        if verbose:
            print(f"Error in recording process: {str(e)}")
        # Set stop event to end audio recording if an error occurs
        stop_event.set()
        return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="High-quality audio recorder")
    parser.add_argument("-d", "--duration", type=int, default=10, help="Maximum recording duration in seconds")
    parser.add_argument("-o", "--output", type=str, default="audio_recording.wav", help="Output file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed logs during recording")
    parser.add_argument("-l", "--list", action="store_true", help="List available audio devices")
    parser.add_argument("-k", "--key", type=str, default="q", help="Key to press to manually stop recording (defaults to 'q')")
    parser.add_argument("--no-manual-interrupt", action="store_true", help="Disable manual interrupt capability")
    
    args = parser.parse_args()
    
    # List devices if requested
    if args.list:
        print("\n=== Available Audio Devices ===")
        list_audio_devices()
        exit(0)
    
    # Create manual stop event
    manual_stop_event = threading.Event()
    
    # Setup keyboard listener if manual interrupt is enabled
    if not args.no_manual_interrupt:
        try:
            from pynput import keyboard
            
            def on_press(key):
                try:
                    # Check if the pressed key matches the interrupt key
                    if hasattr(key, 'char') and key.char == args.key:
                        print(f"\nManual interrupt key '{args.key}' pressed.")
                        manual_stop_event.set()
                        return False  # Stop listener
                except AttributeError:
                    pass  # Special key, ignore
            
            # Start keyboard listener in a separate thread
            print(f"Press '{args.key}' to stop recording early")
            keyboard_listener = keyboard.Listener(on_press=on_press)
            keyboard_listener.daemon = True
            keyboard_listener.start()
        except ImportError:
            print("Warning: pynput module not found. Manual interrupt disabled.")
    
    # Record audio
    record_audio_only(
        output_file=args.output, 
        duration=args.duration, 
        verbose=args.verbose,
        manual_stop_event=manual_stop_event
    )