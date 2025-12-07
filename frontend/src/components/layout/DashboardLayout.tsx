'use client';

import { ReactNode, useEffect } from 'react';
import Sidebar from './Sidebar';
import Navbar from './Navbar';

interface DashboardLayoutProps {
    children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
    // Set dark mode by default
    useEffect(() => {
        document.documentElement.classList.add('dark');
    }, []);

    return (
        <div className="flex h-screen bg-background">
            <Sidebar />
            <div className="flex-1 flex flex-col overflow-hidden">
                <Navbar />
                <main className="flex-1 overflow-y-auto p-4 bg-background">
                    {children}
                </main>
                <div className="h-8 border-t border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 flex items-center px-4">
                    <div className="text-xs text-muted-foreground animate-marquee whitespace-nowrap">
                        <span className="mx-2 text-destructive">⚠️ Critical Alert:</span> Potential data exfiltration detected from host SRV-DB-01
                        <span className="mx-2 text-chart-4">⚠️ Warning:</span> Unusual authentication patterns detected in US-EAST region
                        <span className="mx-2 text-primary">ℹ️ Info:</span> System updates available for 12 endpoints
                    </div>
                </div>
            </div>
        </div>
    );
}
