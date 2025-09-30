# Video CLI - Professional Video Processing Pipeline

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FFmpeg Required](https://img.shields.io/badge/FFmpeg-required-red.svg)](https://ffmpeg.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A powerful command-line tool for automated video processing that concatenates video files, adds subtitles, and mixes background music. Built with Python and FFmpeg for professional video production workflows.

## 🎯 Key Features

- **Smart Video Concatenation**: Automatic resolution/framerate normalization
- **Professional Subtitle Processing**: Soft subtitles & burn-in options
- **Intelligent Audio Mixing**: BGM with automatic duration trimming
- **Cloud Integration**: Google Speech-to-Text for auto-captions
- **Cross-Platform**: Optimized for Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- FFmpeg (with libx264, libass support)

### Installation

```bash
# Clone or download this repository
git clone <repository-url>
cd video-ai

# Create virtual environment
python -m venv .venv

# Activate environment
.venv\Scripts\activate    # Windows
source .venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Simple video merge with default settings
python -m src.video_cli.cli --output final.mp4

# Professional production with burned subtitles and BGM
python -m src.video_cli.cli --output presentation.mp4 --burn-in --bgm-volume 0.2
```

## 📁 Project Structure

```
video-ai/
├── Video/     # Input videos (.mp4, .mov, .mkv, .avi)
├── Caption/   # Subtitle files (.srt)
├── BGM/       # Background music (.mp3, .wav, .m4a)
├── Output/    # Generated videos
└── src/       # Application code
```

## 🛠️ Command Reference

### Essential Commands

| Flag | Description | Example |
|------|-------------|---------|
| `--burn-in` | Hard-code subtitles into video | `--burn-in` |
| `--bgm-volume` | Background music volume (0.0-1.0) | `--bgm-volume 0.2` |
| `--bgm-file` | Specific music file | `--bgm-file "BGM/track.mp3"` |
| `--generate-captions` | Auto-generate via Google STT | `--generate-captions` |

### Advanced Options

```bash
# Custom directories and extensions
python -m src.video_cli.cli \
  --video-dir "RawFootage" \
  --caption-dir "Subtitles" \
  --exts .mp4 .mov \
  --output "final-cut.mp4"

# Multi-language caption generation
python -m src.video_cli.cli \
  --generate-captions \
  --language es-ES \
  --burn-in
```

## 📋 Subtitle Strategies

1. **Per-Video**: Match filenames (`video1.mp4` → `video1.srt`)
2. **Combined**: Single `combined.srt` for entire output
3. **Auto-Generated**: Google Speech-to-Text with `--generate-captions`

## 🎵 Audio Processing

- **Automatic BGM Selection**: First file alphabetically from BGM folder
- **Smart Mixing**: Preserves original audio while adding background music
- **Duration Sync**: BGM automatically trimmed to video length
- **Professional Quality**: AAC 192kbps stereo output

## 🔧 Technical Specs

- **Video**: H.264, CRF 20, up to 1080p@30fps
- **Audio**: AAC-LC 192kbps stereo
- **Subtitles**: MOV_TEXT (soft) or libass (burned)
- **Performance**: Multi-threaded processing with temp file management

## 📖 Full Documentation

For complete CLI reference, troubleshooting, and advanced configuration, see the [detailed documentation](README_FULL.md).

## 🐛 Troubleshooting

**Common Issues:**
- `ffmpeg not found`: Install FFmpeg and add to PATH
- `ModuleNotFoundError`: Activate virtual environment first
- Subtitle rendering issues: Use `--keep-temp` for debugging

**Debug Mode:**
```bash
python -m src.video_cli.cli --keep-temp --output debug-test.mp4
```

## 🤝 Contributing

This tool is designed for professional video workflows. For issues or feature requests, please provide:
- Complete command used
- Error messages
- Input file specifications
- Expected vs actual behavior

---

**Made for content creators, by developers** 🎬✨