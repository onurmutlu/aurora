/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   AuroraOS Operator Console — API Client                         ║
 * ║   Orchestrator backend communication                             ║
 * ║                                                                  ║
 * ║   Baron Baba © SiyahKare, 2025                                   ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

import type {
  ConversationSummary,
  ConversationDetail,
  ConversationMode,
  ConversationPriority,
  ConversationOrigin,
  PerformerSlot,
  Operator,
} from "./types";

const API_BASE = "/v1/orchestrator";

async function jsonFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// ═══════════════════════════════════════════════════════════════════
// CONVERSATIONS
// ═══════════════════════════════════════════════════════════════════

export interface FetchConversationsParams {
  operator_id?: number;
  mode?: ConversationMode;
  priority?: ConversationPriority;
  origin?: ConversationOrigin;
  active_only?: boolean;
  limit?: number;
  offset?: number;
}

export async function fetchConversations(
  params: FetchConversationsParams = {}
): Promise<ConversationSummary[]> {
  const search = new URLSearchParams();
  
  if (params.operator_id) search.set("operator_id", String(params.operator_id));
  if (params.mode) search.set("mode", params.mode);
  if (params.priority) search.set("priority", params.priority);
  if (params.origin) search.set("origin", params.origin);
  if (params.active_only !== undefined) search.set("active_only", String(params.active_only));
  if (params.limit) search.set("limit", String(params.limit));
  if (params.offset) search.set("offset", String(params.offset));

  const query = search.toString();
  return jsonFetch<ConversationSummary[]>(
    `${API_BASE}/conversations${query ? `?${query}` : ""}`
  );
}

export async function fetchConversationDetail(
  conversationId: number
): Promise<ConversationDetail> {
  return jsonFetch<ConversationDetail>(
    `${API_BASE}/conversations/${conversationId}`
  );
}

// ═══════════════════════════════════════════════════════════════════
// OPERATOR REPLY
// ═══════════════════════════════════════════════════════════════════

export interface SendReplyParams {
  conversationId: number;
  text: string;
  sendAs?: "operator" | "agent_style";
  editDraftId?: number;
}

export interface ReplyResponse {
  message_id: number;
  sent: boolean;
  queued_for_outbound: boolean;
}

export async function sendOperatorReply(
  params: SendReplyParams
): Promise<ReplyResponse> {
  return jsonFetch<ReplyResponse>(
    `${API_BASE}/conversations/${params.conversationId}/reply`,
    {
      method: "POST",
      body: JSON.stringify({
        text: params.text,
        send_as: params.sendAs ?? "operator",
        edit_draft_id: params.editDraftId,
      }),
    }
  );
}

// ═══════════════════════════════════════════════════════════════════
// CONVERSATION MODE CHANGE
// ═══════════════════════════════════════════════════════════════════

export async function updateConversationMode(
  conversationId: number,
  mode: ConversationMode
): Promise<{ success: boolean }> {
  return jsonFetch<{ success: boolean }>(
    `${API_BASE}/conversations/${conversationId}/mode`,
    {
      method: "PATCH",
      body: JSON.stringify({ mode }),
    }
  );
}

// ═══════════════════════════════════════════════════════════════════
// PERFORMER SLOTS
// ═══════════════════════════════════════════════════════════════════

export async function fetchPerformerSlots(
  activeOnly: boolean = true
): Promise<PerformerSlot[]> {
  const query = activeOnly ? "?active_only=true" : "";
  return jsonFetch<PerformerSlot[]>(`${API_BASE}/performer-slots${query}`);
}

export interface CreatePerformerSlotParams {
  label: string;
  agent_id: string;
  provider?: string;
  model?: string;
  system_prompt?: string;
  temperature?: number;
  max_tokens?: number;
}

export async function createPerformerSlot(
  params: CreatePerformerSlotParams
): Promise<PerformerSlot> {
  return jsonFetch<PerformerSlot>(`${API_BASE}/performer-slots`, {
    method: "POST",
    body: JSON.stringify(params),
  });
}

// ═══════════════════════════════════════════════════════════════════
// OPERATORS
// ═══════════════════════════════════════════════════════════════════

export async function fetchOperators(): Promise<Operator[]> {
  return jsonFetch<Operator[]>(`${API_BASE}/operators`);
}

export async function updateOperatorStatus(
  operatorId: number,
  isOnline: boolean
): Promise<{ id: number; is_online: boolean }> {
  return jsonFetch<{ id: number; is_online: boolean }>(
    `${API_BASE}/operators/${operatorId}/status`,
    {
      method: "PATCH",
      body: JSON.stringify({ is_online: isOnline }),
    }
  );
}

// ═══════════════════════════════════════════════════════════════════
// OUTBOUND POLLING (for debugging)
// ═══════════════════════════════════════════════════════════════════

export interface OutboundMessage {
  external_user_id: string;
  text: string;
  conversation_id: number;
  message_id: number;
}

export async function fetchOutboundQueue(
  origin: ConversationOrigin,
  limit: number = 10
): Promise<{ messages: OutboundMessage[]; count: number }> {
  return jsonFetch<{ messages: OutboundMessage[]; count: number }>(
    `${API_BASE}/outbound/poll?origin=${origin}&limit=${limit}`
  );
}

