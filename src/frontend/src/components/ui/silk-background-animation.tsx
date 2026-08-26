'use client';

import { useEffect, useRef } from 'react';

function SilkBackgroundAnimation() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
      return;
    }

    let time = 0;
    const speed = 0.042;
    const scale = 2.35;
    const noiseIntensity = 0.75;

    const resizeCanvas = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 1.25);
      const renderScale = 0.58;
      const width = window.innerWidth;
      const height = window.innerHeight;

      canvas.width = Math.floor(width * dpr * renderScale);
      canvas.height = Math.floor(height * dpr * renderScale);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
    };

    const noise = (x: number, y: number) => {
      const g = 2.71828;
      const rx = g * Math.sin(g * x);
      const ry = g * Math.sin(g * y);
      return (rx * ry * (1 + x)) % 1;
    };

    const animate = () => {
      const { width, height } = canvas;
      const gradient = ctx.createLinearGradient(0, 0, width, height);

      gradient.addColorStop(0, '#f8fbff');
      gradient.addColorStop(0.42, '#e7f1fb');
      gradient.addColorStop(1, '#ffffff');

      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);

      const imageData = ctx.createImageData(width, height);
      const data = imageData.data;

      for (let x = 0; x < width; x += 1) {
        for (let y = 0; y < height; y += 1) {
          const u = (x / width) * scale;
          const v = (y / height) * scale;
          const tOffset = speed * time;
          const texX = u + 0.045 * Math.sin(3.4 * v + tOffset * 0.6);
          const texY =
            v +
            0.08 * Math.sin(8 * texX - tOffset) +
            0.035 * Math.cos(5.5 * u + tOffset * 0.85);

          const pattern =
            0.6 +
            0.4 *
              Math.sin(
                5 * (texX + texY + Math.cos(3 * texX + 5 * texY) + 0.02 * tOffset) +
                  Math.sin(20 * (texX + texY - 0.18 * tOffset)),
              );

          const rnd = noise(x, y);
          const intensity = Math.max(0, pattern - (rnd / 15) * noiseIntensity);

          const r = Math.floor(245 - 58 * intensity);
          const g = Math.floor(250 - 42 * intensity);
          const b = Math.floor(255 - 12 * intensity);
          const a = 255;
          const index = (y * width + x) * 4;

          data[index] = r;
          data[index + 1] = g;
          data[index + 2] = b;
          data[index + 3] = a;
        }
      }

      ctx.putImageData(imageData, 0, 0);

      const radial = ctx.createRadialGradient(
        width * 0.5,
        height * 0.4,
        0,
        width * 0.5,
        height * 0.4,
        Math.max(width, height) * 0.65,
      );
      radial.addColorStop(0, 'rgba(40, 100, 164, 0.18)');
      radial.addColorStop(0.55, 'rgba(40, 100, 164, 0.06)');
      radial.addColorStop(1, 'rgba(255, 255, 255, 0.24)');

      ctx.fillStyle = radial;
      ctx.fillRect(0, 0, width, height);

      time += 1;
      animationRef.current = window.requestAnimationFrame(animate);
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);

      if (animationRef.current) {
        window.cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden bg-metro-background">
      <canvas
        ref={canvasRef}
        aria-hidden="true"
        className="absolute inset-0 h-full w-full"
      />
      <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.34))]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_20%,rgba(40,100,164,0.2),transparent_44%)]" />
    </div>
  );
}

export { SilkBackgroundAnimation };
