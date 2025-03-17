#!/usr/bin/env python3
"""
Terminal-based keyboard shortcut handler with simple UI
Uses plain terminal output instead of curses for better compatibility with print statements
"""

import os
import sys
import time
import threading
from pynput import keyboard
from pynput.keyboard import Controller, Key

class TerminalShortcutHandler:
    """Simple terminal UI with keyboard shortcut support"""
    
    def __init__(self):
        self.is_recording = False
        self.keyboard_listener = None
        self.is_running = True
        
    def clear_screen(self):
        """Clear the terminal screen in a cross-platform way"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
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
                    print("\nShortcut triggered: Shift+Alt+Z (¸)")
                    
                    # Create a keyboard controller to send backspace
                    kb = Controller()
                    
                    # Send backspace to delete the "¸" character
                    kb.press(Key.backspace)
                    kb.release(Key.backspace)
                    
                    self.toggle_recording()
                    return True
                
                # Check for key combinations
                elif all(k in current for k in SHORTCUT_COMBO):
                    print("\nKeyboard shortcut triggered: ⇧⌥Z")
                    self.toggle_recording()
                    return True
                elif all(k in current for k in EXIT_COMBO):
                    print("\nExiting...")
                    self.is_running = False
                    return False  # Stop listener
                
            except Exception as e:
                print(f"Error in keyboard listener: {e}")
            
            return True  # Continue listening
        
        def on_release(key):
            try:
                # Remove key from current pressed keys
                if key in current:
                    current.remove(key)
            except Exception as e:
                print(f"Error in keyboard release: {e}")
            
            return self.is_running  # Continue listening if app is running
                
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
            if self.is_recording:
                self.stop_recording()
            else:
                self.start_recording()
        except Exception as e:
            print(f"Error in toggle_recording: {e}")
    
    def start_recording(self):
        """Start recording session (placeholder)"""
        self.is_recording = True
        self.clear_screen()
        self.show_recording_screen()
    
    def display_screen_template(self, title, content, footer_text=None):
        """Common screen display template to reduce code duplication"""
        self.clear_screen()
        print("\n")
        print("=" * 60)
        print(f"{title:^60}")
        print("=" * 60)
        print("\n")
        
        # Display content
        for line in content:
            print(f"  {line}")
        
        print("\n")
        
        # Display footer if provided, otherwise use default
        if footer_text:
            print(f"  {footer_text}")
        else:
            print("  Press ⇧⌥Z (Shift+Alt+Z) to start/stop recording")
            print("  Press Ctrl+C to exit")
        
        print("\n")
        print("=" * 60)
    
    def stop_recording(self):
        """Stop recording session (placeholder)"""
        print("Stopping recording...")
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
        """Display recording done screen"""
        content = ["Your recording has been completed."]
        self.display_screen_template("RECORDING DONE!", content)
    
    def run(self):
        """Main application loop"""
        try:
            # Start keyboard listener
            self.start_keyboard_listener()
            
            # Display main screen
            self.show_main_screen()
            
            # Keep application running until exit signal
            while self.is_running:
                time.sleep(0.1)  # Small sleep to prevent CPU usage
        
        except KeyboardInterrupt:
            print("\nExiting...")
        
        finally:
            # Clean up
            if self.keyboard_listener:
                self.keyboard_listener.stop()
            
            print("Application closed.")

if __name__ == "__main__":
    app = TerminalShortcutHandler()
    app.run()