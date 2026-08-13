import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from leverandor.api.database import create_db_and_tables, engine
from leverandor.api.models import Kunngjoring, LeverandorProfil, Varsling
from leverandor.api.routers import kunngjoring, kvalifikasjon, profil, varsling
from leverandor.api.routers import sjekkliste, bibliotek, dokument, referanse
from leverandor.api.routers.varsling import score_match

load_dotenv()

VERSION = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Anbudsvarsler API", version=VERSION, lifespan=lifespan)

_raw = os.getenv(
    "CORS_ORIGINS",
    "https://anbudsvarsler.netlify.app,http://localhost:3000,http://localhost:8501",
)
_origins = [o.strip() for o in _raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profil.router)
app.include_router(kunngjoring.router)
app.include_router(varsling.router)
app.include_router(kvalifikasjon.router)
app.include_router(sjekkliste.router)
app.include_router(bibliotek.router)
app.include_router(dokument.router)
app.include_router(referanse.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": VERSION}


@app.post("/admin/sync")
def manuell_sync():
    """Kjør Doffin + TED ingest manuelt."""
    from leverandor.ingest.doffin_client import fetch_recent_doffin
    from leverandor.ingest.ted_client import fetch_recent_ted

    try:
        doffin = fetch_recent_doffin(days_back=2)
    except Exception:
        logging.exception("Doffin ingest failed")
        doffin = []

    try:
        ted = fetch_recent_ted(days_back=2)
    except Exception:
        logging.exception("TED ingest failed")
        ted = []

    all_notices = doffin + ted
    new_count = 0
    varsler_count = 0

    try:
        with Session(engine) as session:
            for kunngjoring_obj in all_notices:
                existing = session.exec(
                    select(Kunngjoring).where(
                        Kunngjoring.ekstern_id == kunngjoring_obj.ekstern_id
                    )
                ).first()
                if not existing:
                    session.add(kunngjoring_obj)
                    new_count += 1
            session.commit()

            profiler = session.exec(select(LeverandorProfil)).all()
            saved = session.exec(select(Kunngjoring)).all()
            for p in profiler:
                for k in saved:
                    s = score_match(k, p)
                    if s >= 0.3:
                        exists = session.exec(
                            select(Varsling)
                            .where(Varsling.profil_id == p.id)
                            .where(Varsling.kunngjoring_id == k.id)
                        ).first()
                        if not exists:
                            cpv_match = list(set(k.cpv_koder) & set(p.cpv_koder))
                            session.add(
                                Varsling(
                                    profil_id=p.id,
                                    kunngjoring_id=k.id,
                                    relevans_score=s,
                                    cpv_match=cpv_match,
                                )
                            )
                            varsler_count += 1
            session.commit()
    except Exception:
        logging.exception("DB error during sync")
        return JSONResponse(
            status_code=500,
            content={"error": "Database error during sync — check server logs"},
        )

    return {
        "nye_kunngjøringer": new_count,
        "nye_varsler": varsler_count,
        "totalt_hentet": len(all_notices),
        "doffin": len(doffin),
        "ted": len(ted),
    }
