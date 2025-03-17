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
        
        # Define the hotkey combinations
        self.SHORTCUT_COMBO = {keyboard.Key.shift, keyboard.Key.alt, keyboard.KeyCode.from_char('x')}
        self.EXIT_COMBO = {keyboard.Key.ctrl_l, keyboard.KeyCode.from_char('c')}
    
    def _handle_keypress(self, key, current):
        """
        Handle key press events
        
        Args:
            key: The key that was pressed
            current: Set of currently pressed keys
            
        Returns:
            True to continue listening, False to stop
        """
        try:
            # Add key to current set if it's part of the shortcut
            if key in self.SHORTCUT_COMBO or key in self.EXIT_COMBO:
                current.add(key)
            
            # Check for special character "˛" which is produced by Shift+Alt+X on Mac
            if isinstance(key, keyboard.KeyCode) and hasattr(key, 'char') and key.char == "˛":
                self.callbacks['status']("Shortcut triggered: Shift+Alt+X (˛)")
                
                # Delete the "˛" character
                kb = Controller()
                kb.press(Key.backspace)
                kb.release(Key.backspace)
                
                self.callbacks['toggle']()
                return True
            
            # Check for key combinations
            elif all(k in current for k in self.SHORTCUT_COMBO):
                self.callbacks['status']("Keyboard shortcut triggered: ⇧⌥X")
                self.callbacks['toggle']()
                return True
            elif all(k in current for k in self.EXIT_COMBO):
                self.callbacks['status']("Exiting...")
                self.is_running = False
                return False  # Stop listener
                
        except Exception as e:
            self.callbacks['status'](f"Error in keyboard listener: {e}")
        
        return True  # Continue listening

    def _handle_key_release(self, key, current):
        """
        Handle key release events
        
        Args:
            key: The key that was released
            current: Set of currently pressed keys
            
        Returns:
            True to continue listening, False to stop
        """
        try:
            # Remove key from current pressed keys
            if key in current:
                current.remove(key)
        except Exception as e:
            self.callbacks['status'](f"Error in keyboard release: {e}")
        
        return self.is_running  # Continue listening if app is running

    def start(self):
        """Start listening for keyboard shortcuts"""
        # Set to track currently pressed keys
        current = set()
        
        # Create handler functions with closure over current set
        def on_press(key):
            return self._handle_keypress(key, current)
        
        def on_release(key):
            return self._handle_key_release(key, current)
                
        # Only start if not already running
        if self.keyboard_listener is None or not self.keyboard_listener.is_alive():
            try:
                # Start the listener
                self.keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
                self.keyboard_listener.daemon = True
                self.keyboard_listener.start()
                self.callbacks['status']("Keyboard shortcut listener started")
                return True
            except Exception as e:
                self.callbacks['status'](f"Failed to start keyboard listener: {e}")
                return False
    
    def stop(self):
        """Stop the keyboard listener"""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None