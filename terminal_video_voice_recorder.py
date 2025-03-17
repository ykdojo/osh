#!/usr/bin/env python3
"""
Terminal-based keyboard shortcut handler with simple UI
Uses curses for proper terminal management
"""

import curses
import threading
import time
from pynput import keyboard
from pynput.keyboard import Controller, Key

class CursesShortcutHandler:
    """Terminal UI with keyboard shortcut support using curses"""
    
    def __init__(self):
        self.is_recording = False
        self.keyboard_listener = None
        self.is_running = True
        self.stdscr = None
        self.status_message = ""
    
    def init_curses(self):
        """Initialize curses environment"""
        self.stdscr = curses.initscr()
        curses.noecho()  # Don't echo keypresses
        curses.cbreak()  # React to keys instantly
        self.stdscr.keypad(True)  # Enable keypad mode
        
        # Try to enable colors if terminal supports it
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()  # Use terminal's default colors for better visibility
            
            # Slightly more vibrant but still subtle colors
            curses.init_pair(1, 209, -1)  # Title - slightly brighter coral/orange
            curses.init_pair(2, 68, -1)   # Highlight - slightly brighter blue
            curses.init_pair(3, 147, -1)  # Footer - slightly brighter grayish-lavender
    
    def cleanup_curses(self):
        """Clean up curses on exit"""
        if self.stdscr:
            self.stdscr.keypad(False)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
    
    def start_keyboard_listener(self):
        """Start listening for the keyboard shortcut"""
        # Define the hotkey combinations
        SHORTCUT_COMBO = {keyboard.Key.shift, keyboard.Key.alt, keyboard.KeyCode.from_char('z')}
        EXIT_COMBO = {keyboard.Key.ctrl_l, keyboard.KeyCode.from_char('c')}
        current = set()
        
        def on_press(key):
            try:
                # Add key to current set if it's part of the shortcut
                if key in SHORTCUT_COMBO or key in EXIT_COMBO:
                    current.add(key)
                
                # Check for special character "¸" which is produced by Shift+Alt+Z on Mac
                if isinstance(key, keyboard.KeyCode) and hasattr(key, 'char') and key.char == "¸":
                    self.status_message = "Shortcut triggered: Shift+Alt+Z (¸)"
                    self.refresh_screen()
                    
                    # Create a keyboard controller to send backspace
                    kb = Controller()
                    
                    # Send backspace to delete the "¸" character
                    kb.press(Key.backspace)
                    kb.release(Key.backspace)
                    
                    self.toggle_recording()
                    return True
                
                # Check for key combinations
                elif all(k in current for k in SHORTCUT_COMBO):
                    self.status_message = "Keyboard shortcut triggered: ⇧⌥Z"
                    self.refresh_screen()
                    self.toggle_recording()
                    return True
                elif all(k in current for k in EXIT_COMBO):
                    self.status_message = "Exiting..."
                    self.refresh_screen()
                    self.is_running = False
                    return False  # Stop listener
                
            except Exception as e:
                self.status_message = f"Error in keyboard listener: {e}"
                self.refresh_screen()
            
            return True  # Continue listening
        
        def on_release(key):
            try:
                # Remove key from current pressed keys
                if key in current:
                    current.remove(key)
            except Exception as e:
                self.status_message = f"Error in keyboard release: {e}"
                self.refresh_screen()
            
            return self.is_running  # Continue listening if app is running
                
        # Only start if not already running
        if self.keyboard_listener is None or not self.keyboard_listener.is_alive():
            try:
                # Start the listener
                self.keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
                self.keyboard_listener.daemon = True
                self.keyboard_listener.start()
                self.status_message = "Keyboard shortcut listener started"
                self.refresh_screen()
            except Exception as e:
                self.status_message = f"Failed to start keyboard listener: {e}"
                self.refresh_screen()
    
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
        """Start recording session (placeholder)"""
        self.is_recording = True
        self.show_recording_screen()
    
    def refresh_screen(self):
        """Force screen refresh"""
        if self.stdscr:
            self.stdscr.refresh()
    
    def display_screen_template(self, title, content, footer_text=None):
        """Common screen display template to reduce code duplication"""
        if not self.stdscr:
            return
            
        # Clear screen
        self.stdscr.clear()
        
        # Get terminal dimensions
        height, width = self.stdscr.getmaxyx()
        
        # Display border and title
        self.stdscr.addstr(0, 0, "=" * (width-1))
        
        # Title with color if available
        if curses.has_colors():
            self.stdscr.addstr(1, 0, title.center(width-1), curses.color_pair(1))
        else:
            self.stdscr.addstr(1, 0, title.center(width-1))
            
        self.stdscr.addstr(2, 0, "=" * (width-1))
        
        # Display content
        line_num = 4
        for line in content:
            self.stdscr.addstr(line_num, 0, line)
            line_num += 1
        
        # Display footer
        footer_line = height - 3
        
        # Footer with color if available
        if curses.has_colors():
            color = curses.color_pair(3)
        else:
            color = curses.A_NORMAL
            
        if footer_text:
            self.stdscr.addstr(footer_line, 0, footer_text, color)
        else:
            self.stdscr.addstr(footer_line, 0, "Press ⇧⌥Z (Shift+Alt+Z) to start/stop recording", color)
            self.stdscr.addstr(footer_line + 1, 0, "Press Ctrl+C to exit", color)
        
        # Bottom border
        self.stdscr.addstr(height-1, 0, "=" * (width-1))
        
        # Display status message if any
        if self.status_message:
            msg_y = height - 5
            self.stdscr.addstr(msg_y, 0, self.status_message, curses.A_DIM)
        
        # Update the screen
        self.stdscr.refresh()
    
    def stop_recording(self):
        """Stop recording session (placeholder)"""
        self.status_message = "Stopping recording..."
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
        """Display recording done screen with mock transcription"""
        content = ["Your recording has been completed.", "", "Transcribing..."]
        self.display_screen_template("RECORDING DONE!", content)
        
        # Mock the transcription process with a delay
        threading.Timer(3.0, self.show_transcription).start()
    
    def show_transcription(self):
        """Display mock transcription results"""
        transcript = "This is a mock transcription of what would be the audio content. In a real implementation, this would be the text generated by an AI model after processing the recorded audio from this session."
        content = [
            "Your recording has been completed.",
            "",
            "Transcription:",
            transcript
        ]
        self.display_screen_template("RECORDING DONE!", content)
    
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
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                
            # Clean up curses
            self.cleanup_curses()

if __name__ == "__main__":
    app = CursesShortcutHandler()
    app.run()