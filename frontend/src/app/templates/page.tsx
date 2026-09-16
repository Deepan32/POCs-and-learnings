"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import {
  FileText,
  Plus,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Clock,
  Send,
  Sparkles,
  Smartphone,
  Eye,
  Layers,
  ChevronRight,
  Coins,
} from "lucide-react";
import { ApiClient } from "@/lib/api";
import { MessageTemplate, TemplateStatus, TemplateCategory, TemplatePricingSummary } from "@/types";

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<MessageTemplate[]>([]);
  const [selectedTpl, setSelectedTpl] = useState<MessageTemplate | null>(null);
  const [pricingSummary, setPricingSummary] = useState<TemplatePricingSummary | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);

  // New Template form state
  const [name, setName] = useState("");
  const [category, setCategory] = useState<TemplateCategory>("UTILITY");
  const [bodyText, setBodyText] = useState("Hello {{1}}, your order #{{2}} is confirmed.");
  const [footerText, setFooterText] = useState("ALLSTREAK Verified");

  const loadTemplates = async () => {
    try {
      const [data, pricing] = await Promise.allSettled([
        ApiClient.getTemplates(),
        ApiClient.getTemplatePricingSummary(),
      ]);
      if (data.status === "fulfilled") {
        setTemplates(data.value);
        if (data.value.length > 0 && !selectedTpl) {
          setSelectedTpl(data.value[0]);
        }
      }
      if (pricing.status === "fulfilled") {
        setPricingSummary(pricing.value);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  const handleSync = async () => {
    setSyncing(true);
    try {
      const res = await ApiClient.syncTemplates();
      setTemplates(res.templates);
      alert(`Synchronized ${res.synced_count} templates from Meta Graph API!`);
    } catch (err) {
      console.error(err);
      alert("Template sync failed");
    } finally {
      setSyncing(false);
    }
  };

  const handleCreateTemplate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await ApiClient.createTemplate({
        name,
        category,
        language: "en_US",
        body_text: bodyText,
        footer_text: footerText,
        variables: [
          { variable_index: 1, variable_name: "customer_name", mapping_source: "contact.name" },
          { variable_index: 2, variable_name: "order_id", mapping_source: "lead.company" },
        ],
      });
      setCreateModalOpen(false);
      setName("");
      loadTemplates();
    } catch (err) {
      console.error(err);
      alert("Failed to create template");
    }
  };

  const renderPreviewText = (text: string) => {
    return text.replace("{{1}}", "Rahul Sharma").replace("{{2}}", "#98234");
  };

  return (
    <AppShell>
      <div className="p-8 max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black text-white flex items-center gap-2">
              <FileText className="w-6 h-6 text-emerald-400" />
              <span>WhatsApp Message Templates</span>
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Create and manage Meta-approved message templates required for outside 24h customer window
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={handleSync}
              disabled={syncing}
              className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-750 border border-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-emerald-400 ${syncing ? "animate-spin" : ""}`} />
              <span>Sync with Meta</span>
            </button>
            <button
              onClick={() => setCreateModalOpen(true)}
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-lg transition"
            >
              <Plus className="w-4 h-4" />
              <span>Create Template</span>
            </button>
          </div>
        </div>

        {/* Meta Cloud API Rate Card / Pricing Overview */}
        <div className="p-4 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-slate-850 border border-slate-800 space-y-3 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-2.5">
            <div className="flex items-center gap-2">
              <Coins className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-bold text-white uppercase tracking-wider">
                Meta WhatsApp Cloud API Conversation Pricing (India +91 Official Rates)
              </span>
            </div>
            <span className="text-[11px] text-slate-400">
              Per 24-hour conversation window • Charged to your Meta WABA
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-slate-400">Utility</span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-blue-500/20 text-blue-300">UTILITY</span>
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="text-lg font-black text-white font-mono">₹0.35</span>
                <span className="text-[10px] text-slate-400">/ msg</span>
                <span className="text-[9px] text-slate-400 font-mono">(~$0.0042)</span>
              </div>
              <p className="text-[10px] text-slate-400 leading-tight">
                Order updates, tracking, alerts, hello_world
              </p>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-slate-400">Marketing</span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-purple-500/20 text-purple-300">MARKETING</span>
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="text-lg font-black text-amber-400 font-mono">₹0.88</span>
                <span className="text-[10px] text-slate-400">/ msg</span>
                <span className="text-[9px] text-slate-400 font-mono">(~$0.0107)</span>
              </div>
              <p className="text-[10px] text-slate-400 leading-tight">
                Promotions, discounts, offers, announcements
              </p>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-slate-400">Authentication</span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500/20 text-emerald-300">AUTH</span>
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="text-lg font-black text-white font-mono">₹0.15</span>
                <span className="text-[10px] text-slate-400">/ msg</span>
                <span className="text-[9px] text-slate-400 font-mono">(~$0.0018)</span>
              </div>
              <p className="text-[10px] text-slate-400 leading-tight">
                OTP security codes, verification, account access
              </p>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-slate-400">Service Care</span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-teal-500/20 text-teal-300">FREE</span>
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="text-lg font-black text-emerald-400 font-mono">₹0.00</span>
                <span className="text-[10px] text-emerald-400">/ Free</span>
              </div>
              <p className="text-[10px] text-slate-400 leading-tight">
                Inbound customer queries inside 24-hr session
              </p>
            </div>
          </div>
        </div>

        {/* Templates Grid & Live WhatsApp Phone Mockup */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left 2 Columns: Template List */}
          <div className="lg:col-span-2 space-y-3">
            {templates.map((tpl) => {
              const isSelected = selectedTpl?.id === tpl.id;
              const costInr = tpl.estimated_cost_inr ?? (tpl.category === "MARKETING" ? 0.88 : tpl.category === "AUTHENTICATION" ? 0.15 : 0.35);
              const costUsd = tpl.estimated_cost_usd ?? (tpl.category === "MARKETING" ? 0.0107 : tpl.category === "AUTHENTICATION" ? 0.0018 : 0.0042);
              return (
                <div
                  key={tpl.id}
                  onClick={() => setSelectedTpl(tpl)}
                  className={`p-5 rounded-2xl bg-slate-900 border transition cursor-pointer flex items-start justify-between gap-4 ${
                    isSelected
                      ? "border-emerald-500/80 shadow-lg shadow-emerald-950/40"
                      : "border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <h3 className="font-bold text-sm text-white font-mono">{tpl.name}</h3>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 uppercase">
                        {tpl.category}
                      </span>
                      <span className="text-[10px] text-slate-500 font-mono">
                        {tpl.language}
                      </span>

                      {/* Cost Badge */}
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-400/10 text-amber-300 border border-amber-400/30 font-mono">
                        <Coins className="w-3 h-3 text-amber-400" />
                        <span>₹{costInr.toFixed(2)} / send</span>
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed bg-slate-950 p-2.5 rounded-lg border border-slate-850">
                      {tpl.body_text}
                    </p>

                    <div className="flex items-center justify-between text-[10px] text-slate-500">
                      {tpl.footer_text ? (
                        <p>Footer: {tpl.footer_text}</p>
                      ) : (
                        <p>No footer</p>
                      )}
                      <span className="text-slate-400 font-mono">
                        Approx: ${costUsd.toFixed(4)} USD per recipient
                      </span>
                    </div>
                  </div>

                  <div className="flex flex-col items-end justify-between self-stretch">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase flex items-center gap-1 ${
                        tpl.status === "APPROVED"
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                          : tpl.status === "PENDING"
                          ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                          : "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                      }`}
                    >
                      {tpl.status === "APPROVED" && <CheckCircle2 className="w-3 h-3" />}
                      {tpl.status === "PENDING" && <Clock className="w-3 h-3" />}
                      <span>{tpl.status}</span>
                    </span>

                    <span className="text-[11px] text-slate-500 flex items-center gap-1 hover:text-emerald-400 transition">
                      <span>Preview</span>
                      <ChevronRight className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right Column: Realistic Live WhatsApp Phone Mockup Preview */}
          <div className="p-6 rounded-3xl bg-slate-900 border border-slate-800 flex flex-col items-center">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase mb-4 self-start">
              <Eye className="w-4 h-4 text-emerald-400" />
              <span>Live WhatsApp Client Preview</span>
            </div>

            {selectedTpl ? (
              <>
                <div className="w-[300px] h-[500px] bg-[#0b141a] rounded-[36px] border-[6px] border-slate-800 shadow-2xl flex flex-col overflow-hidden relative">
                  {/* Speaker Notch */}
                  <div className="h-5 bg-slate-800 flex items-center justify-center">
                    <div className="w-12 h-1 bg-slate-700 rounded-full" />
                  </div>

                  {/* WhatsApp Chat Header */}
                  <div className="px-3 py-2 bg-[#1f2c34] flex items-center gap-2.5 border-b border-slate-800">
                    <div className="w-7 h-7 rounded-full bg-emerald-600 flex items-center justify-center font-bold text-xs text-white">
                      A
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-white">ALLSTREAK Verified</p>
                      <p className="text-[9px] text-emerald-400">Official Business Account</p>
                    </div>
                  </div>

                  {/* Chat Wallpaper & Preview Bubble */}
                  <div className="flex-1 whatsapp-bg p-3 flex flex-col justify-end">
                    <div className="bg-[#005c4b] text-white rounded-2xl rounded-tr-none p-3 text-xs shadow-md space-y-1.5">
                      {selectedTpl.header_content && (
                        <p className="font-bold text-xs text-emerald-200 border-b border-emerald-700/50 pb-1">
                          {renderPreviewText(selectedTpl.header_content)}
                        </p>
                      )}
                      <p className="whitespace-pre-line leading-relaxed text-[11px]">
                        {renderPreviewText(selectedTpl.body_text)}
                      </p>
                      {selectedTpl.footer_text && (
                        <p className="text-[9px] text-slate-300/80 pt-1">
                          {selectedTpl.footer_text}
                        </p>
                      )}
                      <div className="flex justify-end text-[8px] text-slate-300">
                        12:30 PM
                      </div>
                    </div>
                  </div>
                </div>

                {/* Pricing summary badge below phone preview */}
                <div className="mt-4 w-[300px] p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1 text-center shadow-lg">
                  <div className="flex items-center justify-center gap-1.5 text-xs font-bold text-amber-300 font-mono">
                    <Coins className="w-3.5 h-3.5 text-amber-400" />
                    <span>
                      Est. Meta Charge: ₹
                      {(
                        selectedTpl.estimated_cost_inr ??
                        (selectedTpl.category === "MARKETING" ? 0.88 : selectedTpl.category === "AUTHENTICATION" ? 0.15 : 0.35)
                      ).toFixed(2)}{" "}
                      / send
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-400">
                    Category: <span className="text-slate-300 font-semibold">{selectedTpl.category}</span> • 24h window
                    initiated upon customer receipt.
                  </p>
                </div>
              </>
            ) : (
              <div className="text-slate-500 text-xs">Select a template to view mockup</div>
            )}
          </div>
        </div>

        {/* Create Template Modal */}
        {createModalOpen && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
              <h2 className="text-base font-bold text-white">Create WhatsApp Template</h2>

              <form onSubmit={handleCreateTemplate} className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Template Name (lowercase, underscores only)
                  </label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value.toLowerCase().replace(/\s+/g, "_"))}
                    placeholder="e.g. shipping_notification"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Category
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value as TemplateCategory)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="UTILITY">UTILITY</option>
                    <option value="MARKETING">MARKETING</option>
                    <option value="AUTHENTICATION">AUTHENTICATION</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Body Text with Variables (&#123;&#123;1&#125;&#125;, &#123;&#123;2&#125;&#125;)
                  </label>
                  <textarea
                    rows={3}
                    required
                    value={bodyText}
                    onChange={(e) => setBodyText(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Footer Text (Optional)
                  </label>
                  <input
                    type="text"
                    value={footerText}
                    onChange={(e) => setFooterText(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                {/* Real-time Meta Cost Estimator */}
                <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Coins className="w-4 h-4 text-amber-400" />
                    <div>
                      <span className="text-xs font-semibold text-white block">
                        Estimated Meta Conversation Cost:
                      </span>
                      <span className="text-[11px] text-slate-400">
                        {category === "MARKETING"
                          ? "Promotional & Marketing rate"
                          : category === "AUTHENTICATION"
                          ? "Auth OTP & Security rate"
                          : "Utility transactional rate"}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-black text-amber-400 font-mono">
                      {category === "MARKETING"
                        ? "₹0.88 / send"
                        : category === "AUTHENTICATION"
                        ? "₹0.15 / send"
                        : "₹0.35 / send"}
                    </span>
                    <span className="block text-[10px] text-slate-500 font-mono">
                      {category === "MARKETING"
                        ? "(~$0.0107 USD)"
                        : category === "AUTHENTICATION"
                        ? "(~$0.0018 USD)"
                        : "(~$0.0042 USD)"}
                    </span>
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-4 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setCreateModalOpen(false)}
                    className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-750"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold shadow-lg"
                  >
                    Submit for Approval
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
