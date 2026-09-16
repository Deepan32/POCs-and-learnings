"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import {
  BarChart3,
  TrendingUp,
  Users,
  MessageSquare,
  Bot,
  Sparkles,
  Headphones,
  CheckCircle2,
  Clock,
  ArrowUpRight,
} from "lucide-react";
import { ApiClient } from "@/lib/api";
import { DashboardMetrics } from "@/types";

export default function AnalyticsPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);

  useEffect(() => {
    async function loadMetrics() {
      try {
        const data = await ApiClient.getDashboardMetrics();
        setMetrics(data);
      } catch (err) {
        console.error(err);
      }
    }
    loadMetrics();
  }, []);

  return (
    <AppShell>
      <div className="p-8 max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-emerald-400" />
            <span>Advanced Analytics & Funnels</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Conversion performance, average response speed, and automation success telemetry
          </p>
        </div>

        {/* Top KPI Metrics Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
            <span className="text-xs text-slate-400 font-medium">Conversion Rate</span>
            <div className="text-3xl font-black text-emerald-400 font-mono">14.3%</div>
            <p className="text-[11px] text-slate-500">From WhatsApp chat to qualified lead</p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
            <span className="text-xs text-slate-400 font-medium">Avg First Response Time</span>
            <div className="text-3xl font-black text-white font-mono">0.8s</div>
            <p className="text-[11px] text-slate-500">Autonomous bot / AI response speed</p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
            <span className="text-xs text-slate-400 font-medium">Handover Escalation Rate</span>
            <div className="text-3xl font-black text-purple-400 font-mono">7.1%</div>
            <p className="text-[11px] text-slate-500">Complex enterprise requests</p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-1">
            <span className="text-xs text-slate-400 font-medium">Automation Success</span>
            <div className="text-3xl font-black text-blue-400 font-mono">98.9%</div>
            <p className="text-[11px] text-slate-500">Successful Meta API dispatches</p>
          </div>
        </div>

        {/* Funnel Breakdown */}
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6">
          <div>
            <h3 className="text-sm font-bold text-white">Conversion Pipeline Funnel</h3>
            <p className="text-xs text-slate-400">Step-by-step visitor progression</p>
          </div>

          <div className="space-y-3">
            {[
              { label: "1. Incoming WhatsApp Chats", count: "1,240", pct: "100%", color: "bg-slate-700" },
              { label: "2. Triggered Automation Reply", count: "1,198", pct: "96.6%", color: "bg-emerald-600" },
              { label: "3. Qualified Leads Captured", count: "322", pct: "25.9%", color: "bg-blue-600" },
              { label: "4. Deals Converted", count: "178", pct: "14.3%", color: "bg-emerald-400" },
            ].map((step, idx) => (
              <div key={idx} className="space-y-1.5">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-300">{step.label}</span>
                  <span className="font-mono text-white">
                    {step.count} ({step.pct})
                  </span>
                </div>
                <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-slate-800">
                  <div className={`${step.color} h-full rounded-full transition-all duration-500`} style={{ width: step.pct }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
