/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   AuroraOS State Dashboard — API Client                          ║
 * ║   Backend communication for government data                      ║
 * ║                                                                  ║
 * ║   Baron Baba © SiyahKare, 2025                                   ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

const API_BASE = "/v1/state";

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
// TYPES
// ═══════════════════════════════════════════════════════════════════

export interface CitizenStats {
  total: number;
  verified: number;
  pending: number;
  online: number;
  banned: number;
  new_today: number;
  basic_count: number;
  silver_count: number;
  gold_count: number;
  platinum_count: number;
  founder_count: number;
}

export interface TreasuryStats {
  reserve: string;
  reserve_raw: number;
  gdp_24h: string;
  gdp_raw: number;
  inflation: string;
  inflation_raw: number;
  liquidity: string;
  transactions_24h: number;
  volume_24h: number;
  avg_transaction: number;
}

export interface ThreatStatus {
  level: string;
  active_threats: number;
  mitigated_24h: number;
  last_incident: string | null;
  details: string;
}

export interface DashboardStats {
  citizens: CitizenStats;
  treasury: TreasuryStats;
  threat: ThreatStatus;
  ai_operations_24h: number;
  flagged_content: number;
}

export interface Citizen {
  id: number;
  citizen_id: string;
  display_name: string;
  email: string | null;
  telegram_id: string | null;
  status: string;
  tier: string;
  is_online: boolean;
  balance: number;
  total_earned: number;
  total_spent: number;
  message_count: number;
  joined_at: string;
  last_seen: string | null;
}

export interface Transaction {
  id: number;
  transaction_id: string;
  type: string;
  amount: number;
  currency: string;
  citizen_id: number | null;
  description: string;
  status: string;
  created_at: string;
}

export interface AIOperation {
  id: number;
  operation_id: string;
  type: string;
  status: string;
  target: string;
  target_type: string;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  result: string | null;
  sentiment: string | null;
  confidence: number | null;
  model_used: string | null;
  created_at: string;
}

export interface ContentFlag {
  id: number;
  flag_id: string;
  type: string;
  severity: number;
  content_type: string;
  content_id: string;
  content_preview: string | null;
  status: string;
  resolution: string | null;
  created_at: string;
  resolved_at: string | null;
}

// ═══════════════════════════════════════════════════════════════════
// API FUNCTIONS
// ═══════════════════════════════════════════════════════════════════

// Dashboard
export async function fetchDashboardStats(): Promise<DashboardStats> {
  return jsonFetch<DashboardStats>(`${API_BASE}/dashboard`);
}

// Citizens
export async function fetchCitizens(params: {
  status?: string;
  tier?: string;
  online_only?: boolean;
  search?: string;
  limit?: number;
  offset?: number;
} = {}): Promise<Citizen[]> {
  const search = new URLSearchParams();
  if (params.status) search.set("status", params.status);
  if (params.tier) search.set("tier", params.tier);
  if (params.online_only) search.set("online_only", "true");
  if (params.search) search.set("search", params.search);
  if (params.limit) search.set("limit", String(params.limit));
  if (params.offset) search.set("offset", String(params.offset));
  
  const query = search.toString();
  return jsonFetch<Citizen[]>(`${API_BASE}/citizens${query ? `?${query}` : ""}`);
}

export async function fetchCitizen(citizenId: string): Promise<Citizen> {
  return jsonFetch<Citizen>(`${API_BASE}/citizens/${citizenId}`);
}

export async function createCitizen(data: {
  display_name: string;
  email?: string;
  phone?: string;
  telegram_id?: string;
  tier?: string;
}): Promise<Citizen> {
  return jsonFetch<Citizen>(`${API_BASE}/citizens`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function verifyCitizen(citizenId: string): Promise<Citizen> {
  return jsonFetch<Citizen>(`${API_BASE}/citizens/${citizenId}/verify`, {
    method: "POST",
  });
}

export async function banCitizen(citizenId: string, reason: string): Promise<void> {
  await jsonFetch<void>(`${API_BASE}/citizens/${citizenId}/ban`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

// Treasury
export async function fetchTransactions(params: {
  type?: string;
  citizen_id?: number;
  limit?: number;
  offset?: number;
} = {}): Promise<Transaction[]> {
  const search = new URLSearchParams();
  if (params.type) search.set("type", params.type);
  if (params.citizen_id) search.set("citizen_id", String(params.citizen_id));
  if (params.limit) search.set("limit", String(params.limit));
  if (params.offset) search.set("offset", String(params.offset));
  
  const query = search.toString();
  return jsonFetch<Transaction[]>(`${API_BASE}/treasury/transactions${query ? `?${query}` : ""}`);
}

export async function createTransaction(data: {
  type: string;
  amount: number;
  citizen_id?: number;
  description: string;
}): Promise<Transaction> {
  return jsonFetch<Transaction>(`${API_BASE}/treasury/transactions`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// AI Operations
export async function fetchAIOperations(params: {
  type?: string;
  status?: string;
  limit?: number;
  offset?: number;
} = {}): Promise<AIOperation[]> {
  const search = new URLSearchParams();
  if (params.type) search.set("type", params.type);
  if (params.status) search.set("status", params.status);
  if (params.limit) search.set("limit", String(params.limit));
  if (params.offset) search.set("offset", String(params.offset));
  
  const query = search.toString();
  return jsonFetch<AIOperation[]>(`${API_BASE}/ai-operations${query ? `?${query}` : ""}`);
}

export async function createAIOperation(data: {
  type: string;
  target: string;
  target_type?: string;
}): Promise<AIOperation> {
  return jsonFetch<AIOperation>(`${API_BASE}/ai-operations`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// Content Flags
export async function fetchFlags(params: {
  status?: string;
  type?: string;
  limit?: number;
  offset?: number;
} = {}): Promise<ContentFlag[]> {
  const search = new URLSearchParams();
  if (params.status) search.set("status", params.status);
  if (params.type) search.set("type", params.type);
  if (params.limit) search.set("limit", String(params.limit));
  if (params.offset) search.set("offset", String(params.offset));
  
  const query = search.toString();
  return jsonFetch<ContentFlag[]>(`${API_BASE}/flags${query ? `?${query}` : ""}`);
}

export async function resolveFlag(flagId: string, data: {
  status: string;
  resolution: string;
}): Promise<ContentFlag> {
  return jsonFetch<ContentFlag>(`${API_BASE}/flags/${flagId}/resolve`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

