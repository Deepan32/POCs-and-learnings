"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  MessageSquare,
  GitFork,
  Zap,
  FileText,
  Users,
  UserCheck,
  BookOpen,
  BarChart3,
  Layers,
  Settings,
  Smartphone,
  Sparkles,
  ShieldCheck,
  ChevronRight,
  LogOut,
  SlidersHorizontal,
} from "lucide-react";

interface SidebarProps {
  onOpenSandbox?: () => void;
}

export function Sidebar({ onOpenSandbox }: SidebarProps) {
  const pathname = usePathname();

  const navItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Client Setup", href: "/client-setup", icon: SlidersHorizontal, isStudio: true },
    { name: "Team Inbox", href: "/inbox", icon: MessageSquare, badge: "3" },
    { name: "Flow Builder", href: "/flows", icon: GitFork, isNew: true },
    { name: "Automations", href: "/automations", icon: Zap },
    { name: "Templates", href: "/templates", icon: FileText },
    { name: "Leads CRM", href: "/leads", icon: Users, badge: "₹95k" },
    { name: "Contacts", href: "/contacts", icon: UserCheck },
    { name: "Knowledge Base", href: "/knowledge-base", icon: BookOpen },
    { name: "Analytics", href: "/analytics", icon: BarChart3 },
    { name: "Integrations", href: "/integrations", icon: Layers },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <aside className="w-64 flex-shrink-0 bg-slate-950 text-slate-200 border-r border-slate-800/80 flex flex-col h-screen select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80 flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 via-emerald-500 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold tracking-tight text-white text-lg font-mono">
                ALLSTREAK
              </span>
              <span className="px-1.5 py-0.2 text-[10px] uppercase font-bold rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                PRO
              </span>
            </div>
            <p className="text-[10px] text-slate-400 tracking-wide font-medium">
              Automate. Engage. Convert.
            </p>
          </div>
        </Link>
      </div>

      {/* Workspace Indicator */}
      <div className="px-4 py-2.5 bg-slate-900/60 border-b border-slate-800/60 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2 overflow-hidden">
          <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10B981]" />
          <span className="font-semibold text-slate-300 truncate">ALLSTREAK Demo</span>
        </div>
        <span className="text-[10px] font-mono text-slate-500 bg-slate-800/60 px-1.5 py-0.5 rounded">
          Cloud API
        </span>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150 ${
                isActive
                  ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm"
                  : "text-slate-400 hover:text-slate-100 hover:bg-slate-900/80"
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? "text-emerald-400" : "text-slate-400"}`} />
                <span>{item.name}</span>
              </div>
              <div className="flex items-center gap-1.5">
                {item.isStudio && (
                  <span className="px-1.5 py-0.2 text-[9px] font-bold rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    STUDIO
                  </span>
                )}
                {item.isNew && (
                  <span className="px-1.5 py-0.2 text-[9px] font-bold rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                    FLOW
                  </span>
                )}
                {item.badge && (
                  <span
                    className={`px-1.5 py-0.5 text-[10px] font-bold rounded-full ${
                      isActive
                        ? "bg-emerald-500 text-slate-950 font-black"
                        : "bg-slate-800 text-slate-300"
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Sandbox Simulator CTA Banner */}
      <div className="p-3 mx-3 mb-3 rounded-xl bg-gradient-to-b from-emerald-950/40 to-slate-900/80 border border-emerald-500/20 text-left">
        <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold mb-1">
          <Smartphone className="w-3.5 h-3.5" />
          <span>Interactive Sandbox</span>
        </div>
        <p className="text-[11px] text-slate-400 mb-2.5 leading-relaxed">
          Test bot replies, buttons, and human handover live in WhatsApp phone mockup!
        </p>
        <button
          onClick={onOpenSandbox}
          className="w-full py-1.5 px-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold transition flex items-center justify-center gap-1.5 shadow-md shadow-emerald-900/30"
        >
          <span>Open Phone Simulator</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* User Footer */}
      <div className="p-3 border-t border-slate-800/80 flex items-center justify-between bg-slate-950">
        <div className="flex items-center gap-2.5 overflow-hidden">
          <div className="w-7 h-7 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-bold text-xs">
            S
          </div>
          <div className="truncate">
            <p className="text-xs font-semibold text-slate-200 truncate">Surya (Owner)</p>
            <p className="text-[10px] text-slate-400 truncate">admin@allstreak.com</p>
          </div>
        </div>
        <button
          onClick={() => {
            localStorage.removeItem("allstreak_token");
            window.location.href = "/login";
          }}
          title="Sign Out"
          className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-900 rounded-lg transition"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </aside>
  );
}
