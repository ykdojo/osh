import os
import threading
import time
import pyaudio
import array
import audioop
from dotenv import load_dotenv
import google.generativeai as genai
from textual.app import App, ComposeResult
from textual.widgets import Static
from pynput import keyboard

# Load environment variables
load_dotenv()

class GeminiApp(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configure Gemini API
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
        
        # Audio recording configuration
        self.is_recording = False
        self.audio_thread = None
        self.audio_data = array.array('h')
        self.average_volume = 0
        self.pyaudio_instance = pyaudio.PyAudio()
        
        # PyAudio stream configuration
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        
        # Flag to track if the hotkey was pressed
        self.hotkey_pressed = False
        
        # Start global hotkey listener in a separate thread
        self.keyboard_thread = threading.Thread(target=self.start_keyboard_listener)
        self.keyboard_thread.daemon = True
        self.keyboard_thread.start()
    
    def get_gemini_response(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text
    
    def record_audio(self):
        """Record audio in a separate thread."""
        # Reset audio data
        self.audio_data = array.array('h')
        stream = self.pyaudio_instance.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        self.is_recording = True
        self.refresh_response()
        
        try:
            while self.is_recording:
                # Read audio chunks from microphone
                data = stream.read(self.chunk)
                self.audio_data.extend(array.array('h', data))
                
                # Calculate volume (RMS of the audio data)
                self.average_volume = audioop.rms(data, 2)  # 2 bytes per sample for paInt16
                
                # Update UI every 0.5 seconds
                if len(self.audio_data) % (self.rate // 2) == 0:
                    self.refresh_response()
        finally:
            stream.stop_stream()
            stream.close()
            self.refresh_response()
    
    def start_recording(self):
        """Start recording audio in a separate thread."""
        if self.is_recording:
            return
            
        self.audio_thread = threading.Thread(target=self.record_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()
    
    def stop_recording(self):
        """Stop recording audio."""
        if not self.is_recording:
            return
            
        self.is_recording = False
        if self.audio_thread:
            self.audio_thread.join(timeout=1.0)
            self.audio_thread = None
    
    def on_hotkey_activated(self):
        """Toggle recording when the hotkey is pressed."""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
        
        self.hotkey_pressed = True
        self.refresh_response()
    
    def refresh_response(self):
        # Schedule this to run in the main thread since Textual is not thread-safe
        self.call_from_thread(self._refresh_response)
    
    def _refresh_response(self):
        response_widget = self.query_one("#response")
        
        if self.is_recording:
            # Display recording status and audio level
            duration = len(self.audio_data) / (self.rate * self.channels)
            volume_bar = '█' * min(40, max(1, self.average_volume // 100))
            
            status = f"🔴 RECORDING ({duration:.1f} seconds)\n"
            status += f"Audio Level: {self.average_volume} {volume_bar}\n"
            status += "Press Shift+Command+Z again to stop recording."
            
            response_widget.update(status)
        elif self.hotkey_pressed and len(self.audio_data) > 0:
            # Recording stopped, show results
            duration = len(self.audio_data) / (self.rate * self.channels)
            prompt = f"Recording finished - {duration:.1f} seconds captured"
            response = f"Recording complete!\n\nAudio data captured: {len(self.audio_data)} samples\nDuration: {duration:.1f} seconds\nAverage volume: {self.average_volume}"
            
            response_widget.update(f"Prompt: {prompt}\n\nResponse:\n{response}")
        elif self.hotkey_pressed:
            prompt = "Shift+Command+Z was pressed!"
            response = "Hotkey detected! Press again to start recording."
            
            response_widget.update(f"Prompt: {prompt}\n\nResponse:\n{response}")
        else:
            prompt = "Hello"
            response = self.get_gemini_response(prompt)
            
            response_widget.update(f"Prompt: {prompt}\n\nResponse:\n{response}")
        
    def compose(self) -> ComposeResult:
        # Send a simple prompt to Gemini
        prompt = "Hello"
        response = self.get_gemini_response(prompt)
        yield Static(f"Prompt: {prompt}\n\nResponse:\n{response}", id="response")

    def on_mount(self) -> None:
        self.query_one("#response").styles.align = ("center", "middle")
    
    def on_unmount(self) -> None:
        """Clean up resources when the app exits."""
        if self.is_recording:
            self.stop_recording()
        self.pyaudio_instance.terminate()
    
    def start_keyboard_listener(self):
        # Define the hotkey combination (Shift+Command+Z on macOS)
        COMBINATION = {keyboard.Key.shift, keyboard.Key.cmd, keyboard.KeyCode.from_char('z')}
        current = set()
        
        def on_press(key):
            if key in COMBINATION:
                current.add(key)
                if all(k in current for k in COMBINATION):
                    self.on_hotkey_activated()
        
        def on_release(key):
            if key in COMBINATION:
                if key in current:
                    current.remove(key)
        
        # Start the listener
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

if __name__ == "__main__":
    app = GeminiApp()
    app.run()