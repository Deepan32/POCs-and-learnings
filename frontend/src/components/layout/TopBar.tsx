"use client";

import React, { useState } from "react";
import { Search, Bell, Moon, Sun, Smartphone, CheckCircle2, ShieldCheck } from "lucide-react";

interface TopBarProps {
  onOpenSearch: () => void;
  onOpenSandbox: () => void;
}

export function TopBar({ onOpenSearch, onOpenSandbox }: TopBarProps) {
  const [isDark, setIsDark] = useState(true);

  const toggleTheme = () => {
    setIsDark(!isDark);
    if (!isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  return (
    <header className="h-14 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-6 flex items-center justify-between z-10 select-none">
      {/* Search Input Trigger */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenSearch}
          className="flex items-center gap-3 px-3.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-400 hover:text-slate-200 hover:border-slate-700 transition w-72 justify-between"
        >
          <div className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-slate-500" />
            <span>Search contacts, leads, templates...</span>
          </div>
          <kbd className="px-1.5 py-0.5 text-[10px] font-mono rounded bg-slate-800 text-slate-400 border border-slate-700">
            ⌘K
          </kbd>
        </button>

        {/* Live Meta API Badge */}
        <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-950/50 border border-emerald-500/30 text-[11px] text-emerald-400">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-medium">Meta Cloud API v21.0</span>
          <span className="text-[10px] bg-emerald-500/20 px-1.5 py-0.2 rounded font-mono font-bold text-emerald-300">
            GREEN
          </span>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Sandbox Quick Button */}
        <button
          onClick={onOpenSandbox}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-semibold transition shadow-sm"
        >
          <Smartphone className="w-3.5 h-3.5 text-emerald-400" />
          <span>Test WhatsApp Simulator</span>
        </button>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition"
          title="Toggle Theme"
        >
          {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 transition relative"
            title="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-emerald-500" />
          </button>
        </div>
      </div>
    </header>
  );
}
