#!/usr/bin/env python3
"""
Terminal-based voice recording handler with simple UI
Uses curses for proper terminal management
"""

import curses
import threading
import time
import os

# Import keyboard shortcut handler
from keyboard_handler import KeyboardShortcutHandler
# Import terminal UI functions
from terminal_ui import init_curses, cleanup_curses, display_screen_template
# Import recording session handler
from recorders.recording_handler import RecordingSession
# Import transcription handler
from transcription_handler import TranscriptionHandler

class CursesShortcutHandler:
    """Terminal UI with keyboard shortcut support using curses"""
    
    def __init__(self):
        self.is_running = True
        self.stdscr = None
        self.status_message = ""
        
        # Initialize recording session handler
        self.recording_session = RecordingSession(status_callback=self.set_status_message)
        
        # Initialize transcription handler
        self.transcription_handler = TranscriptionHandler(
            ui_callback=self.display_screen_template,
            status_callback=self.set_status_message
        )
        
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
            
            # Show the processing screen with appropriate title based on recording mode
            title = "VOICE RECORDING DONE!" if self.recording_session.recording_mode == "audio" else "SCREEN RECORDING DONE!"
            self.display_screen_template(title, content)
            
            # Start transcription using our handler
            self.transcription_handler.transcribe(
                self.recording_session.recording_path,
                self.recording_session.recording_mode
            )
        else:
            error_type = "Voice" if self.recording_session.recording_mode == "audio" else "Screen"
            content.append(f"Error: {error_type} recording failed or was interrupted")
            title = "VOICE RECORDING DONE!" if self.recording_session.recording_mode == "audio" else "SCREEN RECORDING DONE!"
            self.display_screen_template(title, content)
    
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