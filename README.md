# OSH - Automate 99% of your typing for free

**Access the most advanced AI models** for voice transcription. OSH is the open-source solution that lets you speak instead of type, with screen-sharing capabilities that solve the problem of accurately capturing names and technical terms.

- **Free access**: Uses Gemini's API to transcribe your content at no cost
- **Screen + voice recording**: Ensures proper spelling of names and technical terms where other voice-only tools fail
- **Customizable vocabulary**: Add frequently used terms to improve transcription accuracy of specialized terms
- **Open source**: Full control to modify and extend functionality to fit your specific needs

OSH is the **O**pen-source terminal helper that can **S**ee your screen and **H**ear your voice.

> **Note**: This application is primarily designed for macOS but should work on other platforms (Linux, Windows) with appropriate configurations. Some features may require platform-specific adjustments.

## Features

- Terminal-based UI with simple navigation
- Global keyboard shortcuts (⇧⌥X for audio, ⇧⌥Z for screen recording)
- Audio-only or combined screen+audio recording
- Automatic transcription of recordings using Gemini AI
- Text-to-speech for clipboard content (⇧⌥A shortcut)
- Preservation of recording files for future reference
- Simple cleanup script for managing recording files

## Setup & Usage

1. Clone the repository and create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. On macOS, ensure you have portaudio installed (needed for PyAudio):
   ```bash
   brew install portaudio
   ```

4. Start the application:
   ```bash
   bash run.sh
   ```
   
   Or activate the environment manually:
   ```bash
   source activate_env.sh
   python terminal_video_voice_recorder.py
   ```

5. To clean up recording files when needed:
   ```bash
   bash cleanup_recordings.sh
   ```
   This will list all recording files and ask for confirmation before deletion.

6. To use the clipboard-to-speech functionality:
   ```bash
   bash run_clipboard_to_llm.sh
   ```
   Copy text to your clipboard, then press ⇧⌥A to have it read aloud using TTS.

## Keyboard Shortcuts

- **⇧⌥X (Shift+Alt+X)**: Toggle audio-only recording
- **⇧⌥Z (Shift+Alt+Z)**: Toggle screen+audio recording
- **⇧⌥A (Shift+Alt+A)**: Read clipboard content using TTS (when clipboard_to_llm is running)
- **Ctrl+C**: Exit the application

## Permission Requirements

- **Accessibility Permissions**: For keyboard event handling and typing functionality
  - Go to System Settings → Privacy & Security → Accessibility
  - Add your terminal application (Terminal, iTerm2, VS Code)

## Project Structure

- **Core Files**:
  - `terminal_video_voice_recorder.py`: Main application entry point
  - `keyboard_handler.py`: Global keyboard shortcut handling
  - `terminal_ui.py`: Terminal UI components
  
- **Recording Components**:
  - `recorders/recording_handler.py`: Manages recording sessions
  - `recorders/recorder.py`: Core recording functions
  - `audio_recorder.py`: Audio recording functionality
  - `screen_audio_recorder.py`: Screen+audio recording
  
- **Transcription Components**:
  - `transcription_handler.py`: Manages the transcription process
  - `audio_transcription.py`: Audio transcription with Gemini AI
  - `video_transcription.py`: Video transcription with Gemini AI
  
- **Utilities**:
  - `type_text.py`: Utility for typing transcribed text at cursor position
  - `cleanup_recordings.sh`: Script for cleaning up recording files
  - `typing_metrics.py`: Tracks characters and words transcribed 
  - `typing_metrics_web.py`: Web dashboard showing time saved metrics
  - `start_typing_metrics_web.sh`: Script to launch the typing metrics dashboard
  - `clipboard_to_llm.py`: Converts clipboard text to speech using TTS
  - `run_clipboard_to_llm.sh`: Script to run the clipboard-to-speech utility
  
- **Productivity Analytics**:
  - Records character and word counts for successful transcriptions
  - Estimates typing time saved based on configurable typing speed (default: 40 WPM)
  - Provides visualization via a simple web dashboard
  - Access at http://127.0.0.1:5050/ after running `./start_typing_metrics_web.sh`