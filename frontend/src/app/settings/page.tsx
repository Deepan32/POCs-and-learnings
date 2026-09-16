"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import {
  Settings,
  Sparkles,
  Clock,
  Activity,
  ShieldCheck,
  Save,
  CheckCircle2,
  Building,
  User,
} from "lucide-react";
import { ApiClient } from "@/lib/api";
import { AISetting, Workspace } from "@/types";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<"ai" | "workspace" | "hours" | "health">("ai");
  const [aiSettings, setAiSettings] = useState<AISetting | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [health, setHealth] = useState<any>(null);
  const [saved, setSaved] = useState(false);

  // Form states
  const [aiName, setAiName] = useState("Streak AI");
  const [aiTone, setAiTone] = useState("PROFESSIONAL");
  const [aiMode, setAiMode] = useState("AUTO");
  const [instructions, setInstructions] = useState("");
  const [fallbackMessage, setFallbackMessage] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const ai = await ApiClient.getAISettings();
        setAiSettings(ai);
        if (ai) {
          setAiName(ai.ai_name);
          setAiTone(ai.tone);
          setAiMode(ai.mode);
          setInstructions(ai.instructions);
          setFallbackMessage(ai.fallback_message);
        }

        const ws = await ApiClient.getWorkspace();
        setWorkspace(ws);

        const h = await ApiClient.getSystemHealth();
        setHealth(h);
      } catch (err) {
        console.error(err);
      }
    }
    loadData();
  }, []);

  const handleSaveAI = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await ApiClient.updateAISettings({
        ai_name: aiName,
        tone: aiTone,
        mode: aiMode,
        instructions,
        fallback_message: fallbackMessage,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (err) {
      console.error(err);
      alert("Failed to update AI settings");
    }
  };

  return (
    <AppShell>
      <div className="p-8 max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-black text-white flex items-center gap-2">
            <Settings className="w-6 h-6 text-emerald-400" />
            <span>Platform Settings</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Configure AI Agent parameters, business working hours, and inspect system telemetry
          </p>
        </div>

        {/* Tab Selection */}
        <div className="flex gap-2 border-b border-slate-800 pb-2 text-xs font-semibold">
          {[
            { key: "ai", label: "AI Agent & Fallback", icon: Sparkles },
            { key: "workspace", label: "Workspace Profile", icon: Building },
            { key: "hours", label: "Business Hours", icon: Clock },
            { key: "health", label: "System Health", icon: Activity },
          ].map((t) => {
            const Icon = t.icon;
            const isActive = activeTab === t.key;
            return (
              <button
                key={t.key}
                onClick={() => setActiveTab(t.key as any)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl transition ${
                  isActive
                    ? "bg-slate-900 text-emerald-400 border border-emerald-500/30"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{t.label}</span>
              </button>
            );
          })}
        </div>

        {/* AI Agent Configuration Tab */}
        {activeTab === "ai" && (
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6 shadow-xl">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div>
                <h3 className="text-sm font-bold text-white">AI Agent Intelligence Settings</h3>
                <p className="text-xs text-slate-400">
                  Control persona, prompt instructions, and fallback handover behavior
                </p>
              </div>
              {saved && (
                <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-bold bg-emerald-500/10 px-3 py-1 rounded-full">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Saved!</span>
                </span>
              )}
            </div>

            <form onSubmit={handleSaveAI} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    AI Assistant Name
                  </label>
                  <input
                    type="text"
                    value={aiName}
                    onChange={(e) => setAiName(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Tone of Voice
                  </label>
                  <select
                    value={aiTone}
                    onChange={(e) => setAiTone(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="PROFESSIONAL">PROFESSIONAL</option>
                    <option value="FRIENDLY">FRIENDLY</option>
                    <option value="CASUAL">CASUAL</option>
                    <option value="FORMAL">FORMAL</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Operating Mode
                  </label>
                  <select
                    value={aiMode}
                    onChange={(e) => setAiMode(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="AUTO">AUTO (Replies autonomously)</option>
                    <option value="SUGGEST">SUGGEST (Drafts for agent approval)</option>
                    <option value="OFF">OFF (Disabled)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Custom System Instructions & Behavioral Rules
                </label>
                <textarea
                  rows={4}
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white leading-relaxed focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Fallback Handover Message (Sent when confidence is insufficient)
                </label>
                <textarea
                  rows={2}
                  value={fallbackMessage}
                  onChange={(e) => setFallbackMessage(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="pt-2 flex justify-end">
                <button
                  type="submit"
                  className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg transition"
                >
                  <Save className="w-4 h-4" />
                  <span>Save AI Configuration</span>
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Workspace Tab */}
        {activeTab === "workspace" && (
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white">Workspace Details</h3>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-850">
                <span className="text-slate-400 block text-[11px]">Workspace Name</span>
                <span className="text-white font-semibold text-sm">{workspace?.name}</span>
              </div>
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-850">
                <span className="text-slate-400 block text-[11px]">Timezone</span>
                <span className="text-white font-semibold text-sm">{workspace?.timezone}</span>
              </div>
            </div>
          </div>
        )}

        {/* Business Hours Tab */}
        {activeTab === "hours" && (
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white">Weekly Schedule</h3>
            <div className="divide-y divide-slate-800 text-xs">
              {["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].map((day) => (
                <div key={day} className="py-2.5 flex items-center justify-between">
                  <span className="font-semibold text-white">{day}</span>
                  <span className="font-mono text-emerald-400">09:00 AM - 06:00 PM IST</span>
                </div>
              ))}
              <div className="py-2.5 flex items-center justify-between">
                <span className="font-semibold text-white">Saturday</span>
                <span className="font-mono text-emerald-400">10:00 AM - 02:00 PM IST</span>
              </div>
              <div className="py-2.5 flex items-center justify-between">
                <span className="font-semibold text-white">Sunday</span>
                <span className="font-mono text-slate-500">Closed (Auto-away bot active)</span>
              </div>
            </div>
          </div>
        )}

        {/* System Health Tab */}
        {activeTab === "health" && (
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white">Platform System Health</h3>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                {health?.status || "Healthy"}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              {health?.components &&
                Object.entries(health.components).map(([key, val]: any) => (
                  <div
                    key={key}
                    className="p-3.5 rounded-xl bg-slate-950 border border-slate-850 flex items-center justify-between"
                  >
                    <div>
                      <span className="font-bold text-white capitalize">
                        {key.replace(/_/g, " ")}
                      </span>
                      {val.latency_ms && (
                        <p className="text-[10px] text-slate-500 font-mono">
                          Latency: {val.latency_ms}ms
                        </p>
                      )}
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {val.status}
                    </span>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
