'use client';

import { Card } from '@/components/ui/Card';
import { BarChart, PieChart, Activity, TrendingUp } from 'lucide-react';

export default function AnalyticsPage() {
    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold neon-text">Security Analytics</h1>
                <select className="bg-black/40 border border-white/10 rounded px-4 py-2 text-sm">
                    <option>Last 7 Days</option>
                    <option>Last 30 Days</option>
                    <option>Last Quarter</option>
                </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                    { label: 'Total Events', value: '14.2M', change: '+12%', icon: Activity, color: 'text-primary' },
                    { label: 'Alert Volume', value: '1,240', change: '-5%', icon: AlertTriangle, color: 'text-destructive' },
                    { label: 'False Positives', value: '12%', change: '-2%', icon: PieChart, color: 'text-chart-3' },
                    { label: 'Avg Response Time', value: '18m', change: '-4m', icon: TrendingUp, color: 'text-green-400' },
                ].map((stat, i) => (
                    <Card key={i} className="p-4">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-sm text-muted-foreground">{stat.label}</p>
                                <h3 className="text-2xl font-bold mt-1">{stat.value}</h3>
                                <p className={`text-xs mt-1 ${stat.change.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
                                    {stat.change} vs last period
                                </p>
                            </div>
                            <div className={`p-2 rounded bg-white/5 ${stat.color}`}>
                                <stat.icon size={20} />
                            </div>
                        </div>
                    </Card>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="p-6 h-[400px] flex flex-col">
                    <h3 className="font-bold mb-6">Event Volume by Source</h3>
                    <div className="flex-1 flex items-end justify-between gap-2 px-4">
                        {[40, 65, 35, 80, 55, 90, 45].map((h, i) => (
                            <div key={i} className="w-full bg-primary/20 hover:bg-primary/40 transition-colors rounded-t relative group" style={{ height: `${h}%` }}>
                                <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-black border border-white/10 px-2 py-1 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity">
                                    {h * 1000} events
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="flex justify-between mt-4 text-xs text-muted-foreground px-2">
                        <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
                    </div>
                </Card>

                <Card className="p-6 h-[400px] flex flex-col">
                    <h3 className="font-bold mb-6">Top Attack Vectors</h3>
                    <div className="space-y-6">
                        {[
                            { name: 'Brute Force', pct: 45, color: 'bg-destructive' },
                            { name: 'Malware', pct: 25, color: 'bg-chart-4' },
                            { name: 'SQL Injection', pct: 15, color: 'bg-chart-3' },
                            { name: 'Phishing', pct: 10, color: 'bg-chart-2' },
                            { name: 'Other', pct: 5, color: 'bg-chart-1' },
                        ].map((item, i) => (
                            <div key={i}>
                                <div className="flex justify-between text-sm mb-2">
                                    <span>{item.name}</span>
                                    <span>{item.pct}%</span>
                                </div>
                                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                    <div className={`h-full ${item.color}`} style={{ width: `${item.pct}%` }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>
            </div>
        </div>
    );
}

import { AlertTriangle } from 'lucide-react';
