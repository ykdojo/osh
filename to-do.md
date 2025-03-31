# Project To-Do List

## High Priority

### 1. Fix Tooltip on Estimated Time Saved Website
- Tooltip functionality was previously implemented but was lost
- Related files:
  - `/Users/yk/osh/templates/dashboard.html` - Contains the dashboard UI
  - `/Users/yk/osh/typing_metrics_web.py` - Contains the `get_data()` route that provides tooltip data
- The WPM setting (currently set to 40 WPM) should be displayed in a tooltip
- Check commit history for recent changes that may have removed this functionality

### 2. Fix Keyboard Listeners Inconsistency
- Keyboard shortcuts sometimes stop working after a while
- Sometimes only work in the terminal where the app is running, not globally
- Related files:
  - `/Users/yk/osh/keyboard_handler.py` - Main keyboard shortcut handling implementation
- Issues to investigate:
  - Possible memory leaks or resource contention
  - Thread-related issues in the keyboard listener
  - System permissions for keyboard access
  - Consider implementing periodic reconnection of listeners

### 3. Implement Speech Speed Adjustment
- Need to add ability to speed up speech without changing pitch
- Already have a working implementation in `/Users/yk/osh/speed_up_audio.py`
- Need to incorporate this into the clipboard-to-LLM feature
- Related files:
  - `/Users/yk/osh/clipboard_to_llm.py` - Main feature that needs speed adjustment
  - `/Users/yk/osh/gemini_tts_test.py` - Handles TTS functionality
- Current implementation already has a speed_factor parameter in GeminiTTS (set to 1.1)
- Need to add user controls to adjust speed during runtime