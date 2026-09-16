"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import {
  UserCheck,
  Search,
  Plus,
  Phone,
  Mail,
  MessageSquare,
  Tag,
  Calendar,
  ChevronRight,
  Sparkles,
  UserPlus,
  Loader2,
  Send,
} from "lucide-react";
import { ApiClient } from "@/lib/api";
import { Contact } from "@/types";

export default function ContactsPage() {
  const router = useRouter();
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [phone, setPhone] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const loadContacts = async () => {
    setLoading(true);
    try {
      const data = await ApiClient.getContacts(search);
      setContacts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadContacts();
  }, [search]);

  const handleAddContact = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanPhone = phone.replace(/\D/g, "");
    if (!cleanPhone || cleanPhone.length < 7) {
      alert("Please enter a valid WhatsApp phone number with country code.");
      return;
    }
    setSubmitting(true);
    try {
      await ApiClient.createContact({
        phone: cleanPhone.startsWith("91") || cleanPhone.length > 10 ? cleanPhone : "91" + cleanPhone,
        name: name.trim() || undefined,
        email: email.trim() || undefined,
      });
      setModalOpen(false);
      setPhone("");
      setName("");
      setEmail("");
      loadContacts();
    } catch (err: any) {
      alert(err.message || "Failed to add contact");
    } finally {
      setSubmitting(false);
    }
  };

  const handleStartChatFromContact = async (contactPhone: string, contactName?: string) => {
    try {
      await ApiClient.startConversation({
        phone: contactPhone,
        name: contactName,
        mode: "HUMAN",
      });
      router.push("/inbox");
    } catch (err) {
      router.push("/inbox");
    }
  };

  return (
    <AppShell>
      <div className="p-8 max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black text-white flex items-center gap-2">
              <UserCheck className="w-6 h-6 text-emerald-400" />
              <span>Contact Directory</span>
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Customer profiles, WhatsApp phone identifiers, and conversation activity
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative w-64">
              <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search name, phone, email..."
                className="w-full pl-8 pr-3 py-1.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
            </div>

            <button
              onClick={() => setModalOpen(true)}
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-lg shadow-emerald-950/40 transition shrink-0"
            >
              <UserPlus className="w-4 h-4" />
              <span>+ Add Contact</span>
            </button>
          </div>
        </div>

        {/* Contacts Table */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800 uppercase text-[10px] font-bold">
              <tr>
                <th className="p-4">Contact</th>
                <th className="p-4">Phone / WhatsApp ID</th>
                <th className="p-4">Tags</th>
                <th className="p-4 text-center">Chats</th>
                <th className="p-4">Last Active</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {contacts.map((c) => (
                <tr key={c.id} className="hover:bg-slate-850/50 transition">
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-slate-800 text-white font-bold flex items-center justify-center border border-slate-700">
                        {c.name ? c.name[0] : "W"}
                      </div>
                      <div>
                        <p className="font-bold text-white text-xs">{c.name || "WhatsApp User"}</p>
                        <p className="text-[11px] text-slate-400">{c.email || "No email"}</p>
                      </div>
                    </div>
                  </td>
                  <td className="p-4 font-mono text-slate-300">{c.phone}</td>
                  <td className="p-4">
                    <div className="flex flex-wrap gap-1">
                      {c.tags?.map((t) => (
                        <span
                          key={t.id}
                          className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700"
                        >
                          {t.name}
                        </span>
                      ))}
                      {(!c.tags || c.tags.length === 0) && (
                        <span className="text-slate-600 text-[11px]">No tags</span>
                      )}
                    </div>
                  </td>
                  <td className="p-4 text-center font-mono font-bold text-emerald-400">
                    {c.conversation_count}
                  </td>
                  <td className="p-4 text-slate-400 text-[11px]">
                    {c.last_active_at ? new Date(c.last_active_at).toLocaleString() : "Recently"}
                  </td>
                  <td className="p-4 text-right">
                    <button
                      onClick={() => handleStartChatFromContact(c.phone, c.name)}
                      className="px-3 py-1.5 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-semibold inline-flex items-center gap-1.5 transition shadow-sm"
                    >
                      <MessageSquare className="w-3.5 h-3.5" />
                      <span>Chat</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Add Contact Modal */}
        {modalOpen && (
          <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-500/30">
                    <UserPlus className="w-4 h-4" />
                  </div>
                  <div>
                    <h2 className="text-sm font-bold text-white">Add WhatsApp Contact</h2>
                    <p className="text-[11px] text-slate-400">Register a new customer number in the CRM</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="text-slate-400 hover:text-white text-xs font-bold"
                >
                  ✕
                </button>
              </div>

              <form onSubmit={handleAddContact} className="space-y-3.5">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    WhatsApp Phone Number (with Country Code) *
                  </label>
                  <input
                    type="tel"
                    required
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="919876543210"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                  <p className="text-[10px] text-slate-500 mt-1">
                    Enter country code + phone number (e.g. 919876543210 for India).
                  </p>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Contact Name (Optional)
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Rahul Sharma"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Email Address (Optional)
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="e.g. rahul@example.com"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setModalOpen(false)}
                    className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-750"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting || !phone.trim()}
                    className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-lg"
                  >
                    {submitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
                    <span>Save Contact</span>
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
