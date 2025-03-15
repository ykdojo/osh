#!/usr/bin/env python3
import curses
import threading
from pynput import keyboard

class VoiceTranscriptionFunctions:
    """Voice transcription functionality with keyboard shortcut support"""
    
    def __init__(self):
        self.results = []
        self.is_recording = False
        self.current_mic = "Default Microphone"
        self.keyboard_listener = None
        self.stdscr = None
        self.menu_system = None
        
    def start_keyboard_listener(self):
        """Start listening for the keyboard shortcut"""
        # Define the hotkey combination
        SHORTCUT_COMBO = {keyboard.Key.shift, keyboard.Key.cmd, keyboard.KeyCode.from_char('z')}
        current = set()
        
        def on_press(key):
            try:
                # Check if the key is part of our shortcut
                if key in SHORTCUT_COMBO:
                    current.add(key)
                    # If all keys in the combo are pressed, toggle recording
                    if all(k in current for k in SHORTCUT_COMBO):
                        print("Keyboard shortcut triggered: ⇧⌘Z")
                        self.toggle_recording()
            except Exception as e:
                print(f"Error in keyboard listener: {e}")
        
        def on_release(key):
            try:
                # Remove key from current pressed keys
                if key in SHORTCUT_COMBO and key in current:
                    current.remove(key)
            except Exception as e:
                print(f"Error in keyboard release: {e}")
                
        # Only start if not already running
        if self.keyboard_listener is None or not self.keyboard_listener.is_alive():
            try:
                # Start the listener
                self.keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
                self.keyboard_listener.daemon = True
                self.keyboard_listener.start()
                print("Keyboard shortcut listener started")
            except Exception as e:
                print(f"Failed to start keyboard listener: {e}")
        
    def toggle_recording(self):
        """Toggle recording state when shortcut is pressed"""
        try:
            print(f"Toggle recording: current state={self.is_recording}, menu={self.menu_system.current_menu if self.menu_system else 'None'}")
            
            if self.is_recording:
                # Stop recording
                self.stop_recording()
                
                # Return to voice menu
                if self.menu_system and self.stdscr:
                    self.menu_system.current_menu = "menu_voice"
                    try:
                        self.menu_system.draw_menu(self.stdscr)
                    except Exception as e:
                        print(f"Error drawing menu: {e}")
            else:
                # Start recording if we have necessary references
                if self.menu_system and self.stdscr:
                    self.start_recording()
                else:
                    print("Cannot start recording - missing menu system or screen reference")
        except Exception as e:
            print(f"Error in toggle_recording: {e}")
    
    def set_menu_system(self, menu_system):
        """Set reference to the menu system for navigation"""
        self.menu_system = menu_system
    
    def start_recording(self):
        """Start recording session"""
        print("Starting recording")
        self.is_recording = True
        
        # Switch to recording screen menu
        if self.menu_system:
            self.menu_system.current_menu = "recording_screen"
            
        # Show the recording UI
        if self.stdscr:
            try:
                self.show_recording_screen(self.stdscr)
            except Exception as e:
                print(f"Error showing recording screen: {e}")
    
    def stop_recording(self):
        """Stop recording session"""
        print("Stopping recording")
        self.is_recording = False
        result = f"Voice transcribed from {self.current_mic}"
        self.results.append(result)
        print(f"Recording stopped: {result}")
        return result
    
    def transcribe(self, stdscr):
        """Start transcription from menu selection"""
        self.stdscr = stdscr
        
        if not self.is_recording:
            # Start new recording session
            self.start_recording()
        else:
            # Stop existing recording
            self.stop_recording()
            
    def show_recording_screen(self, stdscr):
        """Display a simple recording interface"""
        h, w = stdscr.getmaxyx()
        max_y = h - 1
        max_x = w - 1
        
        # Set current menu to recording screen
        if self.menu_system:
            self.menu_system.current_menu = "recording_screen"
        
        # Clear screen
        stdscr.clear()
        
        # Draw border
        stdscr.box()
        
        # Draw title
        title = " RECORDING "
        x_pos = (w - len(title)) // 2
        if x_pos > 0:
            if curses.has_colors():
                stdscr.addstr(0, x_pos, title, curses.color_pair(2) | curses.A_BOLD)
            else:
                stdscr.addstr(0, x_pos, title, curses.A_BOLD)
        
        # Simple recording message
        recording_msg = f"Recording using {self.current_mic}..."
        x_pos = (w - len(recording_msg)) // 2
        if x_pos > 0:
            stdscr.addstr(h // 2 - 2, x_pos, recording_msg)
        
        # Instructions
        instruction = "Press ⇧⌘Z to stop recording"
        x_pos = (w - len(instruction)) // 2
        if x_pos > 0:
            stdscr.addstr(h // 2 + 2, x_pos, instruction)
        
        stdscr.refresh()
    
    def get_results(self):
        """Return the results of previous operations"""
        if not self.results:
            return ["No transcriptions performed yet"]
        return self.results

# Create a singleton instance
voice_transcription_functions = VoiceTranscriptionFunctions()