"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Sparkles, ArrowRight, Lock, Mail, Loader2, ShieldCheck } from "lucide-react";
import { ApiClient } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@allstreak.com");
  const [password, setPassword] = useState("Allstreak@2026");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await ApiClient.login(email, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (demoEmail: string) => {
    setEmail(demoEmail);
    setPassword("Allstreak@2026");
    setLoading(true);
    setError("");

    try {
      await ApiClient.login(demoEmail, "Allstreak@2026");
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to log in with demo account");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-screen bg-slate-950 flex flex-col justify-center items-center p-4 relative overflow-hidden">
      {/* Background Subtle Gradient Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-emerald-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Brand Header */}
      <div className="flex flex-col items-center mb-8 z-10">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-600 via-emerald-500 to-teal-400 flex items-center justify-center shadow-xl shadow-emerald-500/20 mb-3">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
        <h1 className="text-2xl font-black tracking-tight text-white font-mono">ALLSTREAK</h1>
        <p className="text-xs text-slate-400 font-medium tracking-wide mt-1">
          Automate. Engage. Convert.
        </p>
      </div>

      {/* Card */}
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl z-10">
        <div className="mb-6 text-center">
          <h2 className="text-lg font-bold text-white">Welcome back</h2>
          <p className="text-xs text-slate-400 mt-1">
            Sign in to manage your WhatsApp automations & team inbox
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs text-center font-medium">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Work Email
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full pl-9 pr-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition"
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-xs font-semibold text-slate-300">Password</label>
              <a href="#" className="text-[11px] text-emerald-400 hover:underline">
                Forgot password?
              </a>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-slate-950 font-bold text-xs transition flex items-center justify-center gap-2 shadow-lg shadow-emerald-950/50"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <span>Sign in to Workspace</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* 1-Click Demo Accounts */}
        <div className="mt-6 pt-6 border-t border-slate-800/80">
          <p className="text-[11px] text-slate-400 font-semibold mb-2.5 text-center uppercase tracking-wider">
            Quick 1-Click Demo Access
          </p>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => handleDemoLogin("admin@allstreak.com")}
              className="py-2 px-3 rounded-lg bg-slate-800 hover:bg-slate-750 border border-slate-700 text-xs font-medium text-slate-200 transition text-center hover:border-emerald-500/40"
            >
              <span className="block font-bold text-emerald-400">Owner Demo</span>
              <span className="text-[10px] text-slate-400">admin@allstreak.com</span>
            </button>
            <button
              onClick={() => handleDemoLogin("agent@allstreak.com")}
              className="py-2 px-3 rounded-lg bg-slate-800 hover:bg-slate-750 border border-slate-700 text-xs font-medium text-slate-200 transition text-center hover:border-emerald-500/40"
            >
              <span className="block font-bold text-blue-400">Agent Demo</span>
              <span className="text-[10px] text-slate-400">agent@allstreak.com</span>
            </button>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-slate-400 mt-6">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-emerald-400 font-semibold hover:underline">
            Create workspace
          </Link>
        </p>
      </div>

      <div className="mt-6 text-[11px] text-slate-500 flex items-center gap-2">
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
        <span>Enterprise Meta Cloud API Encryption & Isolated Multi-Tenant DB</span>
      </div>
    </div>
  );
}
