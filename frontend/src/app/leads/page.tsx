"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import {
  Users,
  Plus,
  ArrowRight,
  TrendingUp,
  DollarSign,
  User,
  Phone,
  Building,
  CheckCircle2,
  Clock,
  Sparkles,
  Search,
  Filter,
} from "lucide-react";
import { ApiClient } from "@/lib/api";
import { Lead, LeadStatus, LeadKanbanResponse } from "@/types";

export default function LeadsCRMPage() {
  const [kanban, setKanban] = useState<LeadKanbanResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [draggedLeadId, setDraggedLeadId] = useState<string | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);

  // New Lead Form State
  const [newName, setNewName] = useState("");
  const [newPhone, setNewPhone] = useState("+91");
  const [newCompany, setNewCompany] = useState("");
  const [newValue, setNewValue] = useState("15000");

  const loadKanban = async () => {
    setLoading(true);
    try {
      const data = await ApiClient.getLeadKanban();
      setKanban(data);
    } catch (err) {
      console.error("Failed to load kanban:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadKanban();
  }, []);

  const handleDragStart = (leadId: string) => {
    setDraggedLeadId(leadId);
  };

  const handleDrop = async (targetStage: LeadStatus) => {
    if (!draggedLeadId) return;

    try {
      await ApiClient.updateLeadStage(draggedLeadId, targetStage);
      await loadKanban();
    } catch (err) {
      console.error("Failed to update lead stage:", err);
    } finally {
      setDraggedLeadId(null);
    }
  };

  const handleCreateLead = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await ApiClient.createLead({
        name: newName,
        phone: newPhone,
        company: newCompany,
        value: Number(newValue),
        status: "NEW",
        score: 25,
      });
      setCreateModalOpen(false);
      setNewName("");
      setNewPhone("+91");
      setNewCompany("");
      loadKanban();
    } catch (err) {
      console.error(err);
      alert("Failed to create lead");
    }
  };

  return (
    <AppShell>
      <div className="h-full flex flex-col p-6 space-y-6 overflow-hidden bg-slate-950">
        {/* Top Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 flex-shrink-0">
          <div>
            <h1 className="text-2xl font-black text-white flex items-center gap-2">
              <Users className="w-6 h-6 text-emerald-400" />
              <span>Lead Pipeline CRM</span>
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Drag-and-drop WhatsApp lead opportunities, automated scoring (0-100), and stage tracking
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setCreateModalOpen(true)}
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-lg transition"
            >
              <Plus className="w-4 h-4" />
              <span>New Lead</span>
            </button>
          </div>
        </div>

        {/* Kanban Board Container */}
        <div className="flex-1 overflow-x-auto overflow-y-hidden pb-4">
          <div className="flex gap-4 h-full min-w-max">
            {kanban?.columns?.map((col) => (
              <div
                key={col.stage}
                onDragOver={(e) => e.preventDefault()}
                onDrop={() => handleDrop(col.stage)}
                className="w-80 bg-slate-900/80 border border-slate-800/80 rounded-2xl flex flex-col h-full shadow-lg overflow-hidden"
              >
                {/* Column Header */}
                <div className="p-3.5 border-b border-slate-800 bg-slate-900 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-xs text-white">{col.label}</span>
                    <span className="w-5 h-5 rounded-full bg-slate-800 text-emerald-400 font-mono text-[10px] font-bold flex items-center justify-center border border-slate-700">
                      {col.count}
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-400 font-semibold">
                    ₹{col.total_value.toLocaleString()}
                  </span>
                </div>

                {/* Column Card Drop Zone */}
                <div className="flex-1 p-2.5 overflow-y-auto space-y-2.5 bg-slate-950/40">
                  {col.leads.map((lead) => (
                    <div
                      key={lead.id}
                      draggable
                      onDragStart={() => handleDragStart(lead.id)}
                      className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-emerald-500/50 cursor-grab active:cursor-grabbing transition shadow-md group relative space-y-2.5"
                    >
                      {/* Name & Score Pill */}
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-xs text-white group-hover:text-emerald-300 transition">
                          {lead.name}
                        </span>
                        <div className="flex items-center gap-1 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                          <Sparkles className="w-3 h-3 text-emerald-400" />
                          <span className="font-mono text-[10px] font-bold text-emerald-400">
                            {lead.score}
                          </span>
                        </div>
                      </div>

                      {/* Company & Phone */}
                      <div className="space-y-1 text-[11px] text-slate-400">
                        {lead.company && (
                          <div className="flex items-center gap-1.5">
                            <Building className="w-3 h-3 text-slate-500" />
                            <span className="truncate">{lead.company}</span>
                          </div>
                        )}
                        <div className="flex items-center gap-1.5">
                          <Phone className="w-3 h-3 text-slate-500" />
                          <span className="font-mono">{lead.phone}</span>
                        </div>
                      </div>

                      {/* Notes / Deal Value */}
                      <div className="pt-2 border-t border-slate-850 flex items-center justify-between text-xs">
                        <span className="text-[10px] text-slate-500 uppercase font-semibold">
                          {lead.source}
                        </span>
                        <span className="font-mono font-bold text-emerald-400">
                          ₹{lead.value.toLocaleString()}
                        </span>
                      </div>
                    </div>
                  ))}

                  {col.leads.length === 0 && (
                    <div className="h-32 border border-dashed border-slate-800 rounded-xl flex items-center justify-center text-slate-600 text-[11px]">
                      Drop opportunities here
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Create Lead Modal */}
        {createModalOpen && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
              <h2 className="text-base font-bold text-white">Create New Lead</h2>

              <form onSubmit={handleCreateLead} className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Contact Name
                  </label>
                  <input
                    type="text"
                    required
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    placeholder="e.g. Ramesh Varma"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    WhatsApp Phone
                  </label>
                  <input
                    type="text"
                    required
                    value={newPhone}
                    onChange={(e) => setNewPhone(e.target.value)}
                    placeholder="+919876543210"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Company
                  </label>
                  <input
                    type="text"
                    value={newCompany}
                    onChange={(e) => setNewCompany(e.target.value)}
                    placeholder="e.g. Acme Tech"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Estimated Deal Value (INR)
                  </label>
                  <input
                    type="number"
                    value={newValue}
                    onChange={(e) => setNewValue(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
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
                    Create Lead
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
