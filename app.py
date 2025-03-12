from textual.app import App, ComposeResult
from textual.widgets import Static

class HelloWorld(App):
    def compose(self) -> ComposeResult:
        yield Static("Hello, World!", id="hello")

    def on_mount(self) -> None:
        self.query_one("#hello").styles.align = ("center", "middle")

if __name__ == "__main__":
    app = HelloWorld()
    app.run()