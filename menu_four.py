#!/usr/bin/env python3

class VoiceTranscriptionFunctions:
    """Simple voice transcription functionality"""
    
    def __init__(self):
        self.results = []
    
    def transcribe(self):
        """Record and transcribe voice"""
        return "Voice transcribed"
    
    def get_results(self):
        """Return the results of previous operations"""
        if not self.results:
            return ["No transcriptions performed yet"]
        return self.results

# Create a singleton instance
voice_transcription_functions = VoiceTranscriptionFunctions()