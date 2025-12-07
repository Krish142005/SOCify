'use client';

import { Card } from '@/components/ui/Card';
import { User, Lock, Bell, Globe, Database, Shield } from 'lucide-react';

export default function SettingsPage() {
    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold neon-text">Settings</h1>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                <div className="lg:col-span-1 space-y-2">
                    {[
                        { name: 'General', icon: Globe, active: true },
                        { name: 'Account', icon: User, active: false },
                        { name: 'Security', icon: Lock, active: false },
                        { name: 'Notifications', icon: Bell, active: false },
                        { name: 'Data Sources', icon: Database, active: false },
                        { name: 'API Keys', icon: Shield, active: false },
                    ].map((item, i) => (
                        <button key={i} className={`w-full text-left px-4 py-3 rounded flex items-center gap-3 transition-colors ${item.active ? 'bg-primary/20 text-primary border border-primary/50' : 'hover:bg-white/5 text-muted-foreground'
                            }`}>
                            <item.icon size={18} />
                            {item.name}
                        </button>
                    ))}
                </div>

                <div className="lg:col-span-3 space-y-6">
                    <Card className="p-6">
                        <h3 className="text-xl font-bold mb-6">General Settings</h3>

                        <div className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <label className="text-sm text-muted-foreground">Organization Name</label>
                                    <input type="text" defaultValue="Socify Corp" className="w-full bg-black/40 border border-white/10 rounded px-4 py-2" />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm text-muted-foreground">Timezone</label>
                                    <select className="w-full bg-black/40 border border-white/10 rounded px-4 py-2">
                                        <option>UTC (Coordinated Universal Time)</option>
                                        <option>EST (Eastern Standard Time)</option>
                                        <option>IST (Indian Standard Time)</option>
                                    </select>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm text-muted-foreground">Dashboard Refresh Rate</label>
                                <div className="flex gap-4">
                                    {['10s', '30s', '1m', '5m'].map((t, i) => (
                                        <button key={i} className={`px-4 py-2 rounded border ${i === 1 ? 'bg-primary/20 border-primary text-primary' : 'border-white/10 hover:bg-white/5'}`}>
                                            {t}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div className="pt-6 border-t border-white/10">
                                <h4 className="font-bold mb-4">Theme Customization</h4>
                                <div className="flex gap-4">
                                    <div className="w-12 h-12 rounded-full bg-black border-2 border-primary cursor-pointer ring-2 ring-primary ring-offset-2 ring-offset-black"></div>
                                    <div className="w-12 h-12 rounded-full bg-slate-900 border border-white/10 cursor-pointer opacity-50"></div>
                                    <div className="w-12 h-12 rounded-full bg-blue-950 border border-white/10 cursor-pointer opacity-50"></div>
                                </div>
                            </div>
                        </div>

                        <div className="mt-8 flex justify-end gap-4">
                            <button className="px-6 py-2 rounded hover:bg-white/5">Cancel</button>
                            <button className="px-6 py-2 bg-primary text-black font-bold rounded hover:bg-primary/80">Save Changes</button>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
}
