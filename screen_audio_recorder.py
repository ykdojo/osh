#!/usr/bin/env python3
"""
High-quality screen and audio recorder
Records screen with ffmpeg and audio with sounddevice separately,
then combines them for optimal quality
"""

import subprocess
import time
import os
import tempfile
import threading
import ffmpeg

# Import utility functions and core recording functions
from recorders.utils import combine_audio_video, list_screen_devices, list_audio_devices
from recorders.recorder import record_audio, record_screen


def record_screen_and_audio(output_file='combined_recording.mp4', duration=7, verbose=False, 
                        screen_index=None, manual_stop_event=None, on_recording_started=None,
                        status_callback=None):
    """
    Record high-quality screen and audio simultaneously using threading,
    with audio recording stopping when screen recording finishes
    
    Args:
        output_file (str): Final output file path
        duration (int): Recording duration in seconds for screen recording
        verbose (bool): Whether to show detailed output logs
        screen_index (int, optional): Screen index to capture, if None will use default
        manual_stop_event (threading.Event, optional): Event to trigger manual stopping from outside
        on_recording_started (callable, optional): Callback function to execute when recording actually starts
        status_callback (callable, optional): Callback function to report status updates
    
    Returns:
        str: Path to final combined file or None if failed
    """
    # Import threading here to avoid global import
    import threading
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_video:
        temp_video_path = temp_video.name
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
        temp_audio_path = temp_audio.name
    
    # Variable to hold the result of audio recording
    audio_result = [None]  # Use list to allow modification in thread
    
    # Create an event to signal when screen recording is done
    stop_event = threading.Event()
    
    # Create a default manual stop event if none is provided
    if manual_stop_event is None:
        manual_stop_event = threading.Event()
    
    try:
        if verbose:
            print("=== Starting High-Quality Recording ===")
            print(f"Screen recording duration: {duration} seconds")
            print("Audio will record until screen recording completes")
            if manual_stop_event:
                print("Recording can be stopped early using external control")
            print(f"Final output will be saved to: {output_file}")
        
        # Get screen devices but don't print output
        screen_devices = list_screen_devices(print_output=False)
        
        # If no screen index provided, use the last available screen index
        if screen_index is None:
            # Get the highest screen index available (usually the last screen)
            if screen_devices:
                screen_to_use = max(screen_devices.keys())
            else:
                # Fallback to index 1 if no screens detected
                screen_to_use = 1
        else:
            screen_to_use = screen_index
            
        screen_name = screen_devices.get(screen_to_use, f"Unknown screen at index {screen_to_use}")
        if verbose:
            print(f"Screen to capture: {screen_name}")
        
        # Define function to run audio recording in a thread
        def audio_recording_thread():
            try:
                audio_result[0] = record_audio(temp_audio_path, verbose=verbose, stop_event=stop_event, status_callback=status_callback)
            except Exception as e:
                if verbose:
                    print(f"Error in audio recording thread: {str(e)}")
                audio_result[0] = None
        
        # Create thread for audio recording
        audio_thread = threading.Thread(target=audio_recording_thread)
        
        if verbose:
            print("\nStarting recording now...")
        
        # Start audio recording thread
        audio_thread.start()
        
        # Setup a callback for when the ffmpeg process actually starts
        def on_screen_record_start():
            if verbose:
                print("Screen recording process has actually started")
            # Call the external callback if provided
            if on_recording_started:
                on_recording_started()
        
        # Start screen recording using the updated function and ensure all output is suppressed
        # when not in verbose mode by passing verbose flag
        screen_result = record_screen(
            temp_video_path, 
            duration, 
            framerate=30, 
            resolution='1280x720', 
            screen_index=screen_to_use,
            stop_event=manual_stop_event,
            verbose=verbose,
            on_process_start=on_screen_record_start
        )
        
        screen_complete_time = time.time()
        
        # Signal audio thread to stop recording without duplicate message
        stop_event.set()
        
        # Wait for audio thread to complete
        audio_thread.join()
        audio_complete_time = time.time()
        
        # Calculate the time difference
        time_diff = audio_complete_time - screen_complete_time
        if verbose:
            print(f"Time difference between screen and audio completion: {time_diff:.4f} seconds")
        
        # Check if both recordings succeeded
        if not os.path.exists(temp_video_path) or not audio_result[0]:
            if verbose:
                print("Error: Screen or audio recording failed")
            return None
        
        if verbose:
            print("\nCombining video and audio...")
        result = combine_audio_video(temp_video_path, audio_result[0], output_file, verbose=verbose, time_diff=time_diff)
        
        # Clean up temporary files
        try:
            os.remove(temp_video_path)
            os.remove(temp_audio_path)
        except:
            pass
            
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
        
        # Clean up temporary files
        try:
            os.remove(temp_video_path)
            os.remove(temp_audio_path)
        except:
            pass
        return None

if __name__ == "__main__":
    import argparse
    import threading
    
    parser = argparse.ArgumentParser(description="High-quality screen and audio recorder")
    parser.add_argument("-d", "--duration", type=int, default=7, help="Recording duration in seconds")
    parser.add_argument("-o", "--output", type=str, default="combined_recording.mp4", help="Output file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed logs during recording")
    parser.add_argument("-s", "--screen", type=int, help="Screen index to capture (run with -l to see available screens)")
    parser.add_argument("-l", "--list", action="store_true", help="List available screen and audio devices")
    parser.add_argument("-k", "--key", type=str, default="q", help="Key to press to manually stop recording (defaults to 'q')")
    parser.add_argument("--no-manual-interrupt", action="store_true", help="Disable manual interrupt capability")
    
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
    
    # Record screen and audio
    record_screen_and_audio(
        output_file=args.output, 
        duration=args.duration, 
        verbose=args.verbose,
        screen_index=args.screen,
        manual_stop_event=manual_stop_event
    )