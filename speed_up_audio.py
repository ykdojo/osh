#!/usr/bin/env python3
import argparse
import librosa
import soundfile as sf
import os

def speed_up_audio(input_file, output_file=None, speed_factor=1.5, preserve_pitch=True):
    """
    Speed up an audio file without changing the pitch.
    
    Args:
        input_file (str): Path to the input audio file
        output_file (str, optional): Path to save the output audio file. If None, 
                                     creates a file with "_speedup" suffix.
        speed_factor (float): Speed factor (1.0 = original speed, 2.0 = twice as fast)
        preserve_pitch (bool): Whether to preserve pitch (True) or not (False)
    
    Returns:
        str: Path to the output audio file
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Create output filename if not provided
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_speedup{ext}"
    
    # Load the audio file
    print(f"Loading audio file: {input_file}")
    y, sr = librosa.load(input_file, sr=None)  # sr=None preserves original sample rate
    
    # Get original duration
    original_duration = librosa.get_duration(y=y, sr=sr)
    
    # Speed up the audio without changing pitch
    if preserve_pitch:
        # Time-stretch without pitch change
        print(f"Processing audio at {speed_factor}x speed (preserving pitch)...")
        y_fast = librosa.effects.time_stretch(y, rate=speed_factor)
    else:
        # Simple resampling (changes pitch)
        print(f"Processing audio at {speed_factor}x speed (with pitch change)...")
        y_fast = librosa.effects.pitch_shift(y, sr=sr, n_steps=12*librosa.hz_to_midi(speed_factor))
    
    # Get processed duration
    processed_duration = librosa.get_duration(y=y_fast, sr=sr)
    
    # Save the processed audio
    print(f"Saving processed audio to: {output_file}")
    sf.write(output_file, y_fast, sr)
    
    # Report duration change
    print(f"\nAudio Information:")
    print(f"  Original duration: {original_duration:.2f} seconds")
    print(f"  Processed duration: {processed_duration:.2f} seconds")
    print(f"  Time saved: {original_duration - processed_duration:.2f} seconds ({speed_factor:.1f}x faster)")
    
    return output_file

def main():
    parser = argparse.ArgumentParser(description="Speed up audio without changing pitch")
    parser.add_argument("input_file", help="Path to the input audio file")
    parser.add_argument("-o", "--output-file", help="Path to save the output audio file")
    parser.add_argument("-s", "--speed", type=float, default=1.5, 
                        help="Speed factor (1.0 = original speed, 2.0 = twice as fast)")
    parser.add_argument("--change-pitch", action="store_true", 
                        help="Allow pitch to change with speed (faster = higher pitch)")
    
    args = parser.parse_args()
    
    try:
        output_file = speed_up_audio(
            args.input_file, 
            args.output_file, 
            args.speed, 
            preserve_pitch=not args.change_pitch
        )
        print(f"Successfully processed audio: {output_file}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()