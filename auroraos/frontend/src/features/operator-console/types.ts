/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   AuroraOS Operator Console — Type Definitions                   ║
 * ║   Betül's Cockpit Types                                          ║
 * ║                                                                  ║
 * ║   Baron Baba © SiyahKare, 2025                                   ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

export type ConversationMode = "AI_ONLY" | "HUMAN_ONLY" | "HYBRID_GHOST";
export type ConversationPriority = "LOW" | "NORMAL" | "HIGH" | "VIP";
export type ConversationOrigin = "FLIRTMARKET" | "TELEGRAM" | "WEB" | "ONLYVIPS";

export interface ConversationSummary {
  id: number;
  external_user_id: string;
  performer_slot_id: number;
  performer_slot_label: string;
  agent_id: string;
  operator_id?: number | null;
  mode: ConversationMode;
  priority: ConversationPriority;
  origin: ConversationOrigin;
  message_count: number;
  coins_spent: number;
  last_message_at: string | null;
  last_message_preview: string | null;
  is_active: boolean;
}

export interface ConversationMessage {
  id: number;
  sender: "user" | "agent" | "operator";
  text: string;
  source: string;
  is_draft: boolean;
  edited_by_operator: boolean;
  created_at: string;
}

export interface ConversationDetail {
  id: number;
  external_user_id: string;
  performer_slot_id: number;
  performer_slot_label: string;
  agent_id: string;
  mode: ConversationMode;
  priority: ConversationPriority;
  origin: ConversationOrigin;
  message_count: number;
  coins_spent: number;
  is_active: boolean;
  created_at: string;
  messages: ConversationMessage[];
}

export interface PerformerSlot {
  id: number;
  label: string;
  agent_id: string;
  provider: string;
  model: string;
  is_active: boolean;
  created_at: string;
}

export interface Operator {
  id: number;
  name: string;
  external_id: string | null;
  is_online: boolean;
  max_concurrent_chats: number;
  active_chat_count: number;
}

export interface UserProfile {
  internal_user_id: number;
  display_name: string | null;
  vip_tier: "none" | "silver" | "gold" | "platinum";
  total_coins_spent: number;
}

