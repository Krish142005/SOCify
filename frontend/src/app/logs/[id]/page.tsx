'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card } from '@/components/ui/Card';

export default function LogDetailPage() {
    const params = useParams();
    const router = useRouter();
    const [log, setLog] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchLog = async () => {
            try {
                // In a real app, you'd fetch from backend by ID
                // For now, we'll get it from localStorage (saved on click)
                const savedLog = localStorage.getItem(`log_detail_${params.id}`);
                if (savedLog) {
                    setLog(JSON.parse(savedLog));
                }
            } catch (error) {
                console.error('Failed to fetch log:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchLog();
    }, [params.id]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-lg">Loading log details...</div>
            </div>
        );
    }

    if (!log) {
        return (
            <div className="space-y-6">
                <h1 className="text-3xl font-bold neon-text">Log Not Found</h1>
                <button
                    onClick={() => router.push('/logs')}
                    className="px-4 py-2 bg-primary/20 hover:bg-primary/30 rounded"
                >
                    ← Back to Logs
                </button>
            </div>
        );
    }

    // Extract all fields
    const logSource = log.log?.source || log.source_type || 'unknown';
    const eventSource = log.event?.source || 'N/A';
    const eventId = log.event?.id || 'N/A';
    const eventLevel = log.event?.level || log.level || 'N/A';
    const eventMessage = log.event?.message || log.message || log.raw_log || 'N/A';
    const hostname = log.host?.name || log.metadata?.hostname || 'unknown';
    const timestamp = new Date(log['@timestamp'] || log.timestamp).toLocaleString();

    const getSeverityColor = (level: string) => {
        if (level === 'Error' || level === 'Audit Failure') return 'text-red-500 bg-red-500/20';
        if (level === 'Warning') return 'text-yellow-500 bg-yellow-500/20';
        return 'text-gray-400 bg-gray-500/20';
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold neon-text">Event Details</h1>
                <button
                    onClick={() => router.push('/logs')}
                    className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded transition-colors"
                >
                    ← Back to Logs
                </button>
            </div>

            {/* Main Info Card */}
            <Card className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="text-sm text-muted-foreground">Log Source</label>
                        <div className="mt-1">
                            <span className={`px-3 py-1 text-sm rounded ${logSource === 'application' ? 'bg-blue-500/20 text-blue-400' :
                                    logSource === 'system' ? 'bg-green-500/20 text-green-400' :
                                        logSource === 'security' ? 'bg-purple-500/20 text-purple-400' :
                                            'bg-gray-500/20 text-gray-400'
                                }`}>
                                {logSource.toUpperCase()}
                            </span>
                        </div>
                    </div>

                    <div>
                        <label className="text-sm text-muted-foreground">Timestamp</label>
                        <p className="mt-1 font-mono text-primary">{timestamp}</p>
                    </div>

                    <div>
                        <label className="text-sm text-muted-foreground">Event Source</label>
                        <p className="mt-1 font-mono text-chart-2">{eventSource}</p>
                    </div>

                    <div>
                        <label className="text-sm text-muted-foreground">Event ID</label>
                        <p className="mt-1 font-mono text-chart-3 text-lg font-bold">{eventId}</p>
                    </div>

                    <div>
                        <label className="text-sm text-muted-foreground">Level / Severity</label>
                        <div className="mt-1">
                            <span className={`px-3 py-1 text-sm rounded font-medium ${getSeverityColor(eventLevel)}`}>
                                {eventLevel}
                            </span>
                        </div>
                    </div>

                    <div>
                        <label className="text-sm text-muted-foreground">Hostname</label>
                        <p className="mt-1 font-mono">{hostname}</p>
                    </div>
                </div>
            </Card>

            {/* Event Message */}
            <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4">Event Message</h2>
                <div className="bg-black/30 p-4 rounded font-mono text-sm whitespace-pre-wrap break-words">
                    {eventMessage}
                </div>
            </Card>

            {/* Event Data */}
            {log.event && (
                <Card className="p-6">
                    <h2 className="text-xl font-semibold mb-4">Event Data</h2>
                    <div className="space-y-3">
                        {Object.entries(log.event).map(([key, value]) => (
                            <div key={key} className="grid grid-cols-3 gap-4 py-2 border-b border-white/10">
                                <div className="text-muted-foreground font-mono text-sm">{key}</div>
                                <div className="col-span-2 font-mono text-sm break-words">
                                    {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>
            )}

            {/* Host Information */}
            {log.host && (
                <Card className="p-6">
                    <h2 className="text-xl font-semibold mb-4">Host Information</h2>
                    <div className="space-y-3">
                        {Object.entries(log.host).map(([key, value]) => (
                            <div key={key} className="grid grid-cols-3 gap-4 py-2 border-b border-white/10">
                                <div className="text-muted-foreground font-mono text-sm">{key}</div>
                                <div className="col-span-2 font-mono text-sm">
                                    {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>
            )}

            {/* Agent Information */}
            {log.agent && (
                <Card className="p-6">
                    <h2 className="text-xl font-semibold mb-4">Agent Information</h2>
                    <div className="space-y-3">
                        {Object.entries(log.agent).map(([key, value]) => (
                            <div key={key} className="grid grid-cols-3 gap-4 py-2 border-b border-white/10">
                                <div className="text-muted-foreground font-mono text-sm">{key}</div>
                                <div className="col-span-2 font-mono text-sm">
                                    {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>
            )}

            {/* Tags */}
            {log.tags && log.tags.length > 0 && (
                <Card className="p-6">
                    <h2 className="text-xl font-semibold mb-4">Tags</h2>
                    <div className="flex flex-wrap gap-2">
                        {log.tags.map((tag: string, i: number) => (
                            <span key={i} className="px-3 py-1 bg-primary/20 text-primary rounded text-sm">
                                {tag}
                            </span>
                        ))}
                    </div>
                </Card>
            )}

            {/* Raw JSON */}
            <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4">Raw Event Data (JSON)</h2>
                <div className="bg-black/30 p-4 rounded overflow-x-auto">
                    <pre className="text-xs font-mono text-green-400">
                        {JSON.stringify(log, null, 2)}
                    </pre>
                </div>
            </Card>
        </div>
    );
}
