#!/bin/bash

echo "Setting up system dependencies for audio recognition..."

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux - installing dependencies with apt"
    sudo apt update
    sudo apt install -y \
        ffmpeg \
        libffi-dev \
        libasound2-dev \
        portaudio19-dev \
        python3-dev \
        gcc \
        g++
        
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS - installing dependencies with brew"
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Please install it first:"
        echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        exit 1
    fi
    
    brew install ffmpeg portaudio
    
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "Detected Windows"
    echo "Please install the following manually:"
    echo "1. FFmpeg: https://ffmpeg.org/download.html"
    echo "2. Visual Studio Build Tools or Visual Studio Community"
    echo "3. Add FFmpeg to your PATH"
    
else
    echo "Unknown OS: $OSTYPE"
    echo "Please install ffmpeg and portaudio manually"
fi

echo "System dependencies setup complete!"