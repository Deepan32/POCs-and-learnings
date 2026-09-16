"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import {
  BookOpen,
  Plus,
  Search,
  Sparkles,
  HelpCircle,
  Clock,
  DollarSign,
  ShieldAlert,
  ArrowRight,
  CheckCircle2,
} from "lucide-react";
import { ApiClient } from "@/lib/api";
import { KnowledgeBase } from "@/types";

export default function KnowledgeBasePage() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [testQuery, setTestQuery] = useState("What are your business working hours?");
  const [testResult, setTestResult] = useState<any>(null);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    async function loadKB() {
      try {
        const data = await ApiClient.getKnowledgeBases();
        setKnowledgeBases(data);
      } catch (err) {
        console.error(err);
      }
    }
    loadKB();
  }, []);

  const handleTestRAG = async () => {
    setTesting(true);
    try {
      const res = await ApiClient.queryKnowledgeTest(testQuery);
      setTestResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setTesting(false);
    }
  };

  const allDocs = knowledgeBases.flatMap((kb) => kb.documents || []);

  return (
    <AppShell>
      <div className="p-8 max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black text-white flex items-center gap-2">
              <BookOpen className="w-6 h-6 text-emerald-400" />
              <span>AI Knowledge Base & RAG</span>
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Structured FAQs, products, policies, and semantic context for autonomous WhatsApp replies
            </p>
          </div>
        </div>

        {/* Live RAG Test Box */}
        <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 to-slate-950 border border-slate-800 space-y-3 shadow-xl">
          <div className="flex items-center gap-2 text-xs font-bold text-emerald-400">
            <Sparkles className="w-4 h-4" />
            <span>Semantic RAG Query Tester</span>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={testQuery}
              onChange={(e) => setTestQuery(e.target.value)}
              placeholder="Ask a question about your business..."
              className="flex-1 px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
            />
            <button
              onClick={handleTestRAG}
              disabled={testing}
              className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs rounded-xl transition shadow-md"
            >
              {testing ? "Searching..." : "Test Retrieval"}
            </button>
          </div>

          {testResult && (
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-850 text-xs space-y-2 mt-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>RAG Match Found ({Math.round(testResult.confidence * 100)}% Confidence)</span>
                </span>
                <span className="text-[10px] text-slate-400">
                  Sources: {testResult.source_documents?.join(", ")}
                </span>
              </div>
              <p className="text-slate-200 leading-relaxed pt-1">{testResult.answer}</p>
            </div>
          )}
        </div>

        {/* Knowledge Documents Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {allDocs.map((doc) => (
            <div
              key={doc.id}
              className="p-5 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition space-y-2.5"
            >
              <div className="flex items-center justify-between">
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-emerald-400 border border-slate-700 uppercase">
                  {doc.category}
                </span>
                <span className="text-[10px] text-slate-500">Active</span>
              </div>
              <h3 className="font-bold text-sm text-white">{doc.title}</h3>
              {doc.question && (
                <p className="text-xs text-slate-400 italic">Q: &ldquo;{doc.question}&rdquo;</p>
              )}
              <p className="text-xs text-slate-300 bg-slate-950 p-3 rounded-xl border border-slate-850 leading-relaxed">
                {doc.answer_or_content}
              </p>
              {doc.keywords && (
                <p className="text-[10px] text-slate-500 font-mono">
                  Keywords: {doc.keywords}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
