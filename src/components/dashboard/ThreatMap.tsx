'use client';

import { useEffect, useRef } from 'react';

export default function ThreatMap() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Set canvas dimensions
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    // Radar animation
    let angle = 0;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) * 0.8;
    
    // Generate random threat points
    const threats = Array.from({ length: 15 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      intensity: Math.random(),
      pulse: 0,
      pulsing: false,
    }));
    
    const animate = () => {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw radar circles
      for (let i = 1; i <= 4; i++) {
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius * (i / 4), 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(0, 245, 255, ${0.2 - (i * 0.03)})`;
        ctx.lineWidth = 1;
        ctx.stroke();
      }
      
      // Draw radar sweep
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, angle, angle + 0.1);
      ctx.lineTo(centerX, centerY);
      ctx.fillStyle = 'rgba(0, 245, 255, 0.6)';
      ctx.fill();
      
      // Draw threats
      threats.forEach(threat => {
        // Calculate distance from center
        const dx = threat.x - centerX;
        const dy = threat.y - centerY;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        // Only show threats that are within the radar radius
        if (distance <= radius) {
          // Check if the radar sweep is passing over this threat
          const threatAngle = Math.atan2(dy, dx);
          const normalizedThreatAngle = threatAngle < 0 ? threatAngle + Math.PI * 2 : threatAngle;
          const normalizedSweepAngle = angle % (Math.PI * 2);
          
          // Start pulsing when the sweep passes over
          if (Math.abs(normalizedThreatAngle - normalizedSweepAngle) < 0.1) {
            threat.pulsing = true;
            threat.pulse = 1;
          }
          
          if (threat.pulsing) {
            // Draw pulsing circle
            ctx.beginPath();
            ctx.arc(threat.x, threat.y, 3 + (threat.pulse * 5), 0, Math.PI * 2);
            
            // Color based on intensity (red for high, yellow for medium, green for low)
            let color;
            if (threat.intensity > 0.7) {
              color = `rgba(255, 0, 60, ${0.8 - threat.pulse * 0.8})`;
            } else if (threat.intensity > 0.4) {
              color = `rgba(255, 107, 53, ${0.8 - threat.pulse * 0.8})`;
            } else {
              color = `rgba(0, 245, 255, ${0.8 - threat.pulse * 0.8})`;
            }
            
            ctx.fillStyle = color;
            ctx.fill();
            
            // Reduce pulse over time
            threat.pulse -= 0.01;
            if (threat.pulse <= 0) {
              threat.pulsing = false;
              threat.pulse = 0;
            }
          }
          
          // Draw threat dot
          ctx.beginPath();
          ctx.arc(threat.x, threat.y, 3, 0, Math.PI * 2);
          
          // Color based on intensity
          if (threat.intensity > 0.7) {
            ctx.fillStyle = 'rgba(255, 0, 60, 0.8)';
          } else if (threat.intensity > 0.4) {
            ctx.fillStyle = 'rgba(255, 107, 53, 0.8)';
          } else {
            ctx.fillStyle = 'rgba(0, 245, 255, 0.8)';
          }
          
          ctx.fill();
        }
      });
      
      // Update angle for next frame
      angle += 0.01;
      if (angle > Math.PI * 2) angle = 0;
      
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
    <div className="w-full h-full rounded-lg overflow-hidden border border-border bg-black/20">
      <canvas ref={canvasRef} className="w-full h-full" />
    </div>
  );
}