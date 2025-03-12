import os
from dotenv import load_dotenv
import google.generativeai as genai
from textual.app import App, ComposeResult
from textual.widgets import Static

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
    
    def get_gemini_response(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text
        
    def compose(self) -> ComposeResult:
        # Send a simple prompt to Gemini
        prompt = "Hello"
        response = self.get_gemini_response(prompt)
        yield Static(f"Prompt: {prompt}\n\nResponse:\n{response}", id="response")

    def on_mount(self) -> None:
        self.query_one("#response").styles.align = ("center", "middle")

if __name__ == "__main__":
    app = GeminiApp()
    app.run()