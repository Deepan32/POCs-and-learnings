"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import {
  SlidersHorizontal,
  Building,
  Palette,
  Package,
  MessageSquareQuote,
  Layers,
  Copy,
  History,
  Activity,
  CheckCircle2,
  AlertCircle,
  Plus,
  Trash2,
  ExternalLink,
  Smartphone,
  Save,
  RefreshCw,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Check,
  X,
  Play
} from "lucide-react";
import { ApiClient } from "@/lib/api";
import {
  ClientSetupOverview,
  ProductService,
  QuickReply,
  IndustryTemplate,
  DebuggerTrace,
  WebhookLog
} from "@/types";

export default function ClientSetupPage() {
  const [activeTab, setActiveTab] = useState<
    "overview" | "profile" | "branding" | "catalog" | "quick_replies" | "templates" | "debugger" | "versions"
  >("overview");

  const [overview, setOverview] = useState<ClientSetupOverview | null>(null);
  const [products, setProducts] = useState<ProductService[]>([]);
  const [quickReplies, setQuickReplies] = useState<QuickReply[]>([]);
  const [templates, setTemplates] = useState<IndustryTemplate[]>([]);
  const [traces, setTraces] = useState<DebuggerTrace[]>([]);
  const [webhooks, setWebhooks] = useState<WebhookLog[]>([]);
  const [versions, setVersions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Profile Form State
  const [profileForm, setProfileForm] = useState({
    name: "",
    industry: "",
    timezone: "Asia/Kolkata",
    phone: "",
    email: "",
    website: "",
    address: "",
    city: "",
    instagram: "",
    facebook: "",
    description: "",
    business_hours_config: "Mon-Sat: 09:00 - 20:00, Sun: 10:00 - 18:00"
  });

  // Branding Form State
  const [brandingForm, setBrandingForm] = useState({
    logo_url: "",
    primary_color: "#25D366",
    secondary_color: "#128C7E",
    background_color: "#0B141A",
    text_color: "#E9EDEF",
    button_style: "rounded"
  });

  // Modals
  const [productModalOpen, setProductModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<ProductService | null>(null);
  const [productForm, setProductForm] = useState({
    name: "",
    description: "",
    category: "General",
    price: 0,
    currency: "INR",
    sku: "",
    is_available: true
  });

  const [quickReplyModalOpen, setQuickReplyModalOpen] = useState(false);
  const [quickReplyForm, setQuickReplyForm] = useState({
    shortcut: "",
    title: "",
    message: "",
    category: "General"
  });

  const [cloneModalOpen, setCloneModalOpen] = useState(false);
  const [cloneForm, setCloneForm] = useState({
    target_name: "",
    target_slug: "",
    industry: "",
    copy_branding: true,
    copy_flows: true,
    copy_templates: true,
    copy_products: true,
    copy_quick_replies: true,
    copy_ai_settings: true
  });

  const [versionModalOpen, setVersionModalOpen] = useState(false);
  const [versionTag, setVersionTag] = useState("");
  const [versionNotes, setVersionNotes] = useState("");

  // Debugger Live Test State
  const [simPhone, setSimPhone] = useState("919876543210");
  const [simName, setSimName] = useState("Rahul Sharma");
  const [simMsg, setSimMsg] = useState("Hi, what are your bouquet prices?");
  const [simResult, setSimResult] = useState<any>(null);
  const [simLoading, setSimLoading] = useState(false);

  const showNotification = (msg: string, isError = false) => {
    if (isError) {
      setErrorMsg(msg);
      setTimeout(() => setErrorMsg(null), 4000);
    } else {
      setSuccessMsg(msg);
      setTimeout(() => setSuccessMsg(null), 4000);
    }
  };

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [ovData, prodData, qrData, tplData, traceData, whData, verData] = await Promise.all([
        ApiClient.getClientSetupOverview(),
        ApiClient.listProducts(),
        ApiClient.listQuickReplies(),
        ApiClient.listIndustryTemplates(),
        ApiClient.getDebuggerTraces(),
        ApiClient.getDebuggerWebhooks(),
        ApiClient.listVersions()
      ]);

      setOverview(ovData);
      setProducts(prodData || []);
      setQuickReplies(qrData || []);
      setTemplates(tplData || []);
      setTraces(traceData || []);
      setWebhooks(whData || []);
      setVersions(verData || []);

      if (ovData) {
        setProfileForm({
          name: ovData.name || "",
          industry: ovData.industry || "",
          timezone: ovData.timezone || "Asia/Kolkata",
          phone: ovData.phone || "",
          email: ovData.email || "",
          website: ovData.website || "",
          address: ovData.address || "",
          city: ovData.city || "",
          instagram: ovData.instagram || "",
          facebook: ovData.facebook || "",
          description: ovData.description || "",
          business_hours_config: ovData.business_hours_config || "Mon-Sat: 09:00 - 20:00, Sun: 10:00 - 18:00"
        });

        setBrandingForm({
          logo_url: ovData.logo_url || "",
          primary_color: ovData.primary_color || "#25D366",
          secondary_color: ovData.secondary_color || "#128C7E",
          background_color: ovData.background_color || "#0B141A",
          text_color: ovData.text_color || "#E9EDEF",
          button_style: ovData.button_style || "rounded"
        });
      }
    } catch (err: any) {
      console.error("Failed to load client setup data:", err);
      showNotification("Failed to load client setup: " + (err.message || "Unknown error"), true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await ApiClient.updateBusinessProfile(profileForm);
      showNotification("Business profile saved successfully!");
      loadAllData();
    } catch (err: any) {
      showNotification("Error saving profile: " + err.message, true);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveBranding = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await ApiClient.updateBranding(brandingForm);
      showNotification("Branding & custom styles saved!");
      loadAllData();
    } catch (err: any) {
      showNotification("Error saving branding: " + err.message, true);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editingProduct) {
        await ApiClient.updateProduct(editingProduct.id, productForm);
        showNotification("Product updated successfully!");
      } else {
        await ApiClient.createProduct(productForm);
        showNotification("Product added to catalog!");
      }
      setProductModalOpen(false);
      setEditingProduct(null);
      setProductForm({ name: "", description: "", category: "General", price: 0, currency: "INR", sku: "", is_available: true });
      const updatedProds = await ApiClient.listProducts();
      setProducts(updatedProds);
    } catch (err: any) {
      showNotification("Failed to save product: " + err.message, true);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteProduct = async (id: string) => {
    if (!confirm("Are you sure you want to remove this product?")) return;
    try {
      await ApiClient.deleteProduct(id);
      showNotification("Product removed from catalog");
      setProducts(products.filter(p => p.id !== id));
    } catch (err: any) {
      showNotification("Failed to delete product: " + err.message, true);
    }
  };

  const handleSaveQuickReply = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await ApiClient.createQuickReply(quickReplyForm);
      showNotification("Quick reply shortcut created!");
      setQuickReplyModalOpen(false);
      setQuickReplyForm({ shortcut: "", title: "", message: "", category: "General" });
      const updatedQR = await ApiClient.listQuickReplies();
      setQuickReplies(updatedQR);
    } catch (err: any) {
      showNotification("Failed to save quick reply: " + err.message, true);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteQuickReply = async (id: string) => {
    if (!confirm("Delete this quick reply shortcut?")) return;
    try {
      await ApiClient.deleteQuickReply(id);
      showNotification("Quick reply removed");
      setQuickReplies(quickReplies.filter(q => q.id !== id));
    } catch (err: any) {
      showNotification("Failed to delete quick reply: " + err.message, true);
    }
  };

  const handleApplyTemplate = async (tplId: string, name: string) => {
    if (!confirm(`Apply the "${name}" blueprint? This will populate products, quick replies, and greeting automations.`)) return;
    setSaving(true);
    try {
      const res = await ApiClient.applyIndustryTemplate(tplId);
      showNotification(res.message || `Blueprint applied! Added ${res.products_added} products.`);
      loadAllData();
    } catch (err: any) {
      showNotification("Failed to apply template: " + err.message, true);
    } finally {
      setSaving(false);
    }
  };

  const handleCloneClient = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await ApiClient.cloneClientWorkspace(cloneForm);
      showNotification(`Client cloned! Workspace '${res.new_workspace_name}' is ready.`);
      setCloneModalOpen(false);
      setCloneForm({
        target_name: "",
        target_slug: "",
        industry: "",
        copy_branding: true,
        copy_flows: true,
        copy_templates: true,
        copy_products: true,
        copy_quick_replies: true,
        copy_ai_settings: true
      });
    } catch (err: any) {
      showNotification("Failed to clone client: " + err.message, true);
    } finally {
      setSaving(false);
    }
  };

  const handleCreateSnapshot = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await ApiClient.createVersionSnapshot(versionTag, versionNotes);
      showNotification(`Version snapshot '${versionTag}' captured!`);
      setVersionModalOpen(false);
      setVersionTag("");
      setVersionNotes("");
      const vers = await ApiClient.listVersions();
      setVersions(vers);
    } catch (err: any) {
      showNotification("Failed to create snapshot: " + err.message, true);
    } finally {
      setSaving(false);
    }
  };

  const handleRollback = async (verId: string, tag: string) => {
    if (!confirm(`Rollback client workspace to configuration version '${tag}'? Current uncommitted changes will be replaced.`)) return;
    setSaving(true);
    try {
      const res = await ApiClient.rollbackVersion(verId);
      showNotification(res.message);
      loadAllData();
    } catch (err: any) {
      showNotification("Rollback failed: " + err.message, true);
    } finally {
      setSaving(false);
    }
  };

  const handleRunSimulation = async () => {
    setSimLoading(true);
    try {
      const res = await ApiClient.simulateWebhookPipeline({
        sender_phone: simPhone,
        sender_name: simName,
        message_text: simMsg
      });
      setSimResult(res);
      showNotification("Webhook evaluated through pipeline!");
    } catch (err: any) {
      showNotification("Simulation error: " + err.message, true);
    } finally {
      setSimLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Toast Alerts */}
        {successMsg && (
          <div className="fixed top-5 right-5 z-50 flex items-center gap-2 px-4 py-3 bg-emerald-950 border border-emerald-500 text-emerald-300 rounded-xl shadow-2xl animate-fade-in">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <span className="text-sm font-semibold">{successMsg}</span>
          </div>
        )}
        {errorMsg && (
          <div className="fixed top-5 right-5 z-50 flex items-center gap-2 px-4 py-3 bg-rose-950 border border-rose-500 text-rose-300 rounded-xl shadow-2xl animate-fade-in">
            <AlertCircle className="w-5 h-5 text-rose-400" />
            <span className="text-sm font-semibold">{errorMsg}</span>
          </div>
        )}

        {/* Top Header Banner */}
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-md shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                <SlidersHorizontal className="w-5 h-5 text-slate-950 font-bold" />
              </div>
              <div>
                <div className="flex items-center gap-2.5">
                  <h1 className="text-xl font-extrabold text-white tracking-tight">
                    Client Customization Studio
                  </h1>
                  <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                    {overview?.industry || "Florist / Retail"}
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Custom-tailor branding, catalog, canned replies, and automations for each client without backend code changes.
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2.5 flex-wrap">
            <button
              onClick={() => setVersionModalOpen(true)}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
            >
              <History className="w-3.5 h-3.5 text-slate-400" />
              <span>Snapshot</span>
            </button>
            <button
              onClick={() => setCloneModalOpen(true)}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold shadow-lg shadow-emerald-900/30 transition"
            >
              <Copy className="w-3.5 h-3.5" />
              <span>Clone Client</span>
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-1 border-b border-slate-800/80 pb-px overflow-x-auto">
          {[
            { id: "overview", label: "Client Overview", icon: Building },
            { id: "profile", label: "Business Profile", icon: Building },
            { id: "branding", label: "Branding & Theme", icon: Palette },
            { id: "catalog", label: "Products & Services", icon: Package, badge: products.length },
            { id: "quick_replies", label: "Quick Replies", icon: MessageSquareQuote, badge: quickReplies.length },
            { id: "templates", label: "Sector Blueprints", icon: Layers, badge: "8" },
            { id: "debugger", label: "Automation Debugger", icon: Activity },
            { id: "versions", label: "Snapshots & History", icon: History, badge: versions.length }
          ].map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold whitespace-nowrap transition-all border-b-2 ${
                  active
                    ? "border-emerald-400 text-emerald-400 bg-emerald-500/10 rounded-t-lg"
                    : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/50"
                }`}
              >
                <Icon className={`w-4 h-4 ${active ? "text-emerald-400" : "text-slate-500"}`} />
                <span>{tab.label}</span>
                {tab.badge !== undefined && (
                  <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
                    active ? "bg-emerald-500 text-slate-950" : "bg-slate-800 text-slate-400"
                  }`}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* TAB CONTENT: OVERVIEW */}
        {activeTab === "overview" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <p className="text-xs text-slate-400 font-medium">Active Client</p>
                <p className="text-lg font-bold text-white mt-1">{overview?.name || "ALLSTREAK Client"}</p>
                <p className="text-[11px] text-emerald-400 font-mono mt-0.5">slug: {overview?.slug}</p>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <p className="text-xs text-slate-400 font-medium">Meta WhatsApp Status</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className={`w-2.5 h-2.5 rounded-full ${overview?.whatsapp_connected ? "bg-emerald-400 shadow-[0_0_8px_#10b981]" : "bg-amber-400 shadow-[0_0_8px_#f59e0b]"}`} />
                  <span className="text-sm font-bold text-white">
                    {overview?.whatsapp_connected ? "Connected & Live" : "Simulator Ready"}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  {overview?.whatsapp_phone_number || "Test Sandbox Mode"}
                </p>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <p className="text-xs text-slate-400 font-medium">Catalog Items</p>
                <p className="text-lg font-bold text-white mt-1">{products.length} Products</p>
                <p className="text-[11px] text-slate-400 mt-0.5">{quickReplies.length} Quick Canned Replies</p>
              </div>
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                <p className="text-xs text-slate-400 font-medium">Automations & Flows</p>
                <p className="text-lg font-bold text-white mt-1">{overview?.flows_count || 0} Flows Active</p>
                <p className="text-[11px] text-slate-400 mt-0.5">{overview?.templates_count || 0} Meta Templates</p>
              </div>
            </div>

            {/* Customization Readiness Checklist */}
            <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/80 space-y-4">
              <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Client White-Label & Customization Readiness</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {[
                  { title: "Business Profile Configured", done: Boolean(overview?.phone && overview?.address), desc: "Phone, address, and timings set" },
                  { title: "Branding & Colors Selected", done: Boolean(overview?.primary_color), desc: "Theme palette matches client brand" },
                  { title: "Product / Service Catalog", done: products.length > 0, desc: `${products.length} items ready for AI & bot answers` },
                  { title: "Quick Reply Shortcuts", done: quickReplies.length > 0, desc: `${quickReplies.length} 1-click canned responses configured` },
                  { title: "Welcome Auto-Reply", done: Boolean(overview?.flows_count && overview.flows_count > 0), desc: "First response trigger active" },
                  { title: "Safety Sandbox Tested", done: true, desc: "Verified via live simulator" }
                ].map((chk, i) => (
                  <div key={i} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/60 flex items-start gap-3">
                    <div className={`mt-0.5 w-5 h-5 rounded-full flex items-center justify-center ${chk.done ? "bg-emerald-500/20 text-emerald-400" : "bg-slate-800 text-slate-500"}`}>
                      {chk.done ? <Check className="w-3 h-3 stroke-[3]" /> : <span className="text-[10px]">?</span>}
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-slate-200">{chk.title}</p>
                      <p className="text-[11px] text-slate-400">{chk.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB CONTENT: BUSINESS PROFILE */}
        {activeTab === "profile" && (
          <form onSubmit={handleSaveProfile} className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Building className="w-4 h-4 text-emerald-400" />
                  <span>Client Business Identity</span>
                </h3>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Business / Brand Name</label>
                  <input
                    type="text"
                    value={profileForm.name}
                    onChange={e => setProfileForm({ ...profileForm, name: e.target.value })}
                    required
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                    placeholder="e.g. Wings Flower Boutique"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Industry Sector</label>
                  <input
                    type="text"
                    value={profileForm.industry}
                    onChange={e => setProfileForm({ ...profileForm, industry: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                    placeholder="e.g. Florist & Gifts, Restaurant, Clinic, Real Estate"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Business Description / Tagline</label>
                  <textarea
                    rows={3}
                    value={profileForm.description}
                    onChange={e => setProfileForm({ ...profileForm, description: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                    placeholder="Fresh Dutch flowers, bespoke luxury bouquets, and 2-hour express delivery."
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Operating Hours Schedule</label>
                  <input
                    type="text"
                    value={profileForm.business_hours_config}
                    onChange={e => setProfileForm({ ...profileForm, business_hours_config: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                    placeholder="e.g. Mon-Sat: 09:00 - 21:00, Sun: 10:00 - 18:00"
                  />
                </div>
              </div>

              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Smartphone className="w-4 h-4 text-emerald-400" />
                  <span>Contact & Social Links</span>
                </h3>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Support Phone</label>
                    <input
                      type="text"
                      value={profileForm.phone}
                      onChange={e => setProfileForm({ ...profileForm, phone: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                      placeholder="+91 98765 43210"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Official Email</label>
                    <input
                      type="email"
                      value={profileForm.email}
                      onChange={e => setProfileForm({ ...profileForm, email: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                      placeholder="hello@wingsflower.store"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Website URL</label>
                  <input
                    type="url"
                    value={profileForm.website}
                    onChange={e => setProfileForm({ ...profileForm, website: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                    placeholder="https://wingsflower.store"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">City / Region</label>
                    <input
                      type="text"
                      value={profileForm.city}
                      onChange={e => setProfileForm({ ...profileForm, city: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                      placeholder="Bengaluru"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Instagram Handle</label>
                    <input
                      type="text"
                      value={profileForm.instagram}
                      onChange={e => setProfileForm({ ...profileForm, instagram: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                      placeholder="@wingsflower"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Full Physical Store Address</label>
                  <textarea
                    rows={2}
                    value={profileForm.address}
                    onChange={e => setProfileForm({ ...profileForm, address: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                    placeholder="100 Feet Road, Indiranagar, Bengaluru, Karnataka 560038"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={saving}
                className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold transition shadow-lg shadow-emerald-900/30"
              >
                <Save className="w-4 h-4" />
                <span>{saving ? "Saving Changes..." : "Save Business Profile"}</span>
              </button>
            </div>
          </form>
        )}

        {/* TAB CONTENT: BRANDING & THEME WITH LIVE MOCKUP */}
        {activeTab === "branding" && (
          <form onSubmit={handleSaveBranding} className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Controls */}
              <div className="lg:col-span-7 space-y-4">
                <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Palette className="w-4 h-4 text-emerald-400" />
                    <span>Color Palette & Brand Customizer</span>
                  </h3>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs font-semibold text-slate-300 block mb-1.5">Primary Brand Accent</label>
                      <div className="flex items-center gap-3">
                        <input
                          type="color"
                          value={brandingForm.primary_color}
                          onChange={e => setBrandingForm({ ...brandingForm, primary_color: e.target.value })}
                          className="w-10 h-10 rounded-lg cursor-pointer bg-transparent border-0"
                        />
                        <input
                          type="text"
                          value={brandingForm.primary_color}
                          onChange={e => setBrandingForm({ ...brandingForm, primary_color: e.target.value })}
                          className="w-28 bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-slate-300 block mb-1.5">Secondary Tone</label>
                      <div className="flex items-center gap-3">
                        <input
                          type="color"
                          value={brandingForm.secondary_color}
                          onChange={e => setBrandingForm({ ...brandingForm, secondary_color: e.target.value })}
                          className="w-10 h-10 rounded-lg cursor-pointer bg-transparent border-0"
                        />
                        <input
                          type="text"
                          value={brandingForm.secondary_color}
                          onChange={e => setBrandingForm({ ...brandingForm, secondary_color: e.target.value })}
                          className="w-28 bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono"
                        />
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Logo Image URL</label>
                    <input
                      type="url"
                      value={brandingForm.logo_url}
                      onChange={e => setBrandingForm({ ...brandingForm, logo_url: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                      placeholder="https://clientdomain.com/logo.png"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-2">Interactive Button Style</label>
                    <div className="grid grid-cols-3 gap-3">
                      {["rounded", "pill", "square"].map((style) => (
                        <button
                          key={style}
                          type="button"
                          onClick={() => setBrandingForm({ ...brandingForm, button_style: style })}
                          className={`p-3 text-xs font-bold capitalize border transition ${
                            brandingForm.button_style === style
                              ? "bg-emerald-500/20 border-emerald-500 text-emerald-300"
                              : "bg-slate-950 border-slate-800 text-slate-400 hover:text-white"
                          } ${style === "pill" ? "rounded-full" : style === "square" ? "rounded-none" : "rounded-xl"}`}
                        >
                          {style} Shape
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={saving}
                    className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold transition shadow-lg shadow-emerald-900/30"
                  >
                    <Save className="w-4 h-4" />
                    <span>{saving ? "Saving..." : "Save Branding Theme"}</span>
                  </button>
                </div>
              </div>

              {/* Live WhatsApp Customer Phone Mockup */}
              <div className="lg:col-span-5 flex flex-col items-center">
                <div className="w-full max-w-[320px] rounded-[36px] border-4 border-slate-800 bg-[#0B141A] p-3 shadow-2xl shadow-emerald-950/20 flex flex-col h-[520px] relative overflow-hidden">
                  {/* Phone Notch */}
                  <div className="w-28 h-4 bg-slate-800 rounded-full mx-auto mb-2" />

                  {/* WhatsApp Header */}
                  <div className="flex items-center gap-2.5 pb-2.5 border-b border-slate-800/80">
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs text-white shadow"
                      style={{ backgroundColor: brandingForm.primary_color }}
                    >
                      {overview?.name?.charAt(0) || "W"}
                    </div>
                    <div className="flex-1 truncate">
                      <p className="text-xs font-bold text-slate-200 truncate">{overview?.name || "Wings Flower"}</p>
                      <p className="text-[10px] text-emerald-400 flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                        Online • Verified Business
                      </p>
                    </div>
                  </div>

                  {/* Chat Message Bubble */}
                  <div className="flex-1 py-3 space-y-3 overflow-y-auto text-xs">
                    <div className="bg-[#202C33] text-[#E9EDEF] p-3 rounded-2xl rounded-tl-none max-w-[85%] text-[11px] leading-relaxed shadow">
                      🌸 Welcome to {overview?.name || "Wings Flower"}! Reply 1 for Fresh Bouquets, 2 for Wedding Decor, or 3 for human florist assistance.
                      <span className="text-[9px] text-slate-400 block text-right mt-1">10:32 AM</span>
                    </div>

                    <div
                      className="ml-auto p-3 rounded-2xl rounded-tr-none max-w-[80%] text-[11px] text-white shadow leading-relaxed"
                      style={{ backgroundColor: brandingForm.secondary_color }}
                    >
                      Can you share your rose bouquet prices?
                      <span className="text-[9px] text-emerald-200 block text-right mt-1">10:33 AM ✓✓</span>
                    </div>

                    <div className="bg-[#202C33] text-[#E9EDEF] p-3 rounded-2xl rounded-tl-none max-w-[85%] text-[11px] leading-relaxed shadow space-y-2">
                      <p>✨ Here is our top-selling bouquet:</p>
                      <div className="p-2 rounded-xl bg-slate-900/80 border border-slate-800 text-[10px]">
                        <p className="font-bold text-white">Royal Velvet Rose Bouquet</p>
                        <p className="text-emerald-400 font-bold">₹1,499.00</p>
                      </div>

                      <button
                        type="button"
                        className={`w-full py-1.5 text-[10px] font-bold text-slate-950 transition shadow ${
                          brandingForm.button_style === "pill"
                            ? "rounded-full"
                            : brandingForm.button_style === "square"
                            ? "rounded-none"
                            : "rounded-lg"
                        }`}
                        style={{ backgroundColor: brandingForm.primary_color }}
                      >
                        Order via WhatsApp
                      </button>
                    </div>
                  </div>

                  {/* WhatsApp Composer Bar */}
                  <div className="pt-2 border-t border-slate-800/80 flex items-center gap-2 text-[11px] text-slate-400">
                    <div className="flex-1 bg-slate-900 px-3 py-1.5 rounded-full border border-slate-800 text-slate-500">
                      Message...
                    </div>
                    <div
                      className="w-7 h-7 rounded-full flex items-center justify-center text-slate-950 font-bold shadow"
                      style={{ backgroundColor: brandingForm.primary_color }}
                    >
                      <ArrowRight className="w-3.5 h-3.5" />
                    </div>
                  </div>
                </div>
                <p className="text-[11px] text-slate-500 mt-2 font-medium">Live Customer WhatsApp Preview</p>
              </div>
            </div>
          </form>
        )}

        {/* TAB CONTENT: PRODUCTS & SERVICES CATALOG */}
        {activeTab === "catalog" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white">Products & Services Catalog</h3>
                <p className="text-xs text-slate-400">
                  Used by AI and keyword automations to instantly answer pricing, availability, and ordering questions.
                </p>
              </div>
              <button
                onClick={() => {
                  setEditingProduct(null);
                  setProductForm({ name: "", description: "", category: "General", price: 0, currency: "INR", sku: "", is_available: true });
                  setProductModalOpen(true);
                }}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold transition shadow"
              >
                <Plus className="w-4 h-4" />
                <span>Add Product</span>
              </button>
            </div>

            {products.length === 0 ? (
              <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-slate-800 text-slate-400 space-y-3">
                <Package className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-sm font-semibold">No products in catalog yet</p>
                <p className="text-xs text-slate-500">Click &quot;Add Product&quot; or apply an industry blueprint to populate items.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {products.map(p => (
                  <div key={p.id} className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition">
                    <div>
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300">
                            {p.category || "General"}
                          </span>
                          <h4 className="text-sm font-bold text-white mt-1.5">{p.name}</h4>
                        </div>
                        <span className="text-sm font-extrabold text-emerald-400">
                          ₹{p.price?.toLocaleString()}
                        </span>
                      </div>
                      {p.description && (
                        <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">
                          {p.description}
                        </p>
                      )}
                      {p.sku && (
                        <p className="text-[10px] text-slate-500 font-mono mt-2">SKU: {p.sku}</p>
                      )}
                    </div>

                    <div className="flex items-center justify-between pt-3 mt-3 border-t border-slate-800/80 text-xs">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                        p.is_available ? "bg-emerald-500/15 text-emerald-400" : "bg-rose-500/15 text-rose-400"
                      }`}>
                        {p.is_available ? "In Stock" : "Out of Stock"}
                      </span>
                      <div className="flex items-center gap-1.5">
                        <button
                          onClick={() => {
                            setEditingProduct(p);
                            setProductForm({
                              name: p.name,
                              description: p.description || "",
                              category: p.category || "General",
                              price: p.price || 0,
                              currency: p.currency || "INR",
                              sku: p.sku || "",
                              is_available: p.is_available
                            });
                            setProductModalOpen(true);
                          }}
                          className="px-2 py-1 text-slate-400 hover:text-white rounded hover:bg-slate-800 transition"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteProduct(p.id)}
                          className="p-1 text-slate-500 hover:text-rose-400 rounded hover:bg-slate-800 transition"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB CONTENT: QUICK REPLIES */}
        {activeTab === "quick_replies" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white">Quick Replies & Canned Shortcuts</h3>
                <p className="text-xs text-slate-400">
                  Instant snippets your inbox agents can trigger using &quot;/shortcut&quot; in customer chats.
                </p>
              </div>
              <button
                onClick={() => setQuickReplyModalOpen(true)}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold transition shadow"
              >
                <Plus className="w-4 h-4" />
                <span>Add Quick Reply</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {quickReplies.map(qr => (
                <div key={qr.id} className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                          {qr.shortcut}
                        </span>
                        <h4 className="text-xs font-bold text-white">{qr.title}</h4>
                      </div>
                      <span className="text-[10px] text-slate-500">{qr.category}</span>
                    </div>
                    <p className="text-xs text-slate-300 bg-slate-950/70 p-3 rounded-xl border border-slate-800/80 leading-relaxed">
                      {qr.message}
                    </p>
                  </div>

                  <div className="flex justify-end gap-2 mt-3 pt-2 border-t border-slate-800/80">
                    <button
                      onClick={() => handleDeleteQuickReply(qr.id)}
                      className="p-1 text-slate-500 hover:text-rose-400 rounded transition"
                      title="Delete"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB CONTENT: SECTOR BLUEPRINTS (1-CLICK APPLY) */}
        {activeTab === "templates" && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-bold text-white">8 Commercial Industry Blueprints</h3>
              <p className="text-xs text-slate-400">
                1-click inject complete product catalogs, quick replies, greeting workflows, and color accents.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {templates.map(tpl => (
                <div key={tpl.id} className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between hover:border-emerald-500/40 transition group shadow-lg">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                        {tpl.category}
                      </span>
                      <div className="w-3.5 h-3.5 rounded-full border border-slate-700" style={{ backgroundColor: tpl.primary_color }} />
                    </div>

                    <h4 className="text-sm font-bold text-white group-hover:text-emerald-300 transition">
                      {tpl.name}
                    </h4>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      {tpl.description}
                    </p>

                    <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-1.5 text-[11px] text-slate-400">
                      <p>📦 {tpl.products?.length || 0} Sample Catalog Items</p>
                      <p>⚡ {tpl.quick_replies?.length || 0} Canned Shortcuts</p>
                      <p>🏷️ {tpl.lead_stages?.length || 0} Sales Stages</p>
                    </div>
                  </div>

                  <button
                    onClick={() => handleApplyTemplate(tpl.id, tpl.name)}
                    disabled={saving}
                    className="mt-5 w-full py-2 px-3 rounded-xl bg-slate-800 hover:bg-emerald-600 text-slate-200 hover:text-slate-950 text-xs font-bold transition flex items-center justify-center gap-1.5 border border-slate-700 hover:border-emerald-500 shadow"
                  >
                    <span>Apply Blueprint</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB CONTENT: AUTOMATION DEBUGGER */}
        {activeTab === "debugger" && (
          <div className="space-y-6">
            {/* Live Message Pipeline Simulator */}
            <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Play className="w-4 h-4 text-emerald-400" />
                <span>Live Pipeline Evaluator & Rule Test</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <input
                  type="text"
                  value={simPhone}
                  onChange={e => setSimPhone(e.target.value)}
                  placeholder="Sender Phone (e.g. 919876543210)"
                  className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                />
                <input
                  type="text"
                  value={simName}
                  onChange={e => setSimName(e.target.value)}
                  placeholder="Customer Name"
                  className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                />
                <input
                  type="text"
                  value={simMsg}
                  onChange={e => setSimMsg(e.target.value)}
                  placeholder="Incoming Message Text"
                  className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                />
              </div>

              <div className="flex justify-between items-center">
                <button
                  onClick={handleRunSimulation}
                  disabled={simLoading}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold transition shadow"
                >
                  {simLoading ? "Evaluating Trace..." : "Simulate Incoming Webhook"}
                </button>
              </div>

              {simResult && (
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-emerald-400 overflow-x-auto">
                  <pre>{JSON.stringify(simResult, null, 2)}</pre>
                </div>
              )}
            </div>

            {/* Recent Execution Traces */}
            <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
              <h3 className="text-sm font-bold text-white">Recent Automation Traces</h3>
              {traces.length === 0 ? (
                <p className="text-xs text-slate-500">No recent traces recorded.</p>
              ) : (
                <div className="space-y-2">
                  {traces.slice(0, 10).map(t => (
                    <div key={t.id} className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-slate-200">{t.flow_name}</span>
                          <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                            t.status === "SUCCESS" ? "bg-emerald-500/20 text-emerald-400" : "bg-rose-500/20 text-rose-400"
                          }`}>
                            {t.status}
                          </span>
                        </div>
                        {t.input_text && <p className="text-slate-400 text-[11px] mt-0.5">Input: &quot;{t.input_text}&quot;</p>}
                      </div>
                      <span className="text-[11px] text-slate-500 font-mono">{t.execution_time_ms}ms</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB CONTENT: VERSIONS & ROLLBACK */}
        {activeTab === "versions" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white">Client Configuration Snapshots</h3>
                <p className="text-xs text-slate-400">
                  Safely capture version checkpoints and rollback instantly if a client changes their mind.
                </p>
              </div>
              <button
                onClick={() => setVersionModalOpen(true)}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold transition shadow"
              >
                <History className="w-4 h-4" />
                <span>Create Snapshot</span>
              </button>
            </div>

            {versions.length === 0 ? (
              <div className="p-10 text-center rounded-2xl bg-slate-900/40 border border-slate-800 text-slate-500 text-xs">
                No snapshots saved yet. Click &quot;Create Snapshot&quot; to bookmark the current client setup.
              </div>
            ) : (
              <div className="space-y-3">
                {versions.map(v => (
                  <div key={v.id} className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex items-center justify-between text-xs">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white text-sm">{v.version_tag}</span>
                        <span className="text-[10px] text-slate-500">{new Date(v.created_at).toLocaleString()}</span>
                      </div>
                      {v.notes && <p className="text-slate-400 text-xs mt-1">{v.notes}</p>}
                      <p className="text-[10px] text-slate-500 mt-1 font-mono">By: {v.created_by || "Admin"}</p>
                    </div>

                    <button
                      onClick={() => handleRollback(v.id, v.version_tag)}
                      disabled={saving}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-amber-600 text-slate-200 hover:text-slate-950 font-bold text-xs transition border border-slate-700"
                    >
                      Rollback to this
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* MODAL: ADD / EDIT PRODUCT */}
        {productModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">
                  {editingProduct ? "Edit Product" : "Add Product to Catalog"}
                </h3>
                <button onClick={() => setProductModalOpen(false)} className="text-slate-400 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <form onSubmit={handleSaveProduct} className="space-y-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Product / Service Name</label>
                  <input
                    type="text"
                    value={productForm.name}
                    onChange={e => setProductForm({ ...productForm, name: e.target.value })}
                    required
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                    placeholder="e.g. Royal Velvet Rose Bouquet"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Category</label>
                    <input
                      type="text"
                      value={productForm.category}
                      onChange={e => setProductForm({ ...productForm, category: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                      placeholder="e.g. Bouquets"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Price (₹ INR)</label>
                    <input
                      type="number"
                      value={productForm.price}
                      onChange={e => setProductForm({ ...productForm, price: parseFloat(e.target.value) || 0 })}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                      placeholder="1499"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Description</label>
                  <textarea
                    rows={3}
                    value={productForm.description}
                    onChange={e => setProductForm({ ...productForm, description: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                    placeholder="Details, ingredients, or package highlights..."
                  />
                </div>

                <div className="flex items-center gap-2 pt-2">
                  <input
                    type="checkbox"
                    id="is_available"
                    checked={productForm.is_available}
                    onChange={e => setProductForm({ ...productForm, is_available: e.target.checked })}
                    className="rounded border-slate-800 bg-slate-950 text-emerald-500"
                  />
                  <label htmlFor="is_available" className="text-xs text-slate-300 font-semibold cursor-pointer">
                    Available in Stock for WhatsApp Ordering
                  </label>
                </div>

                <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setProductModalOpen(false)}
                    className="px-3 py-2 rounded-xl text-xs text-slate-400 hover:text-white"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={saving}
                    className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold"
                  >
                    {saving ? "Saving..." : "Save Product"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* MODAL: ADD QUICK REPLY */}
        {quickReplyModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">Add Quick Reply Shortcut</h3>
                <button onClick={() => setQuickReplyModalOpen(false)} className="text-slate-400 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <form onSubmit={handleSaveQuickReply} className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Shortcut</label>
                    <input
                      type="text"
                      value={quickReplyForm.shortcut}
                      onChange={e => setQuickReplyForm({ ...quickReplyForm, shortcut: e.target.value })}
                      required
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono"
                      placeholder="/catalog"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Title</label>
                    <input
                      type="text"
                      value={quickReplyForm.title}
                      onChange={e => setQuickReplyForm({ ...quickReplyForm, title: e.target.value })}
                      required
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                      placeholder="Send Flower Catalog"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Message Body</label>
                  <textarea
                    rows={4}
                    value={quickReplyForm.message}
                    onChange={e => setQuickReplyForm({ ...quickReplyForm, message: e.target.value })}
                    required
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                    placeholder="Write the exact text snippet to send..."
                  />
                </div>

                <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setQuickReplyModalOpen(false)}
                    className="px-3 py-2 rounded-xl text-xs text-slate-400 hover:text-white"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={saving}
                    className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold"
                  >
                    {saving ? "Saving..." : "Add Shortcut"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* MODAL: CLONE CLIENT */}
        {cloneModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Copy className="w-4 h-4 text-emerald-400" />
                  <h3 className="text-sm font-bold text-white">Clone Client Workspace</h3>
                </div>
                <button onClick={() => setCloneModalOpen(false)} className="text-slate-400 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <p className="text-xs text-slate-400 leading-relaxed">
                Duplicates flows, rules, products, branding, and templates to a new client account.
                <span className="block mt-1 font-semibold text-emerald-400">
                  🛡️ Meta credentials, tokens, contacts, and customer chat messages are strictly excluded.
                </span>
              </p>

              <form onSubmit={handleCloneClient} className="space-y-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">New Client Business Name</label>
                  <input
                    type="text"
                    value={cloneForm.target_name}
                    onChange={e => setCloneForm({ ...cloneForm, target_name: e.target.value })}
                    required
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                    placeholder="e.g. Wings Flower - Indiranagar Branch"
                  />
                </div>

                <div className="space-y-2 pt-2 text-xs">
                  {[
                    { key: "copy_branding", label: "Copy Theme & Branding Styles" },
                    { key: "copy_products", label: "Copy Products & Services Catalog" },
                    { key: "copy_quick_replies", label: "Copy Canned Quick Replies" },
                    { key: "copy_flows", label: "Copy Automation Flows & Rules" },
                    { key: "copy_templates", label: "Copy Message Templates" }
                  ].map((opt: any) => (
                    <label key={opt.key} className="flex items-center gap-2 text-slate-300 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={(cloneForm as any)[opt.key]}
                        onChange={e => setCloneForm({ ...cloneForm, [opt.key]: e.target.checked })}
                        className="rounded border-slate-800 bg-slate-950 text-emerald-500"
                      />
                      <span>{opt.label}</span>
                    </label>
                  ))}
                </div>

                <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setCloneModalOpen(false)}
                    className="px-3 py-2 rounded-xl text-xs text-slate-400 hover:text-white"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={saving}
                    className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold shadow"
                  >
                    {saving ? "Cloning Workspace..." : "Create Cloned Client"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* MODAL: SNAPSHOT */}
        {versionModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
            <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">Create Configuration Snapshot</h3>
                <button onClick={() => setVersionModalOpen(false)} className="text-slate-400 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <form onSubmit={handleCreateSnapshot} className="space-y-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Version Tag</label>
                  <input
                    type="text"
                    value={versionTag}
                    onChange={e => setVersionTag(e.target.value)}
                    required
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                    placeholder="e.g. v1.0-launch or florist-custom-v2"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Notes / Description</label>
                  <textarea
                    rows={3}
                    value={versionNotes}
                    onChange={e => setVersionNotes(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                    placeholder="What changed in this configuration snapshot?"
                  />
                </div>

                <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setVersionModalOpen(false)}
                    className="px-3 py-2 rounded-xl text-xs text-slate-400 hover:text-white"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={saving}
                    className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold"
                  >
                    {saving ? "Saving Snapshot..." : "Save Snapshot"}
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
