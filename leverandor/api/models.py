from sqlmodel import SQLModel, Field, JSON, Column
from typing import Optional
from decimal import Decimal
from datetime import datetime


class LeverandorProfil(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    org_nr: str = Field(index=True)
    navn: str
    cpv_koder: list[str] = Field(default=[], sa_column=Column(JSON))
    nuts_regioner: list[str] = Field(default=[], sa_column=Column(JSON))
    min_verdi: Optional[Decimal] = None
    max_verdi: Optional[Decimal] = None
    antall_ansatte: Optional[int] = None
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
