"""
Recorders module for handling screen and audio recording
"""

# Import core functionality to make it available at package level
from recorders.utils import list_audio_devices, list_screen_devices, combine_audio_video
from recorders.recorder import record_audio, record_screen