# Digital Signal Processing Audio Equalizer

A professional-grade multi-band audio equalizer implemented in both Python and Web technologies, demonstrating advanced digital signal processing concepts with real-time audio processing capabilities.

## 🎵 Project Overview

This project implements a sophisticated digital audio equalizer that splits audio signals into multiple frequency bands using bandpass filters and allows independent gain control for each band. The system reconstructs the output signal in real-time, providing professional-quality audio processing.

### 🌟 Key Features

- **Multi-Band Parametric EQ**: 6 frequency bands (Bass, Low Mid, Mid, High Mid, Treble, Presence)
- **Real-Time Processing**: Zero-latency audio processing for live input
- **Dual Implementation**: Both Python (desktop) and Web (browser) versions
- **Frequency Visualization**: Real-time spectrum analyzer with band markers
- **Professional UI**: Dark theme with intuitive controls
- **File Support**: Load and process audio files (WAV, MP3, FLAC, M4A)
- **Live Input**: Real-time microphone processing
- **Master Gain Control**: Overall volume control with clipping protection

## 🏗️ Project Structure

```
project/
├── Python Implementation/          # Desktop application
│   ├── audio_gui.py               # GUI interface using Tkinter
│   ├── audio_processor.py         # Core DSP engine
│   ├── main.py                    # Application entry point
│   └── requirements.txt           # Python dependencies
├── Web Implementation/            # Browser application
│   ├── src/
│   │   ├── components/
│   │   │   ├── AudioProcessor.ts  # Web Audio API processor
│   │   │   ├── BandControls.tsx   # EQ band controls
│   │   │   └── FrequencyVisualizer.tsx # Spectrum analyzer
│   │   ├── App.tsx               # Main React component
│   │   ├── main.tsx              # React entry point
│   │   └── index.css             # Tailwind styles
│   ├── package.json              # Node.js dependencies
│   └── vite.config.ts            # Vite configuration
└── README.md                     # This file
```

## 🚀 Quick Start

### Web Version (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd project/Web\ Implementation
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open in browser**
   - Navigate to `http://localhost:5173`
   - Allow microphone access for live processing

### Python Version

1. **Navigate to Python implementation**
   ```bash
   cd project/Python\ Implementation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 🎛️ How to Use

### Basic Operations

1. **Load Audio File**
   - Click "Upload Audio" (Web) or "Load Audio File" (Python)
   - Select an audio file (MP3, WAV, FLAC, M4A)
   - Click Play to hear the processed audio

2. **Live Microphone Processing**
   - Click "Use Mic" (Web) or "Start Recording" (Python)
   - Speak or play audio into your microphone
   - Adjust EQ bands to hear real-time changes

3. **Adjust EQ Bands**
   - Use vertical sliders to boost (+20dB) or cut (-20dB) frequencies
   - Each band targets specific frequency ranges:
     - **Bass (100Hz)**: Sub-bass and bass frequencies
     - **Low Mid (300Hz)**: Lower midrange, warmth
     - **Mid (1kHz)**: Vocal presence, clarity
     - **High Mid (3kHz)**: Upper midrange, definition
     - **Treble (8kHz)**: High frequencies, brightness
     - **Presence (15kHz)**: Air, sparkle, ultra-high frequencies

4. **Master Controls**
   - Adjust master gain for overall volume
   - Use "Reset" to return all bands to flat response

## 🔧 Technical Implementation

### Digital Signal Processing

#### Filter Design
Each EQ band uses a **biquad peaking filter** with the following characteristics:
- **Filter Type**: IIR (Infinite Impulse Response) peaking EQ
- **Transfer Function**: H(z) = (b₀ + b₁z⁻¹ + b₂z⁻²) / (a₀ + a₁z⁻¹ + a₂z⁻²)
- **Q Factor**: 1.0 for musical response
- **Gain Range**: ±20dB per band

#### Audio Processing Pipeline
```
Input Audio → Band 1 Filter → Band 2 Filter → ... → Band 6 Filter → Master Gain → Output
```

1. **Input**: Audio samples from file or microphone
2. **Band Processing**: Sequential filtering through active EQ bands
3. **Master Gain**: Final level adjustment
4. **Clipping Protection**: Soft limiting to prevent distortion
5. **Output**: Processed audio to speakers/headphones

### Architecture Comparison

| Feature | Python Implementation | Web Implementation |
|---------|----------------------|-------------------|
| **Audio API** | sounddevice + scipy | Web Audio API |
| **GUI Framework** | Tkinter | React + TypeScript |
| **Filter Implementation** | scipy.signal biquad | BiquadFilterNode |
| **Visualization** | matplotlib | HTML5 Canvas |
| **Real-time Processing** | Threading | AudioWorklet |
| **Platform** | Desktop (Windows/Mac/Linux) | Browser (Cross-platform) |

## 📊 Frequency Bands Specification

| Band | Center Frequency | Typical Use Case | Color Code |
|------|-----------------|------------------|------------|
| Bass | 100 Hz | Sub-bass, kick drums, bass guitar | 🔴 Red |
| Low Mid | 300 Hz | Lower midrange, warmth, body | 🟠 Orange |
| Mid | 1 kHz | Vocal presence, snare, clarity | 🟡 Yellow |
| High Mid | 3 kHz | Upper midrange, definition | 🟢 Green |
| Treble | 8 kHz | High frequencies, cymbals | 🔵 Blue |
| Presence | 15 kHz | Air, sparkle, ultra-highs | 🟣 Purple |

## 🎯 Performance Considerations

### Latency Optimization
- **Web**: Uses AudioWorklet for low-latency processing
- **Python**: Optimized buffer sizes and threading
- **Recommended**: Use ASIO drivers (Windows) for minimum latency

### CPU Usage
- Inactive bands (0dB gain) are automatically bypassed
- Efficient biquad filter implementation
- Real-time processing optimized for 44.1kHz sample rate

## 🛠️ Development

### Web Implementation
Built with modern web technologies:
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Vite** for fast development
- **Web Audio API** for audio processing
- **Lucide React** for icons

### Python Implementation
Desktop application using:
- **Tkinter** for GUI
- **NumPy/SciPy** for DSP
- **matplotlib** for visualization
- **sounddevice** for audio I/O
- **librosa** for file loading

## 🔍 Troubleshooting

### Common Issues

#### Web Version
- **No audio output**: Check browser audio permissions
- **High latency**: Use Chrome/Edge for best performance
- **Microphone not working**: Allow microphone access in browser

#### Python Version
- **Import errors**: Install all requirements with `pip install -r requirements.txt`
- **Audio device issues**: Check system audio settings
- **High CPU usage**: Reduce buffer size or close other audio applications

### Browser Compatibility
- ✅ Chrome 66+ (Recommended)
- ✅ Firefox 60+
- ✅ Safari 14.1+
- ✅ Edge 79+

## 📈 Future Enhancements

- [ ] Preset management system
- [ ] Additional filter types (high-pass, low-pass, notch)
- [ ] Spectrum analyzer with peak hold
- [ ] MIDI control support
- [ ] Export processed audio
- [ ] Compressor/limiter integration
- [ ] Reverb and delay effects

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional DSP effects
- UI/UX enhancements
- Performance optimizations
- Mobile responsiveness
- Accessibility features

## 📄 License

This project is open source and available under the MIT License.
