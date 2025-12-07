'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api, Log } from '@/lib/api';
import { Card } from '@/components/ui/Card';

export default function LogsPage() {
    const router = useRouter();
    const [logs, setLogs] = useState<Log[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const data = await api.getLogs(100);
                setLogs(data.results || []);
            } catch (error) {
                console.error('Failed to fetch logs:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchLogs();
        const interval = setInterval(fetchLogs, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleLogClick = (log: Log, index: number) => {
        // Save log to localStorage for detail page
        const logId = `log_${Date.now()}_${index}`;
        localStorage.setItem(`log_detail_${logId}`, JSON.stringify(log));
        router.push(`/logs/${logId}`);
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold neon-text">Log Explorer</h1>
                <p className="text-sm text-muted-foreground">Click on any log to view details</p>
            </div>

            <Card className="overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="bg-white/5 text-muted-foreground uppercase text-xs">
                            <tr>
                                <th className="px-4 py-3">Timestamp</th>
                                <th className="px-4 py-3">Log Source</th>
                                <th className="px-4 py-3">Event Source</th>
                                <th className="px-4 py-3">Event ID</th>
                                <th className="px-4 py-3">Level</th>
                                <th className="px-4 py-3">Host</th>
                                <th className="px-4 py-3">Message</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/10">
                            {loading ? (
                                <tr><td colSpan={7} className="px-4 py-8 text-center">Loading logs...</td></tr>
                            ) : logs.length === 0 ? (
                                <tr><td colSpan={7} className="px-4 py-8 text-center">No logs found</td></tr>
                            ) : (
                                logs.map((log, i) => {
                                    // Extract Windows Event Log fields
                                    const logSource = log.log?.source || log.source_type || 'unknown';
                                    const eventSource = log.event?.source || 'unknown';
                                    const eventId = log.event?.id || '-';
                                    const eventLevel = log.event?.level || log.level || 'unknown';
                                    const eventMessage = log.event?.message || log.message || log.raw_log || 'unknown';
                                    const hostname = log.host?.name || log.metadata?.hostname || 'unknown';

                                    return (
                                        <tr
                                            key={i}
                                            onClick={() => handleLogClick(log, i)}
                                            className="hover:bg-primary/10 transition-colors font-mono cursor-pointer group"
                                        >
                                            <td className="px-4 py-2 whitespace-nowrap text-primary group-hover:text-primary/80">
                                                {new Date(log['@timestamp'] || log.timestamp).toLocaleString()}
                                            </td>
                                            <td className="px-4 py-2">
                                                <span className={`px-2 py-1 text-xs rounded ${logSource === 'application' ? 'bg-blue-500/20 text-blue-400' :
                                                        logSource === 'system' ? 'bg-green-500/20 text-green-400' :
                                                            logSource === 'security' ? 'bg-purple-500/20 text-purple-400' :
                                                                'bg-gray-500/20 text-gray-400'
                                                    }`}>
                                                    {logSource.toUpperCase()}
                                                </span>
                                            </td>
                                            <td className="px-4 py-2 text-chart-2">{eventSource}</td>
                                            <td className="px-4 py-2 text-chart-3 font-semibold">{eventId}</td>
                                            <td className="px-4 py-2">
                                                <span className={`text-xs font-medium ${eventLevel === 'Error' || eventLevel === 'Audit Failure' ? 'text-red-500' :
                                                        eventLevel === 'Warning' ? 'text-yellow-500' :
                                                            'text-gray-400'
                                                    }`}>
                                                    {eventLevel}
                                                </span>
                                            </td>
                                            <td className="px-4 py-2 text-muted-foreground">{hostname}</td>
                                            <td className="px-4 py-2 max-w-xl truncate text-muted-foreground" title={eventMessage}>
                                                {eventMessage}
                                            </td>
                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
}
