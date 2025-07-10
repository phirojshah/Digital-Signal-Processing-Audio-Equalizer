import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, Upload, Mic, MicOff, Volume2, Settings } from 'lucide-react';
import AudioProcessor from './components/AudioProcessor';
import FrequencyVisualizer from './components/FrequencyVisualizer';
import BandControls from './components/BandControls';

export interface BandConfig {
  name: string;
  frequency: number;
  gain: number;
  color: string;
}

function App() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMicActive, setIsMicActive] = useState(false);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [audioContext, setAudioContext] = useState<AudioContext | null>(null);
  const [sourceNode, setSourceNode] = useState<AudioBufferSourceNode | MediaStreamAudioSourceNode | null>(null);
  const [frequencyData, setFrequencyData] = useState<Uint8Array>(new Uint8Array(256));
  const [masterGain, setMasterGain] = useState(0.7);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const audioProcessorRef = useRef<AudioProcessor | null>(null);

  const [bands, setBands] = useState<BandConfig[]>([
    { name: 'Bass', frequency: 100, gain: 0, color: '#EF4444' },
    { name: 'Low Mid', frequency: 300, gain: 0, color: '#F97316' },
    { name: 'Mid', frequency: 1000, gain: 0, color: '#EAB308' },
    { name: 'High Mid', frequency: 3000, gain: 0, color: '#22C55E' },
    { name: 'Treble', frequency: 8000, gain: 0, color: '#3B82F6' },
    { name: 'Presence', frequency: 15000, gain: 0, color: '#8B5CF6' }
  ]);

  useEffect(() => {
    if (!audioContext) {
      const context = new (window.AudioContext || (window as any).webkitAudioContext)();
      setAudioContext(context);
      audioProcessorRef.current = new AudioProcessor(context);
    }
  }, []);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('audio/')) {
      setAudioFile(file);
      setIsMicActive(false);
    }
  };

  const toggleMicrophone = async () => {
    if (!audioContext || !audioProcessorRef.current) return;

    if (isMicActive) {
      setIsMicActive(false);
      stopAudio();
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const micSource = audioContext.createMediaStreamSource(stream);
        
        audioProcessorRef.current.setSource(micSource);
        audioProcessorRef.current.setBands(bands);
        audioProcessorRef.current.setMasterGain(masterGain);
        audioProcessorRef.current.onFrequencyData = setFrequencyData;
        
        setSourceNode(micSource);
        setIsMicActive(true);
        setIsPlaying(true);
        setAudioFile(null);
      } catch (error) {
        console.error('Error accessing microphone:', error);
      }
    }
  };

  const playAudioFile = async () => {
    if (!audioFile || !audioContext || !audioProcessorRef.current) return;

    try {
      const arrayBuffer = await audioFile.arrayBuffer();
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
      
      const fileSource = audioContext.createBufferSource();
      fileSource.buffer = audioBuffer;
      fileSource.loop = true;
      
      audioProcessorRef.current.setSource(fileSource);
      audioProcessorRef.current.setBands(bands);
      audioProcessorRef.current.setMasterGain(masterGain);
      audioProcessorRef.current.onFrequencyData = setFrequencyData;
      
      fileSource.start();
      setSourceNode(fileSource);
      setIsPlaying(true);
    } catch (error) {
      console.error('Error playing audio file:', error);
    }
  };

  const stopAudio = () => {
    if (sourceNode) {
      if ('stop' in sourceNode) {
        sourceNode.stop();
      }
      if ('disconnect' in sourceNode) {
        sourceNode.disconnect();
      }
    }
    setIsPlaying(false);
    setSourceNode(null);
  };

  const togglePlayback = () => {
    if (isPlaying) {
      stopAudio();
    } else if (audioFile) {
      playAudioFile();
    }
  };

  const updateBandGain = (index: number, gain: number) => {
    const newBands = [...bands];
    newBands[index].gain = gain;
    setBands(newBands);
    
    if (audioProcessorRef.current) {
      audioProcessorRef.current.setBands(newBands);
    }
  };

  const updateMasterGain = (gain: number) => {
    setMasterGain(gain);
    if (audioProcessorRef.current) {
      audioProcessorRef.current.setMasterGain(gain);
    }
  };

  const resetAllBands = () => {
    const resetBands = bands.map(band => ({ ...band, gain: 0 }));
    setBands(resetBands);
    if (audioProcessorRef.current) {
      audioProcessorRef.current.setBands(resetBands);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Digital Audio Equalizer
          </h1>
          <p className="text-gray-400 text-lg">
            Professional multi-band frequency processing with real-time visualization
          </p>
        </div>

        {/* Control Panel */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 mb-8 border border-gray-700">
          <div className="flex flex-wrap items-center justify-center gap-4 mb-6">
            <div className="flex items-center gap-2">
              <input
                type="file"
                accept="audio/*"
                onChange={handleFileUpload}
                ref={fileInputRef}
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              >
                <Upload size={20} />
                Upload Audio
              </button>
            </div>

            <button
              onClick={toggleMicrophone}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                isMicActive 
                  ? 'bg-red-600 hover:bg-red-700' 
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {isMicActive ? <MicOff size={20} /> : <Mic size={20} />}
              {isMicActive ? 'Stop Mic' : 'Use Mic'}
            </button>

            {audioFile && (
              <button
                onClick={togglePlayback}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
              >
                {isPlaying ? <Pause size={20} /> : <Play size={20} />}
                {isPlaying ? 'Pause' : 'Play'}
              </button>
            )}
          </div>

          {/* Master Gain Control */}
          <div className="flex items-center justify-center gap-4 mb-6">
            <Volume2 size={20} className="text-gray-400" />
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-400 w-16">Master</span>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={masterGain}
                onChange={(e) => updateMasterGain(parseFloat(e.target.value))}
                className="w-32 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
              />
              <span className="text-sm text-gray-400 w-10">{Math.round(masterGain * 100)}%</span>
            </div>
            <button
              onClick={resetAllBands}
              className="flex items-center gap-2 px-3 py-1 bg-gray-600 hover:bg-gray-700 rounded text-sm transition-colors"
            >
              <Settings size={16} />
              Reset
            </button>
          </div>

          {/* Audio File Info */}
          {audioFile && (
            <div className="text-center text-gray-400 text-sm">
              <p>Loaded: {audioFile.name}</p>
            </div>
          )}
        </div>

        {/* Frequency Visualizer */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 mb-8 border border-gray-700">
          <h2 className="text-xl font-semibold mb-4 text-center">Frequency Spectrum</h2>
          <FrequencyVisualizer frequencyData={frequencyData} bands={bands} />
        </div>

        {/* Band Controls */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <h2 className="text-xl font-semibold mb-6 text-center">Frequency Bands</h2>
          <BandControls bands={bands} onBandChange={updateBandGain} />
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-500 text-sm">
          <p>Built with Web Audio API • Real-time Digital Signal Processing</p>
        </div>
      </div>

      <style jsx>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          width: 16px;
          height: 16px;
          background: #3B82F6;
          border-radius: 50%;
          cursor: pointer;
        }
        
        .slider::-moz-range-thumb {
          width: 16px;
          height: 16px;
          background: #3B82F6;
          border-radius: 50%;
          cursor: pointer;
          border: none;
        }
      `}</style>
    </div>
  );
}

export default App;