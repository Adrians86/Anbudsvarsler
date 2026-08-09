from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from leverandor.api.database import get_session
from leverandor.api.models import Kunngjoring, LeverandorProfil, Varsling

router = APIRouter(prefix="/varsling", tags=["varsling"])

GYLDIGE_STATUSER = {"NY", "SETT", "INTERESSERT", "FORKASTET", "LEVERT", "VUNNET", "TAPT"}


def score_match(kunngjoring: Kunngjoring, profil: LeverandorProfil) -> float:
    """Relevans-score algoritme (0.0 – 1.0)."""
    score = 0.0

    k_cpv = set(kunngjoring.cpv_koder)
    p_cpv = set(profil.cpv_koder)
    if k_cpv & p_cpv:
        overlap = len(k_cpv & p_cpv) / max(len(k_cpv), 1)
        score += min(0.4, overlap * 0.4)

    if not profil.nuts_regioner or kunngjoring.nuts_region in profil.nuts_regioner:
        score += 0.2

    v = kunngjoring.estimert_verdi
    if v is None or (
        (profil.min_verdi is None or v >= profil.min_verdi)
        and (profil.max_verdi is None or v <= profil.max_verdi)
    ):
        score += 0.2

    if kunngjoring.tilbudsfrist:
        dager = (kunngjoring.tilbudsfrist - datetime.utcnow()).days
        if dager >= 14:
            score += 0.1

    score += 0.1

    return round(score, 3)


@router.get("", response_model=list[Varsling])
def mine_varsler(
    profil_id: int = Query(..., description="Profil ID"),
    session: Session = Depends(get_session),
):
    varsler = session.exec(
        select(Varsling)
        .where(Varsling.profil_id == profil_id)
        .order_by(Varsling.relevans_score.desc())  # type: ignore[union-attr]
    ).all()
    return varsler


@router.put("/{varsling_id}/status", response_model=Varsling)
def oppdater_status(
    varsling_id: int,
    ny_status: str = Query(..., description="Ny status"),
    session: Session = Depends(get_session),
):
    if ny_status not in GYLDIGE_STATUSER:
        raise HTTPException(
            status_code=422,
            detail=f"Ugyldig status. Gyldige verdier: {sorted(GYLDIGE_STATUSER)}",
        )
    varsling = session.get(Varsling, varsling_id)
    if not varsling:
        raise HTTPException(status_code=404, detail="Varsling ikke funnet")
    varsling.status = ny_status
    session.add(varsling)
    session.commit()
    session.refresh(varsling)
    return varsling
