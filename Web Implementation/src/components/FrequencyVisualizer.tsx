import React, { useEffect, useRef } from 'react';

interface FrequencyVisualizerProps {
  frequencyData: Uint8Array;
  bands: { name: string; frequency: number; gain: number; color: string }[];
}

const FrequencyVisualizer: React.FC<FrequencyVisualizerProps> = ({ frequencyData, bands }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const draw = () => {
      const width = canvas.width;
      const height = canvas.height;
      const barWidth = width / frequencyData.length;

      // Clear canvas
      ctx.clearRect(0, 0, width, height);

      // Create gradient background
      const gradient = ctx.createLinearGradient(0, 0, 0, height);
      gradient.addColorStop(0, 'rgba(59, 130, 246, 0.1)');
      gradient.addColorStop(1, 'rgba(147, 51, 234, 0.1)');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);

      // Draw frequency bars
      ctx.strokeStyle = 'rgba(59, 130, 246, 0.3)';
      ctx.lineWidth = 1;

      for (let i = 0; i < frequencyData.length; i++) {
        const barHeight = (frequencyData[i] / 255) * height;
        const x = i * barWidth;

        // Create gradient for each bar
        const barGradient = ctx.createLinearGradient(0, height - barHeight, 0, height);
        barGradient.addColorStop(0, 'rgba(59, 130, 246, 0.8)');
        barGradient.addColorStop(0.5, 'rgba(147, 51, 234, 0.6)');
        barGradient.addColorStop(1, 'rgba(59, 130, 246, 0.3)');

        ctx.fillStyle = barGradient;
        ctx.fillRect(x, height - barHeight, barWidth - 1, barHeight);

        // Add glow effect for high frequencies
        if (frequencyData[i] > 128) {
          ctx.shadowColor = 'rgba(59, 130, 246, 0.5)';
          ctx.shadowBlur = 5;
          ctx.fillRect(x, height - barHeight, barWidth - 1, barHeight);
          ctx.shadowBlur = 0;
        }
      }

      // Draw band indicators
      bands.forEach((band, index) => {
        const nyquist = 22050; // Approximate Nyquist frequency
        const bandPosition = (band.frequency / nyquist) * width;
        
        ctx.strokeStyle = band.color;
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        
        ctx.beginPath();
        ctx.moveTo(bandPosition, 0);
        ctx.lineTo(bandPosition, height);
        ctx.stroke();
        
        // Label
        ctx.fillStyle = band.color;
        ctx.font = '12px monospace';
        ctx.fillText(band.name, bandPosition + 5, 20);
        
        ctx.setLineDash([]);
      });

      // Draw frequency scale
      ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
      ctx.font = '10px monospace';
      const frequencies = [100, 1000, 10000];
      frequencies.forEach(freq => {
        const nyquist = 22050;
        const x = (freq / nyquist) * width;
        ctx.fillText(`${freq}Hz`, x, height - 5);
      });

      animationRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [frequencyData, bands]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const resizeCanvas = () => {
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * window.devicePixelRatio;
      canvas.height = rect.height * window.devicePixelRatio;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
      }
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    return () => window.removeEventListener('resize', resizeCanvas);
  }, []);

  return (
    <div className="w-full h-64 bg-gray-900 rounded-lg overflow-hidden">
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
};

export default FrequencyVisualizer;