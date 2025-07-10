import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sounddevice as sd
import librosa
import threading
import time
from audio_processor import AudioProcessor

class AudioEqualizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Digital Audio Equalizer")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Audio processing components
        self.processor = AudioProcessor()
        self.audio_data = None
        self.sample_rate = 44100
        self.is_playing = False
        self.is_recording = False
        self.playback_thread = None
        self.record_thread = None
        self.current_stream = None
        
        # GUI components
        self.setup_styles()
        self.create_widgets()
        self.update_frequency_plot()
        
    def setup_styles(self):
        """Configure ttk styles for dark theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure dark theme colors
        style.configure('Dark.TFrame', background='#2b2b2b')
        style.configure('Dark.TLabel', background='#2b2b2b', foreground='white')
        style.configure('Dark.TButton', background='#404040', foreground='white')
        style.map('Dark.TButton', background=[('active', '#505050')])
        
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Digital Audio Equalizer", 
                               font=('Arial', 20, 'bold'), style='Dark.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Control panel
        self.create_control_panel(main_frame)
        
        # EQ controls
        self.create_eq_controls(main_frame)
        
        # Frequency response plot
        self.create_frequency_plot(main_frame)
        
    def create_control_panel(self, parent):
        """Create audio control panel"""
        control_frame = ttk.Frame(parent, style='Dark.TFrame')
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # File controls
        file_frame = ttk.Frame(control_frame, style='Dark.TFrame')
        file_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(file_frame, text="Load Audio File", command=self.load_audio_file,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(file_frame, text="Play/Pause", command=self.toggle_playback,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(file_frame, text="Stop", command=self.stop_playback,
                  style='Dark.TButton').pack(side=tk.LEFT)
        
        # Recording controls
        record_frame = ttk.Frame(control_frame, style='Dark.TFrame')
        record_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(record_frame, text="Start Recording", command=self.start_recording,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(record_frame, text="Stop Recording", command=self.stop_recording,
                  style='Dark.TButton').pack(side=tk.LEFT)
        
        # Master gain control
        gain_frame = ttk.Frame(control_frame, style='Dark.TFrame')
        gain_frame.pack(side=tk.RIGHT)
        
        ttk.Label(gain_frame, text="Master Gain:", style='Dark.TLabel').pack(side=tk.LEFT)
        
        self.master_gain_var = tk.DoubleVar(value=1.0)
        self.master_gain_scale = ttk.Scale(gain_frame, from_=0.0, to=2.0, 
                                          variable=self.master_gain_var,
                                          orient=tk.HORIZONTAL, length=150,
                                          command=self.update_master_gain)
        self.master_gain_scale.pack(side=tk.LEFT, padx=(5, 0))
        
        self.gain_label = ttk.Label(gain_frame, text="100%", style='Dark.TLabel')
        self.gain_label.pack(side=tk.LEFT, padx=(5, 0))
        
    def create_eq_controls(self, parent):
        """Create equalizer band controls"""
        eq_frame = ttk.LabelFrame(parent, text="Equalizer Bands", style='Dark.TFrame')
        eq_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create frame for band controls
        bands_frame = ttk.Frame(eq_frame, style='Dark.TFrame')
        bands_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.band_vars = []
        self.band_labels = []
        
        band_info = self.processor.get_band_info()
        
        for i, (name, freq, gain) in enumerate(band_info):
            # Band frame
            band_frame = ttk.Frame(bands_frame, style='Dark.TFrame')
            band_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
            
            # Band name and frequency
            ttk.Label(band_frame, text=name, font=('Arial', 10, 'bold'),
                     style='Dark.TLabel').pack()
            ttk.Label(band_frame, text=f"{freq}Hz", style='Dark.TLabel').pack()
            
            # Gain control
            gain_var = tk.DoubleVar(value=gain)
            self.band_vars.append(gain_var)
            
            scale = ttk.Scale(band_frame, from_=20, to=-20, variable=gain_var,
                             orient=tk.VERTICAL, length=200,
                             command=lambda val, idx=i: self.update_band_gain(idx, val))
            scale.pack(pady=10)
            
            # Gain label
            gain_label = ttk.Label(band_frame, text="0.0 dB", style='Dark.TLabel')
            gain_label.pack()
            self.band_labels.append(gain_label)
            
            # Reset button
            ttk.Button(band_frame, text="Reset", 
                      command=lambda idx=i: self.reset_band(idx),
                      style='Dark.TButton').pack(pady=(5, 0))
        
        # Reset all button
        ttk.Button(eq_frame, text="Reset All Bands", command=self.reset_all_bands,
                  style='Dark.TButton').pack(pady=10)
        
        # Test tone generator
        test_frame = ttk.Frame(eq_frame, style='Dark.TFrame')
        test_frame.pack(pady=10)
        
        ttk.Button(test_frame, text="Generate Test Tone", command=self.generate_test_tone,
                  style='Dark.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(test_frame, text="Freq:", style='Dark.TLabel').pack(side=tk.LEFT, padx=(10, 5))
        self.test_freq_var = tk.IntVar(value=1000)
        test_freq_scale = ttk.Scale(test_frame, from_=100, to=10000, 
                                   variable=self.test_freq_var,
                                   orient=tk.HORIZONTAL, length=200)
        test_freq_scale.pack(side=tk.LEFT, padx=(0, 5))
        
        self.test_freq_label = ttk.Label(test_frame, text="1000 Hz", style='Dark.TLabel')
        self.test_freq_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Update test frequency label
        def update_test_freq_label(val):
            self.test_freq_label.config(text=f"{int(float(val))} Hz")
        
        test_freq_scale.config(command=update_test_freq_label)
        
    def create_frequency_plot(self, parent):
        """Create frequency response plot"""
        plot_frame = ttk.LabelFrame(parent, text="Frequency Response", style='Dark.TFrame')
        plot_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(12, 4), dpi=100, facecolor='#2b2b2b')
        self.ax = self.fig.add_subplot(111, facecolor='#1e1e1e')
        
        # Configure plot appearance
        self.ax.set_xlabel('Frequency (Hz)', color='white')
        self.ax.set_ylabel('Magnitude (dB)', color='white')
        self.ax.set_xscale('log')
        self.ax.grid(True, alpha=0.3, color='white')
        self.ax.tick_params(colors='white')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def load_audio_file(self):
        """Load audio file"""
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio Files", "*.wav *.mp3 *.flac *.m4a"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                self.audio_data, self.sample_rate = librosa.load(file_path, sr=None)
                # Update processor sample rate
                self.processor.sample_rate = self.sample_rate
                messagebox.showinfo("Success", f"Loaded: {file_path.split('/')[-1]}\nSample Rate: {self.sample_rate} Hz")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load audio file: {str(e)}")
    
    def generate_test_tone(self):
        """Generate a test tone for EQ testing"""
        duration = 5.0  # 5 seconds
        frequency = self.test_freq_var.get()
        
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        # Generate a sine wave with some harmonics for more interesting EQ testing
        self.audio_data = (np.sin(2 * np.pi * frequency * t) * 0.3 + 
                          np.sin(2 * np.pi * frequency * 2 * t) * 0.1 +
                          np.sin(2 * np.pi * frequency * 3 * t) * 0.05)
        
        messagebox.showinfo("Test Tone", f"Generated {frequency} Hz test tone")
    
    def toggle_playback(self):
        """Toggle audio playback"""
        if self.audio_data is None:
            messagebox.showwarning("Warning", "Please load an audio file or generate a test tone first")
            return
            
        if self.is_playing:
            self.stop_playback()
        else:
            self.start_playback()
    
    def start_playback(self):
        """Start audio playback"""
        if self.audio_data is None:
            return
            
        self.is_playing = True
        self.playback_thread = threading.Thread(target=self._playback_worker)
        self.playback_thread.daemon = True
        self.playback_thread.start()
    
    def stop_playback(self):
        """Stop audio playback"""
        self.is_playing = False
        sd.stop()
        if self.current_stream:
            self.current_stream.close()
            self.current_stream = None
    
    def _playback_worker(self):
        """Audio playback worker thread"""
        try:
            # Process audio through equalizer
            print("Processing audio through EQ...")
            processed_audio = self.processor.process_audio(self.audio_data)
            
            print(f"Original audio range: {self.audio_data.min():.3f} to {self.audio_data.max():.3f}")
            print(f"Processed audio range: {processed_audio.min():.3f} to {processed_audio.max():.3f}")
            
            # Play processed audio
            sd.play(processed_audio, self.sample_rate)
            sd.wait()
        except Exception as e:
            print(f"Playback error: {e}")
            messagebox.showerror("Playback Error", f"Error during playback: {str(e)}")
        finally:
            self.is_playing = False
    
    def start_recording(self):
        """Start real-time audio recording and processing"""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.record_thread = threading.Thread(target=self._recording_worker)
        self.record_thread.daemon = True
        self.record_thread.start()
    
    def stop_recording(self):
        """Stop audio recording"""
        self.is_recording = False
        if self.current_stream:
            self.current_stream.close()
            self.current_stream = None
    
    def _recording_worker(self):
        """Real-time audio processing worker"""
        def audio_callback(indata, outdata, frames, time, status):
            if status:
                print(f"Audio callback status: {status}")
            
            try:
                # Process input audio through equalizer
                input_audio = indata[:, 0] if indata.shape[1] > 0 else indata.flatten()
                processed = self.processor.process_audio(input_audio)
                
                # Output processed audio to both channels
                if outdata.shape[1] == 2:
                    outdata[:, 0] = processed
                    outdata[:, 1] = processed
                else:
                    outdata[:, 0] = processed
            except Exception as e:
                print(f"Audio processing error: {e}")
                outdata.fill(0)  # Output silence on error
        
        try:
            with sd.Stream(callback=audio_callback, channels=2, 
                          samplerate=self.sample_rate, blocksize=512,
                          dtype=np.float32) as stream:
                self.current_stream = stream
                print("Real-time processing started...")
                while self.is_recording:
                    time.sleep(0.1)
        except Exception as e:
            print(f"Recording error: {e}")
            messagebox.showerror("Recording Error", f"Error during recording: {str(e)}")
        finally:
            self.is_recording = False
            self.current_stream = None
            print("Real-time processing stopped.")
    
    def update_band_gain(self, band_index, value):
        """Update EQ band gain"""
        gain_db = float(value)
        self.processor.update_band_gain(band_index, gain_db)
        self.band_labels[band_index].config(text=f"{gain_db:.1f} dB")
        self.update_frequency_plot()
        
        # Visual feedback
        band_info = self.processor.get_band_info()
        print(f"Band {band_index} ({band_info[band_index][0]}): {gain_db:.1f} dB")
    
    def update_master_gain(self, value):
        """Update master gain"""
        gain = float(value)
        self.processor.set_master_gain(gain)
        self.gain_label.config(text=f"{int(gain * 100)}%")
    
    def reset_band(self, band_index):
        """Reset specific band to 0 dB"""
        self.band_vars[band_index].set(0.0)
        self.processor.update_band_gain(band_index, 0.0)
        self.band_labels[band_index].config(text="0.0 dB")
        self.update_frequency_plot()
    
    def reset_all_bands(self):
        """Reset all bands to 0 dB"""
        for i in range(len(self.band_vars)):
            self.reset_band(i)
    
    def update_frequency_plot(self):
        """Update frequency response plot"""
        frequencies, magnitude = self.processor.get_frequency_response()
        
        self.ax.clear()
        self.ax.semilogx(frequencies, magnitude, 'cyan', linewidth=2, label='EQ Response')
        self.ax.axhline(y=0, color='white', linestyle='-', alpha=0.3)
        self.ax.set_xlabel('Frequency (Hz)', color='white')
        self.ax.set_ylabel('Magnitude (dB)', color='white')
        self.ax.set_title('Frequency Response', color='white')
        self.ax.grid(True, alpha=0.3, color='white')
        self.ax.tick_params(colors='white')
        self.ax.set_xlim(20, 20000)
        self.ax.set_ylim(-25, 25)
        
        # Add band frequency markers
        band_info = self.processor.get_band_info()
        colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
        for i, (name, freq, gain) in enumerate(band_info):
            color = colors[i % len(colors)]
            self.ax.axvline(x=freq, color=color, alpha=0.7, linestyle='--', linewidth=1)
            self.ax.text(freq, 22, name, rotation=90, ha='center', va='bottom', 
                        color=color, fontsize=8, weight='bold')
            
            # Show gain value
            if abs(gain) > 0.1:
                self.ax.text(freq, gain + 2, f"{gain:+.1f}dB", ha='center', va='bottom',
                           color=color, fontsize=7, weight='bold')
        
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = AudioEqualizerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
