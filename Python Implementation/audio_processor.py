import numpy as np
from scipy import signal
from scipy.signal import butter, sosfilt, sosfiltfilt
import threading
import time

class AudioProcessor:
    def __init__(self, sample_rate=44100, buffer_size=1024):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.bands = []
        self.master_gain = 1.0
        self.is_processing = False
        
        # Initialize default EQ bands
        self.init_default_bands()
        
    def init_default_bands(self):
        """Initialize default equalizer bands"""
        default_bands = [
            {'name': 'Bass', 'freq': 100, 'gain': 0, 'q': 1.0},
            {'name': 'Low Mid', 'freq': 300, 'gain': 0, 'q': 1.0},
            {'name': 'Mid', 'freq': 1000, 'gain': 0, 'q': 1.0},
            {'name': 'High Mid', 'freq': 3000, 'gain': 0, 'q': 1.0},
            {'name': 'Treble', 'freq': 8000, 'gain': 0, 'q': 1.0},
            {'name': 'Presence', 'freq': 15000, 'gain': 0, 'q': 1.0}
        ]
        
        for band in default_bands:
            self.add_band(band['name'], band['freq'], band['gain'], band['q'])
    
    def add_band(self, name, frequency, gain_db, q_factor):
        """Add a new frequency band"""
        band = {
            'name': name,
            'frequency': frequency,
            'gain_db': gain_db,
            'q_factor': q_factor,
            'filter_coeffs': self._design_peaking_filter(frequency, gain_db, q_factor)
        }
        self.bands.append(band)
    
    def _design_peaking_filter(self, freq, gain_db, q):
        """Design a peaking EQ filter using biquad coefficients"""
        # Convert gain from dB to linear
        A = 10**(gain_db / 40)
        omega = 2 * np.pi * freq / self.sample_rate
        sin_omega = np.sin(omega)
        cos_omega = np.cos(omega)
        alpha = sin_omega / (2 * q)
        
        # Peaking EQ coefficients
        b0 = 1 + alpha * A
        b1 = -2 * cos_omega
        b2 = 1 - alpha * A
        a0 = 1 + alpha / A
        a1 = -2 * cos_omega
        a2 = 1 - alpha / A
        
        # Normalize coefficients
        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0
        
        return b, a
    
    def update_band_gain(self, band_index, gain_db):
        """Update gain for a specific band"""
        if 0 <= band_index < len(self.bands):
            self.bands[band_index]['gain_db'] = gain_db
            freq = self.bands[band_index]['frequency']
            q = self.bands[band_index]['q_factor']
            self.bands[band_index]['filter_coeffs'] = self._design_peaking_filter(freq, gain_db, q)
    
    def set_master_gain(self, gain_linear):
        """Set master gain (0.0 to 2.0)"""
        self.master_gain = max(0.0, min(2.0, gain_linear))
    
    def process_audio(self, audio_data):
        """Process audio through all EQ bands"""
        if len(audio_data.shape) == 1:
            # Mono audio
            processed = self._process_mono(audio_data)
        else:
            # Stereo audio
            processed = np.zeros_like(audio_data)
            for channel in range(audio_data.shape[1]):
                processed[:, channel] = self._process_mono(audio_data[:, channel])
        
        # Apply master gain
        processed *= self.master_gain
        
        # Prevent clipping
        processed = np.clip(processed, -1.0, 1.0)
        
        return processed
    
    def _process_mono(self, mono_audio):
        """Process mono audio through EQ bands"""
        processed = mono_audio.copy()
        
        for band in self.bands:
            if band['gain_db'] != 0:  # Only process if gain is not zero
                b, a = band['filter_coeffs']
                try:
                    processed = signal.lfilter(b, a, processed)
                except:
                    # Fallback if filter becomes unstable
                    continue
        
        return processed
    
    def get_frequency_response(self, frequencies=None):
        """Calculate frequency response of the current EQ settings"""
        if frequencies is None:
            frequencies = np.logspace(1, 4.3, 1000)  # 10Hz to 20kHz
        
        # Initialize with flat response
        total_response = np.ones(len(frequencies), dtype=complex)
        
        for band in self.bands:
            if band['gain_db'] != 0:
                b, a = band['filter_coeffs']
                w, h = signal.freqs(b, a, worN=frequencies * 2 * np.pi / self.sample_rate)
                total_response *= h
        
        # Convert to magnitude in dB
        magnitude_db = 20 * np.log10(np.abs(total_response))
        
        return frequencies, magnitude_db
    
    def reset_all_bands(self):
        """Reset all bands to 0 dB gain"""
        for i in range(len(self.bands)):
            self.update_band_gain(i, 0.0)
    
    def get_band_info(self):
        """Get information about all bands"""
        return [(band['name'], band['frequency'], band['gain_db']) for band in self.bands]
