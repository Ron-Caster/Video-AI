# Video CLI - Professional Video Processing Pipeline

A powerful command-line tool for automated video processing that concatenates video files, adds subtitles, and mixes background music. Built with Python and FFmpeg, this tool provides enterprise-grade video processing capabilities with intelligent subtitle handling and audio mixing.

## Features

- **Intelligent Video Concatenation**: Automatically merges videos from a source directory in alphabetical order with resolution and framerate normalization
- **Advanced Subtitle Processing**: Supports both soft subtitles (embedded tracks) and hard-coded burn-in with automatic time-shifting for multi-video projects
- **Professional Audio Mixing**: Seamlessly blends background music with original audio, automatically trimmed to video duration
- **Google Cloud Speech-to-Text Integration**: Generate subtitles automatically when caption files are unavailable
- **Cross-Platform Compatibility**: Optimized for Windows with robust path handling and fallback mechanisms
- **Batch Processing**: Handle multiple video files with consistent encoding parameters

## System Requirements

- **Python**: 3.10 or higher
- **FFmpeg**: Latest version with libx264, libass, and AAC support
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Optional**: Google Cloud Platform account with Speech-to-Text API enabled

## Installation

### 1. Install FFmpeg

**Windows (recommended):**
```powershell
winget install --id=Gyan.FFmpeg -e
```

**Alternative (Chocolatey):**
```powershell
choco install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

### 2. Set up Python Environment

Clone or download this project, then:

```powershell
# Navigate to project directory
cd "path\to\Video AI"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# OR
source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Optional: Google Cloud Speech-to-Text Setup

For automatic caption generation:

1. Create a Google Cloud Project
2. Enable the Speech-to-Text API
3. Create a service account and download the JSON key
4. Set environment variable:

```powershell
# Windows
setx GOOGLE_APPLICATION_CREDENTIALS "C:\path\to\service-account-key.json"

# macOS/Linux
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

## Project Structure

Create the following directory structure in your project folder:

```
Video AI/
├── Video/          # Input video files (.mp4, .mov, .mkv, .avi)
├── Caption/        # Subtitle files (.srt)
├── BGM/           # Background music files (.mp3, .wav, .m4a, etc.)
├── Output/        # Generated output files
└── src/           # Application source code
```

## Command-Line Interface

### Basic Syntax

```powershell
python -m src.video_cli.cli [OPTIONS]
```

### Core Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--video-dir` | Path | `Video` | Directory containing input video files |
| `--caption-dir` | Path | `Caption` | Directory containing subtitle (.srt) files |
| `--bgm-dir` | Path | `BGM` | Directory containing background music files |
| `--output-dir` | Path | `Output` | Directory for generated output files |
| `--output` | Path | `Output/merged.mp4` | Specific output filename and path |

### Video Processing Options

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--exts` | List | `[".mp4", ".mov", ".mkv", ".avi"]` | Video file extensions to process |

### Audio & Music Options

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--bgm-file` | Path | `None` | Specific background music file (overrides directory scan) |
| `--bgm-volume` | Float | `0.15` | Background music volume level (0.0-1.0) |

### Subtitle Options

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--no-soft-subs` | Flag | `False` | Burn subtitles into video (hard-coded, always visible) |
| `--burn-in` | Flag | `False` | Alias for `--no-soft-subs` |
| `--generate-captions` | Flag | `False` | Use Google Speech-to-Text when no .srt files exist |
| `--language` | String | `en-US` | Language code for speech recognition |
| `--sample-rate` | Integer | `16000` | Audio sample rate for speech processing |

### Debugging Options

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--keep-temp` | Flag | `False` | Preserve temporary files for troubleshooting |

## Usage Examples

### Basic Video Concatenation

Merge all videos in the `Video` folder with default settings:

```powershell
python -m src.video_cli.cli --output Output\final.mp4
```

### Hard-Coded Subtitles with Background Music

Burn subtitles into the video and add background music:

```powershell
python -m src.video_cli.cli --output Output\presentation.mp4 --burn-in --bgm-volume 0.2
```

### Professional Production with Custom Settings

Full-featured processing with specific BGM file and optimized settings:

```powershell
python -m src.video_cli.cli \
  --output Output\production.mp4 \
  --burn-in \
  --bgm-file "BGM\corporate-theme.mp3" \
  --bgm-volume 0.25 \
  --video-dir "RawFootage" \
  --caption-dir "Subtitles"
```

### Automatic Caption Generation

Generate subtitles using Google Speech-to-Text:

```powershell
python -m src.video_cli.cli \
  --output Output\auto-captioned.mp4 \
  --generate-captions \
  --language en-US \
  --burn-in
```

