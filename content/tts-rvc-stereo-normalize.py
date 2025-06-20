#!/usr/bin/env python3

import subprocess
import re
import sys
import os

def analyze_volume(input_file):
    """Analyze audio volume using ffmpeg"""
    cmd = [
        'ffmpeg', '-i', input_file,
        '-af', 'volumedetect',
        '-f', 'null', '-'
    ]
    
    try:
        # Use PIPE for stderr to capture ffmpeg output
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # ffmpeg outputs to stderr, not stdout
        output = result.stderr
        
        # Extract max volume
        max_volume_match = re.search(r'max_volume: (-?\d+\.?\d*) dB', output)
        mean_volume_match = re.search(r'mean_volume: (-?\d+\.?\d*) dB', output)
        
        if max_volume_match:
            max_volume = float(max_volume_match.group(1))
            mean_volume = float(mean_volume_match.group(1)) if mean_volume_match else None
            return max_volume, mean_volume
        else:
            print("Debug output:", output)  # For troubleshooting
            raise ValueError("Could not extract volume information")
            
    except subprocess.CalledProcessError as e:
        print(f"Error analyzing volume: {e}")
        print(f"stderr: {e.stderr}")
        return None, None
    except FileNotFoundError:
        print("❌ ffmpeg not found. Please install ffmpeg.")
        return None, None

def normalize_audio(input_file, output_file, target_db=-1.0, bitrate="320k"):
    """Normalize audio to target dB level"""
    
    print(f"🔍 Analyzing: {input_file}")
    
    # Analyze current volume
    max_volume, mean_volume = analyze_volume(input_file)
    
    if max_volume is None:
        print("❌ Failed to analyze audio volume")
        return False
    
    print(f"📊 Current max volume: {max_volume} dB")
    if mean_volume:
        print(f"📊 Current mean volume: {mean_volume} dB")
    
    # Calculate boost needed
    boost_needed = target_db - max_volume
    print(f"⚡ Boost needed: {boost_needed:.1f} dB")
    
    # Apply normalization
    cmd = [
        'ffmpeg', '-i', input_file,
        '-ac', '2',  # Stereo
        '-b:a', bitrate,
        '-af', f'volume={boost_needed}dB',
        output_file,
        '-y'  # Overwrite existing file
    ]
    
    print(f"🎵 Converting to stereo MP3...")
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ Complete! Output: {output_file}")
        
        # Verify final volume and suggest adjustment if needed
        print("🔍 Final volume check:")
        final_max, final_mean = analyze_volume(output_file)
        if final_max is not None:
            print(f"📊 Final max volume: {final_max:.1f} dB")
            if final_mean:
                print(f"📊 Final mean volume: {final_mean:.1f} dB")
            
            # Check if we hit our target (within 0.5 dB tolerance)
            if abs(final_max - target_db) > 0.5:
                difference = target_db - final_max
                print(f"⚠️  Target was {target_db} dB, got {final_max:.1f} dB")
                print(f"💡 For next time, try target: {target_db + difference:.1f} dB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during conversion: {e}")
        return False

def main():
    # Default paths
    default_input = "/Users/a/Desktop/Share/YT/Scripts/VideoCutter/audio/TTS-RVC.wav"
    default_output = "/Users/a/Desktop/Share/YT/Scripts/VideoCutter/audio/TTS-RVC-dynamic.mp3"
    
    # Get input/output from command line or use defaults
    input_file = sys.argv[1] if len(sys.argv) > 1 else default_input
    output_file = sys.argv[2] if len(sys.argv) > 2 else default_output
    
    # Optional: target dB level (default 0.0 to compensate for MP3 encoding loss)
    target_db = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    normalize_audio(input_file, output_file, target_db)

if __name__ == "__main__":
    main()