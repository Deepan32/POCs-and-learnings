"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { GlobalSearchModal } from "@/components/search/GlobalSearchModal";
import { SandboxPhoneModal } from "@/components/sandbox/SandboxPhoneModal";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isSandboxOpen, setIsSandboxOpen] = useState(false);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 dark">
      {/* Navigation Sidebar */}
      <Sidebar onOpenSandbox={() => setIsSandboxOpen(true)} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopBar
          onOpenSearch={() => setIsSearchOpen(true)}
          onOpenSandbox={() => setIsSandboxOpen(true)}
        />
        <main className="flex-1 overflow-y-auto bg-slate-900/50">{children}</main>
      </div>

      {/* Global Modals */}
      <GlobalSearchModal isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
      <SandboxPhoneModal isOpen={isSandboxOpen} onClose={() => setIsSandboxOpen(false)} />
    </div>
  );
}
