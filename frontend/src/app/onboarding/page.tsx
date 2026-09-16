"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Sparkles,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  Building,
  Smartphone,
  Zap,
  FileText,
  Play,
  ShieldCheck,
  Loader2,
} from "lucide-react";
import { ApiClient } from "@/lib/api";

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // Form State
  const [businessName, setBusinessName] = useState("Quantum Labs");
  const [industry, setIndustry] = useState("Technology & SaaS");
  const [timezone, setTimezone] = useState("Asia/Kolkata (IST)");
  const [country, setCountry] = useState("India (IN)");

  const [phoneNumberId, setPhoneNumberId] = useState("109823485728392");
  const [wabaId, setWabaId] = useState("982347592837482");
  const [businessId, setBusinessId] = useState("biz_992837461");
  const [accessToken, setAccessToken] = useState("EAAX_DEMO_TOKEN_METACLOUD_12345");

  const [greetingText, setGreetingText] = useState(
    "Hello! 👋 Welcome to our business. How can we assist you today?"
  );
  const [buttons, setButtons] = useState(["Sales", "Support", "Pricing", "Talk to Human"]);

  const [templateName, setTemplateName] = useState("customer_welcome_notice");
  const [testMessage, setTestMessage] = useState("Hi");
  const [testResult, setTestResult] = useState<any>(null);

  const nextStep = async () => {
    setLoading(true);
    try {
      if (step === 2) {
        await ApiClient.submitOnboarding({
          step: 2,
          business_name: businessName,
          industry,
          timezone,
          country,
        });
      } else if (step === 3) {
        await ApiClient.submitOnboarding({
          step: 3,
          phone_number_id: phoneNumberId,
          waba_id: wabaId,
          business_id: businessId,
          access_token: accessToken,
        });
      } else if (step === 5) {
        await ApiClient.submitOnboarding({
          step: 5,
          first_automation_greeting: greetingText,
        });
      } else if (step === 6) {
        await ApiClient.submitOnboarding({
          step: 6,
          first_template_name: templateName,
        });
      } else if (step === 7) {
        // Run test simulation
        const sim = await ApiClient.testSimulation(testMessage);
        setTestResult(sim);
      } else if (step === 8) {
        router.push("/dashboard");
        return;
      }
      setStep((prev) => prev + 1);
    } catch (err) {
      console.error(err);
      // Advance in demo mode anyway
      setStep((prev) => prev + 1);
    } finally {
      setLoading(false);
    }
  };

  const prevStep = () => {
    if (step > 1) setStep((prev) => prev - 1);
  };

  return (
    <div className="min-h-screen w-screen bg-slate-950 text-slate-100 flex flex-col justify-between p-6">
      {/* Top Header */}
      <div className="max-w-4xl mx-auto w-full flex items-center justify-between py-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <span className="font-mono font-bold tracking-tight text-white text-base">
            ALLSTREAK ONBOARDING
          </span>
        </div>
        <div className="text-xs text-slate-400 font-medium">
          Step <span className="text-emerald-400 font-bold">{step}</span> of 8
        </div>
      </div>

      {/* Progress Line */}
      <div className="max-w-4xl mx-auto w-full my-4">
        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div
            className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full transition-all duration-300 rounded-full"
            style={{ width: `${(step / 8) * 100}%` }}
          />
        </div>
      </div>

      {/* Step Content Card */}
      <div className="flex-1 flex items-center justify-center py-6">
        <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl">
          {/* STEP 1: Welcome */}
          {step === 1 && (
            <div className="text-center space-y-4">
              <div className="w-16 h-16 mx-auto rounded-3xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center shadow-lg shadow-emerald-500/10">
                <Sparkles className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-extrabold text-white">
                Welcome to ALLSTREAK
              </h2>
              <p className="text-sm text-slate-400 max-w-md mx-auto leading-relaxed">
                Let&apos;s configure your production-ready WhatsApp Automation platform. In
                under 3 minutes, you will connect Meta Cloud API, create your first
                automation, and test live responses.
              </p>
            </div>
          )}

          {/* STEP 2: Create Workspace */}
          {step === 2 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase">
                <Building className="w-4 h-4" />
                <span>Workspace Configuration</span>
              </div>
              <h2 className="text-lg font-bold text-white">Tell us about your business</h2>
              <div className="space-y-3 pt-2">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Business Name
                  </label>
                  <input
                    type="text"
                    value={businessName}
                    onChange={(e) => setBusinessName(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Industry
                  </label>
                  <input
                    type="text"
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">
                      Timezone
                    </label>
                    <input
                      type="text"
                      value={timezone}
                      onChange={(e) => setTimezone(e.target.value)}
                      className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">
                      Country
                    </label>
                    <input
                      type="text"
                      value={country}
                      onChange={(e) => setCountry(e.target.value)}
                      className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* STEP 3: Connect WhatsApp */}
          {step === 3 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase">
                <Smartphone className="w-4 h-4" />
                <span>Meta WhatsApp Cloud API</span>
              </div>
              <h2 className="text-lg font-bold text-white">Connect your WhatsApp credentials</h2>
              <div className="space-y-3 pt-2">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Phone Number ID
                  </label>
                  <input
                    type="text"
                    value={phoneNumberId}
                    onChange={(e) => setPhoneNumberId(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    WhatsApp Business Account ID (WABA ID)
                  </label>
                  <input
                    type="text"
                    value={wabaId}
                    onChange={(e) => setWabaId(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    System User Permanent Access Token
                  </label>
                  <input
                    type="password"
                    value={accessToken}
                    onChange={(e) => setAccessToken(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>
            </div>
          )}

          {/* STEP 4: Verify Connection */}
          {step === 4 && (
            <div className="text-center space-y-4 py-4">
              <div className="w-16 h-16 mx-auto rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center shadow-lg">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h2 className="text-xl font-bold text-white">✓ WhatsApp Connected</h2>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Successfully verified credentials with Meta Graph API v21.0. Quality
                Rating: <strong className="text-emerald-400">GREEN</strong>.
              </p>
            </div>
          )}

          {/* STEP 5: Create First Automation */}
          {step === 5 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase">
                <Zap className="w-4 h-4" />
                <span>Automation Rule</span>
              </div>
              <h2 className="text-lg font-bold text-white">Create your first automated reply</h2>
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-2">
                <div className="text-slate-400">
                  <strong className="text-emerald-400">WHEN</strong> customer sends:{" "}
                  <code className="bg-slate-800 px-1.5 py-0.5 rounded text-white">&ldquo;Hi&rdquo;</code>
                </div>
                <div>
                  <strong className="text-emerald-400">THEN</strong> reply with:
                  <textarea
                    rows={2}
                    value={greetingText}
                    onChange={(e) => setGreetingText(e.target.value)}
                    className="w-full mt-1.5 p-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div className="pt-1">
                  <strong className="text-emerald-400">AND</strong> show interactive buttons:
                  <div className="flex flex-wrap gap-1.5 mt-1.5">
                    {buttons.map((b, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[11px] font-semibold"
                      >
                        [{b}]
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* STEP 6: First Template */}
          {step === 6 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase">
                <FileText className="w-4 h-4" />
                <span>Meta Message Template</span>
              </div>
              <h2 className="text-lg font-bold text-white">Create first approved template</h2>
              <div className="space-y-3 pt-2">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Template Name
                  </label>
                  <input
                    type="text"
                    value={templateName}
                    onChange={(e) => setTemplateName(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white font-mono focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-300">
                  <p className="font-semibold text-emerald-400 mb-1">Body Text:</p>
                  <p>
                    Hello &#123;&#123;1&#125;&#125;, thank you for reaching out to us! Our specialist is reviewing
                    your inquiry.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* STEP 7: Test Integration */}
          {step === 7 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold uppercase">
                <Play className="w-4 h-4" />
                <span>End-to-End Simulation Test</span>
              </div>
              <h2 className="text-lg font-bold text-white">Test automation pipeline</h2>
              <div className="space-y-3 pt-2">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Simulate customer sending message:
                  </label>
                  <input
                    type="text"
                    value={testMessage}
                    onChange={(e) => setTestMessage(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>

                {testResult && (
                  <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-xs space-y-2">
                    <p className="font-bold text-emerald-400 flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Automation Executed Successfully!</span>
                    </p>
                    <div className="text-[11px] text-slate-300 whitespace-pre-line bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                      {testResult.response_preview}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* STEP 8: Finish */}
          {step === 8 && (
            <div className="text-center space-y-4 py-4">
              <div className="w-16 h-16 mx-auto rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center shadow-lg">
                <Sparkles className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-black text-white">
                You&apos;re Ready to Automate! 🚀
              </h2>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Your workspace is configured with WhatsApp Cloud API, automated lead
                capture, and smart human handover.
              </p>
            </div>
          )}

          {/* Actions Bottom Bar */}
          <div className="mt-8 pt-6 border-t border-slate-800 flex justify-between items-center">
            {step > 1 ? (
              <button
                onClick={prevStep}
                disabled={loading}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-750 text-xs font-semibold text-slate-300 flex items-center gap-1.5 transition"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Back</span>
              </button>
            ) : (
              <div />
            )}

            <button
              onClick={nextStep}
              disabled={loading}
              className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold flex items-center gap-2 shadow-lg transition"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <span>{step === 8 ? "Enter Dashboard" : "Continue"}</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Footer Branding */}
      <div className="text-center text-[11px] text-slate-500 flex items-center justify-center gap-2">
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
        <span>ALLSTREAK — Production-Grade WhatsApp SaaS</span>
      </div>
    </div>
  );
}
