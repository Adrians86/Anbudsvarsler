from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from leverandor.api.database import get_session
from leverandor.api.models import ReferanseProsjekt

router = APIRouter(prefix="/referanse", tags=["referanse"])


@router.get("/{profil_id}")
def hent_referanser(profil_id: int, db: Session = Depends(get_session)):
    return db.exec(select(ReferanseProsjekt).where(ReferanseProsjekt.profil_id == profil_id)).all()


@router.post("", status_code=201)
def legg_til_referanse(ref: ReferanseProsjekt, db: Session = Depends(get_session)):
    db.add(ref)
    db.commit()
    db.refresh(ref)
    return ref


@router.put("/{ref_id}")
def oppdater_referanse(ref_id: int, oppdatering: dict, db: Session = Depends(get_session)):
    ref = db.get(ReferanseProsjekt, ref_id)
    if not ref:
        raise HTTPException(status_code=404, detail="Referanseprosjekt ikke funnet")
    for k, v in oppdatering.items():
        if hasattr(ref, k):
            setattr(ref, k, v)
    db.commit()
    db.refresh(ref)
    return ref


@router.delete("/{ref_id}")
def slett_referanse(ref_id: int, db: Session = Depends(get_session)):
    ref = db.get(ReferanseProsjekt, ref_id)
    if not ref:
        raise HTTPException(status_code=404, detail="Referanseprosjekt ikke funnet")
    db.delete(ref)
    db.commit()
    return {"slettet": ref_id}
