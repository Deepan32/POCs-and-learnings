"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import {
  Zap,
  Plus,
  Trash2,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  ShieldAlert,
  Edit2,
  Tag,
  Headphones,
  Users,
} from "lucide-react";
import { ApiClient } from "@/lib/api";
import { AutomationRule } from "@/types";

export default function AutomationsPage() {
  const [rules, setRules] = useState<AutomationRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);

  // New Rule Form State
  const [name, setName] = useState("");
  const [priority, setPriority] = useState(10);
  const [triggerKeyword, setTriggerKeyword] = useState("");
  const [matchType, setMatchType] = useState("contains");
  const [contactIsNew, setContactIsNew] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [buttonsStr, setButtonsStr] = useState("Sales, Support, Pricing, Talk to Human");
  const [createLead, setCreateLead] = useState(true);
  const [addTag, setAddTag] = useState("WhatsApp Lead");
  const [isHandover, setIsHandover] = useState(false);

  const fetchRules = async () => {
    setLoading(true);
    try {
      const data = await ApiClient.getRules();
      setRules(data);
    } catch (err) {
      console.error("Failed to load rules:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const buttonsArr = buttonsStr
        .split(",")
        .map((b) => b.trim())
        .filter(Boolean);

      await ApiClient.createRule({
        name,
        priority: Number(priority),
        trigger_keyword: triggerKeyword,
        match_type: matchType,
        condition_contact_is_new: contactIsNew,
        action_reply_text: replyText,
        action_buttons_json: JSON.stringify(buttonsArr),
        action_create_lead: createLead,
        action_add_tag: addTag || null,
        action_handover: isHandover,
      });

      setModalOpen(false);
      fetchRules();
    } catch (err) {
      console.error(err);
      alert("Failed to create rule");
    }
  };

  return (
    <AppShell>
      <div className="p-8 max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black text-white flex items-center gap-2">
              <Zap className="w-6 h-6 text-emerald-400" />
              <span>No-Code Automation Rules</span>
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Configure WHEN / IF / THEN triggers with priority order and conflict prevention
            </p>
          </div>

          <button
            onClick={() => setModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-lg transition"
          >
            <Plus className="w-4 h-4" />
            <span>Create Rule</span>
          </button>
        </div>

        {/* Priority Engine Info Banner */}
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>
              <strong>Priority Engine Active:</strong> Rules execute sequentially by priority rank
              (1 is highest priority). Conflicting responses are suppressed automatically.
            </span>
          </div>
          <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
            Loop Safe
          </span>
        </div>

        {/* Rules Table / Cards */}
        <div className="space-y-3">
          {rules.map((rule) => {
            let parsedButtons: string[] = [];
            if (rule.action_buttons_json) {
              try {
                parsedButtons = JSON.parse(rule.action_buttons_json);
              } catch {}
            }

            return (
              <div
                key={rule.id}
                className="p-5 rounded-2xl bg-slate-900 border border-slate-800/80 hover:border-slate-700 transition flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-2">
                  <div className="flex items-center gap-2.5">
                    <span className="w-6 h-6 rounded-md bg-slate-800 font-mono font-bold text-xs flex items-center justify-center text-emerald-400 border border-slate-700">
                      P{rule.priority}
                    </span>
                    <h3 className="font-bold text-sm text-white">{rule.name}</h3>
                    {rule.action_handover && (
                      <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 text-[10px] font-bold">
                        Human Handover
                      </span>
                    )}
                  </div>

                  {/* Flow Grammar */}
                  <div className="flex flex-wrap items-center gap-2 text-xs">
                    <span className="text-slate-400 font-medium">WHEN customer sends</span>
                    <code className="px-2 py-0.5 rounded bg-slate-950 text-emerald-300 font-mono border border-slate-800">
                      &ldquo;{rule.trigger_keyword}&rdquo; ({rule.match_type})
                    </code>
                    {rule.condition_contact_is_new && (
                      <>
                        <span className="text-amber-400 font-medium">IF</span>
                        <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                          New Contact
                        </span>
                      </>
                    )}
                    <span className="text-slate-400 font-medium">THEN</span>
                    <span className="text-slate-200">Reply & Show Buttons</span>
                  </div>

                  {/* Action Badges */}
                  <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px]">
                    {rule.action_create_lead && (
                      <span className="flex items-center gap-1 text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                        <Users className="w-3 h-3" />
                        <span>Auto-Create Lead (+20 Score)</span>
                      </span>
                    )}
                    {rule.action_add_tag && (
                      <span className="flex items-center gap-1 text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">
                        <Tag className="w-3 h-3" />
                        <span>Tag: {rule.action_add_tag}</span>
                      </span>
                    )}
                    {parsedButtons.length > 0 && (
                      <span className="text-slate-400">
                        Buttons: {parsedButtons.map((b) => `[${b}]`).join(" ")}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end md:self-center">
                  <span
                    className={`text-xs px-2.5 py-1 rounded-full font-bold ${
                      rule.is_active
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : "bg-slate-800 text-slate-500"
                    }`}
                  >
                    {rule.is_active ? "ACTIVE" : "PAUSED"}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Create Rule Modal */}
        {modalOpen && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
              <h2 className="text-base font-bold text-white">Create Automation Rule</h2>

              <form onSubmit={handleCreateRule} className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Rule Name
                  </label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Sales Inquiry Responder"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Trigger Keyword
                    </label>
                    <input
                      type="text"
                      required
                      value={triggerKeyword}
                      onChange={(e) => setTriggerKeyword(e.target.value)}
                      placeholder="e.g. sales"
                      className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">
                      Priority Rank (1 = Highest)
                    </label>
                    <input
                      type="number"
                      required
                      value={priority}
                      onChange={(e) => setPriority(Number(e.target.value))}
                      className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Reply Text Message
                  </label>
                  <textarea
                    rows={3}
                    required
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    placeholder="Thank you for reaching out! A specialist will contact you shortly."
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Interactive Quick Reply Buttons (Comma separated)
                  </label>
                  <input
                    type="text"
                    value={buttonsStr}
                    onChange={(e) => setButtonsStr(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div className="flex items-center gap-6 pt-2 text-xs">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={createLead}
                      onChange={(e) => setCreateLead(e.target.checked)}
                      className="rounded border-slate-800 bg-slate-950 text-emerald-500"
                    />
                    <span>Auto-create Lead in CRM</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={isHandover}
                      onChange={(e) => setIsHandover(e.target.checked)}
                      className="rounded border-slate-800 bg-slate-950 text-purple-500"
                    />
                    <span>Switch to Human Handover</span>
                  </label>
                </div>

                <div className="flex justify-end gap-2 pt-4 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setModalOpen(false)}
                    className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-750"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold shadow-lg"
                  >
                    Save Rule
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
