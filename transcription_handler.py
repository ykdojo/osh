#!/usr/bin/env python3
"""
Transcription handler for audio and video recordings.
Manages the transcription process and results presentation.
"""

import os
import threading
from audio_transcription import transcribe_audio
from video_transcription import transcribe_video
from type_text import type_text

class TranscriptionHandler:
    """Handles transcription of audio and video recordings"""
    
    def __init__(self, ui_callback=None, status_callback=None):
        """
        Initialize the transcription handler
        
        Args:
            ui_callback: Function to call to update UI with content
            status_callback: Function to call to update status message
        """
        self.ui_callback = ui_callback
        self.status_callback = status_callback
        self.transcription = None
    
    def set_status(self, message):
        """Update status via callback"""
        if self.status_callback:
            self.status_callback(message)
    
    def transcribe(self, recording_path, recording_mode):
        """
        Start transcription process in a separate thread
        
        Args:
            recording_path: Path to the recording file
            recording_mode: 'audio' or 'video'
        """
        # Start transcription in a separate thread
        transcription_thread = threading.Thread(
            target=self._transcribe_thread_func,
            args=(recording_path, recording_mode)
        )
        transcription_thread.daemon = True
        transcription_thread.start()
        
        return transcription_thread
    
    def _transcribe_thread_func(self, recording_path, recording_mode):
        """Thread function to handle transcription process"""
        try:
            if recording_mode == "audio":
                self.set_status("Transcribing audio with Gemini AI...")
                self.transcription = transcribe_audio(
                    audio_file_path=recording_path,
                    verbose=False
                )
            else:  # video mode
                self.set_status("Transcribing video with Gemini AI...")
                self.transcription = transcribe_video(
                    video_file_path=recording_path,
                    verbose=False
                )
            
            # Keep all recording files (both audio and video)
            if self.transcription and os.path.exists(recording_path):
                self.set_status("Transcription complete! Recording file preserved.")
            
            # Show transcription results
            self.show_transcription(recording_path)
        except Exception as e:
            self.set_status(f"Transcription error: {str(e)}")
            # Fall back to showing just the recording path if transcription fails
            self.show_recording_path(recording_path, recording_mode)
    
    def show_transcription(self, recording_path):
        """Display transcription and type it at cursor position"""
        # If transcription failed or is empty, fall back to showing the recording path
        if not self.transcription:
            return
        
        # Prepare transcription display content
        # Truncate the transcription to around 5 lines for display
        transcription_display = self.transcription[:500]
        if len(self.transcription) > 500:
            transcription_display += "..."
            
        # Split into lines for display
        display_lines = []
        for i in range(0, len(transcription_display), 60):
            display_lines.append(transcription_display[i:i+60])
        
        # Display information about the transcription
        content = [
            "Your recording has been transcribed!",
            "",
            "Transcription preview:",
            ""  # Add a blank line after the preview heading
        ]
        
        # Add truncated transcription lines
        content.extend(display_lines)
        
        # Add separator and info about typing
        content.append("")
        content.append("")
        content.append("-----")
        content.append("")
        content.append("Transcription has been typed at your cursor position.")
        
        # Add note about recording file location
        if os.path.exists(recording_path):
            content.append("")
            content.append(f"Recording file preserved at: {recording_path}")
        
        # Update UI via callback
        if self.ui_callback:
            self.ui_callback("TRANSCRIPTION COMPLETE!", content)
        
        # Type the transcription at the cursor position without countdown or verbose output
        type_text(self.transcription, countdown=False, verbose=False)
    
    def show_recording_path(self, recording_path, recording_mode):
        """Display recording path info when transcription fails"""
        # Determine correct message based on recording mode
        recording_type = "voice" if recording_mode == "audio" else "screen"
        
        # Check if the recording file still exists
        if recording_path and not os.path.exists(recording_path):
            content = [
                "Your recording has been completed, but the file is no longer available.",
                "",
                "The recording file may have been deleted or moved."
            ]
            
            # Update UI via callback
            if self.ui_callback:
                self.ui_callback("RECORDING UNAVAILABLE", content)
            return
        
        # Get file size in MB if file exists
        if recording_path and os.path.exists(recording_path):
            file_size = os.path.getsize(recording_path) / (1024 * 1024)
            recording_info = f"{recording_type.capitalize()} recording saved: {recording_path} ({file_size:.2f} MB)"
            
            # Display information about the recording
            content = [
                f"Your {recording_type} recording has been completed.",
                "",
                "Recording information:",
                recording_info,
                "",
                "Recording path has been typed at your cursor position."
            ]
            
            # Add note about transcription failure
            content.append("")
            content.append("Note: Transcription was not completed. The recording file is preserved.")
            
            # Set appropriate title
            title = "VOICE RECORDING DONE!" if recording_mode == "audio" else "SCREEN RECORDING DONE!"
            
            # Update UI via callback
            if self.ui_callback:
                self.ui_callback(title, content)
            
            # Type the recording path at the cursor position without countdown or verbose output
            if recording_path and os.path.exists(recording_path):
                type_text(recording_path, countdown=False, verbose=False)
        else:
            # Handle case where recording path doesn't exist
            content = [
                f"Your {recording_type} recording has been completed, but the file was not saved.",
                "",
                "The recording file may have been deleted or was not created properly."
            ]
            
            # Set appropriate title
            title = "RECORDING UNAVAILABLE"
            
            # Update UI via callback
            if self.ui_callback:
                self.ui_callback(title, content)