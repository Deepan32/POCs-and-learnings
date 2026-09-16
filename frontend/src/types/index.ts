export type Role = "OWNER" | "ADMIN" | "AGENT";

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone_number?: string;
  avatar_url?: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  industry?: string;
  timezone: string;
  country: string;
  is_active: boolean;
  business_hours_config?: string;
  created_at: string;
  role?: Role;
}

export interface WhatsAppAccount {
  id: string;
  workspace_id: string;
  phone_number_id: string;
  waba_id: string;
  business_id?: string;
  display_phone_number?: string;
  verified_name?: string;
  is_active: boolean;
  quality_rating: string;
  webhook_verify_token: string;
  created_at: string;
}

export interface Tag {
  id: string;
  name: string;
  color: string;
}

export interface Contact {
  id: string;
  workspace_id: string;
  whatsapp_id: string;
  phone: string;
  name?: string;
  email?: string;
  avatar_url?: string;
  conversation_count: number;
  last_active_at?: string;
  created_at: string;
  tags: Tag[];
}

export type ConversationMode = "BOT" | "AI" | "HUMAN";
export type ConversationStatus = "OPEN" | "RESOLVED" | "SNOOZED";

export interface Conversation {
  id: string;
  workspace_id: string;
  contact_id: string;
  assigned_agent_id?: string;
  mode: ConversationMode;
  status: ConversationStatus;
  unread_count: number;
  last_message_preview?: string;
  last_message_at?: string;
  last_customer_message_at?: string;
  window_expires_at?: string;
  is_window_open: boolean;
  handover_reason?: string;
  handover_at?: string;
  lead_id?: string;
  created_at: string;
  contact?: Contact;
  assigned_agent?: User;
}

export type MessageDirection = "INBOUND" | "OUTBOUND";
export type MessageOrigin = "CUSTOMER" | "BOT" | "AI" | "HUMAN";
export type MessageDeliveryStatus = "PENDING" | "SENT" | "DELIVERED" | "READ" | "FAILED";
export type MessageType = "TEXT" | "IMAGE" | "VIDEO" | "AUDIO" | "DOCUMENT" | "LOCATION" | "INTERACTIVE" | "BUTTON" | "TEMPLATE";

export interface Message {
  id: string;
  conversation_id: string;
  sender_id?: string;
  meta_message_id?: string;
  direction: MessageDirection;
  origin: MessageOrigin;
  status: MessageDeliveryStatus;
  message_type: MessageType;
  body?: string;
  buttons_json?: string;
  template_name?: string;
  is_from_template: boolean;
  sent_at?: string;
  delivered_at?: string;
  read_at?: string;
  failed_at?: string;
  created_at: string;
}

export type LeadStatus = "NEW" | "CONTACTED" | "QUALIFIED" | "PROPOSAL" | "NEGOTIATION" | "CONVERTED" | "LOST";

export interface LeadStageHistory {
  id: string;
  from_stage?: LeadStatus;
  to_stage: LeadStatus;
  notes?: string;
  created_at: string;
  changed_by?: User;
}

export interface Lead {
  id: string;
  workspace_id: string;
  contact_id: string;
  assigned_agent_id?: string;
  name: string;
  phone: string;
  email?: string;
  company?: string;
  source: string;
  status: LeadStatus;
  value: number;
  score: number;
  notes?: string;
  last_contact_at?: string;
  created_at: string;
  contact?: {
    id: string;
    phone: string;
    name?: string;
    email?: string;
    avatar_url?: string;
  };
  assigned_agent?: User;
  stage_history: LeadStageHistory[];
}

export interface LeadKanbanColumn {
  stage: LeadStatus;
  label: string;
  count: number;
  total_value: number;
  leads: Lead[];
}

export interface LeadKanbanResponse {
  columns: LeadKanbanColumn[];
}

export type TemplateStatus = "DRAFT" | "PENDING" | "APPROVED" | "REJECTED" | "PAUSED";
export type TemplateCategory = "MARKETING" | "UTILITY" | "AUTHENTICATION";
export type TemplateHeaderType = "NONE" | "TEXT" | "IMAGE" | "DOCUMENT" | "VIDEO";

export interface TemplateVariable {
  variable_index: number;
  variable_name: string;
  mapping_source: string;
}

export interface MessageTemplate {
  id: string;
  workspace_id: string;
  meta_template_id?: string;
  name: string;
  category: TemplateCategory;
  language: string;
  status: TemplateStatus;
  rejection_reason?: string;
  header_type: TemplateHeaderType;
  header_content?: string;
  body_text: string;
  footer_text?: string;
  buttons_json?: string;
  estimated_cost_inr?: number;
  estimated_cost_usd?: number;
  cost_badge?: string;
  created_at: string;
  variables: TemplateVariable[];
}

export interface TemplatePricingRate {
  inr: number;
  usd: number;
  label: string;
  description: string;
}

export interface TemplatePricingSummary {
  rates: Record<string, TemplatePricingRate>;
  currency: string;
  symbol: string;
  country: string;
  meta_billing_note: string;
}

