from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from leverandor.api.database import get_session
from leverandor.api.models import LeverandorProfil

router = APIRouter(prefix="/profil", tags=["profil"])


@router.post("", response_model=LeverandorProfil, status_code=201)
def opprett_profil(profil: LeverandorProfil, session: Session = Depends(get_session)):
    session.add(profil)
    session.commit()
    session.refresh(profil)
    return profil


@router.get("/{profil_id}", response_model=LeverandorProfil)
def hent_profil(profil_id: int, session: Session = Depends(get_session)):
    profil = session.get(LeverandorProfil, profil_id)
    if not profil:
        raise HTTPException(status_code=404, detail="Profil ikke funnet")
    return profil


@router.put("/{profil_id}", response_model=LeverandorProfil)
def oppdater_profil(
    profil_id: int,
    data: LeverandorProfil,
    session: Session = Depends(get_session),
):
    profil = session.get(LeverandorProfil, profil_id)
    if not profil:
        raise HTTPException(status_code=404, detail="Profil ikke funnet")
    update_data = data.model_dump(exclude_unset=True, exclude={"id", "created_at"})
    for key, value in update_data.items():
        setattr(profil, key, value)
    session.add(profil)
    session.commit()
    session.refresh(profil)
    return profil


@router.delete("/{profil_id}", status_code=204)
def slett_profil(profil_id: int, session: Session = Depends(get_session)):
    profil = session.get(LeverandorProfil, profil_id)
    if not profil:
        raise HTTPException(status_code=404, detail="Profil ikke funnet")
    session.delete(profil)
    session.commit()
