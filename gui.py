"""
Video CLI GUI - Tkinter Frontend
Professional interface for the Video CLI processing pipeline
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
from pathlib import Path
import os
import sys


class VideoCLIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video CLI - Professional Video Processing")
        self.root.geometry("900x800")
        self.root.minsize(800, 600)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Variables
        self.setup_variables()
        
        # Find project root and venv
        self.project_root = self.find_project_root()
        self.venv_path = self.project_root / ".venv"
        
        # Create UI
        self.create_widgets()
        
        # Set default directories
        self.set_default_directories()
        
    def setup_variables(self):
        """Initialize all tkinter variables"""
        # Directory paths
        self.video_dir = tk.StringVar()
        self.caption_dir = tk.StringVar()
        self.bgm_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.output_file = tk.StringVar()
        
        # Processing options
        self.bgm_file = tk.StringVar()
        self.bgm_volume = tk.DoubleVar(value=0.15)
        self.burn_in = tk.BooleanVar()
        self.generate_captions = tk.BooleanVar()
        self.language = tk.StringVar(value="en-US")
        self.sample_rate = tk.IntVar(value=16000)
        self.keep_temp = tk.BooleanVar()
        
        # Video extensions
        self.extensions = tk.StringVar(value=".mp4 .mov .mkv .avi")
    
    def find_project_root(self):
        """Find the project root directory"""
        current = Path(__file__).parent
        while current.parent != current:
            if (current / "src" / "video_cli").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Video CLI - Professional Video Processing", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Create notebook for organized tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(1, weight=1)
        
        # Tab 1: Directories
        dir_frame = ttk.Frame(notebook, padding="10")
        notebook.add(dir_frame, text="Directories")
        self.create_directory_tab(dir_frame)
        
        # Tab 2: Processing Options
        options_frame = ttk.Frame(notebook, padding="10")
        notebook.add(options_frame, text="Processing Options")
        self.create_options_tab(options_frame)
        
        # Tab 3: Advanced Settings
        advanced_frame = ttk.Frame(notebook, padding="10")
        notebook.add(advanced_frame, text="Advanced Settings")
        self.create_advanced_tab(advanced_frame)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Process Videos", command=self.process_videos,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Preview Command", command=self.preview_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset Defaults", command=self.reset_defaults).pack(side=tk.LEFT, padx=5)
        
        # Output log
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="5")
        log_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
    
    def create_directory_tab(self, parent):
        """Create directory selection tab"""
        # Input Directories
        input_frame = ttk.LabelFrame(parent, text="Input Directories", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Video directory
        ttk.Label(input_frame, text="Video Directory:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(input_frame, textvariable=self.video_dir).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(input_frame, text="Browse", command=lambda: self.browse_directory(self.video_dir)).grid(row=0, column=2, pady=2)
        
        # Caption directory
        ttk.Label(input_frame, text="Caption Directory:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(input_frame, textvariable=self.caption_dir).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(input_frame, text="Browse", command=lambda: self.browse_directory(self.caption_dir)).grid(row=1, column=2, pady=2)
        
        # BGM directory
        ttk.Label(input_frame, text="BGM Directory:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(input_frame, textvariable=self.bgm_dir).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(input_frame, text="Browse", command=lambda: self.browse_directory(self.bgm_dir)).grid(row=2, column=2, pady=2)
        
        # Output Configuration
        output_frame = ttk.LabelFrame(parent, text="Output Configuration", padding="10")
        output_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        # Output directory
        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(output_frame, textvariable=self.output_dir).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(output_frame, text="Browse", command=lambda: self.browse_directory(self.output_dir)).grid(row=0, column=2, pady=2)
        
        # Output filename
        ttk.Label(output_frame, text="Output Filename:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(output_frame, textvariable=self.output_file).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Label(output_frame, text="(e.g., final.mp4)", font=('Arial', 8)).grid(row=1, column=3, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Directory info
        info_frame = ttk.LabelFrame(parent, text="Directory Structure Info", padding="10")
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        info_text = ("• Video: Place your input videos (.mp4, .mov, .mkv, .avi)\n"
                    "• Caption: Place matching .srt files or combined.srt\n"
                    "• BGM: Place background music files (.mp3, .wav, .m4a)\n"
                    "• Output: Generated videos will be saved here")
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)
        
        parent.columnconfigure(0, weight=1)
    
    def create_options_tab(self, parent):
        """Create processing options tab"""
        # Subtitle Options
        subtitle_frame = ttk.LabelFrame(parent, text="Subtitle Options", padding="10")
        subtitle_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5), pady=(0, 10))
        
        ttk.Checkbutton(subtitle_frame, text="Burn-in subtitles (hard-coded into video)", 
                       variable=self.burn_in).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(subtitle_frame, text="Generate captions using Google Speech-to-Text", 
                       variable=self.generate_captions).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        ttk.Label(subtitle_frame, text="Language code:").grid(row=2, column=0, sticky=tk.W, pady=2)
        lang_combo = ttk.Combobox(subtitle_frame, textvariable=self.language, width=10)
        lang_combo['values'] = ('en-US', 'es-ES', 'fr-FR', 'de-DE', 'it-IT', 'pt-BR', 'ru-RU', 'ja-JP', 'ko-KR', 'zh-CN')
        lang_combo.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Audio Options
        audio_frame = ttk.LabelFrame(parent, text="Audio & BGM Options", padding="10")
        audio_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(0, 10))
        
        ttk.Label(audio_frame, text="Specific BGM file:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(audio_frame, textvariable=self.bgm_file, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(audio_frame, text="Browse", command=self.browse_bgm_file).grid(row=0, column=2, pady=2)
        
        ttk.Label(audio_frame, text="BGM Volume:").grid(row=1, column=0, sticky=tk.W, pady=2)
        volume_frame = ttk.Frame(audio_frame)
        volume_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        
        volume_scale = ttk.Scale(volume_frame, from_=0.0, to=1.0, variable=self.bgm_volume, 
                               orient=tk.HORIZONTAL, length=200)
        volume_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        volume_frame.columnconfigure(0, weight=1)
        
        volume_label = ttk.Label(volume_frame, text="0.15")
        volume_label.grid(row=0, column=1, padx=(5, 0))
        
        def update_volume_label(*args):
            volume_label.config(text=f"{self.bgm_volume.get():.2f}")
        self.bgm_volume.trace('w', update_volume_label)
        
        # Video Extensions
        ext_frame = ttk.LabelFrame(parent, text="Video File Extensions", padding="10")
        ext_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        ext_frame.columnconfigure(1, weight=1)
        
        ttk.Label(ext_frame, text="Extensions to process:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(ext_frame, textvariable=self.extensions).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        ttk.Label(ext_frame, text="Space-separated (e.g., .mp4 .mov .mkv)", 
                 font=('Arial', 8)).grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
    
    def create_advanced_tab(self, parent):
        """Create advanced settings tab"""
        # Speech-to-Text Settings
        stt_frame = ttk.LabelFrame(parent, text="Speech-to-Text Settings", padding="10")
        stt_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5), pady=(0, 10))
        
        ttk.Label(stt_frame, text="Sample Rate (Hz):").grid(row=0, column=0, sticky=tk.W, pady=2)
        rate_combo = ttk.Combobox(stt_frame, textvariable=self.sample_rate, width=10)
        rate_combo['values'] = (8000, 16000, 22050, 44100, 48000)
        rate_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Debug Options
        debug_frame = ttk.LabelFrame(parent, text="Debug Options", padding="10")
        debug_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=(0, 10))
        
        ttk.Checkbutton(debug_frame, text="Keep temporary files for debugging", 
                       variable=self.keep_temp).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # System Information
        sys_frame = ttk.LabelFrame(parent, text="System Information", padding="10")
        sys_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Check for required components
        ffmpeg_status = "✓ Available" if self.check_ffmpeg() else "✗ Not found"
        venv_status = "✓ Found" if self.venv_path.exists() else "✗ Not found"
        
        info_text = f"Project Root: {self.project_root}\n"
        info_text += f"Virtual Environment: {venv_status}\n"
        info_text += f"FFmpeg: {ffmpeg_status}\n"
        info_text += f"Python: {sys.version.split()[0]}"
        
        ttk.Label(sys_frame, text=info_text, justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)
        
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
    
    def set_default_directories(self):
        """Set default directory paths"""
        self.video_dir.set(str(self.project_root / "Video"))
        self.caption_dir.set(str(self.project_root / "Caption"))
        self.bgm_dir.set(str(self.project_root / "BGM"))
        self.output_dir.set(str(self.project_root / "Output"))
        self.output_file.set("merged.mp4")
    
    def browse_directory(self, var):
        """Browse for directory"""
        directory = filedialog.askdirectory(initialdir=var.get())
        if directory:
            var.set(directory)
    
    def browse_bgm_file(self):
        """Browse for BGM file"""
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.m4a *.flac *.aac *.ogg"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            initialdir=self.bgm_dir.get(),
            filetypes=filetypes
        )
        if filename:
            self.bgm_file.set(filename)
    
    def check_ffmpeg(self):
        """Check if FFmpeg is available"""
        try:
            subprocess.run(["ffmpeg", "-version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def build_command(self):
        """Build the CLI command"""
        if not self.venv_path.exists():
            raise FileNotFoundError("Virtual environment not found. Please ensure .venv exists in the project directory.")
        
        # Base command with venv activation
        if os.name == 'nt':  # Windows
            python_exe = self.venv_path / "Scripts" / "python.exe"
        else:  # Unix-like
            python_exe = self.venv_path / "bin" / "python"
        
        cmd = [str(python_exe), "-m", "src.video_cli.cli"]
        
        # Add arguments
        if self.video_dir.get():
            cmd.extend(["--video-dir", self.video_dir.get()])
        if self.caption_dir.get():
            cmd.extend(["--caption-dir", self.caption_dir.get()])
        if self.bgm_dir.get():
            cmd.extend(["--bgm-dir", self.bgm_dir.get()])
        if self.output_dir.get():
            cmd.extend(["--output-dir", self.output_dir.get()])
        
        # Output file
        if self.output_file.get():
            output_path = Path(self.output_dir.get()) / self.output_file.get()
            cmd.extend(["--output", str(output_path)])
        
        # Processing options
        if self.bgm_file.get():
            cmd.extend(["--bgm-file", self.bgm_file.get()])
        
        cmd.extend(["--bgm-volume", str(self.bgm_volume.get())])
        
        if self.burn_in.get():
            cmd.append("--burn-in")
        
        if self.generate_captions.get():
            cmd.append("--generate-captions")
            cmd.extend(["--language", self.language.get()])
            cmd.extend(["--sample-rate", str(self.sample_rate.get())])
        
        if self.keep_temp.get():
            cmd.append("--keep-temp")
        
        # Extensions
        if self.extensions.get().strip():
            ext_list = self.extensions.get().split()
            cmd.extend(["--exts"] + ext_list)
        
        return cmd
    
    def preview_command(self):
        """Preview the command that would be executed"""
        try:
            cmd = self.build_command()
            command_str = " ".join(f'"{arg}"' if " " in arg else arg for arg in cmd)
            
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Command Preview")
            preview_window.geometry("700x300")
            
            ttk.Label(preview_window, text="Command that will be executed:", 
                     font=('Arial', 12, 'bold')).pack(anchor=tk.W, padx=10, pady=(10, 5))
            
            text_widget = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD, height=10)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
            text_widget.insert(tk.END, command_str)
            text_widget.config(state=tk.DISABLED)
            
            button_frame = ttk.Frame(preview_window)
            button_frame.pack(pady=10)
            ttk.Button(button_frame, text="Copy to Clipboard", 
                      command=lambda: self.copy_to_clipboard(command_str)).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Close", 
                      command=preview_window.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to build command: {str(e)}")
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", "Command copied to clipboard!")
    
    def log_message(self, message):
        """Add message to log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def process_videos(self):
        """Start video processing in a separate thread"""
        try:
            # Validate inputs
            if not Path(self.video_dir.get()).exists():
                messagebox.showerror("Error", "Video directory does not exist!")
                return
            
            if not self.output_file.get():
                messagebox.showerror("Error", "Please specify an output filename!")
                return
            
            # Disable process button and start progress
            for widget in self.root.winfo_children():
                self.disable_widget_tree(widget)
            self.progress.start()
            
            # Start processing in thread
            thread = threading.Thread(target=self.run_processing, daemon=True)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start processing: {str(e)}")
    
    def disable_widget_tree(self, widget):
        """Recursively disable all widgets"""
        try:
            widget.config(state='disabled')
        except:
            pass
        for child in widget.winfo_children():
            self.disable_widget_tree(child)
    
    def enable_widget_tree(self, widget):
        """Recursively enable all widgets"""
        try:
            widget.config(state='normal')
        except:
            pass
        for child in widget.winfo_children():
            self.enable_widget_tree(child)
    
    def run_processing(self):
        """Run the video processing"""
        try:
            cmd = self.build_command()
            
            self.log_message("=" * 50)
            self.log_message("Starting video processing...")
            self.log_message(f"Command: {' '.join(cmd)}")
            self.log_message("=" * 50)
            
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            # Run the command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            # Stream output
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_message(output.strip())
            
            # Wait for completion
            return_code = process.poll()
            
            # Restore directory
            os.chdir(original_cwd)
            
            if return_code == 0:
                self.log_message("=" * 50)
                self.log_message("✓ Processing completed successfully!")
                self.log_message("=" * 50)
                messagebox.showinfo("Success", "Video processing completed successfully!")
            else:
                self.log_message("=" * 50)
                self.log_message(f"✗ Processing failed with return code: {return_code}")
                self.log_message("=" * 50)
                messagebox.showerror("Error", f"Processing failed with return code: {return_code}")
                
        except Exception as e:
            self.log_message(f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
        
        finally:
            # Re-enable interface
            self.progress.stop()
            for widget in self.root.winfo_children():
                self.enable_widget_tree(widget)
    
    def reset_defaults(self):
        """Reset all settings to defaults"""
        self.set_default_directories()
        self.bgm_file.set("")
        self.bgm_volume.set(0.15)
        self.burn_in.set(False)
        self.generate_captions.set(False)
        self.language.set("en-US")
        self.sample_rate.set(16000)
        self.keep_temp.set(False)
        self.extensions.set(".mp4 .mov .mkv .avi")
        self.output_file.set("merged.mp4")


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = VideoCLIGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()