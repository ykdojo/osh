#!/usr/bin/env python3
"""
Terminal-based voice recording handler with simple UI
Uses curses for proper terminal management
"""

import curses
import threading
import time
import pyperclip
import os

# Import the type_text function for typing transcription at cursor
from type_text import type_text
# Import keyboard shortcut handler
from keyboard_handler import KeyboardShortcutHandler
# Import transcription functions
from audio_transcription import transcribe_audio
from video_transcription import transcribe_video
# Import terminal UI functions
from terminal_ui import init_curses, cleanup_curses, display_screen_template
# Import recording session handler
from recorders.recording_handler import RecordingSession

class CursesShortcutHandler:
    """Terminal UI with keyboard shortcut support using curses"""
    
    def __init__(self):
        self.is_running = True
        self.stdscr = None
        self.status_message = ""
        self.transcription = None
        
        # Initialize recording session handler
        self.recording_session = RecordingSession(status_callback=self.set_status_message)
        
        # Initialize keyboard handler with callbacks
        self.keyboard_handler = KeyboardShortcutHandler({
            'toggle': self.toggle_recording,
            'exit': self.set_exit,
            'status': self.set_status_message
        })
    
    def set_status_message(self, message):
        """Set status message and refresh screen"""
        self.status_message = message
        self.refresh_screen()
        
    def set_exit(self):
        """Set exit flag"""
        self.is_running = False
    
    def init_curses(self):
        """Initialize curses environment"""
        self.stdscr = curses.initscr()
        self.stdscr = init_curses(self.stdscr)
    
    def cleanup_curses(self):
        """Clean up curses on exit"""
        cleanup_curses(self.stdscr)
    
    def start_keyboard_listener(self):
        """Start the keyboard shortcut listener"""
        self.keyboard_handler.start()
    
    def toggle_recording(self, mode="audio"):
        """
        Toggle recording state when shortcut is pressed
        
        Args:
            mode (str): 'audio' for audio-only or 'video' for screen and audio
        """
        try:
            if self.recording_session.is_recording:
                if self.recording_session.stop():
                    self.show_recording_done_screen()
            else:
                if self.recording_session.start(mode):
                    self.show_recording_screen(mode)
        except Exception as e:
            self.status_message = f"Error in toggle_recording: {e}"
            self.refresh_screen()
    
    def refresh_screen(self):
        """Force screen refresh"""
        if self.stdscr:
            self.stdscr.refresh()
    
    def display_screen_template(self, title, content, footer_text=None):
        """Common screen display template to reduce code duplication"""
        display_screen_template(self.stdscr, title, content, self.status_message, footer_text)
    
    
    def show_main_screen(self):
        """Display the main screen with options"""
        content = [
            "Status: Ready", 
            "",
            "Recording options:",
            "• Audio only (⇧⌥X): Record voice without capturing screen",
            "• Screen + Audio (⇧⌥Z): Record both screen and voice"
        ]
        self.display_screen_template("AUDIO/VIDEO RECORDER", content)
    
    def show_recording_screen(self, mode="audio"):
        """
        Display recording screen
        
        Args:
            mode (str): 'audio' for audio-only or 'video' for screen and audio
        """
        if mode == "audio":
            content = ["Voice Recording active...", "Capturing audio only"]
            footer = "Press ⇧⌥X (Shift+Alt+X) to stop recording"
            self.display_screen_template("VOICE RECORDING IN PROGRESS", content, footer)
        else:  # video mode
            content = ["Screen Recording active...", "Capturing screen and audio"]
            footer = "Press ⇧⌥Z (Shift+Alt+Z) to stop recording"
            self.display_screen_template("SCREEN RECORDING IN PROGRESS", content, footer)
    
    def show_recording_done_screen(self):
        """Display recording done screen with recording path info"""
        content = [
            "Your recording has been completed.", 
            "", 
            "Processing recording..."
        ]
        
        if self.recording_session.recording_path:
            content.append(f"Recording saved to: {self.recording_session.recording_path}")
            
            # Start transcription process in a separate thread
            def transcribe_thread_func():
                try:
                    if self.recording_session.recording_mode == "audio":
                        self.status_message = "Transcribing audio with Gemini AI..."
                        self.refresh_screen()
                        self.transcription = transcribe_audio(
                            audio_file_path=self.recording_session.recording_path,
                            verbose=False
                        )
                    else:  # video mode
                        self.status_message = "Transcribing video with Gemini AI..."
                        self.refresh_screen()
                        self.transcription = transcribe_video(
                            video_file_path=self.recording_session.recording_path,
                            verbose=False
                        )
                    
                    # Remove the recording file after successful transcription
                    if self.transcription and os.path.exists(self.recording_session.recording_path):
                        try:
                            os.remove(self.recording_session.recording_path)
                            self.status_message = f"Transcription complete! Recording file deleted."
                        except Exception as e:
                            self.status_message = f"Transcription complete! Failed to remove recording: {e}"
                        
                    self.show_transcription()
                except Exception as e:
                    self.status_message = f"Transcription error: {str(e)}"
                    self.refresh_screen()
                    # Fall back to showing just the recording path if transcription fails
                    self.show_recording_path()
            
            # Show the processing screen with appropriate title based on recording mode
            title = "VOICE RECORDING DONE!" if self.recording_session.recording_mode == "audio" else "SCREEN RECORDING DONE!"
            self.display_screen_template(title, content)
            
            # Start transcription in a separate thread
            transcription_thread = threading.Thread(target=transcribe_thread_func)
            transcription_thread.daemon = True
            transcription_thread.start()
        else:
            error_type = "Voice" if self.recording_session.recording_mode == "audio" else "Screen"
            content.append(f"Error: {error_type} recording failed or was interrupted")
            title = "VOICE RECORDING DONE!" if self.recording_session.recording_mode == "audio" else "SCREEN RECORDING DONE!"
            self.display_screen_template(title, content)
            # Show just the recording path after a delay
            threading.Timer(2.0, self.show_recording_path).start()
    
    def show_recording_path(self):
        """Display recording path info and copy to clipboard"""
        # Check if the recording file still exists (if transcription failed)
        if self.recording_session.recording_path and not os.path.exists(self.recording_session.recording_path):
            # If we're here without transcription but the file is gone, it means
            # transcription failed after the file was deleted, or something unexpected happened
            content = [
                "Your recording has been completed, but the file is no longer available.",
                "",
                "The recording file may have been deleted or moved."
            ]
            
            # Set appropriate title
            title = "RECORDING UNAVAILABLE"
            self.display_screen_template(title, content)
            return
            
        recording_info = self.recording_session.get_recording_info()
        
        # Determine correct message based on recording mode
        recording_type = "voice" if self.recording_session.recording_mode == "audio" else "screen"
        
        # Display information about the recording
        content = [
            f"Your {recording_type} recording has been completed.",
            "",
            "Recording information:",
            recording_info,
            "",
            "Recording path copied to clipboard."
        ]
        
        # Add note about transcription if it failed
        if self.transcription is None:
            content.append("")
            content.append("Note: Transcription was not completed. The recording file is preserved.")
        
        # Set appropriate title
        title = "VOICE RECORDING DONE!" if self.recording_session.recording_mode == "audio" else "SCREEN RECORDING DONE!"
        self.display_screen_template(title, content)
        
        # Type the recording path at the cursor position without countdown or verbose output
        if self.recording_session.recording_path and os.path.exists(self.recording_session.recording_path):
            pyperclip.copy(self.recording_session.recording_path)
            type_text(self.recording_session.recording_path, countdown=False, verbose=False)
            
    def show_transcription(self):
        """Display transcription and type it at cursor position"""
        # If transcription failed or is empty, fall back to showing the recording path
        if not self.transcription:
            self.show_recording_path()
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
            
        # Copy full transcription to clipboard
        pyperclip.copy(self.transcription)
        
        # Display information about the transcription
        content = [
            "Your recording has been transcribed!",
            "",
            "Transcription preview:"
        ]
        
        # Add truncated transcription lines
        content.extend(display_lines)
        
        # Add info about clipboard
        content.append("")
        content.append("Full transcription copied to clipboard.")
        
        # Add note about deleted recording file
        if not os.path.exists(self.recording_session.recording_path):
            content.append("Recording file has been deleted after successful transcription.")
        
        # Display the screen
        self.display_screen_template("TRANSCRIPTION COMPLETE!", content)
        
        # Type the transcription at the cursor position without countdown or verbose output
        type_text(self.transcription, countdown=False, verbose=False)
    
    def run(self):
        """Main application loop"""
        try:
            # Initialize curses
            self.init_curses()
            
            # Start keyboard listener
            self.start_keyboard_listener()
            
            # Display main screen
            self.show_main_screen()
            
            # Keep application running until exit signal
            while self.is_running:
                time.sleep(0.1)  # Small sleep to prevent CPU usage
        
        except KeyboardInterrupt:
            self.status_message = "Exiting..."
            self.refresh_screen()
        
        finally:
            # Clean up
            self.keyboard_handler.stop()
                
            # Clean up curses
            self.cleanup_curses()

if __name__ == "__main__":
    app = CursesShortcutHandler()
    app.run()