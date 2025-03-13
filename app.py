import os
import threading
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
        
        # Flag to track if the hotkey was pressed
        self.hotkey_pressed = False
        
        # Start global hotkey listener in a separate thread
        self.keyboard_thread = threading.Thread(target=self.start_keyboard_listener)
        self.keyboard_thread.daemon = True
        self.keyboard_thread.start()
    
    def get_gemini_response(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text
    
    def on_hotkey_activated(self):
        # This will be called when the hotkey is pressed
        self.hotkey_pressed = True
        self.refresh_response()
    
    def refresh_response(self):
        # Schedule this to run in the main thread since Textual is not thread-safe
        self.call_from_thread(self._refresh_response)
    
    def _refresh_response(self):
        response_widget = self.query_one("#response")
        if self.hotkey_pressed:
            prompt = "Shift+Command+Z was pressed!"
            response = "Hotkey detected! The app has responded to the global shortcut."
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