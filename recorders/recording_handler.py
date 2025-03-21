#!/usr/bin/env python3
"""
Recording handler module to manage audio and video recording sessions
"""

import os
import time
import threading
from audio_recorder import record_audio_only
from screen_audio_recorder import record_screen_and_audio

class RecordingSession:
    """Manages a recording session with audio and video"""
    
    def __init__(self, status_callback=None, recording_started_callback=None):
        self.is_recording = False
        self.recording_path = None
        self.recording_thread = None
        self.manual_stop_event = None
        self.status_callback = status_callback
        self.recording_started_callback = recording_started_callback
        self.recording_mode = None  # 'audio' or 'video'
        self.recording_actually_started = False
    
    def set_status(self, message):
        """Update status message via callback if provided"""
        if self.status_callback:
            self.status_callback(message)
    
    def start(self, mode="audio"):
        """
        Start recording session with audio only or screen and audio
        
        Args:
            mode (str): 'audio' for audio-only or 'video' for screen and audio
        """
        if self.is_recording:
            return False
            
        # Create a new stop event for this recording session
        self.manual_stop_event = threading.Event()
        
        # Reset recording started flag
        self.recording_actually_started = False
        
        # Store the recording mode
        self.recording_mode = mode
        
        # Custom callback function for when ffmpeg/recording process actually starts
        def on_recording_started():
            self.recording_actually_started = True
            if self.recording_started_callback:
                self.recording_started_callback(mode)
        
        # Set the output path based on recording mode
        timestamp = int(time.time())
        if mode == "audio":
            output_file = f"recording_{timestamp}.wav"
            
            # Create and start the recording thread for audio only
            def recording_thread_func():
                try:
                    # Signal that recording is about to start (preparation phase)
                    self.set_status("Preparing audio devices...")
                    
                    # Call record_audio_only with a callback
                    self.recording_path = record_audio_only(
                        output_file=output_file,
                        duration=7200,  # Set to 2 hours (7200 seconds)
                        verbose=False,
                        manual_stop_event=self.manual_stop_event,
                        on_recording_started=on_recording_started,
                        status_callback=self.status_callback
                    )
                except Exception as e:
                    self.set_status(f"Audio recording error: {str(e)}")
                    self.recording_path = None
                    self.is_recording = False
        else:  # video mode
            output_file = f"recording_{timestamp}.mp4"
            
            # Create and start the recording thread for screen and audio
            def recording_thread_func():
                try:
                    # Signal that recording is about to start (preparation phase)
                    self.set_status("Preparing screen and audio devices...")
                    
                    # Call record_screen_and_audio with a callback
                    self.recording_path = record_screen_and_audio(
                        output_file=output_file,
                        duration=7200,  # Set to 2 hours (7200 seconds)
                        verbose=False,
                        manual_stop_event=self.manual_stop_event,
                        on_recording_started=on_recording_started,
                        status_callback=self.status_callback
                    )
                except Exception as e:
                    self.set_status(f"Screen recording error: {str(e)}")
                    self.recording_path = None
                    self.is_recording = False
        
        self.recording_thread = threading.Thread(target=recording_thread_func)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        self.is_recording = True
        return True
    
    def stop(self):
        """Stop the active recording session and return the recording path and mode"""
        if not self.is_recording:
            return None, None
            
        self.set_status("Stopping recording...")
        
        # Set the stop event to stop the recording
        if self.manual_stop_event:
            self.manual_stop_event.set()
        
        # Wait for the recording thread to complete
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=5)  # Wait up to 5 seconds
        
        self.is_recording = False
        
        # Return the recording path and mode directly
        recording_path = self.recording_path
        recording_mode = self.recording_mode
        
        # Reset the instance state
        self.recording_path = None
        self.recording_mode = None
        
        return recording_path, recording_mode
    
    def get_recording_info(self):
        """Get information about the completed recording"""
        if not self.recording_path or not os.path.exists(self.recording_path):
            return "Recording failed or file not found"
        
        # Get file size in MB
        file_size = os.path.getsize(self.recording_path) / (1024 * 1024)
        
        # Include recording mode information
        mode_info = "Audio only" if self.recording_mode == "audio" else "Screen and audio"
        return f"{mode_info} recording saved: {self.recording_path} ({file_size:.2f} MB)"