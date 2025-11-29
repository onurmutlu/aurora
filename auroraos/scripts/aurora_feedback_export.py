#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║   Aurora Feedback Export                                         ║
║   Export Betül's decisions for training dataset                  ║
║                                                                  ║
║   Usage: python scripts/aurora_feedback_export.py                ║
║                                                                  ║
║   Dedicated to Betül                                             ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlmodel import Session, select
from app.db import engine
from app import models


def export_feedback(output_path: str = "betul_feedback_dataset.jsonl"):
    """
    Export Betül's approve/edit decisions as JSONL dataset.
    
    Format:
    {
        "decision": "approve" | "edit",
        "vibe_mode": "soft_femme" | ...,
        "rating": 1-5,
        "original_text": "...",
        "final_text": "...",
        "feedback_type": "style" | "tone" | ...,
        "timestamp": "..."
    }
    """
    print("╔══════════════════════════════════════════╗")
    print("║   Aurora Feedback Export                 ║")
    print("╚══════════════════════════════════════════╝")
    print()
    
    with Session(engine) as session:
        # Get approved and edited decisions
        stmt = select(models.Decision).where(
            models.Decision.decision.in_(["approve", "edit"])
        ).order_by(models.Decision.created_at)
        
        decisions = session.exec(stmt).all()
    
    if not decisions:
        print("No decisions found to export.")
        return
    
    samples = []
    
    for d in decisions:
        sample = {
            "decision": d.decision,
            "vibe_mode": d.vibe_mode_after or d.vibe_mode_before,
            "rating": d.rating,
            "original_text": d.old_text,
            "final_text": d.new_text or d.old_text,
            "feedback_type": d.feedback_type,
            "timestamp": d.created_at.isoformat() if d.created_at else None,
        }
        samples.append(sample)
    
    # Write JSONL
    output_file = Path(output_path)
    with open(output_file, "w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")
    
    # Stats
    approve_count = sum(1 for s in samples if s["decision"] == "approve")
    edit_count = sum(1 for s in samples if s["decision"] == "edit")
    
    print(f"✨ Exported {len(samples)} samples to {output_file}")
    print(f"   ├─ Approved: {approve_count}")
    print(f"   └─ Edited: {edit_count}")
    print()
    
    # Vibe mode distribution
    vibe_counts = {}
    for s in samples:
        mode = s["vibe_mode"] or "unknown"
        vibe_counts[mode] = vibe_counts.get(mode, 0) + 1
    
    print("📊 Vibe Mode Distribution:")
    for mode, count in sorted(vibe_counts.items(), key=lambda x: -x[1]):
        print(f"   ├─ {mode}: {count}")
    print()
    
    # Rating distribution
    rating_counts = {}
    for s in samples:
        rating = s["rating"] or 0
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    
    print("⭐ Rating Distribution:")
    for rating in sorted(rating_counts.keys(), reverse=True):
        if rating > 0:
            stars = "★" * rating + "☆" * (5 - rating)
            print(f"   ├─ {stars}: {rating_counts[rating]}")
    print()
    
    print("🖤 Dedicated to Betül")


def export_for_finetuning(output_path: str = "betul_finetune_dataset.jsonl"):
    """
    Export in OpenAI fine-tuning format.
    
    Format:
    {
        "messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }
    """
    print("Exporting for fine-tuning format...")
    
    with Session(engine) as session:
        # Get high-rated approvals
        stmt = select(models.Decision).where(
            models.Decision.decision == "approve",
            models.Decision.rating >= 4,
        )
        decisions = session.exec(stmt).all()
    
    system_prompt = """Sen Betül'ün tarzında yazan bir AI'sın. 
Kısa, minimal, feminen ve hafif alaycı metinler üretiyorsun.
Az konuşur, çok hissettirirsin."""
    
    samples = []
    for d in decisions:
        if not d.old_text or not d.vibe_mode_after:
            continue
            
        sample = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Vibe: {d.vibe_mode_after}\nBir caption yaz."},
                {"role": "assistant", "content": d.new_text or d.old_text},
            ]
        }
        samples.append(sample)
    
    output_file = Path(output_path)
    with open(output_file, "w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")
    
    print(f"✨ Exported {len(samples)} fine-tuning samples to {output_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Export Betül feedback data")
    parser.add_argument(
        "--format", 
        choices=["jsonl", "finetune"], 
        default="jsonl",
        help="Export format"
    )
    parser.add_argument(
        "--output", 
        default=None,
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    if args.format == "finetune":
        output = args.output or "betul_finetune_dataset.jsonl"
        export_for_finetuning(output)
    else:
        output = args.output or "betul_feedback_dataset.jsonl"
        export_feedback(output)

