'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, Shield, Bell, Activity,
  Workflow, FileText, Settings, ChevronLeft, ChevronRight,
  Globe, Database, Terminal
} from 'lucide-react';

interface SidebarItemProps {
  icon: React.ReactNode;
  label: string;
  href: string;
  isActive: boolean;
  isCollapsed: boolean;
}

const SidebarItem = ({ icon, label, href, isActive, isCollapsed }: SidebarItemProps) => {
  return (
    <Link
      href={href}
      className={`flex items-center p-3 my-1 rounded-lg transition-all duration-200 group
        ${isActive
          ? 'bg-primary/10 text-primary neon-border cyber-glow'
          : 'hover:bg-primary/5 text-sidebar-foreground hover:text-primary'
        }
      `}
    >
      <div className={`${isActive ? 'text-primary' : ''}`}>
        {icon}
      </div>
      {!isCollapsed && (
        <span className={`ml-3 ${isActive ? 'font-medium' : ''}`}>
          {label}
        </span>
      )}
    </Link>
  );
};

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  const sidebarItems = [
    { icon: <LayoutDashboard size={20} />, label: 'Dashboard', href: '/' },
    { icon: <Bell size={20} />, label: 'Alerts', href: '/alerts' },
    { icon: <Shield size={20} />, label: 'Incidents', href: '/incidents' },
    { icon: <Globe size={20} />, label: 'Threat Intel', href: '/threat-intel' },
    { icon: <Workflow size={20} />, label: 'Automation', href: '/automation' },
    { icon: <Database size={20} />, label: 'Log Explorer', href: '/logs' },
    { icon: <Terminal size={20} />, label: 'Query Builder', href: '/query-builder' },
    { icon: <Activity size={20} />, label: 'Analytics', href: '/analytics' },
    { icon: <FileText size={20} />, label: 'Reports', href: '/reports' },
    { icon: <Settings size={20} />, label: 'Settings', href: '/settings' },
  ];

  return (
    <div
      className={`h-screen bg-sidebar border-r border-sidebar-border transition-all duration-300 flex flex-col
        ${collapsed ? 'w-[70px]' : 'w-[240px]'}`
      }
    >
      <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
        <div className="flex items-center">
          {!collapsed && (
            <span className="text-xl font-bold text-primary neon-text">SOCify</span>
          )}
          {collapsed && (
            <span className="text-xl font-bold text-primary neon-text">S</span>
          )}
        </div>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded-full hover:bg-primary/10 text-sidebar-foreground hover:text-primary"
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-4 px-3">
        <nav className="space-y-1">
          {sidebarItems.map((item) => (
            <SidebarItem
              key={item.href}
              icon={item.icon}
              label={item.label}
              href={item.href}
              isActive={pathname === item.href}
              isCollapsed={collapsed}
            />
          ))}
        </nav>
      </div>

      <div className="p-4 border-t border-sidebar-border">
        <div className={`flex items-center ${collapsed ? 'justify-center' : 'space-x-3'}`}>
          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary">
            A
          </div>
          {!collapsed && (
            <div>
              <p className="text-sm font-medium">Analyst</p>
              <p className="text-xs text-sidebar-foreground/70">SOC Team</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}