# Advanced Video Editor GUI (app_gui.py)

A comprehensive video editing application with real-time preview, trimming, audio mixing, and subtitle customization capabilities.

## Features

### 🎬 Video Management
- **Multi-video Loading**: Load and manage multiple video files
- **Video Combination**: Combine multiple videos in sequence
- **Real-time Preview**: Live video preview with frame-by-frame navigation
- **Format Support**: MP4, AVI, MOV, MKV, WMV, FLV

### ✂️ Video Editing
- **Precision Trimming**: Set start/end points with frame accuracy
- **Playback Controls**: Play, pause, seek, frame stepping
- **Timeline Navigation**: Visual timeline representation
- **Export Options**: Export trimmed videos with original quality

### 🎵 Audio Management
- **Multi-track Audio**: Load separate audio tracks and background music
- **Volume Control**: Independent volume controls for each audio source
- **Audio Mixing**: Combine multiple audio sources
- **Format Support**: MP3, WAV, AAC, OGG, FLAC

### 📝 Subtitle & Font System
- **Custom Fonts**: Load TTF/OTF font files
- **Font Customization**: Adjustable size, color, and position
- **Real-time Preview**: Live subtitle preview on video
- **Font Preview**: Dedicated font preview panel
- **Color Picker**: Visual color selection tool

### 🖥️ User Interface
- **Professional Layout**: Clean, organized multi-panel interface
- **Real-time Updates**: Instant feedback for all adjustments
- **Progress Tracking**: Visual progress indicators for operations
- **Responsive Design**: Adaptive layout for different screen sizes

## Installation

### Quick Start
```bash
# Run the launcher script (Windows)
run_app_gui.bat

# Or for Linux/Mac
chmod +x run_app_gui.sh
./run_app_gui.sh
```

### Manual Installation
```bash
# Install required dependencies
pip install -r app_gui_requirements.txt

# Run the application
python app_gui.py
```

### Dependencies
- **opencv-python**: Video processing and frame manipulation
- **pygame**: Audio handling and mixing
- **Pillow (PIL)**: Image processing and font rendering
- **tkinter**: GUI framework (included with Python)
- **numpy**: Array processing (auto-installed with OpenCV)

## Usage Guide

### 1. Loading Videos
1. Click **"Load Videos"** to select multiple video files
2. Videos appear in the list on the left panel
3. Click any video in the list to preview it
4. Use **"Combine Videos"** to merge multiple videos

### 2. Video Playback
- **▶/⏸**: Play/Pause toggle
- **⏮/⏭**: Jump to start/end
- **⏪/⏩**: Seek backward/forward (10 seconds)
- **Position Slider**: Drag to seek to specific position

### 3. Trimming Videos
1. **Set Start Point**: Seek to desired start → Click "Set" next to "Start"
2. **Set End Point**: Seek to desired end → Click "Set" next to "End"
3. **Preview Trim**: Click "Preview Trim" to review selection
4. **Export**: Use "Export Trimmed Video" to save

### 4. Audio Management
1. **Load Audio**: Click "Load Audio Track" for main audio
2. **Load BGM**: Click "Load BGM" for background music
3. **Adjust Volumes**: Use sliders to balance audio levels
4. **Export Mix**: Save audio combinations

### 5. Subtitle Customization
1. **Load Font**: Click "Load Font File" to select TTF/OTF fonts
2. **Adjust Settings**:
   - **Size**: Use spinner to change font size
   - **Color**: Enter hex code or use color picker
   - **Position**: Adjust Y position slider
3. **Add Text**: Type in the text area
4. **Preview**: Enable "Show Preview" to see subtitles on video
5. **Export**: Use "Export with Subtitles" to burn subtitles into video

### 6. Font Preview
- Real-time font preview updates as you adjust settings
- Preview shows "Sample Text Preview" with your font choices
- Test different fonts and sizes before applying to video

## Technical Details

### Video Processing
- Uses OpenCV for robust video handling
- Supports hardware acceleration when available
- Frame-accurate seeking and positioning
- Efficient memory management for large videos

### Audio System
- Pygame mixer for audio playback
- Multi-track mixing capabilities
- Volume normalization and control
- Cross-fade and timing synchronization

### Font Rendering
- PIL (Pillow) for high-quality text rendering
- True Type Font (TTF) and OpenType Font (OTF) support
- Antialiased text rendering
- Customizable positioning and styling

### Export Formats
- **Video**: MP4 (H.264 encoding recommended)
- **Audio**: MP3, WAV with configurable quality
- **Subtitles**: Burned-in (hardcoded) subtitles

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `Left Arrow` | Seek backward |
| `Right Arrow` | Seek forward |
| `Home` | Jump to start |
| `End` | Jump to end |

## Troubleshooting

### Common Issues

**"Could not open video" Error**
- Ensure video file is not corrupted
- Check if codec is supported
- Try converting to MP4 format

**Audio Not Playing**
- Check system audio settings
- Verify audio file format support
- Restart the application

**Font Not Loading**
- Ensure font file is valid TTF/OTF format
- Check file permissions
- Try with different font files

**Performance Issues**
- Close other applications to free memory
- Use smaller video files for testing
- Ensure adequate disk space for temporary files

### System Requirements
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.7 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space for temporary files
- **Graphics**: OpenGL support recommended

## File Structure
```
app_gui.py                 # Main application
app_gui_requirements.txt   # Python dependencies
run_app_gui.bat           # Windows launcher
run_app_gui.sh            # Linux/Mac launcher
test_app_gui.py           # Dependency test script
```

## Advanced Features

### Timeline Visualization
- Visual representation of video timeline
- Trim markers and selection indicators
- Audio track visualization (planned)

### Batch Processing
- Process multiple videos with same settings
- Queue management for exports
- Background processing capabilities

### Export Options
- Quality presets (High, Medium, Low)
- Custom resolution and bitrate
- Format-specific optimizations

## Contributing

This is an independent video editor that doesn't interfere with existing project files. It's designed to be:
- **Modular**: Self-contained with minimal dependencies
- **Extensible**: Easy to add new features
- **User-friendly**: Intuitive interface for all skill levels

## License

This project is part of the Video AI toolkit. See the main project LICENSE for details.

---

**Note**: This advanced video editor (`app_gui.py`) is completely independent of the existing CLI pipeline and won't modify any current Python files in your project.