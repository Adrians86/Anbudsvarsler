from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from leverandor.api.database import get_session
from leverandor.api.models import FirmaDokument

router = APIRouter(prefix="/dokument", tags=["dokument"])


@router.get("/{profil_id}")
def hent_dokumenter(profil_id: int, kategori: str | None = None, db: Session = Depends(get_session)):
    q = select(FirmaDokument).where(FirmaDokument.profil_id == profil_id)
    if kategori:
        q = q.where(FirmaDokument.kategori == kategori)
    return db.exec(q).all()


@router.post("", status_code=201)
def legg_til_dokument(dok: FirmaDokument, db: Session = Depends(get_session)):
    db.add(dok)
    db.commit()
    db.refresh(dok)
    return dok


@router.put("/{dok_id}")
def oppdater_dokument(dok_id: int, oppdatering: dict, db: Session = Depends(get_session)):
    dok = db.get(FirmaDokument, dok_id)
    if not dok:
        raise HTTPException(status_code=404, detail="Dokument ikke funnet")
    for k, v in oppdatering.items():
        if hasattr(dok, k):
            setattr(dok, k, v)
    db.commit()
    db.refresh(dok)
    return dok


@router.delete("/{dok_id}")
def slett_dokument(dok_id: int, db: Session = Depends(get_session)):
    dok = db.get(FirmaDokument, dok_id)
    if not dok:
        raise HTTPException(status_code=404, detail="Dokument ikke funnet")
    db.delete(dok)
    db.commit()
    return {"slettet": dok_id}
