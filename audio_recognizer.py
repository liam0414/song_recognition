#!/usr/bin/env python3
"""
Audio Recognition App using Chromaprint + AcoustID
Recognizes music from audio files or voice recordings
"""

import os
import sys
import tempfile
from typing import Optional, Dict, List
import argparse
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
    ENV_LOADED = True
except ImportError:
    ENV_LOADED = False

try:
    import acoustid
    import librosa
    import numpy as np
    from pydub import AudioSegment
    from pydub.silence import split_on_silence
except ImportError as e:
    print(f"❌ Missing required dependency: {e}")
    print("Install with: pip install pyacoustid requests pydub librosa numpy scipy soundfile")
    print("System dependencies: sudo apt install ffmpeg portaudio19-dev  # Ubuntu/Debian")
    print("                    brew install ffmpeg portaudio            # macOS")
    sys.exit(1)

class AudioRecognizer:
    def __init__(self, acoustid_api_key: str):
        """
        Initialize the audio recognizer
        
        Args:
            acoustid_api_key: Your AcoustID API key (get from https://acoustid.org/new-application)
        """
        self.acoustid_api_key = acoustid_api_key
        
    def preprocess_audio(self, audio_path: str, output_path: str = None) -> str:
        """
        Preprocess audio file for better recognition
        - Convert to mono
        - Normalize sample rate to 22050 Hz
        - Apply noise reduction for humming/voice
        """
        try:
            # Load audio with librosa
            print(f"📁 Loading audio file: {os.path.basename(audio_path)}")
            y, sr = librosa.load(audio_path, sr=22050, mono=True)
            
            # Apply spectral subtraction for noise reduction
            # This helps with humming and voice recordings
            stft = librosa.stft(y)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Simple noise reduction: subtract minimum magnitude
            noise_floor = np.percentile(magnitude, 20, axis=1, keepdims=True)
            magnitude_clean = np.maximum(magnitude - 0.3 * noise_floor, 
                                       0.1 * magnitude)
            
            # Reconstruct audio
            stft_clean = magnitude_clean * np.exp(1j * phase)
            y_clean = librosa.istft(stft_clean)
            
            # Save preprocessed audio
            if output_path is None:
                output_path = tempfile.mktemp(suffix='.wav')
            
            # Normalize to 16-bit
            y_clean = np.clip(y_clean, -1.0, 1.0)
            y_clean = (y_clean * 32767).astype(np.int16)
            
            # Create AudioSegment and export
            audio = AudioSegment(
                y_clean.tobytes(),
                frame_rate=22050,
                sample_width=2,
                channels=1
            )
            audio.export(output_path, format="wav")
            print(f"✅ Audio preprocessed successfully")
            
            return output_path
            
        except Exception as e:
            print(f"⚠️  Warning: Audio preprocessing failed: {e}")
            print(f"📄 Using original file: {audio_path}")
            return audio_path  # Return original if preprocessing fails
    
    def lookup_acoustid(self, path: str, max_results: int) -> Optional[List[Dict]]:
        """
        Look up fingerprint in AcoustID database
        
        Returns:
            List of matching results with acoustid
        """
        try:
            print(f"🔎 Searching AcoustID database...")
            results = []
            for score, recording_id, title, artist in acoustid.match(self.acoustid_api_key, path):
                if(recording_id and title and len(results) < max_results):
                    results.append({
                        "score": score,
                        "recording_id": recording_id,
                        "title": title,
                        "artist": artist
                    })
            return results
            
        except Exception as e:
            print(f"❌ Error looking up AcoustID: {e}")
            if "Invalid API key" in str(e):
                print("🔑 Please check your AcoustID API key")
                print("🌐 Get a new key from: https://acoustid.org/new-application")
            return None
    
    def recognize_audio(self, audio_path: str, max_results: int = 3) -> List[Dict]:
        """
        Main recognition function
        
        Args:
            audio_path: Path to audio file
            max_results: Maximum number of results to return
            
        Returns:
            List of recognition results with detailed information
        """
        print(f"\n🎧 Starting audio recognition")
        print(f"📂 File: {audio_path}")
        print("=" * 50)
        
        # Check if file exists
        if not os.path.exists(audio_path):
            print(f"❌ File not found: {audio_path}")
            return []
        
        # Look up in AcoustID
        matches = self.lookup_acoustid(audio_path, max_results)
        if not matches:
            print("😞 No matches found in AcoustID database")
            print("\n💡 This could be because:")
            print("   • The song is not in the database")
            print("   • The audio quality is too low")
            print("   • The recording is too short or heavily modified")
            print("   • It's a very obscure or new song")
            print("   • The song doesn't have copyright, i.e. classical music")
            return []
        return matches

