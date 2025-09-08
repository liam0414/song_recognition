# 🎵 Audio Recognition App

A Python application that recognizes music from audio files, recordings, or even humming using Chromaprint fingerprinting and the AcoustID database.

## ✨ Features

- 🎧 **Audio File Recognition** - Identify songs from MP3, WAV, FLAC, and other audio formats
- 🎤 **Live Recording** - Record and recognize songs directly from your microphone
- 🎵 **Humming Recognition** - Advanced preprocessing to recognize hummed melodies
- 🔍 **Multiple Results** - Get multiple potential matches with confidence scores
- 🛠️ **Audio Preprocessing** - Automatic noise reduction and audio enhancement

## 🚀 Quick Start

### 1. Get an API Key
Get your free AcoustID API key from: https://acoustid.org/new-application

### 2. Install System Dependencies

**Ubuntu/Debian:**
```bash
./scripts/setup_system_deps.sh
```

**macOS:**
```bash
brew install ffmpeg portaudio
```

**Windows:**
- Install FFmpeg from https://ffmpeg.org/download.html
- Install Visual Studio Build Tools
- Add FFmpeg to your PATH

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt

# For microphone recording (optional):
pip install pyaudio
```

### 4. Set Up Your API Key

**Option 1: Environment Variable**
```bash
export ACOUSTID_API_KEY=your_api_key_here
```

**Option 2: .env File**
```bash
echo "ACOUSTID_API_KEY=your_api_key_here" > .env
```

## 📖 Usage

### Recognize Audio Files
```bash
# Basic usage
python audio_recognizer.py --api-key YOUR_KEY --file song.mp3

# Get more results
python audio_recognizer.py --file song.mp3 --max-results 5
```

### Record and Recognize
```bash
# Record for 15 seconds
python audio_recognizer.py --api-key YOUR_KEY --record 15

# Quick humming test (10 seconds)
python audio_recognizer.py --record 10
```

### Help and Examples
```bash
python audio_recognizer.py --help
```

## 🎯 Example Output

```
🎧 Starting audio recognition
📂 File: song.mp3
==================================================
🔎 Searching AcoustID database...
✅ Audio preprocessed successfully

🎉 Found 2 match(es)!
============================================================

🏆 Match #1 (Confidence: 98.5%)
🎵 Title: Bohemian Rhapsody
🎤 Artist(s): Queen

----------------------------------------

🏆 Match #2 (Confidence: 85.2%)
🎵 Title: Bohemian Rhapsody - Remastered 2011
🎤 Artist(s): Queen
```

## 📁 Project Structure

```
audio-recognition/
├── audio_recognizer.py      # Main application
├── requirements.txt         # Python dependencies
├── requirements-dev.txt     # Development dependencies
├── scripts/
│   └── setup_system_deps.sh # System dependency installer
├── test.py                  # Simple test script
└── .env                     # Your API key (create this)
```

## 🔧 Development

### Install Development Dependencies
```bash
pip install -r requirements-dev.txt
```

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black audio_recognizer.py
isort audio_recognizer.py
flake8 audio_recognizer.py
```

## 💡 Tips for Better Recognition

- **Popular Songs**: Work best as they're more likely to be in the database
- **Audio Quality**: Use clear, high-quality recordings
- **Recording Length**: 15+ seconds recommended for best results
- **Humming**: Stay on pitch and hum the main melody clearly
- **File Formats**: MP3, WAV, FLAC are all supported

## ❓ Troubleshooting

### "No matches found"
- Try popular, well-known songs
- Check audio quality and length
- Some classical/copyright-free music may not be in the database

### "Missing required dependency"
- Run the system dependency setup script
- Install FFmpeg and PortAudio for your platform

### "Invalid API key"
- Verify your AcoustID API key
- Check environment variables or .env file

### PyAudio Installation Issues
- **Ubuntu/Debian**: `sudo apt install portaudio19-dev python3-dev`
- **macOS**: `brew install portaudio`
- **Windows**: Install Visual Studio Build Tools

## 🛠️ Dependencies

- **Core**: acoustid, librosa, pydub, numpy, scipy
- **Optional**: pyaudio (for microphone recording)
- **System**: FFmpeg, PortAudio


- Check the troubleshooting section above
- Review command-line help: `python audio_recognizer.py --help`
- For AcoustID API issues, visit: https://acoustid.o
