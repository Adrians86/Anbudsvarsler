from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from leverandor.api.database import get_session
from leverandor.api.models import Kunngjoring, Kvalifikasjonssjekk, LeverandorProfil, Varsling

router = APIRouter(prefix="/kvalifikasjon", tags=["kvalifikasjon"])

MINIMUM_KRAV = [
    {"id": "K1", "beskrivelse": "Organisasjonsnummer registrert", "felt": "org_nr"},
    {"id": "K2", "beskrivelse": "Minst én CPV-kode definert", "felt": "cpv_koder"},
    {"id": "K3", "beskrivelse": "Antall ansatte oppgitt", "felt": "antall_ansatte"},
]


def sjekk_kvalifikasjon(profil: LeverandorProfil, kunngjoring: Kunngjoring) -> dict:
    mangler = []
    for krav in MINIMUM_KRAV:
        verdi = getattr(profil, krav["felt"], None)
        if not verdi:
            mangler.append(krav["beskrivelse"])

    if not mangler:
        resultat = "GO"
    elif len(mangler) <= 1:
        resultat = "GÅ VIDERE MED FORBEHOLD"
    else:
        resultat = "NO-GO"

    return {
        "resultat": resultat,
        "mangler": mangler,
        "diskvalifiserende": [],
        "rule_hits": [{"rule_id": k["id"], "beskrivelse": k["beskrivelse"]} for k in MINIMUM_KRAV],
    }


class KvalifikasjonRequest(BaseModel):
    varsling_id: int
    profil_id: int


@router.post("", response_model=Kvalifikasjonssjekk, status_code=201)
def utfor_kvalifikasjon(
    req: KvalifikasjonRequest,
    session: Session = Depends(get_session),
):
    varsling = session.get(Varsling, req.varsling_id)
    if not varsling:
        raise HTTPException(status_code=404, detail="Varsling ikke funnet")
    profil = session.get(LeverandorProfil, req.profil_id)
    if not profil:
        raise HTTPException(status_code=404, detail="Profil ikke funnet")
    kunngjoring = session.get(Kunngjoring, varsling.kunngjoring_id)
    if not kunngjoring:
        raise HTTPException(status_code=404, detail="Kunngjøring ikke funnet")

    sjekk = sjekk_kvalifikasjon(profil, kunngjoring)
    kvsjekk = Kvalifikasjonssjekk(
        varsling_id=req.varsling_id,
        profil_id=req.profil_id,
        resultat=sjekk["resultat"],
        mangler=sjekk["mangler"],
        diskvalifiserende=sjekk["diskvalifiserende"],
        rule_hits=sjekk["rule_hits"],
    )
    session.add(kvsjekk)
    session.commit()
    session.refresh(kvsjekk)
    return kvsjekk


@router.get("/{sjekk_id}", response_model=Kvalifikasjonssjekk)
def hent_kvalifikasjon(sjekk_id: int, session: Session = Depends(get_session)):
    sjekk = session.get(Kvalifikasjonssjekk, sjekk_id)
    if not sjekk:
        raise HTTPException(status_code=404, detail="Kvalifikasjonssjekk ikke funnet")
    return sjekk