def record_audio(duration: int = 10, sample_rate: int = 22050) -> str:
    """
    Record audio from microphone (requires pyaudio)
    """
    try:
        import pyaudio
        import wave
        
        # Audio parameters
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        print(f"\n🎤 Recording for {duration} seconds...")
        print("🎵 Start humming or singing now!")
        print("📊 Recording in 3... 2... 1...")
        
        # Open stream
        stream = p.open(format=format,
                       channels=channels,
                       rate=sample_rate,
                       input=True,
                       frames_per_buffer=chunk)
        
        frames = []
        for i in range(0, int(sample_rate / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)
            if i % (sample_rate // chunk) == 0:  # Print every second
                remaining = duration - (i // (sample_rate // chunk))
                print(f"⏱️  {remaining} seconds remaining...")
        
        # Stop recording
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save to temporary file
        temp_file = tempfile.mktemp(suffix='.wav')
        wf = wave.open(temp_file, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        print(f"✅ Recording complete! Saved to: {temp_file}")
        return temp_file
        
    except ImportError:
        print("❌ PyAudio not installed. Install with: pip install pyaudio")
        print("💡 Or use --file option to recognize existing audio files")
        return None
    except Exception as e:
        print(f"❌ Error recording audio: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description='🎵 Audio Recognition using Chromaprint + AcoustID',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            python audio_recognizer.py --api-key YOUR_KEY --file song.mp3
            python audio_recognizer.py --api-key YOUR_KEY --record 15
            python audio_recognizer.py --file song.wav --max-results 5

            Get your free API key from: https://acoustid.org/new-application
        """
    )
    
    parser.add_argument('--api-key', 
                       help='AcoustID API key (or set ACOUSTID_API_KEY in .env)')
    parser.add_argument('--file', 
                       help='Audio file to recognize (MP3, WAV, FLAC, etc.)')
    parser.add_argument('--record', type=int, default=0, 
                       help='Record from microphone for N seconds')
    parser.add_argument('--max-results', type=int, default=3, 
                       help='Maximum number of results to show (1-10)')
    
    args = parser.parse_args()
    
    # Get API key from command line or environment
    api_key = args.api_key or os.getenv('ACOUSTID_API_KEY')
    
    if not api_key:
        print("❌ No API key provided!")
        print("\nOptions:")
        print("1. Use: --api-key YOUR_KEY")
        print("2. Set environment: export ACOUSTID_API_KEY=your_key")
        if ENV_LOADED:
            print("3. Add to .env file: ACOUSTID_API_KEY=your_key")
        else:
            print("3. Install python-dotenv and add to .env file: pip install python-dotenv")
        print("\n🌐 Get your free API key from: https://acoustid.org/new-application")
        return
    
    # Validate max_results
    args.max_results = max(1, min(10, args.max_results))
    
    # Initialize recognizer
    recognizer = AudioRecognizer(api_key)
    
    # Determine audio source
    audio_path = None
    
    if args.record > 0:
        # Record from microphone
        audio_path = record_audio(args.record)
        if not audio_path:
            print("❌ Failed to record audio")
            return
    elif args.file:
        # Use provided file
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            return
        audio_path = args.file
    else:
        print("❌ Please provide either --file or --record option")
        print("💡 Use --help for usage examples")
        return
    
    try:
        # Recognize audio
        results = recognizer.recognize_audio(audio_path, args.max_results)
        
        if not results:
            print("\n😞 No matches found!")
            print("\n💡 Tips for better recognition:")
            print("   • Try popular, well-known songs")
            print("   • Use clear, high-quality audio")
            print("   • Record for 15+ seconds")
            print("   • For humming: stay on pitch and hum the main melody")
        else:
            print(f"\n🎉 Found {len(results)} match(es)!")
            print("=" * 60)
            
            for i, result in enumerate(results, 1):
                print(f"\n🏆 Match #{i} (Confidence: {result['score']:.1%})")
                print(f"🎵 Title: {result['title']}")
                print(f"🎤 Artist(s): {result['artist']}")
                
                if i < len(results):
                    print("-" * 40)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Recognition stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Please check your internet connection and try again")
    finally:
        # Clean up recorded file
        if args.record > 0 and audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)
            print(f"\n🗑️  Cleaned up temporary recording file")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("🎵 Audio Recognition App")
        print("=" * 30)
        print("Recognize songs from audio files, humming, or singing!")
        
        api_key = os.getenv('ACOUSTID_API_KEY')
        if api_key:
            print(f"✅ API key found in environment")
            print("\n🚀 Ready to use! Try:")
            print("   python audio_recognizer.py --file your_song.mp3")
            print("   python audio_recognizer.py --record 15")
        else:
            print("❌ No API key found")
            if ENV_LOADED:
                print("💡 Add ACOUSTID_API_KEY=your_key to your .env file")
            else:
                print("💡 Install python-dotenv: pip install python-dotenv")
                print("💡 Then add ACOUSTID_API_KEY=your_key to .env file")
            print("🌐 Get your free API key from: https://acoustid.org/new-application")
        
        print("\n📖 Usage examples:")
        print("   python audio_recognizer.py --api-key YOUR_KEY --file song.mp3")
        print("   python audio_recognizer.py --api-key YOUR_KEY --record 10")
        print("   python audio_recognizer.py --help")
        
    else:
        main()