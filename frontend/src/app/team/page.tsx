"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import {
  Users,
  Plus,
  Shield,
  Mail,
  UserCheck,
  CheckCircle2,
  Trash2,
} from "lucide-react";
import { ApiClient } from "@/lib/api";

export default function TeamPage() {
  const [members, setMembers] = useState<any[]>([]);
  const [inviteModalOpen, setInviteModalOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("AGENT");

  const loadTeam = async () => {
    try {
      const data = await ApiClient.getTeam();
      setMembers(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadTeam();
  }, []);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await ApiClient.inviteTeamMember({
        email,
        full_name: fullName,
        role,
      });
      setInviteModalOpen(false);
      setEmail("");
      setFullName("");
      loadTeam();
    } catch (err) {
      console.error(err);
      alert("Failed to invite team member");
    }
  };

  return (
    <AppShell>
      <div className="p-8 max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black text-white flex items-center gap-2">
              <Users className="w-6 h-6 text-emerald-400" />
              <span>Team &amp; Role-Based Access Control</span>
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Manage workspace members, assign conversations, and configure Owner / Admin / Agent roles
            </p>
          </div>

          <button
            onClick={() => setInviteModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-lg transition"
          >
            <Plus className="w-4 h-4" />
            <span>Invite Agent</span>
          </button>
        </div>

        {/* Members List */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800 uppercase text-[10px] font-bold">
              <tr>
                <th className="p-4">Member</th>
                <th className="p-4">Email</th>
                <th className="p-4">Role</th>
                <th className="p-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {members.map((m) => (
                <tr key={m.id} className="hover:bg-slate-850/50 transition">
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-slate-800 text-emerald-400 font-bold flex items-center justify-center border border-slate-700">
                        {m.user?.full_name ? m.user.full_name[0] : "U"}
                      </div>
                      <span className="font-bold text-white text-xs">{m.user?.full_name}</span>
                    </div>
                  </td>
                  <td className="p-4 text-slate-300 font-mono">{m.user?.email}</td>
                  <td className="p-4">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                        m.role === "OWNER"
                          ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                          : m.role === "ADMIN"
                          ? "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                          : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                      }`}
                    >
                      {m.role}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="flex items-center gap-1 text-emerald-400 font-semibold">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Active</span>
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Invite Modal */}
        {inviteModalOpen && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
              <h2 className="text-base font-bold text-white">Invite Team Member</h2>

              <form onSubmit={handleInvite} className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Sarah Jenkins"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Work Email
                  </label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="agent@company.com"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Role
                  </label>
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="AGENT">AGENT (Chat, Handover, Manage Leads)</option>
                    <option value="ADMIN">ADMIN (Automations, Templates, Team)</option>
                  </select>
                </div>

                <div className="flex justify-end gap-2 pt-4 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setInviteModalOpen(false)}
                    className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-750"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold shadow-lg"
                  >
                    Send Invitation
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
