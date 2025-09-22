'use client';

import { useEffect, useRef } from 'react';

export default function ThreatStats() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Set canvas dimensions
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    // Threat data
    const threatData = [
      { category: 'Malware', value: 35, color: '#ff003c' },
      { category: 'Phishing', value: 28, color: '#ff6b35' },
      { category: 'Intrusion', value: 22, color: '#9d4edd' },
      { category: 'DDoS', value: 15, color: '#00f5ff' },
      { category: 'Other', value: 10, color: '#39ff14' }
    ];
    
    // Animation properties
    let animationProgress = 0;
    const animationDuration = 60; // frames
    
    const animate = () => {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Calculate bar dimensions
      const barWidth = (canvas.width - 100) / threatData.length;
      const maxBarHeight = canvas.height - 60;
      const barSpacing = 10;
      
      // Update animation progress
      if (animationProgress < animationDuration) {
        animationProgress++;
      }
      
      // Draw bars
      threatData.forEach((threat, index) => {
        const x = 50 + index * (barWidth + barSpacing);
        const progress = Math.min(animationProgress / animationDuration, 1);
        const currentHeight = (threat.value / 100) * maxBarHeight * progress;
        const y = canvas.height - 30 - currentHeight;
        
        // Draw bar with glow effect
        ctx.shadowColor = threat.color;
        ctx.shadowBlur = 10;
        ctx.fillStyle = `${threat.color}40`; // 40 = 25% opacity
        ctx.fillRect(x, y, barWidth, currentHeight);
        
        // Draw bar border
        ctx.strokeStyle = threat.color;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, barWidth, currentHeight);
        
        // Reset shadow
        ctx.shadowBlur = 0;
        
        // Draw category label
        ctx.fillStyle = '#ffffff';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(threat.category, x + barWidth / 2, canvas.height - 10);
        
        // Draw value label
        ctx.fillStyle = threat.color;
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`${Math.round(threat.value * progress)}%`, x + barWidth / 2, y - 10);
        
        // Draw grid lines
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(40, y);
        ctx.lineTo(canvas.width - 40, y);
        ctx.stroke();
      });
      
      requestAnimationFrame(animate);
    };
    
    animate();
    
    // Handle resize
    const handleResize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);
  
  return (
    <div className="w-full h-full rounded-lg overflow-hidden">
      <canvas ref={canvasRef} className="w-full h-full" />
    </div>
  );
}