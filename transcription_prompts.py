#!/usr/bin/env python3
"""
Shared transcription prompts and utilities for Gemini AI transcription
"""

import os

def load_common_words():
    """
    Load common words from the common_words.txt file
    
    Returns:
        list: List of common words to incorporate in prompts
    """
    common_words = []
    common_words_path = os.path.join(os.path.dirname(__file__), "common_words.txt")
    
    if os.path.exists(common_words_path):
        try:
            with open(common_words_path, "r") as f:
                for line in f:
                    # Skip comments and empty lines
                    line = line.strip()
                    if line and not line.startswith("#"):
                        common_words.append(line)
        except Exception as e:
            print(f"Error loading common words: {e}") if __debug__ else None
    
    return common_words

def get_common_words_section():
    """
    Get the formatted common words section for prompts
    
    Returns:
        str: Formatted common words section for prompts
    """
    common_words = load_common_words()
    common_words_section = ""
    
    if common_words:
        common_words_section = "\n        IMPORTANT TERMS TO PRESERVE EXACTLY:\n        - " + "\n        - ".join(common_words) + "\n"
    
    return common_words_section

def get_common_instructions():
    """
    Get the common instructions section used in both audio and video transcription prompts
    
    Returns:
        str: Formatted common instructions 
    """
    return """
        - Clean up speech disfluencies: remove filler words, repetitions, stutters, false starts, self-corrections, and verbal crutches
        - You MUST NOT include phrases like "Here's the transcript:" or any other headers
        - You MUST NOT add timestamps or speaker attributions 
        - You MUST NOT include any introductory or concluding remarks
        - You MUST begin immediately with the transcribed content
        - Use punctuation that naturally fits the context - not every phrase needs a period (question marks for questions, colons for introductions, no punctuation for fragments or headers, etc.)
        - Preserve speech tone and emotion - use exclamation marks for excitement, enthusiasm, or strong emotions, even if it's subtle or mild
        - If the speaker uses incomplete sentences or fragments, preserve them when they're intentional
        - Preserve contractions exactly as spoken (e.g., "I'm" stays as "I'm", not expanded to "I am")
        - Structure paragraphs naturally: group 1-5 related sentences together and only add paragraph breaks for significant topic changes
        - Preserve the original meaning while substantially improving speech clarity
        - ALWAYS maintain the exact capitalization of proper names and terms (e.g., "Claude Code" with both capital Cs)
        - IMPORTANT: Preserve evaluative terms EXACTLY as spoken (e.g., "very good" must not be changed to "pretty good")
        - Format lists properly: one item per line with preserved numbering or bullets
        - Improve sentence flow: avoid starting with "But" or "And" and combine sentences with appropriate conjunctions when needed"""

def get_common_goal():
    """
    Get the common goal statement used in both audio and video transcription prompts
    
    Returns:
        str: Formatted common goal statement
    """
    return """
        Your goal is to produce a transcript that reads as if it were written text rather than spoken words.
        Make it concise, clear, and professional - as if it had been carefully edited for publication."""

def get_audio_transcription_prompt():
    """
    Get the complete prompt for audio transcription
    
    Returns:
        str: Complete audio transcription prompt with common words
    """
    common_words_section = get_common_words_section()
    common_instructions = get_common_instructions()
    common_goal = get_common_goal()
    
    return f"""
        Create a natural, context-appropriate transcription of this audio recording, removing speech disfluencies but preserving the speaker's intent and style.
        
        IMPORTANT: 
        - If there is any audio, attempt to transcribe it even if it seems like background noise
        - Only if there is absolutely no audio at all (complete silence), return exactly "NO_AUDIO"
        - If you've confirmed there is audio but cannot detect any speech, return "NO_AUDIBLE_SPEECH"{common_words_section}
        
        Critical instructions:
{common_instructions}
        - Preserve all technical terms, names, and specialized vocabulary accurately
{common_goal}
        """

def get_video_transcription_prompt():
    """
    Get the complete prompt for video transcription
    
    Returns:
        str: Complete video transcription prompt with common words
    """
    common_words_section = get_common_words_section()
    common_instructions = get_common_instructions()
    common_goal = get_common_goal()
    
    return f"""
        Create a natural, context-appropriate transcription of this video, removing speech disfluencies while carefully using the visual content as context and preserving the speaker's intent and style.
        
        IMPORTANT: 
        - If there is any audio, attempt to transcribe it even if it seems like background noise
        - Only if there is absolutely no audio at all (complete silence), return exactly "NO_AUDIO"
        - If you've confirmed there is audio but cannot detect any speech, return "NO_AUDIBLE_SPEECH"
        - You MUST return these indicators even if there is visual content/activity on the screen{common_words_section}
        
        Critical instructions:
{common_instructions}
        - Pay careful attention to text and names visible on screen (file names, people names, place names)
        - When the speaker refers to on-screen elements, preserve those references accurately
        - Pay special attention to cursor position as it indicates context for insertion points and formatting
        - Note the formatting around the cursor position as it affects how content should be structured
        - Capture technical terms, code, and commands with 100% accuracy
        - Follow the specific capitalization patterns shown on-screen for names, brands, and technical terms
{common_goal}
        """