'use client';

import { useEffect, useState } from 'react';
import { Card } from '@/components/ui/Card';

interface LogEvent {
    '@timestamp': string;
    event?: {
        source?: string;
        id?: number;
        level?: string;
        message?: string;
    };
    log?: {
        source?: string;
        type?: string;
    };
    host?: {
        name?: string;
    };
    message?: string;
}

interface Alert {
    '@timestamp': string;
    alert_id: string;
    rule_id: string;
    rule_name: string;
    severity: string;
    description?: string;
}

interface Stats {
    totalLogs: number;
    totalAlerts: number;
    logsBySource: Record<string, number>;
    alertsBySeverity: Record<string, number>;
}

export default function MonitorPage() {
    const [logs, setLogs] = useState<LogEvent[]>([]);
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [stats, setStats] = useState<Stats>({
        totalLogs: 0,
        totalAlerts: 0,
        logsBySource: {},
        alertsBySeverity: {}
    });
    const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');

    useEffect(() => {
        // WebSocket URLs
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsHost = process.env.NEXT_PUBLIC_API_URL?.replace('http://', '').replace('https://', '') || 'localhost:8000';
        const logsWsUrl = `${wsProtocol}//${wsHost}/ws/logs`;
        const alertsWsUrl = `${wsProtocol}//${wsHost}/ws/alerts`;

        let logsWs: WebSocket | null = null;
        let alertsWs: WebSocket | null = null;
        let reconnectTimeout: NodeJS.Timeout;

        const connectWebSockets = () => {
            setConnectionStatus('connecting');

            // Connect to logs stream
            try {
                logsWs = new WebSocket(logsWsUrl);

                logsWs.onopen = () => {
                    console.log('Connected to logs stream');
                    setConnectionStatus('connected');
                };

                logsWs.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        if (data.type === 'log' && data.data) {
                            const logEvent = data.data;
                            setLogs(prev => [logEvent, ...prev].slice(0, 50)); // Keep last 50 logs

                            // Update stats
                            setStats(prev => {
                                const logSource = logEvent.log?.source || 'unknown';
                                return {
                                    ...prev,
                                    totalLogs: prev.totalLogs + 1,
                                    logsBySource: {
                                        ...prev.logsBySource,
                                        [logSource]: (prev.logsBySource[logSource] || 0) + 1
                                    }
                                };
                            });
                        }
                    } catch (err) {
                        console.error('Error parsing log message:', err);
                    }
                };

                logsWs.onerror = (error) => {
                    console.error('Logs WebSocket error:', error);
                };

                logsWs.onclose = () => {
                    console.log('Logs WebSocket closed');
                    setConnectionStatus('disconnected');
                    // Attempt to reconnect after 5 seconds
                    reconnectTimeout = setTimeout(connectWebSockets, 5000);
                };
            } catch (err) {
                console.error('Failed to connect to logs WebSocket:', err);
                setConnectionStatus('disconnected');
            }

            // Connect to alerts stream
            try {
                alertsWs = new WebSocket(alertsWsUrl);

                alertsWs.onopen = () => {
                    console.log('Connected to alerts stream');
                };

                alertsWs.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        if (data.type === 'alert' && data.data) {
                            const alert = data.data;
                            setAlerts(prev => [alert, ...prev].slice(0, 20)); // Keep last 20 alerts

                            // Update stats
                            setStats(prev => ({
                                ...prev,
                                totalAlerts: prev.totalAlerts + 1,
                                alertsBySeverity: {
                                    ...prev.alertsBySeverity,
                                    [alert.severity]: (prev.alertsBySeverity[alert.severity] || 0) + 1
                                }
                            }));

                            // Show browser notification for critical alerts
                            if (alert.severity === 'Critical' && 'Notification' in window && Notification.permission === 'granted') {
                                new Notification('🚨 Critical Alert', {
                                    body: alert.rule_name,
                                    icon: '/favicon.ico'
                                });
                            }
                        }
                    } catch (err) {
                        console.error('Error parsing alert message:', err);
                    }
                };

                alertsWs.onerror = (error) => {
                    console.error('Alerts WebSocket error:', error);
                };

                alertsWs.onclose = () => {
                    console.log('Alerts WebSocket closed');
                };
            } catch (err) {
                console.error('Failed to connect to alerts WebSocket:', err);
            }
        };

        // Request notification permission
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }

        connectWebSockets();

        // Cleanup on unmount
        return () => {
            clearTimeout(reconnectTimeout);
            if (logsWs) {
                logsWs.close();
            }
            if (alertsWs) {
                alertsWs.close();
            }
        };
    }, []);

    const getSeverityColor = (severity: string) => {
        const colors: Record<string, string> = {
            'Critical': 'text-red-500',
            'High': 'text-orange-500',
            'Medium': 'text-yellow-500',
            'Low': 'text-blue-500'
        };
        return colors[severity] || 'text-gray-500';
    };

    const getSeverityBg = (severity: string) => {
        const colors: Record<string, string> = {
            'Critical': 'bg-red-500/20 border-red-500/50',
            'High': 'bg-orange-500/20 border-orange-500/50',
            'Medium': 'bg-yellow-500/20 border-yellow-500/50',
            'Low': 'bg-blue-500/20 border-blue-500/50'
        };
        return colors[severity] || 'bg-gray-500/20 border-gray-500/50';
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold neon-text">Real-Time Monitor</h1>
                <div className="flex items-center gap-2">
                    <div className={`h-3 w-3 rounded-full ${connectionStatus === 'connected' ? 'bg-green-500 animate-pulse' :
                            connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' :
                                'bg-red-500'
                        }`}></div>
                    <span className="text-sm text-muted-foreground capitalize">{connectionStatus}</span>
                </div>
            </div>

            {/* Statistics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card className="p-6 border-primary/20 bg-gradient-to-br from-primary/10 to-transparent">
                    <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">Total Logs (Session)</p>
                        <p className="text-3xl font-bold neon-text">{stats.totalLogs.toLocaleString()}</p>
                    </div>
                </Card>

                <Card className="p-6 border-red-500/20 bg-gradient-to-br from-red-500/10 to-transparent">
                    <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">Total Alerts (Session)</p>
                        <p className="text-3xl font-bold text-red-500">{stats.totalAlerts.toLocaleString()}</p>
                    </div>
                </Card>

                <Card className="p-6 border-blue-500/20 bg-gradient-to-br from-blue-500/10 to-transparent">
                    <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">Application Logs</p>
                        <p className="text-3xl font-bold text-blue-500">{(stats.logsBySource['application'] || 0).toLocaleString()}</p>
                    </div>
                </Card>

                <Card className="p-6 border-green-500/20 bg-gradient-to-br from-green-500/10 to-transparent">
                    <div className="space-y-2">
                        <p className="text-sm text-muted-foreground">System Logs</p>
                        <p className="text-3xl font-bold text-green-500">{(stats.logsBySource['system'] || 0).toLocaleString()}</p>
                    </div>
                </Card>
            </div>

            {/* Real-Time Feeds */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Logs Feed */}
                <Card className="overflow-hidden">
                    <div className="p-4 border-b border-white/10">
                        <h2 className="text-xl font-semibold">Live Log Feed</h2>
                        <p className="text-sm text-muted-foreground">Latest Windows Event Logs</p>
                    </div>
                    <div className="h-[500px] overflow-y-auto">
                        {logs.length === 0 ? (
                            <div className="flex items-center justify-center h-full text-muted-foreground">
                                <div className="text-center">
                                    <p className="text-lg mb-2">Waiting for logs...</p>
                                    <p className="text-sm">Start the Windows Event Collector to see real-time logs</p>
                                </div>
                            </div>
                        ) : (
                            <div className="divide-y divide-white/10">
                                {logs.map((log, i) => (
                                    <div key={i} className="p-3 hover:bg-white/5 transition-colors">
                                        <div className="flex items-start justify-between gap-2 mb-1">
                                            <div className="flex items-center gap-2">
                                                <span className={`px-2 py-1 text-xs font-medium rounded ${log.log?.source === 'application' ? 'bg-blue-500/20 text-blue-400' :
                                                        log.log?.source === 'system' ? 'bg-green-500/20 text-green-400' :
                                                            log.log?.source === 'security' ? 'bg-purple-500/20 text-purple-400' :
                                                                'bg-gray-500/20 text-gray-400'
                                                    }`}>
                                                    {log.log?.source?.toUpperCase() || 'UNKNOWN'}
                                                </span>
                                                <span className="text-xs font-mono text-muted-foreground">
                                                    {log.event?.source || 'Unknown Source'}
                                                </span>
                                                {log.event?.id && (
                                                    <span className="text-xs font-mono text-primary">
                                                        ID: {log.event.id}
                                                    </span>
                                                )}
                                            </div>
                                            <span className="text-xs text-muted-foreground whitespace-nowrap">
                                                {new Date(log['@timestamp']).toLocaleTimeString()}
                                            </span>
                                        </div>
                                        <p className="text-sm text-foreground/80 line-clamp-2">
                                            {log.event?.message || log.message || 'No message'}
                                        </p>
                                        {log.event?.level && (
                                            <span className={`text-xs font-medium ${log.event.level === 'Error' ? 'text-red-500' :
                                                    log.event.level === 'Warning' ? 'text-yellow-500' :
                                                        'text-gray-400'
                                                }`}>
                                                {log.event.level}
                                            </span>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </Card>

                {/* Alerts Feed */}
                <Card className="overflow-hidden">
                    <div className="p-4 border-b border-white/10">
                        <h2 className="text-xl font-semibold">Live Alerts Feed</h2>
                        <p className="text-sm text-muted-foreground">Triggered Detection Rules</p>
                    </div>
                    <div className="h-[500px] overflow-y-auto">
                        {alerts.length === 0 ? (
                            <div className="flex items-center justify-center h-full text-muted-foreground">
                                <div className="text-center">
                                    <p className="text-lg mb-2">No alerts yet</p>
                                    <p className="text-sm">Alerts will appear here when rules are triggered</p>
                                </div>
                            </div>
                        ) : (
                            <div className="divide-y divide-white/10">
                                {alerts.map((alert, i) => (
                                    <div key={i} className="p-3 hover:bg-white/5 transition-colors">
                                        <div className="flex items-start justify-between gap-2 mb-2">
                                            <span className={`px-2 py-1 text-xs font-bold rounded border ${getSeverityBg(alert.severity)}`}>
                                                {alert.severity}
                                            </span>
                                            <span className="text-xs text-muted-foreground whitespace-nowrap">
                                                {new Date(alert['@timestamp']).toLocaleTimeString()}
                                            </span>
                                        </div>
                                        <h3 className="text-sm font-semibold mb-1">{alert.rule_name}</h3>
                                        <p className="text-xs text-muted-foreground mb-2">
                                            Rule ID: {alert.rule_id}
                                        </p>
                                        {alert.description && (
                                            <p className="text-xs text-foreground/70 line-clamp-2">
                                                {alert.description}
                                            </p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </Card>
            </div>

            {/* Alerts by Severity */}
            <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4">Alerts by Severity (Session)</h2>
                <div className="space-y-3">
                    {Object.entries(stats.alertsBySeverity).length === 0 ? (
                        <p className="text-muted-foreground text-center py-4">No alerts to display</p>
                    ) : (
                        Object.entries(stats.alertsBySeverity)
                            .sort((a, b) => b[1] - a[1])
                            .map(([severity, count]) => (
                                <div key={severity}>
                                    <div className="flex items-center justify-between mb-1">
                                        <span className={`font-medium ${getSeverityColor(severity)}`}>{severity}</span>
                                        <span className="text-muted-foreground">{count}</span>
                                    </div>
                                    <div className="w-full bg-white/10 rounded-full h-2">
                                        <div
                                            className={`h-2 rounded-full ${getSeverityColor(severity).replace('text-', 'bg-')}`}
                                            style={{
                                                width: `${(count / stats.totalAlerts) * 100}%`
                                            }}
                                        ></div>
                                    </div>
                                </div>
                            ))
                    )}
                </div>
            </Card>
        </div>
    );
}
