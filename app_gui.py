"""
Advanced Video Editor GUI - Independent Video Processing Tool
Features: Video preview, trimming, audio mixing, font customization, real-time preview
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
from pathlib import Path
import os
import sys
import json
import tempfile
import shutil
from datetime import timedelta
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageFont, ImageDraw
import pygame
import time


class VideoEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Video Editor - Preview, Trim & Mix")
        self.root.geometry("1200x900")
        self.root.minsize(1000, 700)
        
        # Initialize pygame for audio
        pygame.mixer.init()
        
        # Video and audio state
        self.video_files = []  # All loaded videos
        self.timeline_videos = []  # Videos in timeline order
        self.current_video = None
        self.current_video_index = 0
        self.video_cap = None
        self.total_frames = 0
        self.fps = 30
        self.current_frame = 0
        self.is_playing = False
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Audio state
        self.audio_tracks = []
        self.current_audio = None
        
        # Subtitle state
        self.subtitle_files = []
        self.current_subtitle_file = None
        self.subtitle_tracks = []  # Parsed subtitle data
        
        # Font and text state
        self.font_file = None
        self.font_size = 24
        self.font_color = "#FFFFFF"
        self.subtitle_text = ""
        
        # Trim state
        self.trim_start = 0
        self.trim_end = 0
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Variables
        self.setup_variables()
        
        # Create UI
        self.create_widgets()
        
        # Bind cleanup
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_variables(self):
        """Initialize all tkinter variables"""
        self.video_position = tk.DoubleVar()
        self.audio_volume = tk.DoubleVar(value=0.5)
        self.bgm_volume = tk.DoubleVar(value=0.3)
        self.preview_subtitle = tk.BooleanVar(value=True)
        self.subtitle_position_y = tk.DoubleVar(value=0.85)
        
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Advanced Video Editor", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Left panel - Controls
        left_panel = ttk.Frame(main_frame, padding="5")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.create_control_panel(left_panel)
        
        # Center panel - Video preview
        center_panel = ttk.Frame(main_frame, padding="5")
        center_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.create_video_panel(center_panel)
        
        # Right panel - Audio and effects
        right_panel = ttk.Frame(main_frame, padding="5")
        right_panel.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.create_audio_panel(right_panel)
        
        # Bottom panel - Timeline and export
        bottom_panel = ttk.Frame(main_frame, padding="5")
        bottom_panel.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E))
        self.create_timeline_panel(bottom_panel)
        
    def create_control_panel(self, parent):
        """Create video loading and basic controls"""
        # Video Loading
        video_frame = ttk.LabelFrame(parent, text="Video Management", padding="10")
        video_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        video_frame.columnconfigure(0, weight=1)
        
        ttk.Button(video_frame, text="Load Videos", 
                  command=self.load_videos).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(video_frame, text="Add Subtitle File", 
                  command=self.load_subtitle_file).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Video list
        self.video_listbox = tk.Listbox(video_frame, height=4)
        self.video_listbox.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        self.video_listbox.bind('<<ListboxSelect>>', self.on_video_select)
        
        # Timeline controls
        timeline_controls = ttk.Frame(video_frame)
        timeline_controls.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        timeline_controls.columnconfigure(0, weight=1)
        timeline_controls.columnconfigure(1, weight=1)
        
        ttk.Button(timeline_controls, text="Remove from Timeline", 
                  command=self.remove_from_timeline).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 2))
        ttk.Button(timeline_controls, text="Move Up", 
                  command=self.move_up_timeline).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(2, 0))
        
        # Playback Controls
        playback_frame = ttk.LabelFrame(parent, text="Playback Controls", padding="10")
        playback_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        playback_frame.columnconfigure(1, weight=1)
        
        button_frame = ttk.Frame(playback_frame)
        button_frame.grid(row=0, column=0, columnspan=2, pady=(0, 5))
        
        ttk.Button(button_frame, text="⏮", command=self.seek_start, width=3).pack(side=tk.LEFT, padx=1)
        ttk.Button(button_frame, text="⏪", command=self.seek_backward, width=3).pack(side=tk.LEFT, padx=1)
        self.play_button = ttk.Button(button_frame, text="▶", command=self.toggle_playback, width=3)
        self.play_button.pack(side=tk.LEFT, padx=1)
        ttk.Button(button_frame, text="⏩", command=self.seek_forward, width=3).pack(side=tk.LEFT, padx=1)
        ttk.Button(button_frame, text="⏭", command=self.seek_end, width=3).pack(side=tk.LEFT, padx=1)
        
        # Position slider
        ttk.Label(playback_frame, text="Position:").grid(row=1, column=0, sticky=tk.W)
        self.position_scale = ttk.Scale(playback_frame, from_=0, to=100, 
                                       variable=self.video_position, orient=tk.HORIZONTAL)
        self.position_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        self.position_scale.bind('<Button-1>', self.on_seek_start)
        self.position_scale.bind('<ButtonRelease-1>', self.on_seek_end)
        
        # Trim Controls
        trim_frame = ttk.LabelFrame(parent, text="Trim Settings", padding="10")
        trim_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        trim_frame.columnconfigure(1, weight=1)
        
        ttk.Label(trim_frame, text="Start:").grid(row=0, column=0, sticky=tk.W)
        self.trim_start_var = tk.StringVar(value="00:00:00")
        ttk.Entry(trim_frame, textvariable=self.trim_start_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        ttk.Button(trim_frame, text="Set", command=self.set_trim_start).grid(row=0, column=2, padx=(5, 0))
        
        ttk.Label(trim_frame, text="End:").grid(row=1, column=0, sticky=tk.W)
        self.trim_end_var = tk.StringVar(value="00:00:00")
        ttk.Entry(trim_frame, textvariable=self.trim_end_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        ttk.Button(trim_frame, text="Set", command=self.set_trim_end).grid(row=1, column=2, padx=(5, 0))
        
        ttk.Button(trim_frame, text="Preview Trim", 
                  command=self.preview_trim).grid(row=2, column=0, columnspan=3, pady=(5, 0), sticky=(tk.W, tk.E))
        
        parent.rowconfigure(3, weight=1)
        
    def create_video_panel(self, parent):
        """Create video preview panel"""
        # Video display
        video_frame = ttk.LabelFrame(parent, text="Video Preview", padding="10")
        video_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        video_frame.columnconfigure(0, weight=1)
        video_frame.rowconfigure(0, weight=1)
        
        # Canvas for video
        self.video_canvas = tk.Canvas(video_frame, bg='black', width=640, height=360)
        self.video_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Video info
        info_frame = ttk.Frame(video_frame)
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        info_frame.columnconfigure(1, weight=1)
        
        self.video_info_label = ttk.Label(info_frame, text="No video loaded")
        self.video_info_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        self.time_label = ttk.Label(info_frame, text="00:00:00 / 00:00:00")
        self.time_label.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
    def create_audio_panel(self, parent):
        """Create audio and effects panel"""
        # Audio Management
        audio_frame = ttk.LabelFrame(parent, text="Audio Management", padding="10")
        audio_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        audio_frame.columnconfigure(0, weight=1)
        
        ttk.Button(audio_frame, text="Load Audio Track", 
                  command=self.load_audio).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(audio_frame, text="Load BGM", 
                  command=self.load_bgm).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Audio list
        self.audio_listbox = tk.Listbox(audio_frame, height=3)
        self.audio_listbox.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Volume Controls
        volume_frame = ttk.LabelFrame(parent, text="Volume Controls", padding="10")
        volume_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        volume_frame.columnconfigure(1, weight=1)
        
        ttk.Label(volume_frame, text="Audio:").grid(row=0, column=0, sticky=tk.W)
        audio_scale = ttk.Scale(volume_frame, from_=0.0, to=1.0, variable=self.audio_volume, orient=tk.HORIZONTAL)
        audio_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Label(volume_frame, text="BGM:").grid(row=1, column=0, sticky=tk.W)
        bgm_scale = ttk.Scale(volume_frame, from_=0.0, to=1.0, variable=self.bgm_volume, orient=tk.HORIZONTAL)
        bgm_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # Font and Subtitle Controls
        font_frame = ttk.LabelFrame(parent, text="Subtitle & Font", padding="10")
        font_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        font_frame.columnconfigure(1, weight=1)
        
        # Subtitle file info
        subtitle_info_frame = ttk.Frame(font_frame)
        subtitle_info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.subtitle_file_label = ttk.Label(subtitle_info_frame, text="No subtitle file loaded", 
                                           foreground="gray")
        self.subtitle_file_label.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(font_frame, text="Load Font File", 
                  command=self.load_font).grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(font_frame, text="Size:").grid(row=2, column=0, sticky=tk.W)
        self.font_size_var = tk.IntVar(value=24)
        font_size_spin = ttk.Spinbox(font_frame, from_=8, to=72, textvariable=self.font_size_var, width=5)
        font_size_spin.grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        font_size_spin.bind('<Return>', self.update_font_preview)
        
        ttk.Label(font_frame, text="Color:").grid(row=3, column=0, sticky=tk.W)
        color_frame = ttk.Frame(font_frame)
        color_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        self.font_color_var = tk.StringVar(value="#FFFFFF")
        color_entry = ttk.Entry(color_frame, textvariable=self.font_color_var, width=8)
        color_entry.grid(row=0, column=0, sticky=tk.W)
        color_entry.bind('<Return>', self.update_font_preview)
        ttk.Button(color_frame, text="Pick", command=self.pick_color).grid(row=0, column=1, padx=(5, 0))
        
        ttk.Label(font_frame, text="Custom Text:").grid(row=4, column=0, sticky=tk.W)
        self.subtitle_entry = tk.Text(font_frame, height=3, width=20)
        self.subtitle_entry.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        self.subtitle_entry.bind('<KeyRelease>', self.update_subtitle_preview)
        
        ttk.Checkbutton(font_frame, text="Show Preview", 
                       variable=self.preview_subtitle).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        ttk.Label(font_frame, text="Y Position:").grid(row=7, column=0, sticky=tk.W)
        position_scale = ttk.Scale(font_frame, from_=0.0, to=1.0, variable=self.subtitle_position_y, orient=tk.HORIZONTAL)
        position_scale.grid(row=7, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # Font Preview
        preview_frame = ttk.LabelFrame(parent, text="Font Preview", padding="10")
        preview_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        self.font_preview_canvas = tk.Canvas(preview_frame, height=60, bg='black')
        self.font_preview_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E))
        preview_frame.columnconfigure(0, weight=1)
        
        parent.rowconfigure(4, weight=1)
        
    def create_timeline_panel(self, parent):
        """Create timeline and export controls"""
        # Timeline
        timeline_frame = ttk.LabelFrame(parent, text="Timeline", padding="10")
        timeline_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        timeline_frame.columnconfigure(0, weight=1)
        
        # Timeline canvas with scrollbar
        timeline_container = ttk.Frame(timeline_frame)
        timeline_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        timeline_container.columnconfigure(0, weight=1)
        
        self.timeline_canvas = tk.Canvas(timeline_container, height=120, bg='gray90')
        timeline_scrollbar = ttk.Scrollbar(timeline_container, orient="horizontal", command=self.timeline_canvas.xview)
        self.timeline_canvas.configure(xscrollcommand=timeline_scrollbar.set)
        
        self.timeline_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E))
        timeline_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Timeline info
        timeline_info = ttk.Frame(timeline_frame)
        timeline_info.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.timeline_info_label = ttk.Label(timeline_info, text="Timeline: No videos loaded")
        self.timeline_info_label.grid(row=0, column=0, sticky=tk.W)
        
        # Bind timeline click
        self.timeline_canvas.bind('<Button-1>', self.on_timeline_click)
        
        # Export Controls
        export_frame = ttk.LabelFrame(parent, text="Export Options", padding="10")
        export_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Button(export_frame, text="Export Final Video", 
                  command=self.export_final_video).grid(row=0, column=0, pady=2, sticky=(tk.W, tk.E))
        ttk.Button(export_frame, text="Export Audio Only", 
                  command=self.export_audio).grid(row=1, column=0, pady=2, sticky=(tk.W, tk.E))
        
        # Export options
        options_frame = ttk.Frame(export_frame)
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.include_subtitles = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include Subtitles", 
                       variable=self.include_subtitles).grid(row=0, column=0, sticky=tk.W)
        
        self.include_audio_mix = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include Audio Mix", 
                       variable=self.include_audio_mix).grid(row=1, column=0, sticky=tk.W)
        
        # Progress
        self.progress = ttk.Progressbar(export_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        parent.columnconfigure(0, weight=2)
        parent.columnconfigure(1, weight=1)
        
    def load_videos(self):
        """Load multiple video files and add to timeline"""
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
            ("All files", "*.*")
        ]
        files = filedialog.askopenfilenames(filetypes=filetypes)
        
        if files:
            new_videos = [Path(f) for f in files]
            self.video_files.extend(new_videos)
            
            # Add new videos to timeline
            for video in new_videos:
                if video not in self.timeline_videos:
                    self.timeline_videos.append(video)
            
            # Update video list
            self.video_listbox.delete(0, tk.END)
            for i, video in enumerate(self.timeline_videos):
                self.video_listbox.insert(tk.END, f"{i+1}. {video.name}")
            
            # Update timeline visual
            self.update_timeline_display()
            
            # Load first video for preview
            if self.timeline_videos:
                self.load_video(self.timeline_videos[0])
                self.current_video_index = 0
    
    def on_video_select(self, event):
        """Handle video selection from timeline list"""
        selection = self.video_listbox.curselection()
        if selection and self.timeline_videos:
            index = selection[0]
            self.load_video(self.timeline_videos[index])
            self.current_video_index = index
            self.update_timeline_display()
    
    def load_video(self, video_path):
        """Load a single video for preview"""
        try:
            if self.video_cap:
                self.video_cap.release()
            
            self.current_video = video_path
            self.video_cap = cv2.VideoCapture(str(video_path))
            
            if not self.video_cap.isOpened():
                messagebox.showerror("Error", f"Could not open video: {video_path.name}")
                return
            
            self.total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.video_cap.get(cv2.CAP_PROP_FPS) or 30
            duration = self.total_frames / self.fps
            
            # Update UI
            self.video_info_label.config(text=f"Video: {video_path.name}")
            self.time_label.config(text=f"00:00:00 / {self.format_time(duration)}")
            self.position_scale.config(to=self.total_frames-1)
            self.video_position.set(0)
            
            # Set trim end to video duration
            self.trim_end = duration
            self.trim_end_var.set(self.format_time(duration))
            
            # Show first frame
            self.show_frame(0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load video: {str(e)}")
    
    def show_frame(self, frame_number):
        """Display a specific frame"""
        if not self.video_cap:
            return
        
        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.video_cap.read()
        
        if ret:
            # Resize frame to fit canvas
            canvas_width = self.video_canvas.winfo_width()
            canvas_height = self.video_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Calculate scaling
                h, w = frame_rgb.shape[:2]
                scale = min(canvas_width/w, canvas_height/h)
                new_w, new_h = int(w*scale), int(h*scale)
                
                # Resize frame
                frame_resized = cv2.resize(frame_rgb, (new_w, new_h))
                
                # Add subtitle if enabled
                if self.preview_subtitle.get() and self.subtitle_entry.get(1.0, tk.END).strip():
                    frame_resized = self.add_subtitle_to_frame(frame_resized)
                
                # Convert to PhotoImage
                image = Image.fromarray(frame_resized)
                self.photo = ImageTk.PhotoImage(image)
                
                # Center on canvas
                x = (canvas_width - new_w) // 2
                y = (canvas_height - new_h) // 2
                
                self.video_canvas.delete("all")
                self.video_canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
        
        # Update current frame and time
        self.current_frame = frame_number
        current_time = frame_number / self.fps
        total_time = self.total_frames / self.fps
        self.time_label.config(text=f"{self.format_time(current_time)} / {self.format_time(total_time)}")
        self.video_position.set(frame_number)
    
    def add_subtitle_to_frame(self, frame):
        """Add subtitle text to frame"""
        try:
            # Get current subtitle text based on time position
            current_time = self.current_frame / self.fps if self.fps > 0 else 0
            subtitle_text = self.get_current_subtitle_text(current_time)
            
            # If no subtitle from file, use custom text
            if not subtitle_text:
                subtitle_text = self.subtitle_entry.get(1.0, tk.END).strip()
            
            if not subtitle_text:
                return frame
            
            # Convert to PIL Image
            pil_image = Image.fromarray(frame)
            draw = ImageDraw.Draw(pil_image)
            
            # Load font
            try:
                if self.font_file and Path(self.font_file).exists():
                    font = ImageFont.truetype(self.font_file, self.font_size_var.get())
                else:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # Calculate position
            text_bbox = draw.textbbox((0, 0), subtitle_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (pil_image.width - text_width) // 2
            y = int(pil_image.height * self.subtitle_position_y.get()) - text_height // 2
            
            # Draw text with outline
            color = self.font_color_var.get()
            outline_color = "#000000" if color != "#000000" else "#FFFFFF"
            
            # Draw outline
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        draw.text((x+dx, y+dy), subtitle_text, font=font, fill=outline_color)
            
            # Draw main text
            draw.text((x, y), subtitle_text, font=font, fill=color)
            
            return np.array(pil_image)
            
        except Exception as e:
            print(f"Error adding subtitle: {e}")
            return frame
    
    def get_current_subtitle_text(self, current_time):
        """Get subtitle text for current time position"""
        if not self.subtitle_tracks:
            return ""
        
        for subtitle in self.subtitle_tracks:
            if subtitle['start'] <= current_time <= subtitle['end']:
                return subtitle['text']
        
        return ""
    
    def toggle_playback(self):
        """Toggle video playback"""
        if not self.video_cap:
            return
        
        self.is_playing = not self.is_playing
        self.play_button.config(text="⏸" if self.is_playing else "▶")
        
        if self.is_playing:
            self.play_video()
    
    def play_video(self):
        """Play video continuously"""
        if not self.is_playing or not self.video_cap:
            return
        
        if self.current_frame < self.total_frames - 1:
            self.show_frame(self.current_frame + 1)
            # Schedule next frame
            delay = int(1000 / self.fps)
            self.root.after(delay, self.play_video)
        else:
            # End of video
            self.is_playing = False
            self.play_button.config(text="▶")
    
    def seek_start(self):
        """Seek to start"""
        self.show_frame(0)
    
    def seek_end(self):
        """Seek to end"""
        if self.total_frames > 0:
            self.show_frame(self.total_frames - 1)
    
    def seek_forward(self):
        """Seek forward 10 seconds"""
        if self.video_cap:
            new_frame = min(self.current_frame + int(10 * self.fps), self.total_frames - 1)
            self.show_frame(new_frame)
    
    def seek_backward(self):
        """Seek backward 10 seconds"""
        if self.video_cap:
            new_frame = max(self.current_frame - int(10 * self.fps), 0)
            self.show_frame(new_frame)
    
    def on_seek_start(self, event):
        """Start seeking"""
        self.was_playing = self.is_playing
        if self.is_playing:
            self.toggle_playback()
    
    def on_seek_end(self, event):
        """End seeking"""
        if self.video_cap:
            frame = int(self.video_position.get())
            self.show_frame(frame)
        
        if self.was_playing:
            self.toggle_playback()
    
    def set_trim_start(self):
        """Set trim start to current position"""
        if self.video_cap:
            self.trim_start = self.current_frame / self.fps
            self.trim_start_var.set(self.format_time(self.trim_start))
    
    def set_trim_end(self):
        """Set trim end to current position"""
        if self.video_cap:
            self.trim_end = self.current_frame / self.fps
            self.trim_end_var.set(self.format_time(self.trim_end))
    
    def preview_trim(self):
        """Preview the trimmed section"""
        if not self.video_cap:
            return
        
        start_frame = int(self.trim_start * self.fps)
        self.show_frame(start_frame)
        messagebox.showinfo("Trim Preview", 
                           f"Trim: {self.format_time(self.trim_start)} to {self.format_time(self.trim_end)}\n"
                           f"Duration: {self.format_time(self.trim_end - self.trim_start)}")
    
    def load_audio(self):
        """Load audio track"""
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.aac *.ogg *.flac"),
            ("All files", "*.*")
        ]
        file = filedialog.askopenfilename(filetypes=filetypes)
        
        if file:
            self.audio_tracks.append({"path": file, "type": "audio", "name": Path(file).name})
            self.audio_listbox.insert(tk.END, f"Audio: {Path(file).name}")
    
    def load_bgm(self):
        """Load background music"""
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.aac *.ogg *.flac"),
            ("All files", "*.*")
        ]
        file = filedialog.askopenfilename(filetypes=filetypes)
        
        if file:
            self.audio_tracks.append({"path": file, "type": "bgm", "name": Path(file).name})
            self.audio_listbox.insert(tk.END, f"BGM: {Path(file).name}")
    
    def load_font(self):
        """Load font file"""
        filetypes = [
            ("Font files", "*.ttf *.otf"),
            ("All files", "*.*")
        ]
        file = filedialog.askopenfilename(filetypes=filetypes)
        
        if file:
            self.font_file = file
            self.update_font_preview()
            messagebox.showinfo("Font Loaded", f"Loaded font: {Path(file).name}")
    
    def pick_color(self):
        """Pick font color"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(color=self.font_color_var.get())
        if color[1]:
            self.font_color_var.set(color[1])
            self.update_font_preview()
    
    def update_font_preview(self, event=None):
        """Update font preview"""
        try:
            # Clear canvas
            self.font_preview_canvas.delete("all")
            
            # Sample text
            sample_text = "Sample Text Preview"
            
            # Create preview image
            img = Image.new('RGB', (300, 60), color='black')
            draw = ImageDraw.Draw(img)
            
            # Load font
            try:
                if self.font_file and Path(self.font_file).exists():
                    font = ImageFont.truetype(self.font_file, self.font_size_var.get())
                else:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # Calculate position
            text_bbox = draw.textbbox((0, 0), sample_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (300 - text_width) // 2
            y = (60 - text_height) // 2
            
            # Draw text
            color = self.font_color_var.get()
            draw.text((x, y), sample_text, font=font, fill=color)
            
            # Convert to PhotoImage and display
            self.font_preview_photo = ImageTk.PhotoImage(img)
            self.font_preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.font_preview_photo)
            
        except Exception as e:
            print(f"Error updating font preview: {e}")
    
    def update_subtitle_preview(self, event=None):
        """Update subtitle preview in video"""
        if self.video_cap and self.preview_subtitle.get():
            self.show_frame(self.current_frame)
    
    def load_subtitle_file(self):
        """Load subtitle file (SRT format)"""
        filetypes = [
            ("Subtitle files", "*.srt *.vtt"),
            ("All files", "*.*")
        ]
        file = filedialog.askopenfilename(filetypes=filetypes)
        
        if file:
            self.current_subtitle_file = Path(file)
            self.parse_subtitle_file(file)
            self.subtitle_file_label.config(
                text=f"Subtitle: {Path(file).name}", 
                foreground="green"
            )
            messagebox.showinfo("Subtitle Loaded", f"Loaded subtitle: {Path(file).name}")
    
    def parse_subtitle_file(self, file_path):
        """Parse SRT subtitle file"""
        try:
            self.subtitle_tracks = []
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple SRT parsing
            blocks = content.strip().split('\n\n')
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    # Parse time format: 00:00:00,000 --> 00:00:00,000
                    if '-->' in lines[1]:
                        time_parts = lines[1].split(' --> ')
                        start_time = self.parse_srt_time(time_parts[0])
                        end_time = self.parse_srt_time(time_parts[1])
                        text = '\n'.join(lines[2:])
                        
                        self.subtitle_tracks.append({
                            'start': start_time,
                            'end': end_time,
                            'text': text
                        })
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse subtitle file: {str(e)}")
    
    def parse_srt_time(self, time_str):
        """Parse SRT time format to seconds"""
        # Format: 00:00:00,000
        time_str = time_str.replace(',', '.')
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    
    def remove_from_timeline(self):
        """Remove selected video from timeline"""
        selection = self.video_listbox.curselection()
        if selection and self.timeline_videos:
            index = selection[0]
            removed_video = self.timeline_videos.pop(index)
            
            # Update video list
            self.video_listbox.delete(0, tk.END)
            for i, video in enumerate(self.timeline_videos):
                self.video_listbox.insert(tk.END, f"{i+1}. {video.name}")
            
            # Update timeline display
            self.update_timeline_display()
            
            # Load next video if current was removed
            if index == self.current_video_index and self.timeline_videos:
                new_index = min(index, len(self.timeline_videos) - 1)
                self.load_video(self.timeline_videos[new_index])
                self.current_video_index = new_index
    
    def move_up_timeline(self):
        """Move selected video up in timeline"""
        selection = self.video_listbox.curselection()
        if selection and self.timeline_videos:
            index = selection[0]
            if index > 0:
                # Swap with previous
                self.timeline_videos[index], self.timeline_videos[index-1] = \
                    self.timeline_videos[index-1], self.timeline_videos[index]
                
                # Update video list
                self.video_listbox.delete(0, tk.END)
                for i, video in enumerate(self.timeline_videos):
                    self.video_listbox.insert(tk.END, f"{i+1}. {video.name}")
                
                # Update selection
                self.video_listbox.selection_set(index-1)
                
                # Update timeline display
                self.update_timeline_display()
    
    def update_timeline_display(self):
        """Update the visual timeline representation"""
        self.timeline_canvas.delete("all")
        
        if not self.timeline_videos:
            self.timeline_info_label.config(text="Timeline: No videos loaded")
            return
        
        # Calculate total duration and positions
        canvas_width = max(800, len(self.timeline_videos) * 120)
        self.timeline_canvas.config(scrollregion=(0, 0, canvas_width, 120))
        
        total_duration = 0
        x_pos = 10
        video_positions = []
        
        for i, video in enumerate(self.timeline_videos):
            # Get video duration (simplified - you'd normally read actual duration)
            duration = 60  # Placeholder duration
            
            # Draw video block
            block_width = max(100, duration * 2)  # Scale duration to pixels
            color = "lightblue" if i == self.current_video_index else "lightgray"
            
            rect = self.timeline_canvas.create_rectangle(
                x_pos, 20, x_pos + block_width, 80,
                fill=color, outline="black", width=2
            )
            
            # Add video name
            self.timeline_canvas.create_text(
                x_pos + block_width // 2, 50,
                text=video.stem[:10], font=("Arial", 8), width=block_width-10
            )
            
            video_positions.append((x_pos, x_pos + block_width, duration))
            x_pos += block_width + 5
            total_duration += duration
        
        # Update timeline info
        self.timeline_info_label.config(
            text=f"Timeline: {len(self.timeline_videos)} videos, {self.format_time(total_duration)} total"
        )
    
    def on_timeline_click(self, event):
        """Handle click on timeline to jump to video segment"""
        if not self.timeline_videos:
            return
        
        # Simple implementation - jump to video based on click position
        canvas_x = self.timeline_canvas.canvasx(event.x)
        
        # Find which video segment was clicked
        x_pos = 10
        for i, video in enumerate(self.timeline_videos):
            block_width = 100  # Simplified
            if x_pos <= canvas_x <= x_pos + block_width:
                self.load_video(video)
                self.current_video_index = i
                self.update_timeline_display()
                break
            x_pos += block_width + 5
    
    def export_final_video(self):
        """Export final video based on timeline with all effects"""
        if not self.timeline_videos:
            messagebox.showwarning("Warning", "No videos in timeline")
            return
        
        output_file = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        
        if output_file:
            self.progress.start()
            thread = threading.Thread(target=self._export_final_video_thread, args=(output_file,), daemon=True)
            thread.start()
    
    def _export_final_video_thread(self, output_file):
        """Export final video in background thread"""
        try:
            # Create input list file for timeline videos
            input_list = self.temp_dir / "timeline_input.txt"
            with open(input_list, 'w') as f:
                for video in self.timeline_videos:
                    f.write(f"file '{video.absolute()}'\n")
            
            # Build FFmpeg command based on options
            cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(input_list)]
            
            # Add audio mixing if selected
            audio_inputs = []
            if self.include_audio_mix.get() and self.audio_tracks:
                for i, track in enumerate(self.audio_tracks):
                    cmd.extend(["-i", track["path"]])
                    audio_inputs.append(i + 1)  # Input 0 is video
            
            # Add subtitle filter if selected and available
            filter_complex = []
            if self.include_subtitles.get():
                if self.current_subtitle_file and self.current_subtitle_file.exists():
                    # Add subtitle file input
                    cmd.extend(["-i", str(self.current_subtitle_file)])
                    subtitle_path = str(self.current_subtitle_file).replace('\\', '/')
                    filter_complex.append(f"[0:v]subtitles='{subtitle_path}'[v]")
                elif self.subtitle_entry.get(1.0, tk.END).strip():
                    # Burn in custom text (simplified)
                    text = self.subtitle_entry.get(1.0, tk.END).strip().replace("'", "\\'")
                    filter_complex.append(f"[0:v]drawtext=text='{text}':fontsize={self.font_size_var.get()}:fontcolor={self.font_color_var.get()}:x=(w-text_w)/2:y=h*{self.subtitle_position_y.get()}[v]")
            
            # Add audio mixing filter if needed
            if audio_inputs:
                audio_filter = "[0:a]"
                for i in audio_inputs:
                    audio_filter += f"[{i}:a]"
                audio_filter += f"amix=inputs={len(audio_inputs)+1}:duration=first[a]"
                filter_complex.append(audio_filter)
            
            # Apply filters
            if filter_complex:
                cmd.extend(["-filter_complex", ";".join(filter_complex)])
                if self.include_subtitles.get() and any("[v]" in f for f in filter_complex):
                    cmd.extend(["-map", "[v]"])
                else:
                    cmd.extend(["-map", "0:v"])
                    
                if audio_inputs:
                    cmd.extend(["-map", "[a]"])
                else:
                    cmd.extend(["-map", "0:a"])
            else:
                cmd.extend(["-c", "copy"])
            
            # Add output
            cmd.append(str(output_file))
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.root.after(0, lambda: messagebox.showinfo("Success", "Final video exported successfully!"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to export video: {result.stderr}"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error exporting final video: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.progress.stop())
    
    def export_audio(self):
        """Export audio mix only"""
        if not self.audio_tracks:
            messagebox.showwarning("Warning", "No audio tracks loaded")
            return
        
        output_file = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3"), ("WAV files", "*.wav"), ("All files", "*.*")]
        )
        
        if output_file:
            self.progress.start()
            thread = threading.Thread(target=self._export_audio_thread, args=(output_file,), daemon=True)
            thread.start()
    
    def _export_audio_thread(self, output_file):
        """Export audio mix in background thread"""
        try:
            if len(self.audio_tracks) == 1:
                # Single audio file - just copy
                cmd = ["ffmpeg", "-y", "-i", self.audio_tracks[0]["path"], 
                      "-acodec", "libmp3lame", str(output_file)]
            else:
                # Mix multiple audio files
                cmd = ["ffmpeg", "-y"]
                for track in self.audio_tracks:
                    cmd.extend(["-i", track["path"]])
                
                # Create mix filter
                mix_filter = "".join([f"[{i}:a]" for i in range(len(self.audio_tracks))])
                mix_filter += f"amix=inputs={len(self.audio_tracks)}:duration=first[a]"
                
                cmd.extend(["-filter_complex", mix_filter, "-map", "[a]", 
                           "-acodec", "libmp3lame", str(output_file)])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.root.after(0, lambda: messagebox.showinfo("Success", "Audio exported successfully!"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to export audio: {result.stderr}"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error exporting audio: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.progress.stop())
    
    def format_time(self, seconds):
        """Format seconds as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def on_closing(self):
        """Cleanup on window close"""
        try:
            if self.video_cap:
                self.video_cap.release()
            pygame.mixer.quit()
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except:
            pass
        finally:
            self.root.destroy()


def main():
    """Main application entry point"""
    # Check dependencies
    try:
        import cv2
        import pygame
        from PIL import Image, ImageTk, ImageFont, ImageDraw
    except ImportError as e:
        messagebox.showerror("Missing Dependencies", 
                           f"Required package not found: {e}\n\n"
                           "Please install: pip install opencv-python pygame pillow")
        return
    
    root = tk.Tk()
    app = VideoEditorGUI(root)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()