from sqlmodel import SQLModel, Field, JSON, Column
from typing import Optional
from decimal import Decimal
from datetime import datetime


class LeverandorProfil(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    org_nr: str = Field(index=True)
    navn: str
    # Kontakt
    kontaktperson: Optional[str] = None
    epost: Optional[str] = None
    telefon: Optional[str] = None
    nettsted: Optional[str] = None
    # Adresse
    adresse: Optional[str] = None
    postnr: Optional[str] = None
    sted: Optional[str] = None
    organisasjonsform: Optional[str] = None
    # Økonomi
    antall_ansatte: Optional[int] = None
    aarlig_omsetning_nok: Optional[int] = None
    # Profil
    cpv_koder: list[str] = Field(default=[], sa_column=Column(JSON))
    nuts_regioner: list[str] = Field(default=[], sa_column=Column(JSON))
    min_verdi: Optional[Decimal] = None
    max_verdi: Optional[Decimal] = None
    kontrakt_preferanse: Optional[str] = None  # "rammeavtale" | "enkelt" | "begge"
    sertifiseringer: list[str] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Kunngjoring(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    kilde: str                        # "DOFFIN" | "TED"
    ekstern_id: str = Field(index=True, unique=True)
    tittel: str
    oppdragsgiver: str
    cpv_koder: list[str] = Field(default=[], sa_column=Column(JSON))
    nuts_region: Optional[str] = None
    estimert_verdi: Optional[Decimal] = None
    tilbudsfrist: Optional[datetime] = None
    publisert: datetime
    url: str
    raa_data: dict = Field(default={}, sa_column=Column(JSON))
    hentet_at: datetime = Field(default_factory=datetime.utcnow)


class Varsling(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profil_id: int = Field(foreign_key="leverandorprofil.id")
    kunngjoring_id: int = Field(foreign_key="kunngjoring.id")
    relevans_score: float
    cpv_match: list[str] = Field(default=[], sa_column=Column(JSON))
    status: str = "NY"               # NY|SETT|INTERESSERT|FORKASTET|LEVERT|VUNNET|TAPT
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Kvalifikasjonssjekk(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    varsling_id: int = Field(foreign_key="varsling.id")
    profil_id: int = Field(foreign_key="leverandorprofil.id")
    resultat: str                    # "GO" | "NO-GO" | "GÅ VIDERE MED FORBEHOLD"
    mangler: list[str] = Field(default=[], sa_column=Column(JSON))
    diskvalifiserende: list[str] = Field(default=[], sa_column=Column(JSON))
    rule_hits: list[dict] = Field(default=[], sa_column=Column(JSON))
    bekreftet_av_bruker: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SjekklisteElement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    varsling_id: int = Field(foreign_key="varsling.id")
    profil_id: int = Field(foreign_key="leverandorprofil.id")
    tekst: str
    ferdig: bool = False
    frist: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Bibliotekelement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profil_id: int = Field(foreign_key="leverandorprofil.id")
    kategori: str                    # "sertifikat" | "årsregnskap" | "referanse" | "mal" | "annet"
    tittel: str
    innhold: str = ""
    tags: list[str] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FirmaDokument(SQLModel, table=True):
    """Firmadokumenter med utløpsdato — brukt i kvalifikasjonssjekken."""
    id: Optional[int] = Field(default=None, primary_key=True)
    profil_id: int = Field(foreign_key="leverandorprofil.id")
    kategori: str   # "skatteattest"|"hms_erklæring"|"firmaattest"|"forsikringsbevis"|"årsregnskap"|"iso_sertifikat"|"hms_kort"|"egenerklæring"|"annet"
    tittel: str
    utloep_dato: Optional[datetime] = None
    lastet_opp: bool = False
    fil_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReferanseProsjekt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profil_id: int = Field(foreign_key="leverandorprofil.id")
    prosjektnavn: str
    oppdragsgiver_navn: str
    oppdragsgiver_org_nr: Optional[str] = None
    kontraktsverdi_nok: Optional[int] = None
    periode_fra: Optional[str] = None
    periode_til: Optional[str] = None
    cpv: Optional[str] = None
    beskrivelse: Optional[str] = None
    kontaktperson: Optional[str] = None
    kontakttelefon: Optional[str] = None
    kan_kontaktes: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
