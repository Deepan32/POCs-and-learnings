"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import {
  Search,
  Bot,
  Sparkles,
  Headphones,
  Check,
  CheckCheck,
  Send,
  Clock,
  AlertTriangle,
  User,
  Tag as TagIcon,
  Briefcase,
  ChevronRight,
  RotateCcw,
  CheckCircle2,
  Phone,
  Mail,
  Calendar,
  FileText,
  ShieldAlert,
  Loader2,
  RefreshCw,
  Coins,
  Plus,
  UserPlus,
  MessageSquarePlus,
} from "lucide-react";
import { ApiClient } from "@/lib/api";
import { Conversation, Message, ConversationMode, Lead } from "@/types";

export default function TeamInboxPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConv, setSelectedConv] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeTab, setActiveTab] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [templates, setTemplates] = useState<any[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>("");
  const [aiSuggestions, setAiSuggestions] = useState<any[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);

  // Manual New WhatsApp Chat State
  const [newChatModalOpen, setNewChatModalOpen] = useState(false);
  const [manualPhone, setManualPhone] = useState("");
  const [manualName, setManualName] = useState("");
  const [manualMsgType, setManualMsgType] = useState<"TEMPLATE" | "CUSTOM" | "EMPTY">("TEMPLATE");
  const [manualTemplate, setManualTemplate] = useState("");
  const [manualCustomMsg, setManualCustomMsg] = useState("Hello! Welcome to ALLSTREAK. How can we help you today?");
  const [manualMode, setManualMode] = useState<ConversationMode>("HUMAN");
  const [startingChat, setStartingChat] = useState(false);

  // Load conversations with automatic background sync
  const fetchConvs = React.useCallback(async (showLoading = true) => {
    if (showLoading) setLoading(true);
    try {
      const isSpecialTab = ["🔥 hot leads", "💬 warm", "⚠️ attention"].includes(activeTab);
      const data = await ApiClient.getConversations({
        tab: !isSpecialTab && activeTab !== "all" ? activeTab : undefined,
        search: searchQuery || undefined,
      });
      setConversations(data);
      if (data.length > 0) {
        setSelectedConv((prev) => {
          if (!prev) return data[0];
          const updated = data.find((c) => c.id === prev.id);
          return updated || prev;
        });
      }
    } catch (err) {
      console.error("Failed to load conversations:", err);
    } finally {
      if (showLoading) setLoading(false);
    }
  }, [activeTab, searchQuery]);

  useEffect(() => {
    fetchConvs(true);
    const interval = setInterval(() => fetchConvs(false), 3000);
    return () => clearInterval(interval);
  }, [fetchConvs]);


  // Load AI Suggestions for selected conversation
  useEffect(() => {
    if (!selectedConv) {
      setAiSuggestions([]);
      return;
    }
    setLoadingSuggestions(true);
    ApiClient.getAISuggestions(selectedConv.id)
      .then((res) => {
        if (res && res.suggestions) {
          setAiSuggestions(res.suggestions);
        }
      })
      .catch((err) => {
        console.warn("AI suggestions fetch notice:", err);
      })
      .finally(() => setLoadingSuggestions(false));
  }, [selectedConv]);

  // Load templates
  useEffect(() => {
    async function loadTemplates() {
      try {
        const tpls = await ApiClient.getTemplates();
        setTemplates(tpls);
      } catch (err) {
        console.error("Failed to load templates:", err);
      }
    }
    loadTemplates();
  }, []);

  // Load messages for selected conversation
  useEffect(() => {
    if (!selectedConv) return;
    async function fetchMsgs() {
      try {
        const msgs = await ApiClient.getMessages(selectedConv!.id);
        setMessages(msgs);
      } catch (err) {
        console.error("Failed to load messages:", err);
      }
    }
    fetchMsgs();

    // Auto-poll or WebSocket heartbeat can also trigger
    const interval = setInterval(fetchMsgs, 4000);
    return () => clearInterval(interval);
  }, [selectedConv]);

  const handleSendMessage = async () => {
    if (!selectedConv || !inputText.trim()) return;
    setSending(true);

    try {
      if (selectedTemplate) {
        // Send Template message
        await ApiClient.sendTemplate(selectedConv.id, {
          template_name: selectedTemplate,
          variable_values: {
            "1": selectedConv.contact?.name || "Valued Customer",
            "2": "#28492",
          },
        });
        setSelectedTemplate("");
      } else {
        // Send Regular Message
        await ApiClient.sendMessage(selectedConv.id, {
          body: inputText,
          message_type: "TEXT",
        });
      }
      setInputText("");
      // Refresh messages
      const msgs = await ApiClient.getMessages(selectedConv.id);
      setMessages(msgs);
    } catch (err: any) {
      alert(err.message || "Failed to send message");
    } finally {
      setSending(false);
    }
  };

  const handleHandover = async () => {
    if (!selectedConv) return;
    try {
      const updated = await ApiClient.triggerHandover(
        selectedConv.id,
        "Manual takeover by agent from Team Inbox"
      );
      setSelectedConv(updated);
      setConversations((prev) =>
        prev.map((c) => (c.id === updated.id ? updated : c))
      );
    } catch (err) {
      console.error(err);
    }
  };

  const handleReturnToBot = async () => {
    if (!selectedConv) return;
    try {
      const updated = await ApiClient.returnToAutomation(selectedConv.id, "BOT");
      setSelectedConv(updated);
      setConversations((prev) =>
        prev.map((c) => (c.id === updated.id ? updated : c))
      );
    } catch (err) {
      console.error(err);
    }
  };

  const handleResolve = async () => {
    if (!selectedConv) return;
    try {
      const updated = await ApiClient.resolveConversation(selectedConv.id);
      setSelectedConv(updated);
      setConversations((prev) =>
        prev.map((c) => (c.id === updated.id ? updated : c))
      );
    } catch (err) {
      console.error(err);
    }
  };

  const handleStartNewChat = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleaned = manualPhone.replace(/\D/g, "");
    if (!cleaned || cleaned.length < 7) {
      alert("Please enter a valid WhatsApp phone number with country code.");
      return;
    }
    setStartingChat(true);
    try {
      const conv = await ApiClient.startConversation({
        phone: manualPhone.trim(),
        name: manualName.trim() || undefined,
        initial_message: manualMsgType === "CUSTOM" ? manualCustomMsg.trim() : undefined,
        template_name: manualMsgType === "TEMPLATE" ? (manualTemplate || (templates.length > 0 ? templates[0].name : undefined)) : undefined,
        mode: manualMode,
      });

      setNewChatModalOpen(false);
      setManualPhone("");
      setManualName("");

      // Refresh and select
      await fetchConvs(false);
      setSelectedConv(conv);
      const msgs = await ApiClient.getMessages(conv.id);
      setMessages(msgs);
    } catch (err: any) {
      alert(err.message || "Failed to start conversation with this number");
    } finally {
      setStartingChat(false);
    }
  };

  const getModeBadge = (mode: ConversationMode) => {
    if (mode === "HUMAN") {
      return (
        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30 flex items-center gap-1">
          <Headphones className="w-3 h-3" />
          <span>HUMAN AGENT</span>
        </span>
      );
    } else if (mode === "AI") {
      return (
        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30 flex items-center gap-1">
          <Sparkles className="w-3 h-3" />
          <span>AI AGENT</span>
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
        <Bot className="w-3 h-3" />
        <span>STREAK BOT</span>
      </span>
    );
  };

  return (
    <AppShell>
      <div className="h-full flex overflow-hidden bg-slate-950">
        {/* LEFT PANEL: Conversation List */}
        <div className="w-80 border-r border-slate-800 bg-slate-950 flex flex-col h-full flex-shrink-0">
          {/* Header & Search */}
          <div className="p-3.5 border-b border-slate-800 space-y-2.5">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-white font-mono tracking-tight flex items-center gap-1.5">
                <span>INBOX CHATS</span>
              </h2>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  {conversations.length} Active
                </span>
                <button
                  onClick={() => fetchConvs(true)}
                  className="p-1 rounded-lg bg-slate-850 hover:bg-slate-700 text-slate-300 hover:text-white transition"
                  title="Refresh conversations"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-emerald-400" : ""}`} />
                </button>
              </div>
            </div>

            {/* + New Chat (Manual Number) Action Button */}
            <button
              onClick={() => {
                setManualTemplate(templates.length > 0 ? templates[0].name : "");
                setNewChatModalOpen(true);
              }}
              className="w-full py-2 px-3 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-600 hover:from-emerald-500 hover:to-teal-500 text-slate-950 font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-950/40 transition"
            >
              <UserPlus className="w-4 h-4" />
              <span>+ Start New Chat (Add Number)</span>
            </button>

            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search name, phone, message..."
                className="w-full pl-8 pr-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
            </div>

            {/* Filter Tabs */}
            <div className="flex gap-1 overflow-x-auto pb-1 text-xs">
              {["all", "🔥 hot leads", "💬 warm", "⚠️ attention", "unread", "human", "ai"].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-2.5 py-1 rounded-md capitalize font-medium text-[11px] transition shrink-0 ${
                    activeTab === tab
                      ? "bg-emerald-500 text-slate-950 font-bold"
                      : "bg-slate-900 text-slate-400 hover:text-white"
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>

          {/* Conversations Thread List */}
          <div className="flex-1 overflow-y-auto divide-y divide-slate-850">
            {loading ? (
              <div className="p-8 text-center text-slate-500 text-xs flex flex-col items-center gap-2">
                <Loader2 className="w-5 h-5 text-emerald-400 animate-spin" />
                <span>Syncing inbox...</span>
              </div>
            ) : conversations.filter((c) => {
                if (activeTab === "🔥 hot leads") {
                  return (c as any).lead && ((c as any).lead.status === "QUALIFIED" || ((c as any).lead.score || 0) >= 50);
                }
                if (activeTab === "💬 warm") {
                  return (c as any).lead && (c as any).lead.status === "INQUIRY";
                }
                if (activeTab === "⚠️ attention") {
                  return !c.is_window_open || c.unread_count > 0;
                }
                return true;
              }).length === 0 ? (
              <div className="p-8 text-center text-slate-500 text-xs">
                No conversations found in this view.
              </div>
            ) : (
              conversations.filter((c) => {
                if (activeTab === "🔥 hot leads") {
                  return (c as any).lead && ((c as any).lead.status === "QUALIFIED" || ((c as any).lead.score || 0) >= 50);
                }
                if (activeTab === "💬 warm") {
                  return (c as any).lead && (c as any).lead.status === "INQUIRY";
                }
                if (activeTab === "⚠️ attention") {
                  return !c.is_window_open || c.unread_count > 0;
                }
                return true;
              }).map((c) => {
                const isSelected = selectedConv?.id === c.id;
                return (
                  <div
                    key={c.id}
                    onClick={() => setSelectedConv(c)}
                    className={`p-3 cursor-pointer transition flex items-start gap-3 relative ${
                      isSelected
                        ? "bg-slate-900 border-l-4 border-emerald-500"
                        : "hover:bg-slate-900/60"
                    }`}
                  >
                    <div className="w-9 h-9 rounded-full bg-slate-800 text-slate-200 border border-slate-700 flex items-center justify-center font-bold text-xs shrink-0">
                      {c.contact?.name ? c.contact.name[0].toUpperCase() : "W"}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-0.5">
                        <span className="font-semibold text-xs text-white truncate">
                          {c.contact?.name || c.contact?.phone}
                        </span>
                        <span className="text-[10px] text-slate-500 font-mono">
                          {c.last_message_at
                            ? new Date(c.last_message_at).toLocaleTimeString([], {
                                hour: "2-digit",
                                minute: "2-digit",
                              })
                            : ""}
                        </span>
                      </div>

                      <p className="text-[11px] text-slate-400 truncate mb-1">
                        {c.last_message_preview || "No message yet"}
                      </p>

                      <div className="flex items-center justify-between">
                        <span
                          className={`text-[9px] font-bold px-1.5 py-0.2 rounded uppercase ${
                            c.mode === "HUMAN"
                              ? "bg-purple-500/20 text-purple-300"
                              : c.mode === "AI"
                              ? "bg-blue-500/20 text-blue-300"
                              : "bg-emerald-500/20 text-emerald-300"
                          }`}
                        >
                          {c.mode}
                        </span>

                        {c.unread_count > 0 && (
                          <span className="w-4 h-4 rounded-full bg-emerald-500 text-slate-950 font-black text-[10px] flex items-center justify-center">
                            {c.unread_count}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* CENTER PANEL: Active Chat Thread */}
        {selectedConv ? (
          <div className="flex-1 flex flex-col h-full bg-[#0b141a] border-r border-slate-800 relative">
            {/* Chat Top Header */}
            <div className="h-16 px-4 bg-slate-900 border-b border-slate-800 flex items-center justify-between z-10">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-slate-800 text-white flex items-center justify-center font-bold text-sm">
                  {selectedConv.contact?.name ? selectedConv.contact.name[0] : "W"}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-white">
                      {selectedConv.contact?.name || selectedConv.contact?.phone}
                    </span>
                    {getModeBadge(selectedConv.mode)}
                  </div>
                  <p className="text-[11px] text-slate-400 font-mono">
                    {selectedConv.contact?.phone}
                  </p>
                </div>
              </div>

              {/* Handover & Resolution Buttons */}
              <div className="flex items-center gap-2">
                {selectedConv.mode !== "HUMAN" ? (
                  <button
                    onClick={handleHandover}
                    className="px-3 py-1.5 rounded-lg bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/40 text-purple-300 text-xs font-semibold flex items-center gap-1.5 transition"
                  >
                    <Headphones className="w-3.5 h-3.5" />
                    <span>Take Over as Human</span>
                  </button>
                ) : (
                  <button
                    onClick={handleReturnToBot}
                    className="px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-300 text-xs font-semibold flex items-center gap-1.5 transition"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Return to Automation</span>
                  </button>
                )}

                <button
                  onClick={handleResolve}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 border border-slate-700 text-xs font-medium flex items-center gap-1.5 transition"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Resolve</span>
                </button>
              </div>
            </div>

            {/* Meta 24-Hour Customer Window Banner */}
            <div
              className={`px-4 py-2 text-xs flex items-center justify-between border-b ${
                selectedConv.is_window_open
                  ? "bg-emerald-950/40 border-emerald-500/20 text-emerald-300"
                  : "bg-amber-950/40 border-amber-500/30 text-amber-300"
              }`}
            >
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                <span>
                  {selectedConv.is_window_open
                    ? "WhatsApp 24-Hour Customer Service Window: OPEN (Free-form messages allowed)"
                    : "WhatsApp Customer Window CLOSED: Approved Meta template required to message"}
                </span>
              </div>
              <span className="text-[10px] font-mono uppercase bg-black/40 px-2 py-0.5 rounded font-bold">
                {selectedConv.is_window_open ? "24h Active" : "Template Only"}
              </span>
            </div>

            {/* Message Thread Body */}
            <div className="flex-1 whatsapp-bg overflow-y-auto p-4 space-y-3">
              {messages.map((m) => {
                const isCustomer = m.direction === "INBOUND";
                return (
                  <div
                    key={m.id}
                    className={`flex flex-col ${isCustomer ? "items-start" : "items-end"}`}
                  >
                    <div
                      className={`max-w-[70%] rounded-2xl px-3.5 py-2.5 text-xs shadow-md relative ${
                        isCustomer
                          ? "bg-[#202c33] text-slate-100 rounded-tl-none"
                          : "bg-[#005c4b] text-white rounded-tr-none"
                      }`}
                    >
                      {/* Sender Origin Tag */}
                      {!isCustomer && (
                        <div className="flex items-center gap-1 text-[10px] font-bold text-emerald-300 mb-1">
                          {m.origin === "BOT" && <Bot className="w-3 h-3" />}
                          {m.origin === "AI" && <Sparkles className="w-3 h-3 text-blue-300" />}
                          {m.origin === "HUMAN" && (
                            <Headphones className="w-3 h-3 text-purple-300" />
                          )}
                          <span>
                            {m.origin === "HUMAN"
                              ? "Human Agent (Surya)"
                              : m.origin === "AI"
                              ? "Streak AI"
                              : "Bot Automation"}
                          </span>
                        </div>
                      )}

                      <p className="whitespace-pre-line leading-relaxed">{m.body}</p>

                      {/* Delivery Status & Time */}
                      <div className="flex items-center justify-end gap-1.5 mt-1 text-[10px] text-slate-400">
                        <span>
                          {new Date(m.created_at).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                        {!isCustomer && (
                          <span title={
                            m.status === "READ"
                              ? "Read by recipient"
                              : m.status === "DELIVERED"
                              ? "Delivered to WhatsApp"
                              : m.status === "SENT"
                              ? "Sent via Meta Graph API"
                              : m.status === "PENDING"
                              ? "Sending to WhatsApp..."
                              : "Delivery Failed"
                          }>
                            {m.status === "READ" ? (
                              <CheckCheck className="w-3.5 h-3.5 text-sky-400" />
                            ) : m.status === "DELIVERED" ? (
                              <CheckCheck className="w-3.5 h-3.5 text-slate-400" />
                            ) : m.status === "SENT" ? (
                              <Check className="w-3.5 h-3.5 text-slate-400" />
                            ) : m.status === "PENDING" ? (
                              <Clock className="w-3.5 h-3.5 text-amber-400/80 animate-pulse" />
                            ) : (
                              <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                            )}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Smart Composer */}
            <div className="p-3 bg-slate-900 border-t border-slate-800 space-y-2.5">
              {/* AI Suggestion Quick Chips */}
              {aiSuggestions.length > 0 && (
                <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
                  <span className="text-[10px] font-bold text-amber-400 flex items-center gap-1 shrink-0 bg-amber-400/10 px-2 py-1 rounded-md border border-amber-400/20">
                    <Sparkles className="w-3 h-3" />
                    <span>AI Suggest:</span>
                  </span>
                  {aiSuggestions.map((sug) => (
                    <button
                      key={sug.id}
                      onClick={() => setInputText(sug.text)}
                      title={sug.text}
                      className="px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-emerald-950/60 text-slate-300 hover:text-emerald-300 border border-slate-800 hover:border-emerald-500/40 text-[11px] font-medium transition truncate max-w-xs shrink-0 flex items-center gap-1.5 shadow-sm"
                    >
                      <span className="text-amber-400 text-[10px]">⚡</span>
                      <span className="truncate">{sug.label}</span>
                    </button>
                  ))}
                </div>
              )}

              {/* Template Selector Shortcut & Dynamic Cost Tracker */}
              {(() => {
                const activeTplObj = templates.find((t) => t.name === selectedTemplate);
                const costInr = activeTplObj
                  ? activeTplObj.estimated_cost_inr ?? (activeTplObj.category === "MARKETING" ? 0.88 : activeTplObj.category === "AUTHENTICATION" ? 0.15 : 0.35)
                  : 0;
                const costUsd = activeTplObj
                  ? activeTplObj.estimated_cost_usd ?? (activeTplObj.category === "MARKETING" ? 0.0107 : activeTplObj.category === "AUTHENTICATION" ? 0.0018 : 0.0042)
                  : 0;

                return (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between flex-wrap gap-2 text-xs">
                      <div className="flex items-center gap-2">
                        <span className="text-slate-400 flex items-center gap-1 font-medium">
                          <FileText className="w-3.5 h-3.5 text-purple-400" />
                          <span>Insert Template:</span>
                        </span>
                        <select
                          value={selectedTemplate}
                          onChange={(e) => {
                            setSelectedTemplate(e.target.value);
                            if (e.target.value) {
                              setInputText(`[Template: ${e.target.value}]`);
                            }
                          }}
                          className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
                        >
                          <option value="">None (Free-form text)</option>
                          {templates.map((t) => (
                            <option key={t.id} value={t.name}>
                              {t.name} ({t.category})
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Live Cost Pill */}
                      {activeTplObj ? (
                        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-400/10 border border-amber-400/30 text-[11px] font-mono font-bold text-amber-300 shadow-sm">
                          <Coins className="w-3.5 h-3.5 text-amber-400" />
                          <span>Est. Send Cost: ₹{costInr.toFixed(2)}</span>
                          <span className="text-slate-400 font-normal text-[10px]">
                            ({activeTplObj.category} • ~${costUsd.toFixed(4)})
                          </span>
                        </div>
                      ) : selectedConv.is_window_open ? (
                        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-[11px] font-mono text-emerald-400">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                          <span>Est. Meta Cost: ₹0.00 (Free 24h Window)</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-rose-500/10 border border-rose-500/20 text-[11px] font-mono text-rose-400">
                          <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                          <span>Window Closed: Select Template</span>
                        </div>
                      )}
                    </div>

                    {/* Input Area */}
                    <div className="flex items-center gap-2">
                      <textarea
                        rows={2}
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" && !e.shiftKey) {
                            e.preventDefault();
                            handleSendMessage();
                          }
                        }}
                        placeholder={
                          selectedConv.is_window_open
                            ? "Type an agent reply (Enter to send, Shift+Enter for newline)..."
                            : "Window closed. Select a template above to message this customer..."
                        }
                        className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 resize-none"
                      />
                      <button
                        onClick={handleSendMessage}
                        disabled={sending || !inputText.trim()}
                        className="h-10 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-slate-950 font-bold text-xs flex items-center gap-2 transition shadow-lg"
                      >
                        {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                        <span>Send</span>
                      </button>
                    </div>

                    {/* Cost transparency helper */}
                    <div className="flex items-center justify-between text-[10px] text-slate-500 px-1 font-mono">
                      <span>
                        {activeTplObj
                          ? `Meta Cloud API billing rate: ₹${costInr.toFixed(2)} INR for 24h ${activeTplObj.category.toLowerCase()} conversation.`
                          : selectedConv.is_window_open
                          ? "Free customer-care response inside active 24-hour service window."
                          : "Outside 24-hour service window. Meta requires an approved template to reach customer."}
                      </span>
                      <span>
                        {activeTplObj ? `Template: ${activeTplObj.name}` : "Free-form Response"}
                      </span>
                    </div>
                  </div>
                );
              })()}
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-slate-500 text-xs">
            Select a conversation to inspect thread.
          </div>
        )}

        {/* RIGHT PANEL: Customer & Lead 360 Profile */}
        {selectedConv && (
          <div className="w-80 border-l border-slate-800 bg-slate-950 flex flex-col h-full overflow-y-auto p-4 space-y-6 flex-shrink-0">
            {/* Customer Avatar & Quick Actions */}
            <div className="text-center pb-4 border-b border-slate-800">
              <div className="w-16 h-16 mx-auto rounded-full bg-slate-800 text-white font-bold text-xl flex items-center justify-center border border-slate-700 mb-2">
                {selectedConv.contact?.name ? selectedConv.contact.name[0] : "W"}
              </div>
              <h3 className="font-bold text-sm text-white">
                {selectedConv.contact?.name || "WhatsApp Contact"}
              </h3>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                {selectedConv.contact?.phone}
              </p>
            </div>

            {/* Lead CRM Information */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Briefcase className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Lead Score & Status</span>
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Lead Score:</span>
                  <div className="flex items-center gap-1.5">
                    <div className="w-16 bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div className="bg-emerald-400 h-full rounded-full" style={{ width: "85%" }} />
                    </div>
                    <span className="font-mono font-bold text-xs text-emerald-400">85/100</span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Pipeline Stage:</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">
                    QUALIFIED
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Deal Value:</span>
                  <span className="font-mono font-bold text-xs text-white">₹12,000</span>
                </div>
              </div>
            </div>

            {/* Contact Tags */}
            <div className="space-y-2">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <TagIcon className="w-3.5 h-3.5 text-blue-400" />
                <span>Tags</span>
              </span>
              <div className="flex flex-wrap gap-1.5">
                <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                  Hot Lead
                </span>
                <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  Pricing Inquiry
                </span>
              </div>
            </div>

            {/* Handover Timeline & Reason */}
            {selectedConv.handover_reason && (
              <div className="p-3.5 rounded-xl bg-purple-950/30 border border-purple-500/30 space-y-1.5 text-xs">
                <span className="font-bold text-purple-300 flex items-center gap-1.5">
                  <Headphones className="w-3.5 h-3.5" />
                  <span>Handover Reason</span>
                </span>
                <p className="text-slate-300 text-[11px] leading-relaxed">
                  {selectedConv.handover_reason}
                </p>
                {selectedConv.handover_at && (
                  <p className="text-[10px] text-purple-400 font-mono pt-1">
                    {new Date(selectedConv.handover_at).toLocaleString()}
                  </p>
                )}
              </div>
            )}
          </div>
        )}

        {/* Start New WhatsApp Conversation (Manual Number) Modal */}
        {newChatModalOpen && (
          <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-5">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-500/30">
                    <UserPlus className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="text-base font-bold text-white">Start New WhatsApp Chat</h2>
                    <p className="text-[11px] text-slate-400">
                      Enter any WhatsApp number manually to initiate a conversation
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setNewChatModalOpen(false)}
                  className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 text-xs font-bold"
                >
                  ✕
                </button>
              </div>

              <form onSubmit={handleStartNewChat} className="space-y-4">
                {/* Phone Number Input */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center justify-between">
                    <span>WhatsApp Phone Number (with Country Code) *</span>
                    <span className="text-[10px] text-slate-500 font-normal">e.g. 919876543210</span>
                  </label>
                  <div className="relative flex items-center">
                    <div className="absolute left-3 flex items-center gap-1.5 text-xs font-bold text-slate-400 font-mono border-r border-slate-800 pr-2.5">
                      <span>📱</span>
                      <span>+</span>
                    </div>
                    <input
                      type="tel"
                      required
                      value={manualPhone}
                      onChange={(e) => setManualPhone(e.target.value)}
                      placeholder="91 98765 43210"
                      className="w-full pl-14 pr-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                  <p className="text-[10px] text-slate-500 mt-1">
                    India (+91) or International country code. Leading zeros or spaces are auto-formatted.
                  </p>
                </div>

                {/* Contact Name Input */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Customer / Business Name (Optional)
                  </label>
                  <input
                    type="text"
                    value={manualName}
                    onChange={(e) => setManualName(e.target.value)}
                    placeholder="e.g. Rahul Sharma, Surya Jewels"
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                {/* Initial Message Type Selection */}
                <div className="space-y-2">
                  <label className="block text-xs font-semibold text-slate-300">
                    Initial Outbound Message
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      type="button"
                      onClick={() => setManualMsgType("TEMPLATE")}
                      className={`p-2.5 rounded-xl border text-xs font-semibold flex flex-col items-center gap-1 transition ${
                        manualMsgType === "TEMPLATE"
                          ? "bg-emerald-950/60 border-emerald-500 text-emerald-300 shadow-md"
                          : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                      }`}
                    >
                      <FileText className="w-3.5 h-3.5 text-purple-400" />
                      <span className="text-[11px]">Template</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setManualMsgType("CUSTOM")}
                      className={`p-2.5 rounded-xl border text-xs font-semibold flex flex-col items-center gap-1 transition ${
                        manualMsgType === "CUSTOM"
                          ? "bg-emerald-950/60 border-emerald-500 text-emerald-300 shadow-md"
                          : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                      }`}
                    >
                      <Send className="w-3.5 h-3.5 text-blue-400" />
                      <span className="text-[11px]">Custom Text</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setManualMsgType("EMPTY")}
                      className={`p-2.5 rounded-xl border text-xs font-semibold flex flex-col items-center gap-1 transition ${
                        manualMsgType === "EMPTY"
                          ? "bg-emerald-950/60 border-emerald-500 text-emerald-300 shadow-md"
                          : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                      }`}
                    >
                      <MessageSquarePlus className="w-3.5 h-3.5 text-amber-400" />
                      <span className="text-[11px]">Open Only</span>
                    </button>
                  </div>

                  {/* Template Picker */}
                  {manualMsgType === "TEMPLATE" && (
                    <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-slate-400 font-medium">Select Approved Template:</span>
                        {manualTemplate && (
                          <span className="text-[10px] font-mono font-bold text-amber-300 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/30">
                            Est. ₹
                            {(
                              templates.find((t) => t.name === manualTemplate)?.estimated_cost_inr ??
                              (templates.find((t) => t.name === manualTemplate)?.category === "MARKETING" ? 0.88 : 0.35)
                            ).toFixed(2)}{" "}
                            / send
                          </span>
                        )}
                      </div>
                      <select
                        value={manualTemplate}
                        onChange={(e) => setManualTemplate(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
                      >
                        {templates.map((t) => (
                          <option key={t.id} value={t.name}>
                            {t.name} ({t.category}) — ₹{t.estimated_cost_inr ?? (t.category === "MARKETING" ? "0.88" : "0.35")}
                          </option>
                        ))}
                      </select>
                      <p className="text-[10px] text-slate-500">
                        Meta-approved template initiates a fresh 24-hour customer conversation window.
                      </p>
                    </div>
                  )}

                  {/* Custom Message Text */}
                  {manualMsgType === "CUSTOM" && (
                    <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                      <label className="block text-xs text-slate-400 font-medium">
                        Initial Message Text:
                      </label>
                      <textarea
                        rows={2}
                        value={manualCustomMsg}
                        onChange={(e) => setManualCustomMsg(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500 resize-none"
                      />
                    </div>
                  )}
                </div>

                {/* Conversation Mode */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Initial Chat Mode
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => setManualMode("HUMAN")}
                      className={`p-2 rounded-xl border text-xs font-semibold flex items-center justify-center gap-1.5 transition ${
                        manualMode === "HUMAN"
                          ? "bg-purple-950/60 border-purple-500 text-purple-300"
                          : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                      }`}
                    >
                      <Headphones className="w-3.5 h-3.5" />
                      <span>Human Agent</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setManualMode("BOT")}
                      className={`p-2 rounded-xl border text-xs font-semibold flex items-center justify-center gap-1.5 transition ${
                        manualMode === "BOT"
                          ? "bg-emerald-950/60 border-emerald-500 text-emerald-300"
                          : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                      }`}
                    >
                      <Bot className="w-3.5 h-3.5" />
                      <span>Streak Bot</span>
                    </button>
                  </div>
                </div>

                {/* Buttons */}
                <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setNewChatModalOpen(false)}
                    className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-750 transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={startingChat || !manualPhone.trim()}
                    className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-lg transition"
                  >
                    {startingChat ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        <span>Starting Chat...</span>
                      </>
                    ) : (
                      <>
                        <Send className="w-3.5 h-3.5" />
                        <span>Start WhatsApp Chat</span>
                      </>
                    )}
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
