'use client';

import { useEffect, useState } from 'react';
import { api, Alert } from '@/lib/api';
import { Card } from '@/components/ui/Card';

export default function AlertsPage() {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const data = await api.getAlerts(100);
                setAlerts(data.alerts || []);
            } catch (error) {
                console.error('Failed to fetch alerts:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchAlerts();
        const interval = setInterval(fetchAlerts, 10000);
        return () => clearInterval(interval);
    }, []);

    const normalizeSeverity = (sev: string) => sev.toLowerCase();

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold neon-text">Security Alerts</h1>
                <div className="flex gap-2">
                    <span className="px-3 py-1 rounded-full bg-red-500/20 text-red-500 border border-red-500/50">
                        {alerts.filter(a => normalizeSeverity(a.severity) === 'critical').length} Critical
                    </span>
                    <span className="px-3 py-1 rounded-full bg-orange-500/20 text-orange-500 border border-orange-500/50">
                        {alerts.filter(a => normalizeSeverity(a.severity) === 'high').length} High
                    </span>
                    <span className="px-3 py-1 rounded-full bg-yellow-500/20 text-yellow-500 border border-yellow-500/50">
                        {alerts.filter(a => normalizeSeverity(a.severity) === 'medium').length} Medium
                    </span>
                    <span className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-500 border border-blue-500/50">
                        {alerts.filter(a => normalizeSeverity(a.severity) === 'low').length} Low
                    </span>
                </div>
            </div>

            <div className="grid gap-4">
                {loading ? (
                    <div className="text-center py-10 text-muted-foreground">Loading alerts...</div>
                ) : alerts.length === 0 ? (
                    <div className="text-center py-10 text-muted-foreground">
                        <p className="text-lg mb-2">✨ No active alerts detected</p>
                        <p className="text-sm">Windows Event Logs are being monitored. Alerts will appear here when rules are triggered.</p>
                    </div>
                ) : (
                    alerts.map((alert: any) => {
                        const severity = normalizeSeverity(alert.severity);
                        const timestamp = alert['@timestamp'] || alert.created_at || alert.timestamp;
                        const borderColor = severity === 'critical' ? '#ef4444' :
                            severity === 'high' ? '#f97316' :
                                severity === 'medium' ? '#eab308' : '#3b82f6';

                        return (
                            <Card key={alert.alert_id} className="p-4 hover:bg-white/5 transition-colors border-l-4 border-l-red-500">
                                <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className={`w-2 h-2 rounded-full ${alert.status === 'open' ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
                                            <h3 className="font-semibold text-lg">{alert.rule_name}</h3>
                                            <span className="text-xs text-muted-foreground font-mono">ID: {alert.rule_id}</span>
                                        </div>
                                        <p className="text-muted-foreground text-sm mb-3">{alert.description}</p>

                                        {alert.matched_events && alert.matched_events.length > 0 && (
                                            <div className="mb-2 p-2 bg-black/20 rounded text-xs font-mono">
                                                <span className="text-muted-foreground">Matched Events: </span>
                                                <span className="text-primary">{alert.matched_events.length}</span>
                                                {alert.matched_events[0]?.log?.source && (
                                                    <>
                                                        <span className="text-muted-foreground ml-3">Source: </span>
                                                        <span className="text-chart-2">{alert.matched_events[0].log.source}</span>
                                                    </>
                                                )}
                                                {alert.matched_events[0]?.event?.id && (
                                                    <>
                                                        <span className="text-muted-foreground ml-3">Event ID: </span>
                                                        <span className="text-chart-3">{alert.matched_events[0].event.id}</span>
                                                    </>
                                                )}
                                            </div>
                                        )}

                                        <div className="flex gap-4 text-xs text-muted-foreground">
                                            <span>⏰ {new Date(timestamp).toLocaleString()}</span>
                                            {alert.mitre_tactics && alert.mitre_tactics.length > 0 && (
                                                <span>🎯 MITRE: {alert.mitre_tactics.join(', ')}</span>
                                            )}
                                        </div>
                                    </div>
                                    <div className="text-right ml-4">
                                        <span className={`px-3 py-1 rounded text-xs font-bold uppercase border ${severity === 'critical' ? 'text-red-500 bg-red-500/10 border-red-500/50' :
                                                severity === 'high' ? 'text-orange-500 bg-orange-500/10 border-orange-500/50' :
                                                    severity === 'medium' ? 'text-yellow-500 bg-yellow-500/10 border-yellow-500/50' :
                                                        'text-blue-500 bg-blue-500/10 border-blue-500/50'
                                            }`}>
                                            {alert.severity}
                                        </span>
                                    </div>
                                </div>
                            </Card>
                        );
                    })
                )}
            </div>
        </div>
    );
}
