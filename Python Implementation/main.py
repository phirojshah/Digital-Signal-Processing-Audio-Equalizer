#!/usr/bin/env python3
"""
Digital Signal Processing Audio Equalizer
A Python implementation of a multi-band audio equalizer with real-time processing capabilities.

Features:
- Multi-band parametric equalizer (6 bands by default)
- Real-time audio processing from microphone
- Audio file playback with EQ processing
- Frequency response visualization
- Master gain control
- Individual band reset and global reset

Author: DSP Audio Equalizer
"""

import tkinter as tk
from audio_gui import AudioEqualizerGUI
import sys
import os

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'numpy', 'scipy', 'matplotlib', 'sounddevice', 'librosa'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install missing packages using:")
        print("pip install " + " ".join(missing_packages))
        return False
    
    return True

def main():
    """Main application entry point"""
    print("Digital Signal Processing Audio Equalizer")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # Create and run the GUI application
        root = tk.Tk()
        app = AudioEqualizerGUI(root)
        
        print("Starting GUI application...")
        print("Features available:")
        print("  - Load and play audio files with EQ processing")
        print("  - Real-time microphone input processing")
        print("  - 6-band parametric equalizer")
        print("  - Frequency response visualization")
        print("  - Master gain control")
        
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
