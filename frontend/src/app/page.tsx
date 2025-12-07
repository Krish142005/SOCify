'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import ThreatMap from '@/components/dashboard/ThreatMap';
import ThreatStats from '@/components/dashboard/ThreatStats';
import { Card } from '@/components/ui/Card';
import { Shield, AlertTriangle, Activity, Target } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState({
    activeThreats: 0,
    criticalAlerts: 0,
    mttr: '0m',
    mitreCoverage: '0%'
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await api.getStats();
        setStats({
          activeThreats: data.activeThreats,
          criticalAlerts: data.criticalAlerts,
          mttr: '45m', // Placeholder for now
          mitreCoverage: '78%' // Placeholder for now
        });
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold neon-text">SOC Dashboard</h1>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-muted-foreground">Active Threats</p>
              <h2 className="text-3xl font-bold text-white mt-1">{stats.activeThreats}</h2>
              <p className="text-xs text-chart-4 mt-1">+3 from last period</p>
            </div>
            <div className="p-2 rounded-full bg-primary/20 text-primary">
              <Shield size={20} />
            </div>
          </div>
        </Card>

        <Card className="p-4 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-r from-destructive/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-muted-foreground">Critical Alerts</p>
              <h2 className="text-3xl font-bold text-white mt-1">{stats.criticalAlerts}</h2>
              <p className="text-xs text-destructive mt-1">+2 from last period</p>
            </div>
            <div className="p-2 rounded-full bg-destructive/20 text-destructive">
              <AlertTriangle size={20} />
            </div>
          </div>
        </Card>

        <Card className="p-4 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-r from-secondary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-muted-foreground">MTTR</p>
              <h2 className="text-3xl font-bold text-white mt-1">{stats.mttr}</h2>
              <p className="text-xs text-secondary mt-1">-12m from last period</p>
            </div>
            <div className="p-2 rounded-full bg-secondary/20 text-secondary">
              <Activity size={20} />
            </div>
          </div>
        </Card>

        <Card className="p-4 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-r from-accent/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-muted-foreground">MITRE Coverage</p>
              <h2 className="text-3xl font-bold text-white mt-1">{stats.mitreCoverage}</h2>
              <p className="text-xs text-chart-4 mt-1">+5% from last period</p>
            </div>
            <div className="p-2 rounded-full bg-accent/20 text-accent">
              <Target size={20} />
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[400px]">
        {/* Threat Radar */}
        <Card className="lg:col-span-2 p-4 flex flex-col">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            Live Threat Radar
          </h3>
          <div className="flex-1 relative">
            <ThreatMap />
          </div>
        </Card>

        {/* Threat Stats */}
        <Card className="p-4 flex flex-col">
          <h3 className="text-lg font-semibold mb-4">Threat Distribution</h3>
          <div className="flex-1">
            <ThreatStats />
          </div>
        </Card>
      </div>

      {/* Active Incidents List */}
      <Card className="p-4">
        <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
        <div className="space-y-2">
          {/* We can fetch recent logs here later */}
          <div className="p-3 bg-white/5 rounded flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="w-1.5 h-1.5 rounded-full bg-chart-4" />
              <span className="text-sm font-mono text-muted-foreground">System scan initiated by admin</span>
            </div>
            <span className="text-xs text-muted-foreground">Just now</span>
          </div>
          <div className="p-3 bg-white/5 rounded flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="w-1.5 h-1.5 rounded-full bg-primary" />
              <span className="text-sm font-mono text-muted-foreground">New rule "SSH Brute Force" enabled</span>
            </div>
            <span className="text-xs text-muted-foreground">2m ago</span>
          </div>
          <div className="p-3 bg-white/5 rounded flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="w-1.5 h-1.5 rounded-full bg-secondary" />
              <span className="text-sm font-mono text-muted-foreground">Agent connected from host: Shubhang</span>
            </div>
            <span className="text-xs text-muted-foreground">5m ago</span>
          </div>
        </div>
      </Card>
    </div>
  );
}
