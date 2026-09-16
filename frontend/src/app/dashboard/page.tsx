"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import {
  MessageSquare,
  Users,
  Bot,
  Sparkles,
  Headphones,
  TrendingUp,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Clock,
  Send,
  Zap,
} from "lucide-react";
import { ApiClient } from "@/lib/api";
import { DashboardMetrics } from "@/types";

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await ApiClient.getDashboardMetrics();
        setMetrics(data);
      } catch (err) {
        console.error("Failed to load dashboard metrics:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <AppShell>
      <div className="p-8 max-w-7xl mx-auto space-y-8">
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2.5">
              <span>Business Overview</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-mono font-bold border border-emerald-500/30">
                LIVE
              </span>
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Real-time WhatsApp activity, automated conversions, and team inbox health
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/inbox"
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs flex items-center gap-2 transition shadow-lg shadow-emerald-950/40"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Open Team Inbox</span>
            </Link>
            <Link
              href="/flows"
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 font-semibold text-xs flex items-center gap-2 transition"
            >
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>Visual Flows</span>
            </Link>
          </div>
        </div>

        {/* 9 Metric Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {metrics?.cards?.map((card, idx) => (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-slate-900 border border-slate-800/80 shadow-md hover:border-slate-700 transition relative overflow-hidden group"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-slate-400">{card.title}</span>
                <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  {card.trend}
                </span>
              </div>
              <div className="text-3xl font-black text-white font-mono tracking-tight">
                {card.value}
              </div>
              <p className="text-[11px] text-slate-500 mt-2">{card.description}</p>
              <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl pointer-events-none group-hover:bg-emerald-500/10 transition" />
            </div>
          ))}
        </div>

        {/* Middle Charts & Distribution Split */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Messages Volume Over Time Chart */}
          <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900 border border-slate-800/80 shadow-md">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-sm font-bold text-white">Messages & Inbound Activity</h3>
                <p className="text-xs text-slate-400">Total volume over the last 7 days</p>
              </div>
              <span className="text-xs font-mono text-emerald-400 font-semibold bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
                +38.5% this week
              </span>
            </div>

            {/* Custom Bar Visualizer */}
            <div className="h-48 flex items-end justify-between gap-3 pt-4 px-2 border-b border-slate-800">
              {metrics?.messages_chart?.map((point, idx) => (
                <div key={idx} className="flex-1 flex flex-col items-center gap-2 group">
                  <span className="text-[10px] font-mono text-slate-400 opacity-0 group-hover:opacity-100 transition">
                    {point.count}
                  </span>
                  <div
                    className="w-full bg-gradient-to-t from-emerald-600 to-teal-400 rounded-t-lg transition-all duration-300 group-hover:brightness-125"
                    style={{ height: `${Math.max(15, (point.count / 25) * 100)}%` }}
                  />
                  <span className="text-[10px] text-slate-400 font-medium">{point.timestamp}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Bot vs AI vs Human Handover Split */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800/80 shadow-md flex flex-col justify-between">
            <div>
              <h3 className="text-sm font-bold text-white">Conversation Distribution</h3>
              <p className="text-xs text-slate-400">Breakdown by resolution mode</p>

              <div className="space-y-4 mt-6">
                {/* Bot */}
                <div>
                  <div className="flex justify-between text-xs mb-1.5">
                    <span className="flex items-center gap-2 text-slate-300">
                      <Bot className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Bot Automation</span>
                    </span>
                    <span className="font-mono font-bold text-white">
                      {metrics?.conversation_split?.bot_percentage || 65}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-emerald-500 h-full rounded-full"
                      style={{ width: `${metrics?.conversation_split?.bot_percentage || 65}%` }}
                    />
                  </div>
                </div>

                {/* AI Agent */}
                <div>
                  <div className="flex justify-between text-xs mb-1.5">
                    <span className="flex items-center gap-2 text-slate-300">
                      <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                      <span>AI Agent (RAG)</span>
                    </span>
                    <span className="font-mono font-bold text-white">
                      {metrics?.conversation_split?.ai_percentage || 25}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-blue-500 h-full rounded-full"
                      style={{ width: `${metrics?.conversation_split?.ai_percentage || 25}%` }}
                    />
                  </div>
                </div>

                {/* Human Handover */}
                <div>
                  <div className="flex justify-between text-xs mb-1.5">
                    <span className="flex items-center gap-2 text-slate-300">
                      <Headphones className="w-3.5 h-3.5 text-purple-400" />
                      <span>Human Handover</span>
                    </span>
                    <span className="font-mono font-bold text-white">
                      {metrics?.conversation_split?.human_percentage || 10}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-purple-500 h-full rounded-full"
                      style={{ width: `${metrics?.conversation_split?.human_percentage || 10}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 mt-6 flex items-center justify-between text-xs">
              <span className="text-slate-400">Total Handovers:</span>
              <span className="font-mono font-bold text-purple-400">
                {metrics?.human_handovers || 0} chats
              </span>
            </div>
          </div>
        </div>

        {/* Bottom Split: Recent Conversations & Recent Leads */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Conversations */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800/80 shadow-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-emerald-400" />
                <span>Recent WhatsApp Threads</span>
              </h3>
              <Link
                href="/inbox"
                className="text-xs text-emerald-400 hover:underline flex items-center gap-1"
              >
                <span>View Inbox</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="space-y-2.5">
              {metrics?.recent_activities?.map((item) => (
                <Link
                  key={item.id}
                  href={`/inbox`}
                  className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 hover:bg-slate-950 border border-slate-800/80 text-xs transition"
                >
                  <div className="truncate max-w-[75%]">
                    <p className="font-medium text-slate-200 truncate">{item.preview}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className={`text-[10px] font-bold px-1.5 py-0.2 rounded uppercase ${
                          item.mode === "HUMAN"
                            ? "bg-purple-500/20 text-purple-300"
                            : item.mode === "AI"
                            ? "bg-blue-500/20 text-blue-300"
                            : "bg-emerald-500/20 text-emerald-300"
                        }`}
                      >
                        {item.mode}
                      </span>
                      <span className="text-[10px] text-slate-500">
                        {new Date(item.updated_at).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                    </div>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300">
                    {item.status}
                  </span>
                </Link>
              ))}
            </div>
          </div>

          {/* Lead Pipeline Quick View */}
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800/80 shadow-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Users className="w-4 h-4 text-emerald-400" />
                <span>Lead Pipeline Summary</span>
              </h3>
              <Link
                href="/leads"
                className="text-xs text-emerald-400 hover:underline flex items-center gap-1"
              >
                <span>View Kanban</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="space-y-3">
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-400">Total Active Pipeline</p>
                  <p className="text-2xl font-black font-mono text-emerald-400 mt-1">
                    ₹95,000
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-400">New Leads This Week</p>
                  <p className="text-xl font-bold text-white mt-1">+{metrics?.new_leads || 4}</p>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/20 text-xs text-slate-300 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Meta 24h Customer Service Window Enforced</span>
                </div>
                <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                  ACTIVE
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
