#!/usr/bin/env python3
"""
Utility functions for recording devices
"""

import sounddevice as sd
import subprocess
import ffmpeg

def list_audio_devices():
    """List all available audio input devices"""
    print("Available audio input devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:  # Only input devices
            print(f"[{i}] {device['name']} (Inputs: {device['max_input_channels']})")
    return devices

def list_screen_devices(print_output=True):
    """
    List available avfoundation devices (screens) with enhanced descriptions.
    
    Args:
        print_output (bool): Whether to print the device list
        
    Returns:
        dict: Dictionary mapping screen indices to screen names
    """
    try:
        # This command lists available devices on macOS
        result = subprocess.run(
            ['ffmpeg', '-f', 'avfoundation', '-list_devices', 'true', '-i', ''],
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Only print if requested
        if print_output:
            print(result.stderr)
            
        # Get more detailed display information from system_profiler
        display_info = {}
        try:
            displays = subprocess.run(
                ['system_profiler', 'SPDisplaysDataType'],
                stdout=subprocess.PIPE,
                text=True
            )
            
            # Extract display names with better parsing
            display_data = displays.stdout
            in_display_section = False
            current_display = None
            
            for line in display_data.split('\n'):
                line = line.strip()
                
                # Check if we've reached the displays section
                if "Displays:" in line:
                    in_display_section = True
                    continue
                
                if not in_display_section:
                    continue
                    
                # Start of a new display entry
                if line and ":" in line and not line.startswith(" "):
                    current_display = line.split(":")[0].strip()
                    display_info[current_display] = {
                        "name": current_display,
                        "is_main": False,
                        "resolution": "",
                        "type": ""
                    }
                # Properties within a display entry
                elif current_display and ":" in line:
                    key, value = [x.strip() for x in line.split(":", 1)]
                    
                    if key == "Main Display" and value == "Yes":
                        display_info[current_display]["is_main"] = True
                    elif key == "Resolution":
                        display_info[current_display]["resolution"] = value
                    elif key == "Display Type":
                        display_info[current_display]["type"] = value
        except Exception as display_err:
            if print_output:
                print(f"Warning: Could not get detailed display info: {str(display_err)}")
            
        # Parse the output to extract screen names
        screens = {}
        lines = result.stderr.split('\n')
        for line in lines:
            if '[AVFoundation indev' in line and 'Capture screen' in line:
                parts = line.strip().split('] [')
                if len(parts) >= 2:
                    index_part = parts[1].split(']')[0]
                    name_part = parts[1].split('] ')[1]
                    try:
                        index = int(index_part)
                        
                        # Try to enhance screen descriptions with more details
                        if "Capture screen" in name_part and display_info:
                            screen_num = name_part.split("Capture screen ")[1]
                            
                            # In macOS, Capture screen 0 is typically the main display
                            if screen_num == "0":
                                for display_name, info in display_info.items():
                                    if info.get("is_main"):
                                        display_type = info.get("type", "")
                                        desc = display_name
                                        if display_type:
                                            desc = f"{display_name} ({display_type})"
                                        name_part = f"Capture screen 0 - {desc}"
                                        break
                            # Other displays
                            else:
                                # Find any non-main displays
                                non_main_displays = [d for d, info in display_info.items() if not info.get("is_main")]
                                if len(non_main_displays) >= int(screen_num):
                                    display_name = non_main_displays[int(screen_num)-1]
                                    info = display_info[display_name]
                                    resolution = info.get("resolution", "").split(" @")[0]
                                    if resolution:
                                        name_part = f"Capture screen {screen_num} - {display_name} ({resolution})"
                                    else:
                                        name_part = f"Capture screen {screen_num} - {display_name}"
                                    
                        screens[index] = name_part
                    except:
                        pass
                        
        return screens
    except Exception as e:
        if print_output:
            print(f"Error listing devices: {str(e)}")
        return {}

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