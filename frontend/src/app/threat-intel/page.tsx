'use client';

import { Card } from '@/components/ui/Card';
import { Globe, Shield, AlertTriangle, Database } from 'lucide-react';

export default function ThreatIntelPage() {
    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold neon-text">Threat Intelligence</h1>
                <button className="px-4 py-2 bg-primary hover:bg-primary/80 text-black font-bold rounded transition-colors">
                    Update Feeds
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="p-4 flex items-center gap-4">
                    <div className="p-3 rounded-full bg-chart-1/20 text-chart-1">
                        <Globe size={24} />
                    </div>
                    <div>
                        <p className="text-sm text-muted-foreground">Global Threat Level</p>
                        <h3 className="text-2xl font-bold text-chart-1">Elevated</h3>
                    </div>
                </Card>
                <Card className="p-4 flex items-center gap-4">
                    <div className="p-3 rounded-full bg-chart-2/20 text-chart-2">
                        <Database size={24} />
                    </div>
                    <div>
                        <p className="text-sm text-muted-foreground">IOCs in Database</p>
                        <h3 className="text-2xl font-bold text-white">2.4M</h3>
                    </div>
                </Card>
                <Card className="p-4 flex items-center gap-4">
                    <div className="p-3 rounded-full bg-chart-3/20 text-chart-3">
                        <Shield size={24} />
                    </div>
                    <div>
                        <p className="text-sm text-muted-foreground">Active Feeds</p>
                        <h3 className="text-2xl font-bold text-white">14</h3>
                    </div>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="p-6">
                    <h3 className="text-xl font-bold mb-4 text-chart-4">Latest Threat Feeds</h3>
                    <div className="space-y-4">
                        {[
                            { name: 'AlienVault OTX', status: 'Active', lastUpdate: '5m ago', type: 'Reputation' },
                            { name: 'MISP Community', status: 'Active', lastUpdate: '12m ago', type: 'Malware' },
                            { name: 'CISA Alerts', status: 'Active', lastUpdate: '1h ago', type: 'Advisory' },
                            { name: 'Abuse.ch', status: 'Syncing...', lastUpdate: '2m ago', type: 'Botnet' },
                        ].map((feed, i) => (
                            <div key={i} className="flex justify-between items-center p-3 bg-white/5 rounded hover:bg-white/10 transition-colors">
                                <div>
                                    <div className="font-bold text-white">{feed.name}</div>
                                    <div className="text-xs text-muted-foreground">{feed.type}</div>
                                </div>
                                <div className="text-right">
                                    <div className={`text-sm ${feed.status === 'Active' ? 'text-green-400' : 'text-yellow-400'}`}>{feed.status}</div>
                                    <div className="text-xs text-muted-foreground">{feed.lastUpdate}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>

                <Card className="p-6">
                    <h3 className="text-xl font-bold mb-4 text-destructive">Trending Campaigns</h3>
                    <div className="space-y-4">
                        {[
                            { name: 'APT29 Phishing', severity: 'Critical', region: 'Global' },
                            { name: 'LockBit 3.0 Ransomware', severity: 'High', region: 'North America' },
                            { name: 'Cobalt Strike Beacon', severity: 'High', region: 'Europe' },
                            { name: 'Log4Shell Exploitation', severity: 'Medium', region: 'Global' },
                        ].map((campaign, i) => (
                            <div key={i} className="flex items-center gap-4 p-3 bg-white/5 rounded border-l-2 border-destructive">
                                <AlertTriangle className="text-destructive" size={20} />
                                <div className="flex-1">
                                    <div className="font-bold text-white">{campaign.name}</div>
                                    <div className="text-xs text-muted-foreground">{campaign.region}</div>
                                </div>
                                <span className="px-2 py-1 rounded bg-destructive/20 text-destructive text-xs font-bold">
                                    {campaign.severity}
                                </span>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>
        </div>
    );
}
