const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiClient {
  private static getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("allstreak_token");
  }

  private static getWorkspaceId(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("allstreak_workspace_id");
  }

  public static setAuth(token: string, workspaceId: string) {
    if (typeof window === "undefined") return;
    localStorage.setItem("allstreak_token", token);
    localStorage.setItem("allstreak_workspace_id", workspaceId);
  }

  public static clearAuth() {
    if (typeof window === "undefined") return;
    localStorage.removeItem("allstreak_token");
    localStorage.removeItem("allstreak_workspace_id");
  }

  private static async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const workspaceId = this.getWorkspaceId();

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    if (workspaceId) {
      headers["X-Workspace-ID"] = workspaceId;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      // If unauthorized, redirect to login if client-side
      if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
        // window.location.href = "/login";
      }
    }

    if (!response.ok) {
      let errorMsg = "API request failed";
      try {
        const errJson = await response.json();
        errorMsg = errJson.detail || JSON.stringify(errJson);
      } catch {
        errorMsg = await response.text();
      }
      throw new Error(errorMsg);
    }

    return response.json();
  }

  // Auth
  static async login(email: string, password: string) {
    const data = await this.request<any>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    this.setAuth(data.access_token, data.workspace_id);
    return data;
  }

  static async register(payload: { email: string; password: string; full_name: string; workspace_name?: string }) {
    const data = await this.request<any>("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    this.setAuth(data.access_token, data.workspace_id);
    return data;
  }

  static async getMe() {
    return this.request<any>("/api/v1/auth/me");
  }

  // Workspace & Onboarding
  static async getWorkspace() {
    return this.request<any>("/api/v1/workspace");
  }

  static async updateWorkspace(payload: any) {
    return this.request<any>("/api/v1/workspace", {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }

  static async submitOnboarding(payload: any) {
    return this.request<any>("/api/v1/workspace/onboarding", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  // Dashboard
  static async getDashboardMetrics() {
    return this.request<any>("/api/v1/dashboard");
  }

  // Conversations & Team Inbox
  static async getConversations(params?: { tab?: string; conv_status?: string; search?: string }) {
    const q = new URLSearchParams();
    if (params?.tab) q.set("tab", params.tab);
    if (params?.conv_status) q.set("conv_status", params.conv_status);
    if (params?.search) q.set("search", params.search);
    return this.request<any[]>(`/api/v1/conversations?${q.toString()}`);
  }

  static async startConversation(payload: { phone: string; name?: string; initial_message?: string; template_name?: string; mode?: string }) {
    return this.request<any>("/api/v1/conversations/start", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  static async getConversation(id: string) {
    return this.request<any>(`/api/v1/conversations/${id}`);
  }

  static async getMessages(conversationId: string) {
    return this.request<any[]>(`/api/v1/conversations/${conversationId}/messages`);
  }

  static async sendMessage(conversationId: string, payload: { body?: string; buttons?: string[]; message_type?: string }) {
    return this.request<any>(`/api/v1/conversations/${conversationId}/reply`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  static async sendTemplate(conversationId: string, payload: { template_name: string; language_code?: string; variable_values?: Record<string, string> }) {
    return this.request<any>(`/api/v1/conversations/${conversationId}/reply-template`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  static async triggerHandover(conversationId: string, reason?: string) {
    return this.request<any>(`/api/v1/conversations/${conversationId}/handover`, {
      method: "POST",
      body: JSON.stringify({ reason: reason || "Manual takeover by agent" }),
    });
  }

  static async returnToAutomation(conversationId: string, target_mode: string = "BOT") {
    return this.request<any>(`/api/v1/conversations/${conversationId}/return-to-automation`, {
      method: "POST",
      body: JSON.stringify({ target_mode }),
    });
  }

  static async resolveConversation(conversationId: string) {
    return this.request<any>(`/api/v1/conversations/${conversationId}/resolve`, {
      method: "POST",
    });
  }

  // Leads CRM
  static async getLeads(status?: string, search?: string) {
    const q = new URLSearchParams();
    if (status) q.set("lead_status", status);
    if (search) q.set("search", search);
    return this.request<any[]>(`/api/v1/leads?${q.toString()}`);
  }

  static async getLeadKanban() {
    return this.request<any>("/api/v1/leads/kanban");
  }

  static async updateLeadStage(leadId: string, stage: string, notes?: string) {
    return this.request<any>(`/api/v1/leads/${leadId}/stage`, {
      method: "PUT",
      body: JSON.stringify({ status: stage, notes }),
    });
  }

  static async convertLead(leadId: string) {
    return this.request<any>(`/api/v1/leads/${leadId}/convert`, {
      method: "POST",
    });
  }

  static async createLead(payload: any) {
    return this.request<any>("/api/v1/leads", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  // Contacts
  static async getContacts(search?: string) {
    const q = new URLSearchParams();
    if (search) q.set("search", search);
    return this.request<any[]>(`/api/v1/contacts?${q.toString()}`);
  }

  static async getContact(id: string) {
    return this.request<any>(`/api/v1/contacts/${id}`);
  }

  static async createContact(payload: { phone: string; name?: string; email?: string; notes?: string }) {
    return this.request<any>("/api/v1/contacts", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  // Automations & Rules
  static async getFlows() {
    return this.request<any[]>("/api/v1/automations/flows");
  }

  static async createFlow(payload: any) {
    return this.request<any>("/api/v1/automations/flows", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  static async updateFlow(id: string, payload: any) {
    return this.request<any>(`/api/v1/automations/flows/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }

  static async testSimulation(message_text: string, contact_phone?: string) {
    return this.request<any>("/api/v1/automations/test-simulation", {
      method: "POST",
      body: JSON.stringify({ message_text, contact_phone }),
    });
  }

  static async getRules() {
    return this.request<any[]>("/api/v1/automations/rules");
  }

  static async createRule(payload: any) {
    return this.request<any>("/api/v1/automations/rules", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  // Templates
  static async getTemplates() {
    return this.request<any[]>("/api/v1/templates");
  }

  static async getTemplatePricingSummary() {
    return this.request<any>("/api/v1/templates/pricing-summary");
  }

  static async createTemplate(payload: any) {
    return this.request<any>("/api/v1/templates", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  static async syncTemplates() {
    return this.request<any>("/api/v1/templates/sync", {
      method: "POST",
    });
  }

  // Knowledge Base & AI
  static async getKnowledgeBases() {
    return this.request<any[]>("/api/v1/knowledge");
  }

  static async queryKnowledgeTest(query: string) {
    return this.request<any>("/api/v1/knowledge/query-test", {
      method: "POST",
      body: JSON.stringify({ query }),
    });
  }

  static async getAISettings() {
    return this.request<any>("/api/v1/ai/settings");
  }

  static async updateAISettings(payload: any) {
    return this.request<any>("/api/v1/ai/settings", {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }

  // Team
  static async getTeam() {
    return this.request<any[]>("/api/v1/team");
  }

  static async inviteTeamMember(payload: any) {
    return this.request<any>("/api/v1/team/invite", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  // Integrations
  static async getWhatsAppIntegration() {
    return this.request<any>("/api/v1/integrations/whatsapp");
  }

  static async connectWhatsApp(payload: any) {
    return this.request<any>("/api/v1/integrations/whatsapp/connect", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  static async getWhatsAppWebhookInfo() {
    return this.request<any>("/api/v1/integrations/whatsapp/webhook-info");
  }

  static async sendTestWhatsAppMessage(to_phone: string, message?: string) {
    return this.request<any>("/api/v1/integrations/whatsapp/send-test-message", {
      method: "POST",
      body: JSON.stringify({ to_phone, message }),
    });
  }

  static async testWhatsAppConnection() {
    return this.request<any>("/api/v1/integrations/whatsapp/test", {
      method: "POST",
    });
  }

  static async disconnectWhatsApp() {
    return this.request<any>("/api/v1/integrations/whatsapp", {
      method: "DELETE",
    });
  }

  // Global Search
  static async globalSearch(query: string) {
    return this.request<any>(`/api/v1/search?q=${encodeURIComponent(query)}`);
  }

  // System Health
  static async getSystemHealth() {
    return this.request<any>("/api/v1/system/health");
  }

  // Sandbox Live Message Simulator
  static async simulateSandboxMessage(phone: string, name: string, message: string) {
    return this.request<any>("/api/v1/sandbox/simulate-message", {
      method: "POST",
      body: JSON.stringify({ phone, name, message }),
    });
  }

  // Client Customization Studio
  static async getClientSetupOverview() {
    return this.request<any>("/api/v1/client-setup/overview");
  }

  static async updateBusinessProfile(payload: any) {
    return this.request<any>("/api/v1/client-setup/profile", {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }

  static async updateBranding(payload: any) {
    return this.request<any>("/api/v1/client-setup/branding", {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }

  // Products & Services Catalog
  static async listProducts() {
    return this.request<any[]>("/api/v1/client-setup/products");
  }

  static async createProduct(payload: any) {
    return this.request<any>("/api/v1/client-setup/products", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  static async updateProduct(id: string, payload: any) {
    return this.request<any>(`/api/v1/client-setup/products/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }

  static async deleteProduct(id: string) {
    return this.request<any>(`/api/v1/client-setup/products/${id}`, {
      method: "DELETE",
    });
  }

  // Quick Replies
  static async listQuickReplies() {
    return this.request<any[]>("/api/v1/client-setup/quick-replies");
  }

  static async createQuickReply(payload: any) {
    return this.request<any>("/api/v1/client-setup/quick-replies", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  static async updateQuickReply(id: string, payload: any) {
    return this.request<any>(`/api/v1/client-setup/quick-replies/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  }

  static async deleteQuickReply(id: string) {
    return this.request<any>(`/api/v1/client-setup/quick-replies/${id}`, {
      method: "DELETE",
    });
  }

  // Industry Blueprints
  static async listIndustryTemplates() {
    return this.request<any[]>("/api/v1/client-setup/templates");
  }

  static async applyIndustryTemplate(templateId: string) {
    return this.request<any>(`/api/v1/client-setup/templates/${templateId}/apply`, {
      method: "POST",
    });
  }

  // Client Clone Engine
  static async cloneClientWorkspace(payload: any) {
    return this.request<any>("/api/v1/client-setup/clone", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  // Version Snapshots & Rollback
  static async listVersions() {
    return this.request<any[]>("/api/v1/client-setup/versions");
  }

  static async createVersionSnapshot(versionTag: string, notes?: string) {
    return this.request<any>("/api/v1/client-setup/versions", {
      method: "POST",
      body: JSON.stringify({ version_tag: versionTag, notes }),
    });
  }

  static async rollbackVersion(versionId: string) {
    return this.request<any>(`/api/v1/client-setup/versions/${versionId}/rollback`, {
      method: "POST",
    });
  }

  // AI Response Suggester
  static async getAISuggestions(conversationId: string) {
    return this.request<any>("/api/v1/inbox/suggest", {
      method: "POST",
      body: JSON.stringify({ conversation_id: conversationId }),
    });
  }

  // Automation Debugger & Webhook Traces
  static async getDebuggerTraces() {
    return this.request<any[]>("/api/v1/debugger/traces");
  }

  static async getDebuggerWebhooks() {
    return this.request<any[]>("/api/v1/debugger/webhooks");
  }

  static async simulateWebhookPipeline(payload: any) {
    return this.request<any>("/api/v1/debugger/simulate-webhook", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }
}


