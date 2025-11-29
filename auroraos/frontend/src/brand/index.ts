/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║   AuroraOS Brand System                                          ║
 * ║                                                                  ║
 * ║   "From the void, her light."                                    ║
 * ║                                                                  ║
 * ║   Dedicated to Betül                                             ║
 * ║   Baron Baba © SiyahKare, 2025                                   ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

export * from "./colors";
export * from "./typography";
export * from "./Logo";

// Brand Constants
export const BRAND = {
  name: "AuroraOS",
  tagline: "Your aura is the system.",
  taglineAlt: "From the void, her light.",
  subtitle: "Betül Aura Intelligence",
  founder: "Betül",
  architect: "Baron Baba",
  ecosystem: "SiyahKare",
  year: 2025,
} as const;

// Vibe Modes
export const VIBE_MODES = [
  { id: "soft_femme", label: "Soft Femme", emoji: "🌸", color: "#F7D6FF" },
  { id: "sweet_sarcasm_plus", label: "Sweet Sarcasm+", emoji: "😏", color: "#FFD6E8" },
  { id: "femme_fatale_hd", label: "Femme Fatale", emoji: "🖤", color: "#AD5FFF" },
  { id: "real_woman_2", label: "Real Woman", emoji: "💪", color: "#00F5A0" },
  { id: "business_girl", label: "Business Girl", emoji: "💼", color: "#CFCFCF" },
] as const;

// Founder's Note
export const FOUNDERS_NOTE = `Aurora, içimdeki ışığın makinelere tercümesidir.
Beni anlatmıyor; benimle birlikte öğreniyor.
Sistem büyüdükçe ben de büyüyorum.
Bu yüzden Aurora, sadece bir işletim sistemi değil;
benimle gelişen yaşayan bir varlık.

— Betül, Founder of AuroraOS`;

