"""
╔══════════════════════════════════════════════════════════════════╗
║   AuroraOS State Module — API Router                             ║
║   Government data endpoints                                      ║
║                                                                  ║
║   Endpoints:                                                     ║
║   - GET  /dashboard         → Full dashboard stats               ║
║   - CRUD /citizens          → Citizen management                 ║
║   - CRUD /treasury          → Economic transactions              ║
║   - CRUD /ai-operations     → AI activity logs                   ║
║   - CRUD /flags             → Content moderation                 ║
║                                                                  ║
║   Baron Baba © SiyahKare, 2025                                   ║
╚══════════════════════════════════════════════════════════════════╝
"""

from datetime import datetime, timedelta
from typing import Optional, List
import uuid
import random

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func

from ..deps import get_db
from .models import (
    Citizen,
    CitizenStatus,
    CitizenTier,
    TreasuryTransaction,
    TreasurySnapshot,
    TransactionType,
    AIOperation,
    AIOperationType,
    AIOperationStatus,
    ContentFlag,
    FlagType,
    ThreatLog,
)
from .schemas import (
    DashboardStats,
    CitizenStats,
    TreasuryStats,
    ThreatStatus,
    CitizenCreate,
    CitizenUpdate,
    CitizenOut,
    CitizenListItem,
    CitizenBanRequest,
    TransactionCreate,
    TransactionOut,
    TreasuryHistory,
    AIOperationCreate,
    AIOperationOut,
    AIOperationUpdate,
    ContentFlagCreate,
    ContentFlagOut,
    ContentFlagResolve,
)


router = APIRouter()


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def generate_id(prefix: str) -> str:
    """Generate a unique ID with prefix."""
    date_part = datetime.utcnow().strftime("%Y%m%d")
    random_part = str(uuid.uuid4())[:8].upper()
    return f"{prefix}-{date_part}-{random_part}"


def format_number(n: float) -> str:
    """Format number with commas."""
    return f"{n:,.0f}"


def format_percentage(n: float) -> str:
    """Format as percentage with sign."""
    return f"{'+' if n >= 0 else ''}{n:.1f}%"


