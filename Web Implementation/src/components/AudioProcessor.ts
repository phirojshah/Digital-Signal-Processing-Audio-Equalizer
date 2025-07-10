export default class AudioProcessor {
  private context: AudioContext;
  private source: AudioNode | null = null;
  private masterGainNode: GainNode;
  private analyser: AnalyserNode;
  private bandFilters: BiquadFilterNode[] = [];
  private bandGains: GainNode[] = [];
  private mixer: GainNode;
  private frequencyData: Uint8Array;
  
  public onFrequencyData: ((data: Uint8Array) => void) | null = null;

  constructor(context: AudioContext) {
    this.context = context;
    this.masterGainNode = context.createGain();
    this.analyser = context.createAnalyser();
    this.mixer = context.createGain();
    
    this.analyser.fftSize = 512;
    this.analyser.smoothingTimeConstant = 0.8;
    this.frequencyData = new Uint8Array(this.analyser.frequencyBinCount);
    
    // Connect master gain to destination
    this.masterGainNode.connect(context.destination);
    
    // Connect analyzer to master gain for visualization
    this.analyser.connect(this.masterGainNode);
    
    // Start frequency analysis
    this.startFrequencyAnalysis();
  }

  private startFrequencyAnalysis() {
    const updateFrequency = () => {
      this.analyser.getByteFrequencyData(this.frequencyData);
      if (this.onFrequencyData) {
        this.onFrequencyData(this.frequencyData);
      }
      requestAnimationFrame(updateFrequency);
    };
    updateFrequency();
  }

  setSource(source: AudioNode) {
    // Disconnect previous source
    if (this.source) {
      this.source.disconnect();
    }
    
    this.source = source;
    
    // Connect source to mixer
    this.source.connect(this.mixer);
    
    // Connect mixer to analyzer
    this.mixer.connect(this.analyser);
  }

  setBands(bands: { name: string; frequency: number; gain: number; color: string }[]) {
    // Clear existing filters and gains
    this.bandFilters.forEach(filter => filter.disconnect());
    this.bandGains.forEach(gain => gain.disconnect());
    
    this.bandFilters = [];
    this.bandGains = [];

    if (!this.source) return;

    // Create bandpass filters and gain nodes for each band
    bands.forEach((band, index) => {
      // Create bandpass filter
      const filter = this.context.createBiquadFilter();
      filter.type = 'peaking';
      filter.frequency.value = band.frequency;
      filter.Q.value = 1.0;
      filter.gain.value = band.gain;
      
      // Create gain node for this band
      const gainNode = this.context.createGain();
      gainNode.gain.value = this.dbToLinear(band.gain);
      
      // Connect: mixer -> filter -> gain -> analyzer
      this.mixer.connect(filter);
      filter.connect(gainNode);
      gainNode.connect(this.analyser);
      
      this.bandFilters.push(filter);
      this.bandGains.push(gainNode);
    });
  }

  setMasterGain(gain: number) {
    this.masterGainNode.gain.value = gain;
  }

  private dbToLinear(db: number): number {
    return Math.pow(10, db / 20);
  }

  updateBandGain(bandIndex: number, gainDb: number) {
    if (this.bandFilters[bandIndex] && this.bandGains[bandIndex]) {
      this.bandFilters[bandIndex].gain.value = gainDb;
      this.bandGains[bandIndex].gain.value = this.dbToLinear(gainDb);
    }
  }

  disconnect() {
    if (this.source) {
      this.source.disconnect();
    }
    this.bandFilters.forEach(filter => filter.disconnect());
    this.bandGains.forEach(gain => gain.disconnect());
    this.masterGainNode.disconnect();
    this.analyser.disconnect();
    this.mixer.disconnect();
  }
}