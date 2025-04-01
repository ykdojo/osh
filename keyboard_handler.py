#!/usr/bin/env python3
"""
Keyboard shortcut handler module for terminal applications
Provides keyboard shortcut detection and callback execution
"""

from pynput import keyboard
from pynput.keyboard import Controller, Key

class KeyboardShortcutHandler:
    """Handles keyboard shortcuts for terminal applications"""
    
    def __init__(self, callback_functions):
        """
        Initialize keyboard handler with callback functions
        
        Args:
            callback_functions: Dict with keys 'toggle', 'exit', 'status'
                - toggle: Function to call when shortcut is triggered
                - exit: Function to call when exit combo is triggered
                - status: Function to update status messages
        """
        self.keyboard_listener = None
        self.is_running = True
        self.callbacks = callback_functions
    
    def _handle_keypress(self, key):
        """
        Handle key press events
        
        Args:
            key: The key that was pressed
            
        Returns:
            True to continue listening, False to stop
        """
        try:
            # Check for special character "˛" which is produced by Shift+Alt+X on Mac (audio shortcut)
            if isinstance(key, keyboard.KeyCode) and hasattr(key, 'char') and key.char == "˛":
                self.callbacks['status']("Audio shortcut triggered: Shift+Alt+X (˛)")
                
                # Delete the "˛" character
                kb = Controller()
                kb.press(Key.backspace)
                kb.release(Key.backspace)
                
                self.callbacks['toggle']("audio")
                return True
            
            # Check for special character "¸" which is produced by Shift+Alt+Z on Mac (video shortcut)
            if isinstance(key, keyboard.KeyCode) and hasattr(key, 'char') and key.char == "¸":
                self.callbacks['status']("Video shortcut triggered: Shift+Alt+Z (¸)")
                
                # Delete the "¸" character
                kb = Controller()
                kb.press(Key.backspace)
                kb.release(Key.backspace)
                
                self.callbacks['toggle']("video")
                return True
            
            # Direct check for Ctrl+C similar to clipboard_to_llm.py
            if key == keyboard.Key.ctrl_l and hasattr(key, 'vk'):
                self.callbacks['status']("Exiting...")
                self.is_running = False
                return False  # Stop listener
                
        except Exception as e:
            self.callbacks['status'](f"Error in keyboard listener: {e}")
        
        return True  # Continue listening

    def _handle_key_release(self, key):
        """
        Handle key release events
        
        Args:
            key: The key that was released
            
        Returns:
            True to continue listening, False to stop
        """
        # We're not tracking keys anymore, just return running state
        return self.is_running  # Continue listening if app is running

    def start(self):
        """Start listening for keyboard shortcuts"""
        # Try to stop any existing listener first
        if self.keyboard_listener is not None:
            try:
                self.keyboard_listener.stop()
            except:
                pass
            self.keyboard_listener = None
            
        # Create handler functions
        def on_press(key):
            return self._handle_keypress(key)
        
        def on_release(key):
            return self._handle_key_release(key)
        
        try:
            # Start the listener with a clean state
            self.keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
            self.keyboard_listener.daemon = True
            self.keyboard_listener.start()
            self.callbacks['status']("Keyboard shortcut listener started")
            
            # Give a moment for the listener to initialize
            import time
            time.sleep(0.1)
            
            # Verify it actually started
            if not self.keyboard_listener.is_alive():
                raise Exception("Listener failed to start")
                
            return True
        except Exception as e:
            self.callbacks['status'](f"Failed to start keyboard listener: {e}")
            self.keyboard_listener = None
            return False
    
    def stop(self):
        """Stop the keyboard listener and release resources"""
        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
            except Exception as e:
                if self.callbacks and 'status' in self.callbacks:
                    self.callbacks['status'](f"Error stopping keyboard listener: {e}")
            finally:
                self.keyboard_listener = None
                
        # Reset our running state to ensure a clean restart if needed
        self.is_running = False