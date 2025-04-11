# Claude Code Preferences

## Git Preferences
- Do not include co-authorship lines in commits
- Do not add Claude Code attribution in commit messages
- Push commits to origin after committing changes

## Memory Instructions
- When asked to "remember" something, add it to this CLAUDE.md file
- Store all important project conventions, rules, and structures here for future reference

## Project Information
- This is a Textual-based Python application with Gemini AI integration
- The app uses pynput for global keyboard shortcuts
- Adding chmod permissions to Python files is not necessary
- To open GitHub Desktop, use the terminal command "github" (not to be confused with "gh" which is the GitHub CLI)

## Environment Setup
- Python scripts should use the virtual environment in the venv directory
- Use `source activate_env.sh` to activate the virtual environment
- The application requires a .env file with API keys (never commit or open this file)
- A .env.sample file should exist to show the required environment variables without real values
- Before installing new Python packages or running pip commands, always activate the virtual environment first
- When adding new dependencies, always update requirements.txt

## Security Rules
- Never read, display, or access .env files or any files containing credentials/API keys
- Do not access or display sensitive information such as API keys, passwords, or tokens
- Inform the user if they're about to commit sensitive information

## Project Structure Notes
- Main files:
  - menu_system.py - Handles UI and menu navigation with curses
  - voice_transcription.py - Handles voice recording functionality and keyboard shortcuts
  - screen_audio_recorder.py - Orchestrates screen and audio recording, combining them into a final output
  - screen_audio_gemini.py - Combines screen/audio recording with Gemini transcription
- The recorders module contains core recording functionality:
  - recorders/utils.py - Utility functions for device listing and audio/video combining
  - recorders/recorder.py - Core functions for audio and screen recording
  - recorders/recording_handler.py - Manages recording sessions for both audio and video
- The menu system is in menu_system.py with main menu and submenus defined in the main() function
- Functional menus should have their implementation in separate files
- Voice transcription is the primary menu and should always be the first option
- Keep all menus simple and minimal - avoid adding unnecessary options
- Other files are supporting files or legacy code
- Remember to make incremental changes rather than large rewrites
- Recording files are automatically deleted after successful transcription

## File Reorganization Plans
- Consider renaming `recorder.py` to `capture_functions.py` to better describe its role
- Move functionality from `audio_recorder.py` to `recorders/audio.py` 
- Move functionality from `screen_audio_recorder.py` to `recorders/screen_audio.py`
- This would better organize code by keeping recorder-related code in the recorders folder
- Need to search for all import statements referencing these files to update them

## Common Words Feature
- Edit the common_words.txt file to customize how transcriptions handle specific words
- Gemini will preserve the exact form of these words in transcriptions
- This is useful for technical terms, brand names, product names, etc.
- The common_words.txt file is loaded by the load_common_words() function in transcription_prompts.py
- Add one word per line, blank lines and lines starting with # are ignored
- These words are used in both audio and video transcription prompts

## Transcription Prompts
- Shared prompt text is maintained in transcription_prompts.py
- Audio and video transcription prompts are defined in this central module
- Contains the load_common_words() function for common words inclusion
- Provides get_audio_transcription_prompt() and get_video_transcription_prompt() functions

## Typing Metrics Feature
- Tracks character and word counts from successful transcriptions
- Stores data in typing_metrics.csv in the project directory
- Integrates with the transcription flow via transcription_handler.py
- Web dashboard available via typing_metrics_web.py (port 5050)
- Uses Chart.js for professional visualization
- Calculates time saved based on standard typing speed (40 WPM)
- View data by day, week, or month

## Design Preferences
- Use subtle, muted colors rather than vibrant ones
- Menu highlights: Use light dusty blue (color 74), not grayish or too vibrant blue
- Title text: Subtle coral/orange (color 173) that complements the blue highlight
- Footer: Light grayish-lavender (color 145) for better visibility
- Use complementary colors that work well together (blue selection with orange title)
- Minimalist approach: Make small, incremental changes and validate with user
- When user says "remember stuff", update this CLAUDE.md file