### Batch Processing with Custom Extensions

Process specific video formats from multiple directories:

```powershell
python -m src.video_cli.cli \
  --video-dir "Projects\Episode1" \
  --exts .mp4 .mov \
  --output Output\episode1-final.mp4 \
  --bgm-volume 0.1
```

## Subtitle File Strategies

### Option 1: Per-Video Subtitles

Name subtitle files to match video files:
- `Video\intro.mp4` → `Caption\intro.srt`
- `Video\main.mp4` → `Caption\main.srt`
- `Video\outro.mp4` → `Caption\outro.srt`

The tool automatically time-shifts each subtitle file based on cumulative video durations.

### Option 2: Combined Subtitles

Create a single subtitle file covering the entire merged video:
- `Caption\combined.srt`

This file should contain timestamps for the complete final video duration.

### Option 3: Automatic Generation

Use Google Speech-to-Text when no subtitle files exist:
- Requires `--generate-captions` flag
- Needs Google Cloud credentials configured
- Supports multiple languages via `--language` parameter

## Background Music Integration

### Automatic Selection

Place music files in the `BGM` directory. The tool selects the first file alphabetically.

### Manual Selection

Specify exact music file:
```powershell
--bgm-file "BGM\my-soundtrack.mp3"
```

### Volume Control

Adjust background music volume (recommended range: 0.1-0.3):
```powershell
--bgm-volume 0.2  # 20% of original volume
```

### Audio Mixing Behavior

- **With Original Audio**: BGM is mixed with existing video audio
- **Silent Videos**: BGM becomes the primary audio track
- **Duration**: BGM is automatically trimmed to match video length
- **Format**: Output uses AAC audio codec at 192kbps

## Technical Specifications

### Video Processing

- **Codec**: H.264 (libx264) with medium preset
- **Quality**: CRF 20 (high quality, reasonable file size)
- **Resolution**: Maintains original aspect ratio, maximum 1080p
- **Frame Rate**: Normalized to 30fps
- **Color**: YUV420P for maximum compatibility

### Audio Processing

- **Codec**: AAC-LC at 192kbps
- **Channels**: Stereo (2 channels)
- **Sample Rate**: 48kHz output
- **Mixing**: Advanced filter graphs for seamless audio blending

### Subtitle Rendering

- **Soft Subtitles**: MOV_TEXT format for MP4 containers
- **Hard Subtitles**: libass filter with automatic font fallback
- **Encoding**: UTF-8 with error handling for international characters

## Troubleshooting

### Common Issues

**FFmpeg Not Found**
```
Error: ffmpeg not found in PATH
```
**Solution**: Install FFmpeg and ensure it's in your system PATH.

**Module Import Errors**
```
ModuleNotFoundError: No module named 'srt'
```
**Solution**: Activate virtual environment and install dependencies:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Subtitle Rendering Failures**
```
Error applying option to filter 'subtitles'
```
**Solution**: The tool automatically falls back to simpler path handling. If issues persist, try:
- Moving files to paths without spaces
- Using the `--keep-temp` flag to inspect intermediate files

**Google Speech-to-Text Errors**
```
RuntimeError: google-cloud-speech is required
```
**Solution**: 
1. Verify Google Cloud credentials are configured
2. Ensure Speech-to-Text API is enabled
3. Check internet connectivity

### Performance Optimization

**Large Video Files**: Use `--keep-temp` to monitor processing stages and identify bottlenecks.

**Slow Rendering**: Consider reducing video resolution in source files before processing.

**Memory Usage**: Close other applications during processing of large video files.

### Debug Mode

Enable detailed logging and preserve intermediate files:
```powershell
python -m src.video_cli.cli --output debug-test.mp4 --keep-temp --burn-in
```

This creates additional files in the output directory for analysis.

## Advanced Configuration

### Custom Video Extensions

Process additional video formats:
```powershell
--exts .mp4 .mov .mkv .avi .webm .flv
```

### Multi-Language Support

Generate captions in different languages:
```powershell
--generate-captions --language es-ES  # Spanish
--generate-captions --language fr-FR  # French
--generate-captions --language de-DE  # German
```

### High-Quality Audio Processing

For professional audio mixing:
```powershell
--sample-rate 48000  # Higher quality speech processing
--bgm-volume 0.15    # Conservative mixing level
```

## Contributing

This tool is designed for professional video processing workflows. For feature requests or bug reports, please ensure you include:

1. Complete command used
2. Error messages (if any)
3. Sample input file characteristics
4. Expected vs. actual behavior

## License

This project is available for educational and professional use. Please ensure FFmpeg licensing compliance for commercial deployments.
