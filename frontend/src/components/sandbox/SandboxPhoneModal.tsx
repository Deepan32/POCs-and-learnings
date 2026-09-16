"use client";

import React, { useState } from "react";
import {
  X,
  Send,
  User,
  ShieldAlert,
  Sparkles,
  Bot,
  CheckCheck,
  Headphones,
  ArrowRight,
  RefreshCcw,
} from "lucide-react";
import { ApiClient } from "@/lib/api";

interface SandboxPhoneModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ChatBubble {
  id: string;
  sender: "customer" | "bot" | "human";
  text: string;
  time: string;
  buttons?: string[];
}

export function SandboxPhoneModal({ isOpen, onClose }: SandboxPhoneModalProps) {
  const [messages, setMessages] = useState<ChatBubble[]>([
    {
      id: "1",
      sender: "customer",
      text: "Hi",
      time: "12:00 PM",
    },
    {
      id: "2",
      sender: "bot",
      text: "Hello! 👋 Welcome to ALLSTREAK. How can we help you accelerate your business today?",
      time: "12:00 PM",
      buttons: ["Sales", "Support", "Pricing", "Talk to Human"],
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [handoverActive, setHandoverActive] = useState(false);

  if (!isOpen) return null;

  const sendMessage = async (textToSend: string) => {
    if (!textToSend.trim()) return;

    const newMsg: ChatBubble = {
      id: String(Date.now()),
      sender: "customer",
      text: textToSend,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, newMsg]);
    setInputText("");
    setLoading(true);

    try {
      // Call backend sandbox simulation endpoint
      const result = await ApiClient.simulateSandboxMessage(
        "+919876543210",
        "Sandbox Demo Tester",
        textToSend
      );

      if (result.reply_received && result.latest_reply) {
        setMessages((prev) => [
          ...prev,
          {
            id: String(Date.now() + 1),
            sender: result.is_handover ? "human" : "bot",
            text: result.latest_reply || "",
            time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
            buttons: result.buttons || undefined,
          },
        ]);
      }

      if (result.is_handover) {
        setHandoverActive(true);
      }
    } catch (err) {
      console.error("Sandbox simulation failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleButtonClick = (btnText: string) => {
    sendMessage(btnText);
  };

  const resetSandbox = () => {
    setHandoverActive(false);
    setMessages([
      {
        id: "1",
        sender: "customer",
        text: "Hi",
        time: "12:00 PM",
      },
      {
        id: "2",
        sender: "bot",
        text: "Hello! 👋 Welcome to ALLSTREAK. How can we help you accelerate your business today?",
        time: "12:00 PM",
        buttons: ["Sales", "Support", "Pricing", "Talk to Human"],
      },
    ]);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="relative flex flex-col items-center">
        {/* Top Sandbox Notice Badge */}
        <div className="mb-3 px-4 py-1.5 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs font-semibold flex items-center gap-2 shadow-lg">
          <ShieldAlert className="w-4 h-4 text-amber-400" />
          <span>ALLSTREAK SANDBOX SIMULATOR — NO REAL WHATSAPP MESSAGES SENT</span>
          <button
            onClick={resetSandbox}
            className="ml-2 px-2 py-0.5 rounded bg-amber-500/30 hover:bg-amber-500/50 text-white text-[10px] font-bold flex items-center gap-1 transition"
          >
            <RefreshCcw className="w-3 h-3" />
            <span>Reset</span>
          </button>
        </div>

        {/* Mobile Phone Mockup Frame */}
        <div className="w-[380px] h-[660px] bg-slate-900 border-[10px] border-slate-800 rounded-[45px] shadow-[0_25px_60px_-15px_rgba(0,0,0,0.8)] flex flex-col overflow-hidden relative">
          {/* Phone Speaker Notch */}
          <div className="absolute top-2 left-1/2 -translate-x-1/2 w-32 h-4 bg-slate-800 rounded-full z-20 flex items-center justify-center">
            <div className="w-10 h-1.5 bg-slate-700 rounded-full" />
          </div>

          {/* WhatsApp Header */}
          <div className="pt-7 pb-3 px-4 bg-[#1f2c34] text-white flex items-center justify-between border-b border-[#2a3942] z-10">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-9 h-9 rounded-full bg-emerald-700 flex items-center justify-center font-bold text-sm">
                  A
                </div>
                <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-400 rounded-full border-2 border-[#1f2c34]" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="font-semibold text-sm">ALLSTREAK Demo</span>
                  <span className="text-[10px] px-1 rounded bg-emerald-500/20 text-emerald-300">
                    Official
                  </span>
                </div>
                <p className="text-[10px] text-emerald-400 font-medium">
                  {handoverActive ? "Agent Connected (Human)" : "Online (Streak Bot)"}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-full transition"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Handover Notice Banner */}
          {handoverActive && (
            <div className="px-3 py-1.5 bg-indigo-950/80 border-b border-indigo-500/40 text-indigo-200 text-[11px] flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <Headphones className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
                <span>Human Handover Active!</span>
              </div>
              <span className="text-[9px] uppercase font-bold text-indigo-300">Agent Mode</span>
            </div>
          )}

          {/* Chat Messages Body */}
          <div className="flex-1 whatsapp-bg overflow-y-auto p-3 space-y-3">
            <div className="text-center my-1">
              <span className="text-[10px] px-2.5 py-1 rounded-md bg-slate-800/80 text-slate-400 shadow-sm">
                Today
              </span>
            </div>

            {messages.map((m) => {
              const isCustomer = m.sender === "customer";
              return (
                <div
                  key={m.id}
                  className={`flex flex-col ${isCustomer ? "items-end" : "items-start"}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-3 py-2 text-xs shadow-sm relative ${
                      isCustomer
                        ? "bg-[#005c4b] text-white rounded-tr-none"
                        : "bg-[#202c33] text-slate-100 rounded-tl-none"
                    }`}
                  >
                    {!isCustomer && (
                      <div className="flex items-center gap-1 text-[10px] font-bold text-emerald-400 mb-0.5">
                        {m.sender === "bot" ? (
                          <>
                            <Bot className="w-3 h-3" />
                            <span>Streak Bot</span>
                          </>
                        ) : (
                          <>
                            <Headphones className="w-3 h-3 text-indigo-400" />
                            <span className="text-indigo-400">Human Specialist</span>
                          </>
                        )}
                      </div>
                    )}
                    <p className="leading-relaxed whitespace-pre-line">{m.text}</p>
                    <div className="flex items-center justify-end gap-1 mt-1 text-[9px] text-slate-400">
                      <span>{m.time}</span>
                      {isCustomer && <CheckCheck className="w-3 h-3 text-sky-400" />}
                    </div>
                  </div>

                  {/* Interactive Buttons (WhatsApp Quick Reply Buttons) */}
                  {m.buttons && m.buttons.length > 0 && (
                    <div className="mt-1.5 flex flex-wrap gap-1.5 max-w-[85%]">
                      {m.buttons.map((btn, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleButtonClick(btn)}
                          className="px-3 py-1.5 rounded-lg bg-[#202c33] hover:bg-[#2a3942] border border-[#00a884]/40 text-[#00a884] hover:text-emerald-300 text-xs font-semibold shadow transition active:scale-95"
                        >
                          {btn}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}

            {loading && (
              <div className="flex items-start">
                <div className="bg-[#202c33] text-slate-400 rounded-2xl rounded-tl-none px-3 py-2 text-xs flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce" />
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce [animation-delay:0.2s]" />
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            )}
          </div>

          {/* WhatsApp Composer Bottom */}
          <div className="p-2.5 bg-[#202c33] border-t border-[#2a3942] flex items-center gap-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage(inputText)}
              placeholder="Type a message (e.g. 'Hi' or 'pricing')..."
              className="flex-1 bg-[#2a3942] text-white placeholder-slate-400 text-xs rounded-full px-3.5 py-2 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
            <button
              onClick={() => sendMessage(inputText)}
              disabled={!inputText.trim()}
              className="w-8 h-8 rounded-full bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white flex items-center justify-center transition"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
