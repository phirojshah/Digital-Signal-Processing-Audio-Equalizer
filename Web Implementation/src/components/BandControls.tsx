import React from 'react';

interface BandControlsProps {
  bands: { name: string; frequency: number; gain: number; color: string }[];
  onBandChange: (index: number, gain: number) => void;
}

const BandControls: React.FC<BandControlsProps> = ({ bands, onBandChange }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
      {bands.map((band, index) => (
        <div key={index} className="bg-gray-700/50 rounded-lg p-4 border border-gray-600">
          <div className="text-center mb-4">
            <h3 className="font-semibold text-lg" style={{ color: band.color }}>
              {band.name}
            </h3>
            <p className="text-gray-400 text-sm">{band.frequency}Hz</p>
          </div>
          
          <div className="flex flex-col items-center">
            <div className="h-32 flex items-center">
              <input
                type="range"
                min="-20"
                max="20"
                step="0.5"
                value={band.gain}
                onChange={(e) => onBandChange(index, parseFloat(e.target.value))}
                className="vertical-slider"
                style={{
                  writingMode: 'bt-lr',
                  WebkitAppearance: 'slider-vertical',
                  width: '8px',
                  height: '120px',
                  background: `linear-gradient(to top, ${band.color}20, ${band.color}60)`,
                  outline: 'none',
                  cursor: 'pointer'
                }}
              />
            </div>
            
            <div className="mt-2 text-center">
              <span className="text-sm font-mono" style={{ color: band.color }}>
                {band.gain > 0 ? '+' : ''}{band.gain.toFixed(1)}dB
              </span>
            </div>
          </div>
          
          <div className="mt-3 flex justify-center">
            <button
              onClick={() => onBandChange(index, 0)}
              className="px-2 py-1 bg-gray-600 hover:bg-gray-500 rounded text-xs transition-colors"
            >
              Reset
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default BandControls;