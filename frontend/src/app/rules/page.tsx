'use client';

import { useEffect, useState } from 'react';
import { api, Rule } from '@/lib/api';
import { Card } from '@/components/ui/Card';

export default function RulesPage() {
    const [rules, setRules] = useState<Rule[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchRules = async () => {
            try {
                const data = await api.getRules();
                setRules(data || []);
            } catch (error) {
                console.error('Failed to fetch rules:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchRules();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold neon-text">Detection Rules</h1>
                <span className="text-muted-foreground">{rules.length} Active Rules</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {loading ? (
                    <div className="col-span-full text-center py-10">Loading rules...</div>
                ) : (
                    rules.map((rule) => (
                        <Card key={rule.rule_id} className="p-4 hover:border-primary transition-colors flex flex-col h-full">
                            <div className="flex justify-between items-start mb-2">
                                <h3 className="font-bold text-lg line-clamp-1" title={rule.name}>{rule.name}</h3>
                                <span className={`px-2 py-0.5 rounded text-xs uppercase ${rule.severity === 'critical' ? 'text-destructive border border-destructive' :
                                        rule.severity === 'high' ? 'text-chart-4 border border-chart-4' :
                                            'text-primary border border-primary'
                                    }`}>
                                    {rule.severity}
                                </span>
                            </div>
                            <p className="text-sm text-muted-foreground mb-4 flex-grow line-clamp-3">{rule.description}</p>
                            <div className="flex justify-between items-center text-xs text-muted-foreground mt-auto pt-4 border-t border-white/10">
                                <span className="uppercase tracking-wider">{rule.type}</span>
                                <span className={rule.enabled !== false ? 'text-green-400' : 'text-red-400'}>
                                    {rule.enabled !== false ? '● Enabled' : '○ Disabled'}
                                </span>
                            </div>
                        </Card>
                    ))
                )}
            </div>
        </div>
    );
}
