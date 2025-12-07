'use client';

import { useEffect, useRef, useState } from 'react';
import { api, Alert } from '@/lib/api';

export default function ThreatStats() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [stats, setStats] = useState([
        { category: 'Critical', value: 0, color: '#ff003c' },
        { category: 'High', value: 0, color: '#ff6b35' },
        { category: 'Medium', value: 0, color: '#fca311' },
        { category: 'Low', value: 0, color: '#00f5ff' }
    ]);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await api.getAlerts(1000);
                const alerts: Alert[] = data.alerts || [];

                const counts = {
                    critical: 0,
                    high: 0,
                    medium: 0,
                    low: 0
                };

                alerts.forEach(a => {
                    if (counts[a.severity as keyof typeof counts] !== undefined) {
                        counts[a.severity as keyof typeof counts]++;
                    }
                });

                const total = alerts.length || 1; // Avoid division by zero

                setStats([
                    { category: 'Critical', value: Math.round((counts.critical / total) * 100), color: '#ff003c' },
                    { category: 'High', value: Math.round((counts.high / total) * 100), color: '#ff6b35' },
                    { category: 'Medium', value: Math.round((counts.medium / total) * 100), color: '#fca311' },
                    { category: 'Low', value: Math.round((counts.low / total) * 100), color: '#00f5ff' }
                ]);
            } catch (error) {
                console.error('Failed to fetch threat stats:', error);
            }
        };

        fetchStats();
        const interval = setInterval(fetchStats, 5000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Set canvas dimensions
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;

        // Animation properties
        let animationProgress = 0;
        const animationDuration = 60; // frames
        let animationFrameId: number;

        const animate = () => {
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Calculate bar dimensions
            const barWidth = (canvas.width - 100) / stats.length;
            const maxBarHeight = canvas.height - 60;
            const barSpacing = 10;

            // Update animation progress
            if (animationProgress < animationDuration) {
                animationProgress++;
            }

            // Draw bars
            stats.forEach((threat, index) => {
                const x = 50 + index * (barWidth + barSpacing);
                const progress = Math.min(animationProgress / animationDuration, 1);
                // Ensure at least a small bar is visible if value is 0 but category exists
                const displayValue = Math.max(threat.value, 2);
                const currentHeight = (displayValue / 100) * maxBarHeight * progress;
                const y = canvas.height - 30 - currentHeight;

                // Draw bar with glow effect
                ctx.shadowColor = threat.color;
                ctx.shadowBlur = 10;
                ctx.fillStyle = `${threat.color}40`; // 25% opacity
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
                ctx.fillText(`${threat.value}%`, x + barWidth / 2, y - 10);

                // Draw grid lines
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(40, y);
                ctx.lineTo(canvas.width - 40, y);
                ctx.stroke();
            });

            animationFrameId = requestAnimationFrame(animate);
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
            cancelAnimationFrame(animationFrameId);
        };
    }, [stats]);

    return (
        <div className="w-full h-full rounded-lg overflow-hidden">
            <canvas ref={canvasRef} className="w-full h-full" />
        </div>
    );
}
