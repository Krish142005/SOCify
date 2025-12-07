'use client';

import { Card } from '@/components/ui/Card';
import { Search, Save, Clock, Play } from 'lucide-react';

export default function QueryBuilderPage() {
    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold neon-text">Query Builder</h1>

            <Card className="p-6">
                <div className="flex gap-4 mb-4">
                    <div className="flex-1 relative">
                        <Search className="absolute left-3 top-3 text-muted-foreground" size={20} />
                        <textarea
                            className="w-full bg-black/40 border border-white/10 rounded-lg p-3 pl-10 font-mono text-sm min-h-[120px] focus:outline-none focus:border-primary text-green-400 placeholder:text-gray-600"
                            placeholder="SELECT * FROM logs WHERE severity = 'critical' AND source.ip LIKE '192.168.%'"
                            defaultValue="source = 'firewall' AND destination_port = 22 | stats count by source_ip"
                        />
                    </div>
                </div>

                <div className="flex justify-between items-center">
                    <div className="flex gap-2">
                        <button className="px-4 py-2 bg-white/5 hover:bg-white/10 rounded text-sm flex items-center gap-2">
                            <Clock size={16} /> Last 24 Hours
                        </button>
                        <button className="px-4 py-2 bg-white/5 hover:bg-white/10 rounded text-sm flex items-center gap-2">
                            <Save size={16} /> Save Query
                        </button>
                    </div>
                    <button className="px-6 py-2 bg-primary hover:bg-primary/80 text-black font-bold rounded flex items-center gap-2">
                        <Play size={18} /> Run Query
                    </button>
                </div>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                <Card className="lg:col-span-1 p-4">
                    <h3 className="font-bold mb-4 text-muted-foreground uppercase text-xs">Saved Queries</h3>
                    <div className="space-y-2">
                        {['SSH Brute Force Attempts', 'High Volume Traffic', 'Admin Login Failures', 'New User Creations', 'Malware Signatures'].map((q, i) => (
                            <div key={i} className="p-2 hover:bg-white/5 rounded cursor-pointer text-sm truncate">
                                {q}
                            </div>
                        ))}
                    </div>
                </Card>

                <Card className="lg:col-span-3 p-4 min-h-[400px] flex items-center justify-center text-muted-foreground border-dashed border-2 border-white/10">
                    <div className="text-center">
                        <Search size={48} className="mx-auto mb-4 opacity-20" />
                        <p>Run a query to see results</p>
                    </div>
                </Card>
            </div>
        </div>
    );
}
