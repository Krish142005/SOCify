'use client';

import { Card } from '@/components/ui/Card';
import { FileText, Download, Calendar, Mail } from 'lucide-react';

export default function ReportsPage() {
    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold neon-text">Reports</h1>
                <button className="px-4 py-2 bg-primary hover:bg-primary/80 text-black font-bold rounded transition-colors flex items-center gap-2">
                    <FileText size={18} /> Generate New Report
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-4">
                    <h3 className="text-lg font-bold text-muted-foreground uppercase text-xs mb-4">Recent Reports</h3>
                    {[
                        { name: 'Weekly Security Summary', date: 'Nov 21, 2025', type: 'PDF', size: '2.4 MB' },
                        { name: 'Incident Response: INC-2025-001', date: 'Nov 20, 2025', type: 'PDF', size: '1.1 MB' },
                        { name: 'Monthly Compliance Audit', date: 'Nov 01, 2025', type: 'CSV', size: '450 KB' },
                        { name: 'User Activity Log Export', date: 'Oct 31, 2025', type: 'JSON', size: '15 MB' },
                        { name: 'Firewall Traffic Analysis', date: 'Oct 28, 2025', type: 'PDF', size: '5.8 MB' },
                    ].map((report, i) => (
                        <Card key={i} className="p-4 flex items-center justify-between hover:bg-white/5 transition-colors group">
                            <div className="flex items-center gap-4">
                                <div className="p-3 rounded bg-white/5 text-primary group-hover:bg-primary group-hover:text-black transition-colors">
                                    <FileText size={24} />
                                </div>
                                <div>
                                    <h4 className="font-bold">{report.name}</h4>
                                    <p className="text-xs text-muted-foreground">{report.date} • {report.type} • {report.size}</p>
                                </div>
                            </div>
                            <button className="p-2 hover:bg-white/10 rounded text-muted-foreground hover:text-white">
                                <Download size={20} />
                            </button>
                        </Card>
                    ))}
                </div>

                <div className="space-y-6">
                    <Card className="p-6">
                        <h3 className="font-bold mb-4 flex items-center gap-2">
                            <Calendar size={20} className="text-primary" /> Scheduled Reports
                        </h3>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center text-sm">
                                <span>Daily Executive Brief</span>
                                <span className="text-green-400">08:00 AM</span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span>Weekly Threat Analysis</span>
                                <span className="text-green-400">Mon 09:00 AM</span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span>Monthly Compliance</span>
                                <span className="text-green-400">1st 10:00 AM</span>
                            </div>
                        </div>
                        <button className="w-full mt-6 py-2 border border-white/10 hover:bg-white/5 rounded text-sm">
                            Manage Schedule
                        </button>
                    </Card>

                    <Card className="p-6">
                        <h3 className="font-bold mb-4 flex items-center gap-2">
                            <Mail size={20} className="text-chart-4" /> Email Recipients
                        </h3>
                        <div className="space-y-2 mb-4">
                            <div className="px-3 py-2 bg-white/5 rounded text-sm flex justify-between">
                                <span>ciso@socify.io</span>
                                <span className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded">Admin</span>
                            </div>
                            <div className="px-3 py-2 bg-white/5 rounded text-sm flex justify-between">
                                <span>security-team@socify.io</span>
                                <span className="text-xs bg-white/10 px-2 py-0.5 rounded">Team</span>
                            </div>
                        </div>
                        <button className="w-full py-2 border border-white/10 hover:bg-white/5 rounded text-sm">
                            Edit Recipients
                        </button>
                    </Card>
                </div>
            </div>
        </div>
    );
}
