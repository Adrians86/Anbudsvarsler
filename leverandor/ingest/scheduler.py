from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select

from leverandor.api.database import engine
from leverandor.api.models import LeverandorProfil, Kunngjoring, Varsling
from leverandor.ingest.doffin_client import fetch_recent_doffin
from leverandor.ingest.ted_client import fetch_recent_ted


def run_daily_sync(session: Session | None = None):
    """Hent kunngjøringer fra Doffin og TED, upsert til DB, generer varsler."""
    own_session = session is None
    if own_session:
        session = Session(engine)

    try:
        doffin = fetch_recent_doffin(days_back=2)
        ted = fetch_recent_ted(days_back=2)
        all_notices = doffin + ted

        new_count = 0
        for kunngjoring in all_notices:
            existing = session.exec(
                select(Kunngjoring).where(Kunngjoring.ekstern_id == kunngjoring.ekstern_id)
            ).first()
            if not existing:
                session.add(kunngjoring)
                new_count += 1

        session.commit()

        profiler = session.exec(select(LeverandorProfil)).all()
        saved_notices = session.exec(select(Kunngjoring)).all()
        varsler_count = 0
        for profil in profiler:
            for k in saved_notices:
                from leverandor.api.routers.varsling import score_match

                score = score_match(k, profil)
                if score >= 0.3:
                    existing_v = session.exec(
                        select(Varsling)
                        .where(Varsling.profil_id == profil.id)
                        .where(Varsling.kunngjoring_id == k.id)
                    ).first()
                    if not existing_v:
                        cpv_match = list(set(k.cpv_koder) & set(profil.cpv_koder))
                        v = Varsling(
                            profil_id=profil.id,
                            kunngjoring_id=k.id,
                            relevans_score=score,
                            cpv_match=cpv_match,
                        )
                        session.add(v)
                        varsler_count += 1

        session.commit()
        print(f"Sync ferdig: {new_count} nye kunngjøringer, {varsler_count} nye varsler")
    finally:
        if own_session:
            session.close()


scheduler = BackgroundScheduler(timezone="Europe/Oslo")
scheduler.add_job(run_daily_sync, "cron", hour=6, minute=0)
