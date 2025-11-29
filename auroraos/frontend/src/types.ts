// frontend/src/types.ts
// AuroraOS — Betül Console Type Definitions

export interface ContentVariant {
  id: number;
  vibe_mode: string;
  text: string;
  meta?: string | null;
}

export interface ContentItem {
  id: number;
  type: string;
  target_channel: string;
  status: string;
  scheduled_at?: string | null;
  created_by: string;
  created_at: string;
  selected_variant_id?: number | null;
  variants: ContentVariant[];
}

export interface DecisionPayload {
  decision: "approve" | "reject" | "edit" | "reschedule";
  feedback_type?: string;
  rating?: number;
  old_text?: string;
  new_text?: string;
  vibe_mode_before?: string;
  vibe_mode_after?: string;
}

export interface VibeState {
  current_mode: string;
  energy_level: number;
  note?: string;
}

