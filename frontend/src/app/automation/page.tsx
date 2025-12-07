'use client';

import { Card } from '@/components/ui/Card';
import { Play, Pause, Settings, Zap } from 'lucide-react';

export default function AutomationPage() {
    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold neon-text">SOAR Automation</h1>
                <button className="px-4 py-2 bg-primary hover:bg-primary/80 text-black font-bold rounded transition-colors flex items-center gap-2">
                    <Zap size={18} /> New Playbook
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[
                    { name: 'Phishing Response', status: 'Active', triggers: 142, success: '98%' },
                    { name: 'Malware Containment', status: 'Active', triggers: 28, success: '100%' },
                    { name: 'User Account Lockout', status: 'Paused', triggers: 0, success: 'N/A' },
                    { name: 'IP Blocking (Firewall)', status: 'Active', triggers: 567, success: '99.5%' },
                    { name: 'Vulnerability Scan', status: 'Scheduled', triggers: 1, success: '100%' },
                    { name: 'Slack Notification', status: 'Active', triggers: 1205, success: '100%' },
                ].map((playbook, i) => (
                    <Card key={i} className="p-6 hover:border-primary transition-colors group">
                        <div className="flex justify-between items-start mb-4">
                            <div className="p-3 rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-black transition-colors">
                                <Zap size={24} />
                            </div>
                            <div className={`px-2 py-1 rounded text-xs font-bold ${playbook.status === 'Active' ? 'bg-green-500/20 text-green-400' :
                                    playbook.status === 'Paused' ? 'bg-yellow-500/20 text-yellow-400' :
                                        'bg-blue-500/20 text-blue-400'
                                }`}>
                                {playbook.status}
                            </div>
                        </div>

                        <h3 className="text-xl font-bold mb-2">{playbook.name}</h3>

                        <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-white/10">
                            <div>
                                <p className="text-xs text-muted-foreground">Triggers (24h)</p>
                                <p className="text-lg font-mono text-white">{playbook.triggers}</p>
                            </div>
                            <div>
                                <p className="text-xs text-muted-foreground">Success Rate</p>
                                <p className="text-lg font-mono text-green-400">{playbook.success}</p>
                            </div>
                        </div>

                        <div className="flex gap-2 mt-4">
                            <button className="flex-1 py-2 bg-white/5 hover:bg-white/10 rounded flex justify-center items-center text-sm">
                                <Settings size={14} className="mr-2" /> Configure
                            </button>
                            <button className="p-2 bg-white/5 hover:bg-white/10 rounded text-primary">
                                {playbook.status === 'Active' ? <Pause size={16} /> : <Play size={16} />}
                            </button>
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    );
}
