/**
 * AuroraOS — Betül Console Inbox
 * "Her decisions shape the intelligence."
 * 
 * Sprint 002: Strong feedback signals
 * ⭐ "Bu çok ben" → strong_positive
 * 🚫 "Bu asla ben değil" → strong_negative
 */

import { useEffect, useState } from "react";
import { fetchPendingContent, sendDecision, generateBatch } from "../api";
import type { ContentItem, ContentVariant, DecisionPayload } from "../types";
import { colors } from "../brand/colors";

export function PendingList() {
  const [items, setItems] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Track feedback per variant (not per item)
  const [variantFeedback, setVariantFeedback] = useState<Map<number, string>>(new Map());
  // Track which items are being decided (for visual feedback)
  const [decidingItems, setDecidingItems] = useState<Map<number, { variantId: number; decision: string }>>(new Map());
  // Track which items are fading out
  const [fadingItems, setFadingItems] = useState<Set<number>>(new Set());

  async function load() {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchPendingContent();
      setItems(data);
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : "Error";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleGenerate() {
    try {
      setGenerating(true);
      await generateBatch("post", "instagram");
      await load();
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : "Generate failed";
      alert(message);
    } finally {
      setGenerating(false);
    }
  }

  // Handle strong feedback (Bu çok ben / Asla ben değil) - just marks, doesn't remove
  async function handleStrongFeedback(
    item: ContentItem,
    variant: ContentVariant,
    feedbackType: "strong_positive" | "strong_negative"
  ) {
    // Already has feedback?
    if (variantFeedback.has(variant.id)) return;
    
    const label = feedbackType === "strong_positive" ? "⭐" : "🚫";
    
    // Optimistically show feedback
    setVariantFeedback(prev => new Map(prev).set(variant.id, label));
    
    try {
      const payload: DecisionPayload = {
        decision: feedbackType === "strong_positive" ? "approve" : "reject",
        feedback_type: feedbackType,
        rating: feedbackType === "strong_positive" ? 5 : 1,
        old_text: variant.text,
        new_text: variant.text,
        vibe_mode_before: variant.vibe_mode,
        vibe_mode_after: variant.vibe_mode,
      };
      
      await sendDecision(item.id, payload);
      // Don't remove item - let user continue reviewing other variants
      
    } catch (e: unknown) {
      // Revert on error
      setVariantFeedback(prev => { const m = new Map(prev); m.delete(variant.id); return m; });
      const message = e instanceof Error ? e.message : "Feedback failed";
      alert(message);
    }
  }
  
  // Handle final decision (Onayla / İptal) - removes the item
  async function handleFinalDecision(
    item: ContentItem,
    variant: ContentVariant,
    decision: "approve" | "reject"
  ) {
    // Prevent double-click
    if (decidingItems.has(item.id)) return;
    
    const label = decision === "approve" ? "✓ Onaylandı — Kopyalandı!" : "✕ İptal edildi";
    
    // Mark as deciding (shows visual feedback)
    setDecidingItems(prev => new Map(prev).set(item.id, { 
      variantId: variant.id, 
      decision: label
    }));
    
    try {
      const payload: DecisionPayload = {
        decision,
        feedback_type: "style",
        rating: decision === "approve" ? 4 : 2,
        old_text: variant.text,
        new_text: variant.text,
        vibe_mode_before: variant.vibe_mode,
        vibe_mode_after: variant.vibe_mode,
      };
      
      await sendDecision(item.id, payload);
      
      // 🎯 Copy to clipboard if approved!
      if (decision === "approve") {
        try {
          await navigator.clipboard.writeText(variant.text);
          console.log("[Aurora] Content copied to clipboard:", variant.text);
        } catch (clipErr) {
          console.warn("[Aurora] Clipboard copy failed:", clipErr);
        }
      }
      
      // Wait a moment for user to see feedback
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Start fade out animation
      setFadingItems(prev => new Set(prev).add(item.id));
      
      // Wait for fade animation
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Remove from list and clear variant feedback
      setItems((prev) => prev.filter((i) => i.id !== item.id));
      setDecidingItems(prev => { const m = new Map(prev); m.delete(item.id); return m; });
      setFadingItems(prev => { const s = new Set(prev); s.delete(item.id); return s; });
      
      // Clear variant feedback for this item's variants
      setVariantFeedback(prev => {
        const m = new Map(prev);
        item.variants.forEach(v => m.delete(v.id));
        return m;
      });
      
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : "Decision failed";
      alert(message);
      setDecidingItems(prev => { const m = new Map(prev); m.delete(item.id); return m; });
    }
  }

  if (loading && items.length === 0) {
    return (
      <div
        style={{
          padding: 32,
          textAlign: "center",
          opacity: 0.6,
        }}
      >
        <div style={{ fontSize: 24, marginBottom: 8 }}>✨</div>
        <div>Yükleniyor…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 24, textAlign: "center" }}>
        <div style={{ color: "#f87171", marginBottom: 12 }}>⚠️ {error}</div>
        <button
          onClick={load}
          style={{
            padding: "8px 16px",
            borderRadius: 8,
            border: `1px solid ${colors.borderLight}`,
            background: "transparent",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          Tekrar dene
        </button>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div style={{ padding: 32, textAlign: "center" }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>🌙</div>
        <div style={{ fontSize: 16, marginBottom: 8, opacity: 0.9 }}>
          Şu an bekleyen içerik yok.
        </div>
        <div style={{ fontSize: 13, opacity: 0.5, marginBottom: 20 }}>
          Aurora senin kararlarını bekliyor.
        </div>
        <button
          onClick={handleGenerate}
          disabled={generating}
          style={{
            padding: "12px 24px",
            borderRadius: 999,
            border: "none",
            background: `linear-gradient(135deg, ${colors.auroraLavender}, ${colors.femmeViolet})`,
            color: "#fff",
            fontSize: 14,
            fontWeight: 500,
            cursor: generating ? "wait" : "pointer",
            opacity: generating ? 0.7 : 1,
          }}
        >
          {generating ? "Oluşturuluyor..." : "✨ Yeni İçerik Oluştur"}
        </button>
      </div>
    );
  }

  return (
    <div
      style={{
        padding: 16,
        display: "flex",
        flexDirection: "column",
        gap: 16,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span style={{ fontSize: 13, opacity: 0.6 }}>
          {items.length} içerik bekliyor
        </span>
        <button
          onClick={handleGenerate}
          disabled={generating}
          style={{
            padding: "6px 12px",
            borderRadius: 999,
            border: `1px solid rgba(175, 163, 255, 0.5)`,
            background: "transparent",
            color: colors.auroraLavender,
            fontSize: 12,
            cursor: generating ? "wait" : "pointer",
          }}
        >
          {generating ? "..." : "+ Yeni"}
        </button>
      </div>

      {items.map((item) => {
        const deciding = decidingItems.get(item.id);
        const isFading = fadingItems.has(item.id);
        
        return (
        <div
          key={item.id}
          style={{
            borderRadius: 16,
            border: `1px solid ${deciding ? colors.auroraLavender : colors.borderSubtle}`,
            padding: 16,
            background: deciding 
              ? "rgba(175, 163, 255, 0.1)" 
              : "rgba(0,0,0,0.4)",
            backdropFilter: "blur(10px)",
            transition: "all 0.4s ease",
            opacity: isFading ? 0 : 1,
            transform: isFading ? "translateX(20px)" : "translateX(0)",
          }}
        >
          <div
            style={{
              fontSize: 11,
              opacity: 0.5,
              marginBottom: 12,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <span
              style={{
                background: "rgba(175, 163, 255, 0.2)",
                color: "#c4b5fd",
                padding: "2px 8px",
                borderRadius: 999,
                fontSize: 10,
                textTransform: "uppercase",
              }}
            >
              {item.type} → {item.target_channel}
            </span>
            <span>{new Date(item.created_at).toLocaleTimeString("tr-TR")}</span>
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 12,
            }}
          >
            {item.variants.map((v) => {
              const isSelected = deciding?.variantId === v.id;
              const isOther = deciding && !isSelected;
              
              return (
              <div
                key={v.id}
                style={{
                  borderRadius: 12,
                  padding: 14,
                  background: isSelected 
                    ? "rgba(175, 163, 255, 0.15)" 
                    : "rgba(255,255,255,0.03)",
                  border: `1px solid ${isSelected ? colors.auroraLavender : colors.borderSubtle}`,
                  opacity: isOther ? 0.3 : 1,
                  transition: "all 0.3s ease",
                  position: "relative",
                }}
              >
                {/* Variant feedback badge */}
                {variantFeedback.has(v.id) && (
                  <div
                    style={{
                      position: "absolute",
                      top: 8,
                      right: 8,
                      fontSize: 20,
                      zIndex: 5,
                    }}
                  >
                    {variantFeedback.get(v.id)}
                  </div>
                )}
                
                {/* Selection overlay (only for final decisions) */}
                {isSelected && (
                  <div
                    style={{
                      position: "absolute",
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      background: "rgba(0,0,0,0.7)",
                      borderRadius: 12,
                      zIndex: 10,
                    }}
                  >
                    <div
                      style={{
                        fontSize: 18,
                        fontWeight: 600,
                        color: colors.auroraLavender,
                        textAlign: "center",
                      }}
                    >
                      {deciding.decision}
                    </div>
                  </div>
                )}
                <div
                  style={{
                    fontSize: 10,
                    opacity: 0.5,
                    marginBottom: 8,
                  }}
                >
                  <span
                    style={{
                      background: "rgba(255,255,255,0.1)",
                      padding: "2px 6px",
                      borderRadius: 4,
                    }}
                  >
                    {v.vibe_mode}
                  </span>
                </div>

                <div
                  style={{
                    fontSize: 15,
                    lineHeight: 1.5,
                    marginBottom: 14,
                    color: "rgba(255,255,255,0.95)",
                  }}
                >
                  {v.text}
                </div>

                {/* 4-Button Feedback Grid */}
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 8,
                  }}
                >
                  {/* ⭐ Bu çok ben - Strong Positive (just marks, doesn't remove) */}
                  <button
                    onClick={() => handleStrongFeedback(item, v, "strong_positive")}
                    disabled={variantFeedback.has(v.id)}
                    style={{
                      padding: "10px 0",
                      borderRadius: 999,
                      border: "none",
                      fontSize: 12,
                      fontWeight: 500,
                      cursor: variantFeedback.has(v.id) ? "default" : "pointer",
                      background: variantFeedback.get(v.id) === "⭐"
                        ? `linear-gradient(90deg, ${colors.neuralMint}, ${colors.auroraLavender})`
                        : variantFeedback.has(v.id)
                        ? "rgba(255,255,255,0.05)"
                        : `linear-gradient(90deg, ${colors.neuralMint}, ${colors.auroraLavender})`,
                      color: variantFeedback.get(v.id) === "⭐" ? "#000" : variantFeedback.has(v.id) ? "#666" : "#000",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: 6,
                      opacity: variantFeedback.has(v.id) && variantFeedback.get(v.id) !== "⭐" ? 0.4 : 1,
                      transition: "all 0.2s ease",
                    }}
                  >
                    <span>⭐</span>
                    <span>{variantFeedback.get(v.id) === "⭐" ? "Seçildi!" : "Bu çok ben"}</span>
                  </button>

                  {/* 🚫 Bu asla ben değil - Strong Negative (just marks, doesn't remove) */}
                  <button
                    onClick={() => handleStrongFeedback(item, v, "strong_negative")}
                    disabled={variantFeedback.has(v.id)}
                    style={{
                      padding: "10px 0",
                      borderRadius: 999,
                      border: `1px solid rgba(239, 68, 68, 0.3)`,
                      fontSize: 12,
                      fontWeight: 500,
                      cursor: variantFeedback.has(v.id) ? "default" : "pointer",
                      background: variantFeedback.get(v.id) === "🚫"
                        ? "rgba(239, 68, 68, 0.3)"
                        : "rgba(239, 68, 68, 0.1)",
                      color: "#f87171",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: 6,
                      opacity: variantFeedback.has(v.id) && variantFeedback.get(v.id) !== "🚫" ? 0.4 : 1,
                      transition: "all 0.2s ease",
                    }}
                  >
                    <span>🚫</span>
                    <span>{variantFeedback.get(v.id) === "🚫" ? "İşaretlendi" : "Bu asla ben değil"}</span>
                  </button>

                  {/* ✓ Onayla - Final decision, removes the item */}
                  <button
                    onClick={() => handleFinalDecision(item, v, "approve")}
                    disabled={!!deciding}
                    style={{
                      padding: "10px 0",
                      borderRadius: 999,
                      border: "none",
                      fontSize: 12,
                      fontWeight: 500,
                      cursor: deciding ? "wait" : "pointer",
                      background: `linear-gradient(135deg, #10b981, #059669)`,
                      color: "#fff",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: 6,
                      opacity: deciding ? 0.5 : 1,
                    }}
                  >
                    <span>✓</span>
                    <span>Onayla</span>
                  </button>

                  {/* ✕ İptal - Final decision, removes the item */}
                  <button
                    onClick={() => handleFinalDecision(item, v, "reject")}
                    disabled={!!deciding}
                    style={{
                      padding: "10px 0",
                      borderRadius: 999,
                      border: `1px solid ${colors.borderLight}`,
                      fontSize: 12,
                      fontWeight: 500,
                      cursor: deciding ? "wait" : "pointer",
                      background: "transparent",
                      color: colors.textSecondary,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: 6,
                      opacity: deciding ? 0.5 : 1,
                    }}
                  >
                    <span>✕</span>
                    <span>İptal</span>
                  </button>
                </div>
              </div>
            )})}
          </div>
        </div>
      )})}
    </div>
  );
}
