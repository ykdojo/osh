#!/usr/bin/env python3
"""
Terminal-based keyboard shortcut handler with simple UI
Uses curses for proper terminal management
"""

import curses
import threading
import time
import pyperclip
import os

# Import the type_text function for typing transcription at cursor
from type_text import type_text
# Import the screen and audio recording function
from screen_audio_recorder import record_screen_and_audio
# Import keyboard shortcut handler
from keyboard_handler import KeyboardShortcutHandler
# Import video transcription function
from video_transcription import transcribe_video
# Import terminal UI functions
from terminal_ui import init_curses, cleanup_curses, display_screen_template

class CursesShortcutHandler:
    """Terminal UI with keyboard shortcut support using curses"""
    
    def __init__(self):
        self.is_recording = False
        self.is_running = True
        self.stdscr = None
        self.status_message = ""
        self.manual_stop_event = None
        self.recording_path = None
        self.recording_thread = None
        self.transcription = None
        
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
    
    def toggle_recording(self):
        """Toggle recording state when shortcut is pressed"""
        try:
            if self.is_recording:
                self.stop_recording()
            else:
                self.start_recording()
        except Exception as e:
            self.status_message = f"Error in toggle_recording: {e}"
            self.refresh_screen()
    
    def start_recording(self):
        """Start recording session with screen and audio"""
        # Create a new stop event for this recording session
        self.manual_stop_event = threading.Event()
        
        # Set the output path
        output_file = f"recording_{int(time.time())}.mp4"
        
        # Create and start the recording thread
        def recording_thread_func():
            try:
                self.recording_path = record_screen_and_audio(
                    output_file=output_file,
                    duration=60,  # Set a reasonable default duration
                    verbose=False,
                    manual_stop_event=self.manual_stop_event
                )
            except Exception as e:
                self.status_message = f"Recording error: {str(e)}"
                self.recording_path = None
                self.is_recording = False
                self.refresh_screen()
        
        self.recording_thread = threading.Thread(target=recording_thread_func)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        self.is_recording = True
        self.show_recording_screen()
    
    def refresh_screen(self):
        """Force screen refresh"""
        if self.stdscr:
            self.stdscr.refresh()
    
    def display_screen_template(self, title, content, footer_text=None):
        """Common screen display template to reduce code duplication"""
        display_screen_template(self.stdscr, title, content, self.status_message, footer_text)
    
    def stop_recording(self):
        """Stop the active recording session"""
        self.status_message = "Stopping recording..."
        self.refresh_screen()
        
        # Set the stop event to stop the recording
        if self.manual_stop_event:
            self.manual_stop_event.set()
        
        # Wait for the recording thread to complete
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=5)  # Wait up to 5 seconds
        
        self.is_recording = False
        self.show_recording_done_screen()
        return True
    
    def show_main_screen(self):
        """Display the main screen with options"""
        content = ["Status: Ready"]
        self.display_screen_template("VIDEO VOICE RECORDER", content)
    
    def show_recording_screen(self):
        """Display recording screen"""
        content = ["Recording active..."]
        footer = "Press ⇧⌥Z (Shift+Alt+Z) to stop recording"
        self.display_screen_template("RECORDING IN PROGRESS", content, footer)
    
    def show_recording_done_screen(self):
        """Display recording done screen with recording path info"""
        content = [
            "Your recording has been completed.", 
            "", 
            "Processing recording..."
        ]
        
        if self.recording_path:
            content.append(f"Recording saved to: {self.recording_path}")
            
            # Start transcription process in a separate thread
            def transcribe_thread_func():
                try:
                    self.status_message = "Transcribing video with Gemini AI..."
                    self.refresh_screen()
                    self.transcription = transcribe_video(
                        video_file_path=self.recording_path,
                        verbose=False
                    )
                    self.show_transcription()
                except Exception as e:
                    self.status_message = f"Transcription error: {str(e)}"
                    self.refresh_screen()
                    # Fall back to showing just the recording path if transcription fails
                    self.show_recording_path()
            
            # Show the processing screen
            self.display_screen_template("RECORDING DONE!", content)
            
            # Start transcription in a separate thread
            transcription_thread = threading.Thread(target=transcribe_thread_func)
            transcription_thread.daemon = True
            transcription_thread.start()
        else:
            content.append("Error: Recording failed or was interrupted")
            self.display_screen_template("RECORDING DONE!", content)
            # Show just the recording path after a delay
            threading.Timer(2.0, self.show_recording_path).start()
    
    def show_recording_path(self):
        """Display recording path info and copy to clipboard"""
        recording_info = ""
        
        if self.recording_path and os.path.exists(self.recording_path):
            # Get file size in MB
            file_size = os.path.getsize(self.recording_path) / (1024 * 1024)
            recording_info = f"Recording saved: {self.recording_path} ({file_size:.2f} MB)"
            
            # Copy path to clipboard
            pyperclip.copy(self.recording_path)
        else:
            recording_info = "Recording failed or file not found"
        
        # Display information about the recording
        content = [
            "Your recording has been completed.",
            "",
            "Recording information:",
            recording_info,
            "",
            "Recording path copied to clipboard."
        ]
        self.display_screen_template("RECORDING DONE!", content)
        
        # Type the recording path at the cursor position without countdown or verbose output
        if self.recording_path:
            type_text(self.recording_path, countdown=False, verbose=False)
            
    def show_transcription(self):
        """Display transcription and type it at cursor position"""
        # Update status message
        self.status_message = "Transcription complete!"
        
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