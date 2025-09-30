"""
Test script to verify dependencies and basic functionality for app_gui.py
"""

def test_dependencies():
    """Test if all required dependencies are available"""
    print("Testing dependencies for Advanced Video Editor...")
    
    try:
        import tkinter as tk
        print("✓ tkinter - GUI framework")
    except ImportError:
        print("✗ tkinter - Missing (should be included with Python)")
        return False
    
    try:
        import cv2
        print(f"✓ opencv-python - Video processing (version: {cv2.__version__})")
    except ImportError:
        print("✗ opencv-python - Missing")
        return False
    
    try:
        import pygame
        print(f"✓ pygame - Audio processing (version: {pygame.version.ver})")
    except ImportError:
        print("✗ pygame - Missing")
        return False
    
    try:
        from PIL import Image, ImageTk, ImageFont, ImageDraw
        print(f"✓ Pillow - Image processing (version: {Image.__version__})")
    except ImportError:
        print("✗ Pillow - Missing")
        return False
    
    try:
        import numpy as np
        print(f"✓ numpy - Array processing (version: {np.__version__})")
    except ImportError:
        print("✗ numpy - Missing")
        return False
    
    print("\n✓ All dependencies are available!")
    return True

def test_basic_functionality():
    """Test basic functionality without GUI"""
    print("\nTesting basic functionality...")
    
    try:
        # Test OpenCV video capabilities
        import cv2
        print("✓ OpenCV video support available")
        
        # Test pygame audio
        import pygame
        pygame.mixer.init()
        print("✓ Pygame audio initialized")
        pygame.mixer.quit()
        
        # Test PIL font handling
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (100, 50), 'black')
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text((10, 10), "Test", font=font, fill='white')
        print("✓ PIL text rendering works")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def test_gui_creation():
    """Test GUI creation without showing window"""
    print("\nTesting GUI creation...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # Create root but don't show it
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test basic widget creation
        frame = ttk.Frame(root)
        label = ttk.Label(frame, text="Test")
        button = ttk.Button(frame, text="Test")
        
        print("✓ GUI widgets can be created")
        
        # Cleanup
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ GUI creation test failed: {e}")
        return False

if __name__ == "__main__":
    print("Advanced Video Editor - Dependency and Functionality Test")
    print("=" * 60)
    
    deps_ok = test_dependencies()
    if not deps_ok:
        print("\nPlease install missing dependencies with:")
        print("pip install opencv-python pygame pillow")
        exit(1)
    
    func_ok = test_basic_functionality()
    if not func_ok:
        print("\nBasic functionality test failed!")
        exit(1)
    
    gui_ok = test_gui_creation()
    if not gui_ok:
        print("\nGUI creation test failed!")
        exit(1)
    
    print("\n" + "=" * 60)
    print("✓ All tests passed! The Advanced Video Editor should work properly.")
    print("You can now run: python app_gui.py")