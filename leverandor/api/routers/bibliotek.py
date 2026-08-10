from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from leverandor.api.database import get_session
from leverandor.api.models import Bibliotekelement

router = APIRouter(prefix="/bibliotek", tags=["bibliotek"])


@router.get("/{profil_id}")
def hent_bibliotek(profil_id: int, kategori: str | None = None, db: Session = Depends(get_session)):
    q = select(Bibliotekelement).where(Bibliotekelement.profil_id == profil_id)
    if kategori:
        q = q.where(Bibliotekelement.kategori == kategori)
    return db.exec(q).all()


@router.post("")
def legg_til_element(element: Bibliotekelement, db: Session = Depends(get_session)):
    db.add(element)
    db.commit()
    db.refresh(element)
    return element


@router.delete("/{element_id}")
def slett_element(element_id: int, db: Session = Depends(get_session)):
    element = db.get(Bibliotekelement, element_id)
    if not element:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Element ikke funnet")
    db.delete(element)
    db.commit()
    return {"slettet": element_id}
