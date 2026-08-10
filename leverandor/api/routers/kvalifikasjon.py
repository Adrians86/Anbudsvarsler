from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from leverandor.api.database import get_session
from leverandor.api.models import (
    FirmaDokument, Kunngjoring, Kvalifikasjonssjekk,
    LeverandorProfil, ReferanseProsjekt, Varsling,
)

router = APIRouter(prefix="/kvalifikasjon", tags=["kvalifikasjon"])


def sjekk_kvalifikasjon(
    profil: LeverandorProfil,
    kunngjoring: Kunngjoring,
    session: Session | None = None,
) -> dict:
    """
    FOA kap. 16 + §24-2 kvalifikasjonssjekk.
    Session er valgfri for å bevare testbarhet uten DB.
    """
    nå = datetime.utcnow()
    mangler: list[str] = []
    diskval: list[str] = []
    rule_hits: list[dict] = []

    def hent_dok(kategori: str) -> list:
        if not session:
            return []
        return session.exec(
            select(FirmaDokument)
            .where(FirmaDokument.profil_id == profil.id)
            .where(FirmaDokument.kategori == kategori)
            .where(FirmaDokument.lastet_opp == True)  # noqa: E712
        ).all()

    # §16-2 — Skatteforhold
    skatteattester = hent_dok("skatteattest")
    gyldige_skatt = [d for d in skatteattester if not d.utloep_dato or d.utloep_dato > nå]
    if session and not gyldige_skatt:
        diskval.append("§16-2: Mangler gyldige skatteattester (< 6 mnd)")
        rule_hits.append({
            "regel": "FOA §16-2",
            "beskrivelse": "Last opp skatteattester fra Skatteetaten og kommunen (maks 6 måneder gamle)",
        })

    # §16-3 — HMS
    if session and not hent_dok("hms_erklæring"):
        mangler.append("§16-3: Mangler HMS-erklæring (§5 HMS-forskriften)")
        rule_hits.append({
            "regel": "FOA §16-3",
            "beskrivelse": "Last opp HMS-erklæring signert av øverste leder",
        })

    # §16-4 — Finansiell kapasitet
    if profil.aarlig_omsetning_nok and kunngjoring.estimert_verdi:
        terskel = float(kunngjoring.estimert_verdi) * 2
        if float(profil.aarlig_omsetning_nok) < terskel:
            mangler.append(
                f"§16-4: Omsetning ({profil.aarlig_omsetning_nok:,} NOK) er under 2× estimert kontraktsverdi"
            )
            rule_hits.append({
                "regel": "FOA §16-4",
                "beskrivelse": "Oppdragsgiver kan kreve at omsetning er ≥ 2× kontraktsverdien",
            })

    # §16-5 — Forsikring
    if session and not hent_dok("forsikringsbevis"):
        mangler.append("§16-5: Mangler forsikringsbevis")
        rule_hits.append({
            "regel": "FOA §16-5",
            "beskrivelse": "Last opp gyldig forsikringsbevis",
        })

    # §16-6 — Faglig kompetanse (CPV)
    if not profil.cpv_koder:
        mangler.append("§16-6: Ingen CPV-koder i profilen — faglig kompetanse ikke dokumentert")
        rule_hits.append({
            "regel": "FOA §16-6",
            "beskrivelse": "Legg til relevante CPV-koder i profilen din",
        })
    elif kunngjoring.cpv_koder and not (set(kunngjoring.cpv_koder) & set(profil.cpv_koder)):
        mangler.append("§16-6: Ingen CPV-kodeoverlapp mellom profil og kunngjøring")
        rule_hits.append({
            "regel": "FOA §16-6",
            "beskrivelse": "Oppdater CPV-profilen din til å inkludere koder fra denne kunngjøringen",
        })

    # §16-8 — Referanser
    if session:
        referanser = session.exec(
            select(ReferanseProsjekt).where(ReferanseProsjekt.profil_id == profil.id)
        ).all()
        if not referanser:
            mangler.append("§16-8: Ingen referanseprosjekter registrert i profilen")
            rule_hits.append({
                "regel": "FOA §16-8",
                "beskrivelse": "Legg til minst ett referanseprosjekt i profilen din",
            })

    # §24-2 — Firmaattest < 3 mnd
    firmaattester = hent_dok("firmaattest")
    gyldige_fa = [d for d in firmaattester if not d.utloep_dato or d.utloep_dato > nå]
    if session and not gyldige_fa:
        diskval.append("§24-2: Mangler gyldig firmaattest fra Brønnøysund (< 3 mnd)")
        rule_hits.append({
            "regel": "FOA §24-2",
            "beskrivelse": "Hent fersk firmaattest fra brreg.no (maks 3 måneder gammel)",
        })

    # §24-2 — Etisk egenerklæring
    if session and not hent_dok("egenerklæring"):
        mangler.append("§24-2: Mangler etisk egenerklæring")
        rule_hits.append({
            "regel": "FOA §24-2",
            "beskrivelse": "Last opp signert etisk egenerklæring",
        })

    # Uten session: grunnleggende profilsjekk (bevarer eksisterende testgrenser)
    if not session:
        if not profil.org_nr:
            diskval.append("Mangler organisasjonsnummer")
        if not profil.cpv_koder:
            mangler.append("Ingen CPV-koder definert i profilen")
        if not profil.antall_ansatte:
            mangler.append("Antall ansatte ikke oppgitt")
        # Strengere terskel uten full dokumentasjonssjekk
        if diskval or len(mangler) >= 2:
            return {
                "resultat": "NO-GO",
                "mangler": mangler,
                "diskvalifiserende": diskval,
                "rule_hits": rule_hits,
            }
        if mangler:
            return {
                "resultat": "GÅ VIDERE MED FORBEHOLD",
                "mangler": mangler,
                "diskvalifiserende": diskval,
                "rule_hits": rule_hits,
            }
        return {"resultat": "GO", "mangler": [], "diskvalifiserende": [], "rule_hits": rule_hits}

    # Resultat (med session / full FOA-sjekk)
    if diskval:
        resultat = "NO-GO"
    elif mangler:
        resultat = "GÅ VIDERE MED FORBEHOLD"
    else:
        resultat = "GO"

    return {
        "resultat": resultat,
        "mangler": mangler,
        "diskvalifiserende": diskval,
        "rule_hits": rule_hits,
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

    sjekk = sjekk_kvalifikasjon(profil, kunngjoring, session)
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


@router.put("/{sjekk_id}", response_model=Kvalifikasjonssjekk)
def bekreft_kvalifikasjon(sjekk_id: int, oppdatering: dict, session: Session = Depends(get_session)):
    sjekk = session.get(Kvalifikasjonssjekk, sjekk_id)
    if not sjekk:
        raise HTTPException(status_code=404, detail="Kvalifikasjonssjekk ikke funnet")
    for k, v in oppdatering.items():
        if hasattr(sjekk, k):
            setattr(sjekk, k, v)
    session.add(sjekk)
    session.commit()
    session.refresh(sjekk)
    return sjekk