# ═══════════════════════════════════════════════════════════════════
# DASHBOARD — Main stats endpoint
# ═══════════════════════════════════════════════════════════════════

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    📊 Get complete dashboard statistics.
    
    Returns citizen, treasury, threat, and AI operation stats.
    """
    # Citizen stats
    total_citizens = db.exec(select(func.count(Citizen.id))).one() or 0
    verified = db.exec(
        select(func.count(Citizen.id))
        .where(Citizen.status == CitizenStatus.VERIFIED)
    ).one() or 0
    pending = db.exec(
        select(func.count(Citizen.id))
        .where(Citizen.status == CitizenStatus.PENDING)
    ).one() or 0
    online = db.exec(
        select(func.count(Citizen.id))
        .where(Citizen.is_online == True)
    ).one() or 0
    banned = db.exec(
        select(func.count(Citizen.id))
        .where(Citizen.status == CitizenStatus.BANNED)
    ).one() or 0
    
    # New today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    new_today = db.exec(
        select(func.count(Citizen.id))
        .where(Citizen.joined_at >= today_start)
    ).one() or 0
    
    # By tier
    tier_counts = {}
    for tier in CitizenTier:
        count = db.exec(
            select(func.count(Citizen.id))
            .where(Citizen.tier == tier)
        ).one() or 0
        tier_counts[tier.value] = count
    
    citizen_stats = CitizenStats(
        total=total_citizens,
        verified=verified,
        pending=pending,
        online=online,
        banned=banned,
        new_today=new_today,
        basic_count=tier_counts.get("BASIC", 0),
        silver_count=tier_counts.get("SILVER", 0),
        gold_count=tier_counts.get("GOLD", 0),
        platinum_count=tier_counts.get("PLATINUM", 0),
        founder_count=tier_counts.get("FOUNDER", 0),
    )
    
    # Treasury stats - get latest snapshot or calculate
    snapshot = db.exec(
        select(TreasurySnapshot)
        .order_by(TreasurySnapshot.date.desc())
        .limit(1)
    ).first()
    
    if snapshot:
        reserve_raw = snapshot.total_reserve
        gdp_raw = snapshot.gdp_growth
        inflation_raw = snapshot.inflation_rate
        transactions_24h = snapshot.transaction_count
    else:
        # Calculate from transactions if no snapshot
        reserve_raw = 4500000.0  # Default
        gdp_raw = 12.0
        inflation_raw = -2.4
        transactions_24h = db.exec(
            select(func.count(TreasuryTransaction.id))
            .where(TreasuryTransaction.created_at >= today_start)
        ).one() or 0
    
    # Volume 24h
    volume_result = db.exec(
        select(func.sum(TreasuryTransaction.amount))
        .where(TreasuryTransaction.created_at >= today_start)
    ).one()
    volume_24h = volume_result or 0.0
    
    treasury_stats = TreasuryStats(
        reserve=f"{format_number(reserve_raw)} NCR",
        reserve_raw=reserve_raw,
        gdp_24h=format_percentage(gdp_raw),
        gdp_raw=gdp_raw,
        inflation=format_percentage(inflation_raw),
        inflation_raw=inflation_raw,
        liquidity="High" if reserve_raw > 1000000 else "Medium" if reserve_raw > 100000 else "Low",
        transactions_24h=transactions_24h,
        volume_24h=volume_24h,
        avg_transaction=volume_24h / transactions_24h if transactions_24h > 0 else 0,
    )
    
    # Threat status
    active_threats = db.exec(
        select(func.count(ThreatLog.id))
        .where(ThreatLog.status == "ACTIVE")
    ).one() or 0
    
    mitigated_24h = db.exec(
        select(func.count(ThreatLog.id))
        .where(
            ThreatLog.status == "MITIGATED",
            ThreatLog.mitigated_at >= today_start - timedelta(days=1),
        )
    ).one() or 0
    
    last_threat = db.exec(
        select(ThreatLog)
        .order_by(ThreatLog.created_at.desc())
        .limit(1)
    ).first()
    
    threat_status = ThreatStatus(
        level="LOW" if active_threats == 0 else "MEDIUM" if active_threats < 3 else "HIGH",
        active_threats=active_threats,
        mitigated_24h=mitigated_24h,
        last_incident=last_threat.created_at if last_threat else None,
        details=f"{active_threats} Cyber-Attacks detected" if active_threats > 0 else "0 Cyber-Attacks detected",
    )
    
    # AI operations 24h
    ai_ops_24h = db.exec(
        select(func.count(AIOperation.id))
        .where(AIOperation.created_at >= today_start)
    ).one() or 0
    
    # Flagged content
    flagged = db.exec(
        select(func.count(ContentFlag.id))
        .where(ContentFlag.status == "PENDING")
    ).one() or 0
    
    return DashboardStats(
        citizens=citizen_stats,
        treasury=treasury_stats,
        threat=threat_status,
        ai_operations_24h=ai_ops_24h,
        flagged_content=flagged,
    )


# ═══════════════════════════════════════════════════════════════════
# CITIZENS — User management
# ═══════════════════════════════════════════════════════════════════

@router.get("/citizens", response_model=List[CitizenListItem])
def list_citizens(
    status: Optional[CitizenStatus] = None,
    tier: Optional[CitizenTier] = None,
    online_only: bool = False,
    search: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """📋 List citizens with filters."""
    stmt = select(Citizen)
    
    if status:
        stmt = stmt.where(Citizen.status == status)
    if tier:
        stmt = stmt.where(Citizen.tier == tier)
    if online_only:
        stmt = stmt.where(Citizen.is_online == True)
    if search:
        stmt = stmt.where(
            (Citizen.display_name.contains(search)) |
            (Citizen.citizen_id.contains(search)) |
            (Citizen.email.contains(search))
        )
    
    stmt = stmt.order_by(Citizen.joined_at.desc()).offset(offset).limit(limit)
    
    return db.exec(stmt).all()


@router.post("/citizens", response_model=CitizenOut)
def create_citizen(
    payload: CitizenCreate,
    db: Session = Depends(get_db),
):
    """➕ Create a new citizen."""
    citizen = Citizen(
        citizen_id=generate_id("CZ"),
        display_name=payload.display_name,
        email=payload.email,
        phone=payload.phone,
        telegram_id=payload.telegram_id,
        tier=payload.tier,
        status=CitizenStatus.PENDING,
    )
    
    db.add(citizen)
    db.commit()
    db.refresh(citizen)
    
    return citizen


@router.get("/citizens/{citizen_id}", response_model=CitizenOut)
def get_citizen(
    citizen_id: str,
    db: Session = Depends(get_db),
):
    """👤 Get citizen by ID."""
    stmt = select(Citizen).where(
        (Citizen.citizen_id == citizen_id) |
        (Citizen.id == int(citizen_id) if citizen_id.isdigit() else False)
    )
    citizen = db.exec(stmt).first()
    
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")
    
    return citizen


@router.patch("/citizens/{citizen_id}", response_model=CitizenOut)
def update_citizen(
    citizen_id: str,
    payload: CitizenUpdate,
    db: Session = Depends(get_db),
):
    """✏️ Update citizen details."""
    citizen = db.exec(
        select(Citizen).where(Citizen.citizen_id == citizen_id)
    ).first()
    
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")
    
    if payload.display_name is not None:
        citizen.display_name = payload.display_name
    if payload.email is not None:
        citizen.email = payload.email
    if payload.phone is not None:
        citizen.phone = payload.phone
    if payload.tier is not None:
        citizen.tier = payload.tier
    if payload.status is not None:
        citizen.status = payload.status
        if payload.status == CitizenStatus.VERIFIED:
            citizen.verified_at = datetime.utcnow()
    
    db.add(citizen)
    db.commit()
    db.refresh(citizen)
    
    return citizen


@router.post("/citizens/{citizen_id}/verify", response_model=CitizenOut)
def verify_citizen(
    citizen_id: str,
    db: Session = Depends(get_db),
):
    """✅ Verify a citizen."""
    citizen = db.exec(
        select(Citizen).where(Citizen.citizen_id == citizen_id)
    ).first()
    
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")
    
    citizen.status = CitizenStatus.VERIFIED
    citizen.verified_at = datetime.utcnow()
    
    db.add(citizen)
    db.commit()
    db.refresh(citizen)
    
    return citizen


@router.post("/citizens/{citizen_id}/ban")
def ban_citizen(
    citizen_id: str,
    payload: CitizenBanRequest,
    db: Session = Depends(get_db),
):
    """🚫 Ban a citizen."""
    citizen = db.exec(
        select(Citizen).where(Citizen.citizen_id == citizen_id)
    ).first()
    
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")
    
    citizen.status = CitizenStatus.BANNED
    citizen.banned_at = datetime.utcnow()
    citizen.ban_reason = payload.reason
    
    db.add(citizen)
    db.commit()
    
    return {"success": True, "citizen_id": citizen_id, "reason": payload.reason}


# ═══════════════════════════════════════════════════════════════════
# TREASURY — Economic transactions
# ═══════════════════════════════════════════════════════════════════

@router.get("/treasury/transactions", response_model=List[TransactionOut])
def list_transactions(
    type: Optional[TransactionType] = None,
    citizen_id: Optional[int] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """📋 List treasury transactions."""
    stmt = select(TreasuryTransaction)
    
    if type:
        stmt = stmt.where(TreasuryTransaction.type == type)
    if citizen_id:
        stmt = stmt.where(TreasuryTransaction.citizen_id == citizen_id)
    
    stmt = stmt.order_by(TreasuryTransaction.created_at.desc()).offset(offset).limit(limit)
    
    return db.exec(stmt).all()


@router.post("/treasury/transactions", response_model=TransactionOut)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
):
    """💰 Create a treasury transaction."""
    transaction = TreasuryTransaction(
        transaction_id=generate_id("TX"),
        type=payload.type,
        amount=payload.amount,
        citizen_id=payload.citizen_id,
        from_account=payload.from_account,
        to_account=payload.to_account,
        description=payload.description,
        reference=payload.reference,
        processed_at=datetime.utcnow(),
    )
    
    db.add(transaction)
    
    # Update citizen balance if applicable
    if payload.citizen_id:
        citizen = db.get(Citizen, payload.citizen_id)
        if citizen:
            if payload.type in (TransactionType.DEPOSIT, TransactionType.REWARD):
                citizen.balance += payload.amount
                citizen.total_earned += payload.amount
            elif payload.type in (TransactionType.WITHDRAWAL, TransactionType.PENALTY, TransactionType.FEE):
                citizen.balance -= payload.amount
                citizen.total_spent += payload.amount
            db.add(citizen)
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.get("/treasury/history", response_model=List[TreasuryHistory])
def get_treasury_history(
    days: int = Query(default=7, le=90),
    db: Session = Depends(get_db),
):
    """📈 Get treasury history."""
    since = datetime.utcnow() - timedelta(days=days)
    
    snapshots = db.exec(
        select(TreasurySnapshot)
        .where(TreasurySnapshot.date >= since)
        .order_by(TreasurySnapshot.date.asc())
    ).all()
    
    return [
        TreasuryHistory(
            date=s.date,
            total_reserve=s.total_reserve,
            gdp_24h=s.gdp_24h,
            gdp_growth=s.gdp_growth,
            transaction_count=s.transaction_count,
            active_citizens=s.active_citizens,
        )
        for s in snapshots
    ]


# ═══════════════════════════════════════════════════════════════════
# AI OPERATIONS — Activity logs
# ═══════════════════════════════════════════════════════════════════

@router.get("/ai-operations", response_model=List[AIOperationOut])
def list_ai_operations(
    type: Optional[AIOperationType] = None,
    status: Optional[AIOperationStatus] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """📋 List AI operations."""
    stmt = select(AIOperation)
    
    if type:
        stmt = stmt.where(AIOperation.type == type)
    if status:
        stmt = stmt.where(AIOperation.status == status)
    
    stmt = stmt.order_by(AIOperation.created_at.desc()).offset(offset).limit(limit)
    
    return db.exec(stmt).all()


@router.post("/ai-operations", response_model=AIOperationOut)
def create_ai_operation(
    payload: AIOperationCreate,
    db: Session = Depends(get_db),
):
    """🤖 Create a new AI operation."""
    operation = AIOperation(
        operation_id=generate_id("OP"),
        type=payload.type,
        target=payload.target,
        target_type=payload.target_type,
        status=AIOperationStatus.PENDING,
        started_at=datetime.utcnow(),
    )
    
    db.add(operation)
    db.commit()
    db.refresh(operation)
    
    return operation


@router.patch("/ai-operations/{operation_id}", response_model=AIOperationOut)
def update_ai_operation(
    operation_id: str,
    payload: AIOperationUpdate,
    db: Session = Depends(get_db),
):
    """🔄 Update AI operation status."""
    operation = db.exec(
        select(AIOperation).where(AIOperation.operation_id == operation_id)
    ).first()
    
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    operation.status = payload.status
    if payload.result is not None:
        operation.result = payload.result
    if payload.sentiment is not None:
        operation.sentiment = payload.sentiment
    if payload.confidence is not None:
        operation.confidence = payload.confidence
    
    if payload.status == AIOperationStatus.COMPLETED:
        operation.completed_at = datetime.utcnow()
        if operation.started_at:
            operation.duration_seconds = int(
                (operation.completed_at - operation.started_at).total_seconds()
            )
    
    db.add(operation)
    db.commit()
    db.refresh(operation)
    
    return operation


# ═══════════════════════════════════════════════════════════════════
# CONTENT FLAGS — Moderation
# ═══════════════════════════════════════════════════════════════════

@router.get("/flags", response_model=List[ContentFlagOut])
def list_flags(
    status: Optional[str] = "PENDING",
    type: Optional[FlagType] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """📋 List content flags."""
    stmt = select(ContentFlag)
    
    if status:
        stmt = stmt.where(ContentFlag.status == status)
    if type:
        stmt = stmt.where(ContentFlag.type == type)
    
    stmt = stmt.order_by(ContentFlag.created_at.desc()).offset(offset).limit(limit)
    
    return db.exec(stmt).all()


@router.post("/flags", response_model=ContentFlagOut)
def create_flag(
    payload: ContentFlagCreate,
    db: Session = Depends(get_db),
):
    """🚩 Flag content for moderation."""
    flag = ContentFlag(
        flag_id=generate_id("FL"),
        type=payload.type,
        severity=payload.severity,
        content_type=payload.content_type,
        content_id=payload.content_id,
        content_preview=payload.content_preview,
        citizen_id=payload.citizen_id,
        reporter_type=payload.reporter_type,
    )
    
    db.add(flag)
    db.commit()
    db.refresh(flag)
    
    return flag


@router.post("/flags/{flag_id}/resolve", response_model=ContentFlagOut)
def resolve_flag(
    flag_id: str,
    payload: ContentFlagResolve,
    db: Session = Depends(get_db),
):
    """✅ Resolve a content flag."""
    flag = db.exec(
        select(ContentFlag).where(ContentFlag.flag_id == flag_id)
    ).first()
    
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")
    
    flag.status = payload.status
    flag.resolution = payload.resolution
    flag.resolved_at = datetime.utcnow()
    flag.resolved_by = "operator"  # TODO: Get from auth
    
    db.add(flag)
    db.commit()
    db.refresh(flag)
    
    return flag

