#!/usr/bin/env python3
import curses

class VoiceTranscriptionFunctions:
    """Simple voice transcription functionality"""
    
    def __init__(self):
        self.results = []
        self.is_recording = False
        self.current_mic = "Default Microphone"
    
    def transcribe(self, stdscr):
        """Record and transcribe voice with simple interface"""
        if not self.is_recording:
            # Start recording
            self.is_recording = True
            self.show_recording_screen(stdscr)
            return None
        else:
            # Stop recording
            self.is_recording = False
            result = f"Voice transcribed from {self.current_mic}"
            self.results.append(result)
            return result
            
    def show_recording_screen(self, stdscr):
        """Display a simple recording interface"""
        h, w = stdscr.getmaxyx()
        max_y = h - 1
        max_x = w - 1
        
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