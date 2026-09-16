"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Search, X, User, Users, FileText, Zap, ChevronRight, Loader2 } from "lucide-react";
import { ApiClient } from "@/lib/api";

interface GlobalSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function GlobalSearchModal({ isOpen, onClose }: GlobalSearchModalProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<{
    contacts: any[];
    leads: any[];
    templates: any[];
    automations: any[];
  }>({ contacts: [], leads: [], templates: [], automations: [] });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        isOpen ? onClose() : null;
      }
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (!query.trim()) {
      setResults({ contacts: [], leads: [], templates: [], automations: [] });
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await ApiClient.globalSearch(query);
        setResults(data);
      } catch (err) {
        console.error("Search failed:", err);
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [query]);

  if (!isOpen) return null;

  const hasResults =
    results.contacts.length > 0 ||
    results.leads.length > 0 ||
    results.templates.length > 0 ||
    results.automations.length > 0;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-start justify-center pt-20 p-4">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-700 rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
        {/* Search Input Bar */}
        <div className="p-4 border-b border-slate-800 flex items-center gap-3 bg-slate-950/50">
          <Search className="w-5 h-5 text-emerald-400" />
          <input
            autoFocus
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a contact, lead, phone number, template, or automation..."
            className="flex-1 bg-transparent text-sm text-white placeholder-slate-400 focus:outline-none"
          />
          {loading && <Loader2 className="w-4 h-4 text-emerald-400 animate-spin" />}
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-white rounded-lg transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search Results List */}
        <div className="overflow-y-auto p-4 space-y-4">
          {!query.trim() && (
            <div className="text-center py-8 text-slate-500 text-xs">
              Search across contacts, leads, message templates, and visual workflows.
            </div>
          )}

          {query.trim() && !loading && !hasResults && (
            <div className="text-center py-8 text-slate-400 text-xs">
              No results found for &ldquo;{query}&rdquo;
            </div>
          )}

          {/* Contacts */}
          {results.contacts.length > 0 && (
            <div>
              <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                <User className="w-3.5 h-3.5 text-blue-400" />
                <span>Contacts</span>
              </div>
              <div className="space-y-1">
                {results.contacts.map((c) => (
                  <Link
                    key={c.id}
                    href={c.link}
                    onClick={onClose}
                    className="flex items-center justify-between p-2.5 rounded-lg bg-slate-800/50 hover:bg-slate-800 text-xs transition"
                  >
                    <div>
                      <p className="font-semibold text-white">{c.title}</p>
                      <p className="text-[11px] text-slate-400">{c.subtitle}</p>
                    </div>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Leads */}
          {results.leads.length > 0 && (
            <div>
              <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                <Users className="w-3.5 h-3.5 text-emerald-400" />
                <span>Leads CRM</span>
              </div>
              <div className="space-y-1">
                {results.leads.map((l) => (
                  <Link
                    key={l.id}
                    href={l.link}
                    onClick={onClose}
                    className="flex items-center justify-between p-2.5 rounded-lg bg-slate-800/50 hover:bg-slate-800 text-xs transition"
                  >
                    <div>
                      <p className="font-semibold text-white">{l.title}</p>
                      <p className="text-[11px] text-emerald-400">{l.subtitle}</p>
                    </div>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Templates */}
          {results.templates.length > 0 && (
            <div>
              <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                <FileText className="w-3.5 h-3.5 text-purple-400" />
                <span>Message Templates</span>
              </div>
              <div className="space-y-1">
                {results.templates.map((t) => (
                  <Link
                    key={t.id}
                    href={t.link}
                    onClick={onClose}
                    className="flex items-center justify-between p-2.5 rounded-lg bg-slate-800/50 hover:bg-slate-800 text-xs transition"
                  >
                    <div>
                      <p className="font-semibold text-white">{t.title}</p>
                      <p className="text-[11px] text-slate-400">{t.subtitle}</p>
                    </div>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Automations */}
          {results.automations.length > 0 && (
            <div>
              <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                <span>Automations</span>
              </div>
              <div className="space-y-1">
                {results.automations.map((a) => (
                  <Link
                    key={a.id}
                    href={a.link}
                    onClick={onClose}
                    className="flex items-center justify-between p-2.5 rounded-lg bg-slate-800/50 hover:bg-slate-800 text-xs transition"
                  >
                    <div>
                      <p className="font-semibold text-white">{a.title}</p>
                      <p className="text-[11px] text-slate-400">{a.subtitle}</p>
                    </div>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-slate-800 bg-slate-950 text-[11px] text-slate-500 flex justify-between">
          <span>Tip: Use keywords like &ldquo;hi&rdquo;, &ldquo;Rahul&rdquo;, or &ldquo;welcome&rdquo;</span>
          <kbd className="font-mono text-[10px] bg-slate-800 px-1.5 py-0.5 rounded">ESC to close</kbd>
        </div>
      </div>
    </div>
  );
}
