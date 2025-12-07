const API_BASE_URL = 'http://localhost:8000/api';

export interface Log {
    timestamp: string;
    message: string;
    level: string;
    source: string;
    host: string;
    [key: string]: any;
}

export interface Alert {
    alert_id: string;
    rule_id: string;
    rule_name: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    description: string;
    status: string;
    created_at: string;
    source_ips: string[];
    destination_ips: string[];
    mitre_tactics: string[];
    mitre_techniques: string[];
}

export interface Rule {
    rule_id: string;
    name: string;
    description: string;
    severity: string;
    type: string;
    enabled: boolean;
}

export const api = {
    async getLogs(limit = 100, offset = 0) {
        const res = await fetch(`${API_BASE_URL}/search?limit=${limit}&offset=${offset}`);
        return res.json();
    },

    async getAlerts(limit = 50, offset = 0) {
        const res = await fetch(`${API_BASE_URL}/alerts?limit=${limit}&offset=${offset}`);
        return res.json();
    },

    async getRules() {
        const res = await fetch(`${API_BASE_URL}/rules`);
        return res.json();
    },

    async getStats() {
        // This would ideally come from a stats endpoint, but for now we can aggregate from alerts
        const alerts = await this.getAlerts(1000);
        const logs = await this.getLogs(1);

        return {
            activeThreats: alerts.alerts?.length || 0,
            criticalAlerts: alerts.alerts?.filter((a: Alert) => a.severity === 'critical').length || 0,
            totalLogs: logs.total || 0
        };
    }
};
