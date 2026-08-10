from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from leverandor.api.database import get_session
from leverandor.api.models import SjekklisteElement

router = APIRouter(prefix="/sjekkliste", tags=["sjekkliste"])


@router.get("/{varsling_id}")
def hent_sjekkliste(varsling_id: int, db: Session = Depends(get_session)):
    return db.exec(select(SjekklisteElement).where(SjekklisteElement.varsling_id == varsling_id)).all()


@router.post("")
def opprett_element(element: SjekklisteElement, db: Session = Depends(get_session)):
    db.add(element)
    db.commit()
    db.refresh(element)
    return element


@router.put("/{element_id}")
def oppdater_element(element_id: int, oppdatering: dict, db: Session = Depends(get_session)):
    element = db.get(SjekklisteElement, element_id)
    if not element:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Element ikke funnet")
    for k, v in oppdatering.items():
        if hasattr(element, k):
            setattr(element, k, v)
    db.commit()
    db.refresh(element)
    return element
