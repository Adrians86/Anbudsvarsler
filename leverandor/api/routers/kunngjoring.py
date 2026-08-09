from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from leverandor.api.database import get_session
from leverandor.api.models import Kunngjoring

router = APIRouter(prefix="/kunngjoring", tags=["kunngjoring"])


@router.get("", response_model=list[Kunngjoring])
def sok_kunngjoring(
    cpv: Optional[str] = Query(None, description="CPV-kode filter"),
    region: Optional[str] = Query(None, description="NUTS-region filter"),
    fra: Optional[str] = Query(None, description="Publisert etter dato (YYYY-MM-DD)"),
    session: Session = Depends(get_session),
):
    stmt = select(Kunngjoring)
    results = session.exec(stmt).all()

    if cpv:
        results = [k for k in results if any(cpv in c for c in k.cpv_koder)]
    if region:
        results = [k for k in results if k.nuts_region == region]
    if fra:
        from datetime import datetime
        fra_dt = datetime.fromisoformat(fra)
        results = [k for k in results if k.publisert >= fra_dt]

    return results


@router.get("/{kunngjoring_id}", response_model=Kunngjoring)
def hent_kunngjoring(kunngjoring_id: int, session: Session = Depends(get_session)):
    k = session.get(Kunngjoring, kunngjoring_id)
    if not k:
        raise HTTPException(status_code=404, detail="Kunngjøring ikke funnet")
    return k
