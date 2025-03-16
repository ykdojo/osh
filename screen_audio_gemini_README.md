# Screen Audio Gemini

This tool combines screen/audio recording with Gemini AI video processing. It records your screen with synchronized audio, then optionally processes the recording with Gemini AI for transcription.

## Features

- High-quality screen recording using ffmpeg
- Synchronized audio recording
- Manual interrupt capability (press a key to stop recording)
- Optional Gemini AI transcription of recorded content
- Flexible configuration through command-line arguments

## Setup

1. Make sure the virtual environment is activated:
   ```
   source venv/bin/activate
   ```

2. For Gemini transcription, you need a Gemini API key:
   - Create a `.env` file in the project root
   - Add your Gemini API key: `GEMINI_API_KEY=your_api_key_here`

## Usage

### Basic recording (without transcription):

```bash
python3 screen_audio_gemini.py -d 10 --skip-transcription
```

### Recording with transcription:

```bash
python3 screen_audio_gemini.py -d 10
```

### List available devices:

```bash
python3 screen_audio_gemini.py -l
```

### All available options:

```bash
python3 screen_audio_gemini.py --help
```

Command-line options:
- `-d, --duration`: Recording duration in seconds (default: 7)
- `-o, --output`: Output file path (default: combined_recording.mp4)
- `-v, --verbose`: Show detailed logs during recording
- `-s, --screen`: Screen index to capture (use -l to see available screens)
- `-l, --list`: List available screen and audio devices
- `-k, --key`: Key to press to manually stop recording (default: q)
- `--no-manual-interrupt`: Disable manual interrupt capability
- `--skip-transcription`: Skip Gemini transcription step

## Integration

This script combines functionality from:
1. `screen_audio_recorder.py` - For screen and audio recording
2. `test_gemini_video.py` - For Gemini AI video processing

To use this functionality in your own scripts, you can import the main function:

```python
from screen_audio_gemini import record_and_process

# Record and process video
video_path, transcription = record_and_process(
    output_file='my_recording.mp4',
    duration=5,
    verbose=True,
    skip_transcription=False
)

# Do something with the transcription
if transcription:
    print(f"Transcription length: {len(transcription)} characters")
```