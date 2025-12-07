'use client';

import { useState } from 'react';
import { Bell, Search, Moon, Sun, MessageSquare } from 'lucide-react';

export default function Navbar() {
  const [isDarkMode, setIsDarkMode] = useState(true);

  const toggleTheme = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    document.documentElement.classList.toggle('dark', newMode);
  };

  return (
    <div className="h-16 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 flex items-center justify-between px-4">
      <div className="flex-1">
        <div className="relative max-w-md">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <Search className="h-4 w-4 text-muted-foreground" />
          </div>
          <input
            type="text"
            placeholder="Search threats, logs, incidents..."
            className="w-full py-2 pl-10 pr-4 text-sm bg-muted/50 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          />
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <button className="relative p-2 rounded-full hover:bg-muted/50">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full"></span>
        </button>
        
        <button className="p-2 rounded-full hover:bg-muted/50">
          <MessageSquare className="h-5 w-5" />
        </button>
        
        <button 
          onClick={toggleTheme} 
          className="p-2 rounded-full hover:bg-muted/50"
        >
          {isDarkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </button>

        <div className="h-8 w-[1px] bg-border mx-2"></div>
        
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary">
            A
          </div>
          <div className="hidden md:block">
            <p className="text-sm font-medium">Analyst</p>
            <p className="text-xs text-muted-foreground">SOC Team</p>
          </div>
        </div>
      </div>
    </div>
  );
}