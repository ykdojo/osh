# Claude Code Preferences

## Git Preferences
- Do not include co-authorship lines in commits
- Do not add Claude Code attribution in commit messages

## Memory Instructions
- When asked to "remember" something, add it to this CLAUDE.md file
- Store all important project conventions, rules, and structures here for future reference

## Project Information
- This is a Textual-based Python application with Gemini AI integration
- The app uses pynput for global keyboard shortcuts
- Adding chmod permissions to Python files is not necessary

## Project Structure Notes
- Main files:
  - menu_system.py - Handles UI and menu navigation with curses
  - voice_transcription.py - Handles voice recording functionality and keyboard shortcuts
- The menu system is in menu_system.py with main menu and submenus defined in the main() function
- Functional menus should have their implementation in separate files
- Voice transcription is the primary menu and should always be the first option
- Keep all menus simple and minimal - avoid adding unnecessary options
- Other files are supporting files or legacy code

## Current Development Plans
- Next step: Modify audio/video recording to allow stopping at any time rather than using fixed time limits
- Step after: Implement transcription of recorded voice with Gemini AI
- Focus on flexible, user-controlled recording before expanding transcription features

## Design Preferences
- Use subtle, muted colors rather than vibrant ones
- Menu highlights: Use light dusty blue (color 74), not grayish or too vibrant blue
- Title text: Subtle coral/orange (color 173) that complements the blue highlight
- Footer: Light grayish-lavender (color 145) for better visibility
- Use complementary colors that work well together (blue selection with orange title)
- Minimalist approach: Make small, incremental changes and validate with user
- When user says "remember stuff", update this CLAUDE.md file