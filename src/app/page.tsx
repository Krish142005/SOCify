'use client';

import ThreatMap from '@/components/dashboard/ThreatMap';
import ThreatStats from '@/components/dashboard/ThreatStats';
import { Shield, AlertTriangle, Clock, Target, Activity, BarChart } from 'lucide-react';

export default function Dashboard() {
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold neon-text">SOC Dashboard</h1>
        <div className="flex space-x-2">
          <button className="px-4 py-2 text-sm bg-black/30 border border-[#00f5ff]/30 rounded-md hover:bg-black/50 hover:border-[#00f5ff]/50 transition-all">
            Last 24 Hours
          </button>
          <button className="px-4 py-2 text-sm bg-black/30 border border-[#00f5ff]/30 rounded-md hover:bg-black/50 hover:border-[#00f5ff]/50 transition-all">
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          title="Active Threats" 
          value="12" 
          change="+3" 
          icon={<Shield className="h-5 w-5 text-[#00f5ff]" />} 
          trend="up"
        />
        <MetricCard 
          title="Critical Alerts" 
          value="5" 
          change="+2" 
          icon={<AlertTriangle className="h-5 w-5 text-[#ff003c]" />} 
          trend="up"
        />
        <MetricCard 
          title="MTTR" 
          value="45m" 
          change="-12m" 
          icon={<Clock className="h-5 w-5 text-[#39ff14]" />} 
          trend="down"
        />
        <MetricCard 
          title="MITRE Coverage" 
          value="78%" 
          change="+5%" 
          icon={<Target className="h-5 w-5 text-[#9d4edd]" />} 
          trend="up"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="cyber-card h-[400px] border border-border rounded-lg bg-black/20 backdrop-blur-sm">
            <div className="p-4 border-b border-border">
              <h2 className="text-lg font-semibold flex items-center">
                <Activity className="mr-2 h-5 w-5 text-[#00f5ff]" />
                Live Threat Radar
              </h2>
            </div>
            <div className="p-4 h-[340px]">
              <ThreatMap />
            </div>
          </div>
        </div>
        
        <div>
          <div className="cyber-card h-[400px] border border-border rounded-lg bg-black/20 backdrop-blur-sm">
            <div className="p-4 border-b border-border">
              <h2 className="text-lg font-semibold">Active Incidents</h2>
            </div>
            <div className="p-4 space-y-3 overflow-auto h-[340px]">
              <IncidentItem 
                title="Brute Force Attack" 
                time="12m ago" 
                severity="critical" 
                source="192.168.1.45" 
              />
              <IncidentItem 
                title="Suspicious Login" 
                time="34m ago" 
                severity="high" 
                source="admin@company.com" 
              />
              <IncidentItem 
                title="Malware Detected" 
                time="1h ago" 
                severity="critical" 
                source="Workstation-104" 
              />
              <IncidentItem 
                title="Data Exfiltration" 
                time="2h ago" 
                severity="high" 
                source="User-JDoe" 
              />
              <IncidentItem 
                title="Firewall Bypass" 
                time="3h ago" 
                severity="medium" 
                source="10.0.0.15" 
              />
              <IncidentItem 
                title="Unusual Activity" 
                time="5h ago" 
                severity="medium" 
                source="API Gateway" 
              />
            </div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 gap-6">
        <div className="cyber-card h-[300px] border border-border rounded-lg bg-black/20 backdrop-blur-sm">
          <div className="p-4 border-b border-border">
            <h2 className="text-lg font-semibold flex items-center">
              <BarChart className="mr-2 h-5 w-5 text-[#39ff14]" />
              Threat Distribution
            </h2>
          </div>
          <div className="p-4 h-[240px]">
            <ThreatStats />
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, change, icon, trend }: { 
  title: string; 
  value: string; 
  change: string; 
  icon: React.ReactNode;
  trend: 'up' | 'down';
}) {
  return (
    <div className="cyber-card p-4 border border-border rounded-lg bg-black/20 backdrop-blur-sm">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <h3 className="text-2xl font-bold mt-1">{value}</h3>
        </div>
        <div className="p-2 rounded-full bg-black/30 border border-border">
          {icon}
        </div>
      </div>
      <div className="mt-4 flex items-center">
        <span className={`text-xs ${trend === 'up' ? 'text-[#ff003c]' : 'text-[#39ff14]'}`}>
          {change}
        </span>
        <span className="text-xs text-muted-foreground ml-1">from last period</span>
      </div>
    </div>
  );
}

function IncidentItem({ title, time, severity, source }: {
  title: string;
  time: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  source: string;
}) {
  const severityColors = {
    critical: 'bg-[#ff003c]/10 border-[#ff003c] text-[#ff003c]',
    high: 'bg-[#ff6b35]/10 border-[#ff6b35] text-[#ff6b35]',
    medium: 'bg-[#9d4edd]/10 border-[#9d4edd] text-[#9d4edd]',
    low: 'bg-[#00f5ff]/10 border-[#00f5ff] text-[#00f5ff]',
  };

  return (
    <div className="p-3 border border-border rounded-md bg-black/20 hover:bg-black/30 transition-all cursor-pointer">
      <div className="flex justify-between items-start">
        <h3 className="font-medium">{title}</h3>
        <span className="text-xs text-muted-foreground">{time}</span>
      </div>
      <div className="flex items-center mt-2 justify-between">
        <div className="text-sm text-muted-foreground">
          Source: <span className="text-foreground">{source}</span>
        </div>
        <div className={`px-2 py-0.5 text-xs rounded border ${severityColors[severity]}`}>
          {severity}
        </div>
      </div>
    </div>
  );
}
