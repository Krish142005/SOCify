'use client';

import { useEffect, useState } from 'react';
import { api, Alert } from '@/lib/api';
import { Card } from '@/components/ui/Card';

export default function IncidentsPage() {
    const [incidents, setIncidents] = useState<Alert[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchIncidents = async () => {
            try {
                const data = await api.getAlerts(100);
                // Filter for high and critical severity only
                const criticalAlerts = (data.alerts || []).filter((a: Alert) =>
                    a.severity === 'critical' || a.severity === 'high'
                );
                setIncidents(criticalAlerts);
            } catch (error) {
                console.error('Failed to fetch incidents:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchIncidents();
        const interval = setInterval(fetchIncidents, 10000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold neon-text text-destructive">Active Incidents</h1>

            <div className="grid gap-6">
                {loading ? (
                    <div className="text-center py-10">Loading incidents...</div>
                ) : incidents.length === 0 ? (
                    <div className="text-center py-20 cyber-card">
                        <h2 className="text-2xl font-bold text-green-400 mb-2">System Secure</h2>
                        <p className="text-muted-foreground">No critical incidents requiring immediate attention.</p>
                    </div>
                ) : (
                    incidents.map((incident) => (
                        <Card key={incident.alert_id} className="p-6 border-l-4 border-l-destructive bg-destructive/5">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h2 className="text-2xl font-bold text-white mb-2">{incident.rule_name}</h2>
                                    <p className="text-gray-300 mb-4">{incident.description}</p>

                                    <div className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
                                        <div>
                                            <span className="text-muted-foreground">Source:</span>
                                            <span className="ml-2 text-chart-4">{incident.source_ips?.join(', ')}</span>
                                        </div>
                                        <div>
                                            <span className="text-muted-foreground">Destination:</span>
                                            <span className="ml-2 text-chart-4">{incident.destination_ips?.join(', ')}</span>
                                        </div>
                                        <div>
                                            <span className="text-muted-foreground">Time:</span>
                                            <span className="ml-2">{new Date(incident.created_at).toLocaleString()}</span>
                                        </div>
                                        <div>
                                            <span className="text-muted-foreground">Status:</span>
                                            <span className="ml-2 uppercase font-bold text-destructive">{incident.status}</span>
                                        </div>
                                    </div>

                                    {incident.mitre_tactics && (
                                        <div className="mt-4 flex gap-2">
                                            {incident.mitre_tactics.map(tactic => (
                                                <span key={tactic} className="px-2 py-1 rounded bg-white/10 text-xs border border-white/20">
                                                    {tactic}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>

                                <button className="px-4 py-2 bg-destructive hover:bg-destructive/80 text-white rounded font-bold transition-colors">
                                    Investigate
                                </button>
                            </div>
                        </Card>
                    ))
                )}
            </div>
        </div>
    );
}