export type FlowStatus = "DRAFT" | "PUBLISHED" | "ARCHIVED";
export type TriggerType = "MESSAGE_RECEIVED" | "KEYWORD" | "BUTTON_CLICK" | "NEW_CONTACT" | "NEW_LEAD" | "WEBHOOK" | "SCHEDULE";

export interface AutomationFlow {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  is_active: boolean;
  priority: number;
  version: number;
  status: FlowStatus;
  trigger_type: TriggerType;
  trigger_config?: string;
  nodes_json?: string;
  edges_json?: string;
  triggered_count: number;
  completed_count: number;
  failed_count: number;
  leads_generated_count: number;
  handovers_count: number;
  created_at: string;
}

export interface AutomationRule {
  id: string;
  workspace_id: string;
  name: string;
  priority: number;
  trigger_keyword: string;
  match_type: string;
  condition_contact_is_new: boolean;
  action_reply_text: string;
  action_buttons_json?: string;
  action_create_lead: boolean;
  action_add_tag?: string;
  action_handover: boolean;
  is_active: boolean;
  created_at: string;
}

export interface KnowledgeDocument {
  id: string;
  knowledge_base_id: string;
  title: string;
  category: string;
  question?: string;
  answer_or_content: string;
  keywords?: string;
  is_active: boolean;
  created_at: string;
}

export interface KnowledgeBase {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  documents: KnowledgeDocument[];
}

export type AIMode = "OFF" | "SUGGEST" | "AUTO";
export type AITone = "PROFESSIONAL" | "FRIENDLY" | "CASUAL" | "FORMAL";

export interface AISetting {
  id: string;
  workspace_id: string;
  ai_name: string;
  business_name: string;
  business_description?: string;
  tone: AITone;
  instructions: string;
  fallback_message: string;
  max_tokens: number;
  mode: AIMode;
  auto_handover_on_fallback: boolean;
  confidence_threshold: number;
  created_at: string;
}

export interface MetricCard {
  title: string;
  value: string;
  trend: string;
  trend_positive: boolean;
  description: string;
}

export interface DashboardMetrics {
  total_conversations: number;
  active_conversations: number;
  unread_messages: number;
  new_leads: number;
  qualified_leads: number;
  converted_leads: number;
  bot_replies: number;
  ai_replies: number;
  human_handovers: number;
  cards: MetricCard[];
  messages_chart: { timestamp: string; count: number }[];
  leads_chart: { timestamp: string; count: number }[];
  conversation_split: {
    bot_percentage: number;
    ai_percentage: number;
    human_percentage: number;
  };
  recent_activities: {
    id: string;
    preview: string;
    mode: string;
    status: string;
    updated_at: string;
  }[];
}

export interface ClientSetupOverview {
  workspace_id: string;
  name: string;
  slug: string;
  industry?: string;
  timezone: string;
  country: string;
  phone?: string;
  email?: string;
  website?: string;
  address?: string;
  city?: string;
  instagram?: string;
  facebook?: string;
  description?: string;
  business_hours_config?: string;
  logo_url?: string;
  primary_color?: string;
  secondary_color?: string;
  background_color?: string;
  text_color?: string;
  button_style?: string;
  whatsapp_connected: boolean;
  whatsapp_phone_number?: string;
  whatsapp_quality_rating?: string;
  products_count: number;
  quick_replies_count: number;
  flows_count: number;
  templates_count: number;
  leads_count: number;
}

export interface ProductService {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  category?: string;
  price?: number;
  currency: string;
  image_url?: string;
  sku?: string;
  is_available: boolean;
  tags?: string;
  order_index: number;
  created_at: string;
}

export interface QuickReply {
  id: string;
  workspace_id: string;
  shortcut: string;
  title: string;
  message: string;
  category: string;
  created_at: string;
}

export interface IndustryTemplate {
  id: string;
  name: string;
  category: string;
  icon: string;
  description: string;
  primary_color: string;
  secondary_color: string;
  greeting_message: string;
  products: {
    name: string;
    category: string;
    price: number;
    description: string;
    sku?: string;
  }[];
  quick_replies: {
    shortcut: string;
    title: string;
    message: string;
    category: string;
  }[];
  lead_stages: string[];
}

export interface ClientCloneRequest {
  target_name: string;
  target_slug?: string;
  industry?: string;
  copy_branding: boolean;
  copy_flows: boolean;
  copy_templates: boolean;
  copy_products: boolean;
  copy_quick_replies: boolean;
  copy_ai_settings: boolean;
}

export interface ClientCloneResponse {
  new_workspace_id: string;
  new_workspace_name: string;
  new_workspace_slug: string;
  copied_items: Record<string, number>;
  message: string;
}

export interface AISuggestionItem {
  id: string;
  type: string;
  label: string;
  text: string;
}

export interface DebuggerTrace {
  id: string;
  flow_id: string;
  flow_name: string;
  status: string;
  input_text?: string;
  execution_time_ms: number;
  error_message?: string;
  logs?: any;
  created_at: string;
}

export interface WebhookLog {
  id: string;
  meta_message_id?: string;
  event_type: string;
  status: string;
  processing_time_ms: number;
  raw_payload: string;
  error_message?: string;
  created_at: string;
}

