"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import {
  Layers,
  Smartphone,
  ShieldCheck,
  CheckCircle2,
  Copy,
  Check,
  RefreshCw,
  ExternalLink,
  Key,
  Hash,
  Send,
  Radio,
  HelpCircle,
  AlertCircle,
  Sparkles,
  ArrowRight,
  Eye,
  EyeOff,
  Terminal,
  Activity,
  CheckCheck
} from "lucide-react";
import { ApiClient } from "@/lib/api";

export default function IntegrationsPage() {
  const [account, setAccount] = useState<any | null>(null);
  const [webhookInfo, setWebhookInfo] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  
  // Direct Meta Credentials Form State
  const [accessToken, setAccessToken] = useState("");
  const [phoneNumberId, setPhoneNumberId] = useState("");
  const [wabaId, setWabaId] = useState("");
  const [verifyToken, setVerifyToken] = useState("allstreak_secure_verify_token_2026");
  const [displayPhoneNumber, setDisplayPhoneNumber] = useState("");
  const [verifiedName, setVerifiedName] = useState("");
  const [customPublicUrl, setCustomPublicUrl] = useState("");
  
  // UI states
  const [showToken, setShowToken] = useState(false);
  const [copiedUrl, setCopiedUrl] = useState(false);
  const [copiedToken, setCopiedToken] = useState(false);
  const [successToast, setSuccessToast] = useState<string | null>(null);
  const [errorToast, setErrorToast] = useState<string | null>(null);

  // Live Test Message Form
  const [testPhone, setTestPhone] = useState("");
  const [testMsgText, setTestMsgText] = useState("Hello from ALLSTREAK! Your Meta WhatsApp Cloud API connection is active and verified. 🎉");
  const [sendingTestMsg, setSendingTestMsg] = useState(false);
  const [testMsgStatus, setTestMsgStatus] = useState<any | null>(null);

  // Webhook Events
  const [webhookLogs, setWebhookLogs] = useState<any[]>([]);

  const showToast = (msg: string, isError = false) => {
    if (isError) {
      setErrorToast(msg);
      setTimeout(() => setErrorToast(null), 5000);
    } else {
      setSuccessToast(msg);
      setTimeout(() => setSuccessToast(null), 5000);
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [acc, whInfo, whLogs] = await Promise.all([
        ApiClient.getWhatsAppIntegration().catch(() => null),
        ApiClient.getWhatsAppWebhookInfo().catch(() => null),
        ApiClient.getDebuggerWebhooks().catch(() => [])
      ]);

      if (acc) {
        setAccount(acc);
        setPhoneNumberId(acc.phone_number_id || "");
        setWabaId(acc.waba_id || "");
        setVerifyToken(acc.webhook_verify_token || "allstreak_secure_verify_token_2026");
        setDisplayPhoneNumber(acc.display_phone_number || "");
        setVerifiedName(acc.verified_name || "");
      }
      if (whInfo) {
        setWebhookInfo(whInfo);
      }
      setWebhookLogs(whLogs || []);
    } catch (err: any) {
      console.error("Failed to load WhatsApp integration:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setTestResult(null);

    try {
      const payload = {
        access_token: accessToken.trim(),
        phone_number_id: phoneNumberId.trim(),
        waba_id: wabaId.trim(),
        webhook_verify_token: verifyToken.trim() || "allstreak_secure_verify_token_2026",
        display_phone_number: displayPhoneNumber.trim() || undefined,
        verified_name: verifiedName.trim() || undefined
      };

      const res = await ApiClient.connectWhatsApp(payload);
      setAccount(res);
      showToast("Meta WhatsApp Cloud API credentials saved to .env and database successfully! Webhook details ready below.");

      // Refresh webhook info
      const whInfo = await ApiClient.getWhatsAppWebhookInfo();
      setWebhookInfo(whInfo);
      
      // Auto-test with Meta
      handleTestConnection();
    } catch (err: any) {
      showToast("Failed to connect Meta API: " + (err.message || "Invalid credentials"), true);
    } finally {
      setSubmitting(false);
    }
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await ApiClient.testWhatsAppConnection();
      if (res.success) {
        setTestResult({
          success: true,
          message: `✓ Connected! Verified Name: "${res.verified_name || 'Verified'}", Quality Rating: ${res.quality_rating || 'GREEN'}`
        });
        showToast("Meta API handshake verified successfully!");
      } else {
        setTestResult({
          success: false,
          message: res.message || "Meta validation failed. Check your Access Token & Phone Number ID."
        });
      }
    } catch (err: any) {
      setTestResult({
        success: false,
        message: err.message || "Could not connect to Meta Graph API"
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSendTestMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!testPhone.trim()) {
      showToast("Please enter a destination phone number with country code", true);
      return;
    }
    setSendingTestMsg(true);
    setTestMsgStatus(null);
    try {
      const res = await ApiClient.sendTestWhatsAppMessage(testPhone, testMsgText);
      setTestMsgStatus(res);
      if (res.success) {
        showToast("✓ Live WhatsApp message sent successfully!");
      } else {
        showToast("Meta dispatch note: " + res.message, true);
      }
    } catch (err: any) {
      setTestMsgStatus({ success: false, message: err.message });
      showToast("Error sending test message: " + err.message, true);
    } finally {
      setSendingTestMsg(false);
    }
  };

  const copyText = (text: string, isUrl = true) => {
    navigator.clipboard.writeText(text);
    if (isUrl) {
      setCopiedUrl(true);
      setTimeout(() => setCopiedUrl(false), 2500);
    } else {
      setCopiedToken(true);
      setTimeout(() => setCopiedToken(false), 2500);
    }
    showToast("Copied to clipboard!");
  };

  const generateRandomToken = () => {
    const rand = "allstreak_" + Math.random().toString(36).substring(2, 10) + "_" + Date.now().toString().slice(-4);
    setVerifyToken(rand);
    showToast("Generated new unique verify token: " + rand);
  };

  // Determine computed callback URL (allow ngrok / custom domain override)
  const effectiveCallbackUrl = customPublicUrl.trim()
    ? `${customPublicUrl.trim().replace(/\/+$/, "")}/webhook/whatsapp`
    : webhookInfo?.callback_url || "http://localhost:8000/webhook/whatsapp";

  const effectiveVerifyToken = verifyToken || webhookInfo?.webhook_verify_token || "allstreak_secure_verify_token_2026";

  return (
    <AppShell>
      <div className="p-6 md:p-8 max-w-6xl mx-auto space-y-6">
        {/* Toast Notifications */}
        {successToast && (
          <div className="fixed top-5 right-5 z-50 flex items-center gap-2.5 px-4 py-3 bg-emerald-950 border border-emerald-500 text-emerald-200 rounded-xl shadow-2xl animate-fade-in text-xs font-semibold">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{successToast}</span>
          </div>
        )}
        {errorToast && (
          <div className="fixed top-5 right-5 z-50 flex items-center gap-2.5 px-4 py-3 bg-rose-950 border border-rose-500 text-rose-200 rounded-xl shadow-2xl animate-fade-in text-xs font-semibold">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{errorToast}</span>
          </div>
        )}

        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 via-emerald-500 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                <Smartphone className="w-5 h-5 text-slate-950 font-bold" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-xl font-extrabold text-white tracking-tight font-mono">
                    META CLOUD API INTEGRATION
                  </h1>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                    account?.is_active ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                  }`}>
                    {account?.is_active ? "LIVE CONNECTED" : "SETUP REQUIRED"}
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Connect your Meta WhatsApp Business Account (WABA) credentials & configure the Webhook callback.
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <a
              href="https://developers.facebook.com/apps"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
            >
              <span>Meta App Dashboard</span>
              <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
            </a>
            <button
              onClick={loadData}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
              title="Refresh status"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-emerald-400" : ""}`} />
            </button>
          </div>
        </div>

        {/* PRIMARY META CREDENTIALS SUBMISSION FORM */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7 space-y-6">
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800/90 shadow-xl space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
                <div className="flex items-center gap-2">
                  <Key className="w-4 h-4 text-emerald-400" />
                  <h3 className="text-sm font-bold text-white">
                    {account ? "Update Meta API Credentials" : "Enter Meta Cloud API Credentials"}
                  </h3>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/30 flex items-center gap-1">
                    <Check className="w-3 h-3 stroke-[3]" /> Auto-saves to .env
                  </span>
                  <span className="text-[10px] font-mono text-slate-500 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                    Graph API v21.0
                  </span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/20 flex items-center gap-2 text-xs text-emerald-300">
                <Sparkles className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>
                  <strong>Automatic .env Synchronization:</strong> When you submit, your <code>META_ACCESS_TOKEN</code>, <code>META_PHONE_NUMBER_ID</code>, <code>META_WABA_ID</code>, and <code>META_VERIFY_TOKEN</code> are automatically written to your root <code>.env</code> file.
                </span>
              </div>


              <form onSubmit={handleConnect} className="space-y-4 text-xs">
                {/* 1. Permanent / Temporary Access Token */}
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="font-semibold text-slate-200 flex items-center gap-1.5">
                      <span>Meta Access Token</span>
                      <span className="text-rose-400 font-bold">*</span>
                    </label>
                    <button
                      type="button"
                      onClick={() => setShowToken(!showToken)}
                      className="text-[11px] text-slate-400 hover:text-emerald-400 flex items-center gap-1"
                    >
                      {showToken ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                      <span>{showToken ? "Hide" : "Show"}</span>
                    </button>
                  </div>
                  <input
                    type={showToken ? "text" : "password"}
                    value={accessToken}
                    onChange={(e) => setAccessToken(e.target.value)}
                    required
                    placeholder="EAABw... (System User Token from Business Manager or 24h Access Token)"
                    className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500 rounded-xl px-3.5 py-2.5 text-xs text-white font-mono placeholder-slate-600 focus:outline-none transition shadow-inner"
                  />
                  <p className="text-[11px] text-slate-500 mt-1">
                    Obtained from Meta for Developers &gt; WhatsApp &gt; API Setup, or System User under Meta Business Manager.
                  </p>
                </div>

                {/* 2. Phone Number ID & WABA ID */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="font-semibold text-slate-200 block mb-1 flex items-center gap-1">
                      <span>Phone Number ID</span>
                      <span className="text-rose-400 font-bold">*</span>
                    </label>
                    <input
                      type="text"
                      value={phoneNumberId}
                      onChange={(e) => setPhoneNumberId(e.target.value)}
                      required
                      placeholder="e.g. 104829102938475"
                      className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500 rounded-xl px-3.5 py-2 text-xs text-white font-mono placeholder-slate-600 focus:outline-none transition"
                    />
                  </div>

                  <div>
                    <label className="font-semibold text-slate-200 block mb-1 flex items-center gap-1">
                      <span>WhatsApp Business Account ID</span>
                      <span className="text-rose-400 font-bold">*</span>
                    </label>
                    <input
                      type="text"
                      value={wabaId}
                      onChange={(e) => setWabaId(e.target.value)}
                      required
                      placeholder="e.g. 102938475610293"
                      className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500 rounded-xl px-3.5 py-2 text-xs text-white font-mono placeholder-slate-600 focus:outline-none transition"
                    />
                  </div>
                </div>

                {/* 3. Custom Verify Token */}
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="font-semibold text-slate-200 flex items-center gap-1">
                      <span>Webhook Verify Token</span>
                      <span className="text-emerald-400 text-[10px]">(Secret used by Meta to authenticate webhook)</span>
                    </label>
                    <button
                      type="button"
                      onClick={generateRandomToken}
                      className="text-[11px] text-emerald-400 hover:text-emerald-300 font-medium"
                    >
                      Generate New
                    </button>
                  </div>
                  <input
                    type="text"
                    value={verifyToken}
                    onChange={(e) => setVerifyToken(e.target.value)}
                    required
                    placeholder="allstreak_secure_verify_token_2026"
                    className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500 rounded-xl px-3.5 py-2 text-xs text-white font-mono placeholder-slate-600 focus:outline-none transition"
                  />
                </div>

                {/* 4. Optional Display Phone & Business Name */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="font-semibold text-slate-300 block mb-1">
                      <span>Display Phone Number</span>
                      <span className="text-slate-500 text-[10px] ml-1">(Optional / Auto-detected)</span>
                    </label>
                    <input
                      type="text"
                      value={displayPhoneNumber}
                      onChange={(e) => setDisplayPhoneNumber(e.target.value)}
                      placeholder="+91 98765 43210"
                      className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500 rounded-xl px-3 py-2 text-xs text-white font-mono placeholder-slate-600 focus:outline-none transition"
                    />
                  </div>
                  <div>
                    <label className="font-semibold text-slate-300 block mb-1">
                      <span>Verified Business Name</span>
                      <span className="text-slate-500 text-[10px] ml-1">(Optional)</span>
                    </label>
                    <input
                      type="text"
                      value={verifiedName}
                      onChange={(e) => setVerifiedName(e.target.value)}
                      placeholder="e.g. ALLSTREAK Cloud / Wings Flower"
                      className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-600 focus:outline-none transition"
                    />
                  </div>
                </div>

                {/* Submit Action */}
                <div className="pt-2 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {account && (
                      <button
                        type="button"
                        onClick={handleTestConnection}
                        disabled={testing}
                        className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition border border-slate-700"
                      >
                        <RefreshCw className={`w-3.5 h-3.5 text-emerald-400 ${testing ? "animate-spin" : ""}`} />
                        <span>{testing ? "Testing Handshake..." : "Test Meta API"}</span>
                      </button>
                    )}
                  </div>

                  <button
                    type="submit"
                    disabled={submitting}
                    className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold transition shadow-lg shadow-emerald-900/30"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{submitting ? "Connecting to Meta..." : "Save & Connect Meta API"}</span>
                  </button>
                </div>
              </form>

              {/* Handshake Result Alert */}
              {testResult && (
                <div className={`p-4 rounded-xl text-xs flex items-start gap-2.5 animate-fade-in ${
                  testResult.success
                    ? "bg-emerald-950/40 border border-emerald-500/40 text-emerald-300"
                    : "bg-rose-950/40 border border-rose-500/40 text-rose-300"
                }`}>
                  {testResult.success ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-rose-400 mt-0.5 shrink-0" />
                  )}
                  <div className="leading-relaxed">
                    <p className="font-bold">{testResult.success ? "Meta Graph API Handshake Successful" : "Handshake Error"}</p>
                    <p className="text-[11px] mt-0.5">{testResult.message}</p>
                  </div>
                </div>
              )}
            </div>

            {/* SEND REAL TEST MESSAGE SECTION */}
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800/90 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Send className="w-4 h-4 text-emerald-400" />
                  <h3 className="text-sm font-bold text-white">Send Live Test WhatsApp Message</h3>
                </div>
                <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 font-mono">
                  Outbound Cloud API
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Send a real test message to your personal WhatsApp number to verify your credentials work end-to-end.
              </p>

              <form onSubmit={handleSendTestMessage} className="space-y-3 text-xs">
                <div>
                  <label className="font-semibold text-slate-300 block mb-1">
                    Your WhatsApp Phone Number (with Country Code)
                  </label>
                  <input
                    type="text"
                    value={testPhone}
                    onChange={(e) => setTestPhone(e.target.value)}
                    placeholder="e.g. 919876543210 (without + or dashes)"
                    className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500 rounded-xl px-3.5 py-2 text-xs text-white font-mono placeholder-slate-600 focus:outline-none transition"
                  />
                  <p className="text-[11px] text-slate-500 mt-1">
                    💡 If your Meta App is in Development mode, ensure this number is added to your &quot;To&quot; recipient list under WhatsApp &gt; API Setup in Meta console.
                  </p>
                </div>

                <div>
                  <label className="font-semibold text-slate-300 block mb-1">Message Text</label>
                  <textarea
                    rows={2}
                    value={testMsgText}
                    onChange={(e) => setTestMsgText(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-600 focus:outline-none transition"
                  />
                </div>

                <button
                  type="submit"
                  disabled={sendingTestMsg || !testPhone.trim()}
                  className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs flex items-center gap-2 transition disabled:opacity-40 shadow-lg shadow-emerald-900/30"
                >
                  <Send className={`w-3.5 h-3.5 ${sendingTestMsg ? "animate-pulse" : ""}`} />
                  <span>{sendingTestMsg ? "Sending Message..." : "Send Test WhatsApp Message"}</span>
                </button>

                {testMsgStatus && (
                  <div className={`p-3 rounded-xl text-xs ${
                    testMsgStatus.success
                      ? "bg-emerald-950/40 border border-emerald-500/40 text-emerald-300"
                      : "bg-rose-950/40 border border-rose-500/40 text-rose-300"
                  }`}>
                    <p className="font-bold">{testMsgStatus.success ? "Message Delivered to Meta API!" : "Dispatch Notice"}</p>
                    <p className="text-[11px] mt-0.5">{testMsgStatus.message}</p>
                    {testMsgStatus.meta_message_id && (
                      <p className="font-mono text-[10px] text-emerald-400 mt-1">
                        Meta Message ID: {testMsgStatus.meta_message_id}
                      </p>
                    )}
                  </div>
                )}
              </form>
            </div>
          </div>

          {/* RIGHT PANEL: WEBHOOK DETAILS & META DEVELOPERS INSTRUCTIONS */}
          <div className="lg:col-span-5 space-y-6">
            {/* Instant Webhook Setup Box */}
            <div className="p-6 rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border-2 border-emerald-500/40 shadow-2xl shadow-emerald-950/20 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <Radio className="w-4 h-4 text-emerald-400 animate-pulse" />
                  <h3 className="text-sm font-bold text-white">Meta Webhook Configuration</h3>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  Ready to Paste
                </span>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">
                Copy the <strong>Callback URL</strong> and <strong>Verify Token</strong> below into your Meta for Developers App dashboard under <strong>WhatsApp &gt; Configuration</strong>:
              </p>

              {/* Optional public domain override (e.g. ngrok) */}
              <div className="space-y-1">
                <label className="text-[11px] text-slate-400 flex items-center justify-between">
                  <span>Public HTTPS Host / ngrok Domain (optional):</span>
                  <span className="text-[10px] text-emerald-400 font-mono">ngrok http 8000</span>
                </label>
                <input
                  type="text"
                  value={customPublicUrl}
                  onChange={(e) => setCustomPublicUrl(e.target.value)}
                  placeholder="e.g. https://your-domain.ngrok-free.app"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-emerald-300 font-mono placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                />
              </div>

              {/* Box 1: Callback URL */}
              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    Callback URL
                  </span>
                  <button
                    type="button"
                    onClick={() => copyText(effectiveCallbackUrl, true)}
                    className="flex items-center gap-1 text-[11px] font-bold text-emerald-400 hover:text-emerald-300 transition"
                  >
                    {copiedUrl ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedUrl ? "Copied!" : "Copy URL"}</span>
                  </button>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between overflow-x-auto">
                  <code className="font-mono text-xs text-emerald-400 whitespace-nowrap">
                    {effectiveCallbackUrl}
                  </code>
                </div>
              </div>

              {/* Box 2: Verify Token */}
              <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    Verify Token
                  </span>
                  <button
                    type="button"
                    onClick={() => copyText(effectiveVerifyToken, false)}
                    className="flex items-center gap-1 text-[11px] font-bold text-emerald-400 hover:text-emerald-300 transition"
                  >
                    {copiedToken ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedToken ? "Copied!" : "Copy Token"}</span>
                  </button>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between overflow-x-auto">
                  <code className="font-mono text-xs text-white whitespace-nowrap">
                    {effectiveVerifyToken}
                  </code>
                </div>
              </div>

              {/* Step-by-Step Meta Developer Guide */}
              <div className="pt-2 border-t border-slate-800 space-y-2.5 text-xs text-slate-300">
                <span className="font-bold text-white text-xs block">
                  Quick Step-by-Step Meta Setup:
                </span>
                
                <ol className="space-y-2 text-[11px] text-slate-300 list-decimal list-inside leading-relaxed">
                  <li>
                    Open <a href="https://developers.facebook.com/apps" target="_blank" rel="noopener noreferrer" className="text-emerald-400 underline font-semibold">Meta for Developers</a> &gt; Select your App.
                  </li>
                  <li>
                    In left sidebar, navigate to <strong>WhatsApp &gt; Configuration</strong>.
                  </li>
                  <li>
                    Under <strong>Webhook</strong>, click <strong>Edit</strong> and paste the Callback URL &amp; Verify Token above.
                  </li>
                  <li>
                    Click <strong>Verify and save</strong>. Meta will ping ALLSTREAK and verify in 1 second!
                  </li>
                  <li>
                    Click <strong>Manage</strong> webhook fields &gt; check <strong>messages</strong> to subscribe to incoming chats!
                  </li>
                </ol>
              </div>
            </div>

            {/* LIVE WEBHOOK EVENT LOGS */}
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800/90 shadow-xl space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-emerald-400" />
                  <h3 className="text-sm font-bold text-white">Live Webhook Event Stream</h3>
                </div>
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_#10B981]" />
              </div>

              <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                {webhookLogs.length === 0 ? (
                  <div className="p-6 text-center text-slate-500 text-xs border border-dashed border-slate-800 rounded-xl">
                    <p>Waiting for incoming webhook events...</p>
                    <p className="text-[10px] text-slate-600 mt-1">Send a message from WhatsApp or run the simulator to see events here.</p>
                  </div>
                ) : (
                  webhookLogs.slice(0, 5).map((log) => (
                    <div key={log.id} className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 text-xs space-y-1 font-mono">
                      <div className="flex items-center justify-between text-[10px]">
                        <span className="text-emerald-400 font-bold">{log.event_type}</span>
                        <span className="text-slate-500">{new Date(log.created_at).toLocaleTimeString()}</span>
                      </div>
                      <p className="text-slate-300 text-[11px] truncate">
                        ID: {log.meta_message_id || log.id}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
