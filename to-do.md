# Project To-Do List

## High Priority

### 1. Fix Tooltip on Estimated Time Saved Website
- Tooltip functionality was previously implemented but was lost
- Related files:
  - `/Users/yk/osh/templates/dashboard.html` - Contains the dashboard UI
  - `/Users/yk/osh/typing_metrics_web.py` - Contains the `get_data()` route that provides tooltip data
- The WPM setting (currently set to 40 WPM) should be displayed in a tooltip
- Check commit history for recent changes that may have removed this functionality

### 2. Implement Speech Speed Adjustment
- Need to add ability to speed up speech without changing pitch
- Already have a working implementation in `/Users/yk/osh/speed_up_audio.py`
- Need to incorporate this into the clipboard-to-LLM feature
- Related files:
  - `/Users/yk/osh/clipboard_to_llm.py` - Main feature that needs speed adjustment
  - `/Users/yk/osh/gemini_tts_test.py` - Handles TTS functionality
- Current implementation already has a speed_factor parameter in GeminiTTS (set to 1.1)
- Need to add user controls to adjust speed during runtime

### 3. Add Reading Metrics Visualization
- Create visualization for clipboard-to-LLM feature
- Track and visualize text-to-speech conversion metrics
- Related files:
  - `/Users/yk/osh/clipboard_to_llm.py` - Feature to track metrics from
  - `/Users/yk/osh/typing_metrics_web.py` - Similar implementation exists for typing
- Use interesting content-based metrics such as:
  - Number of pages converted to speech
  - Number of books (equivalent) listened to
  - Number of paragraphs processed
- Include filtering options (day/week/month) similar to typing metrics