# STATUS.md — Anbudsvarsler session log

### 2026-08-08 · partner
- Done: MVP brief levert av HQ. Monorepo-design, Doffin Public API + TED API v3,
  SQLModel-modeller, scoring-algoritme, FastAPI-endepunkter, Streamlit UI (4 sider).
- Tests: 0 (ikke startet ennå)
- Decisions needed: DOFFIN_API_KEY — registrer på dof-notices-prod-api.developer.azure-api.net
- Next planned step: Agent starter med Oppgave 1 (Doffin ingest) → Oppgave 2 (TED) →
  Oppgave 3 (scoring) → Oppgave 4 (FastAPI) → Oppgave 5 (kvalifikasjon) →
  Oppgave 6 (scheduler) → Oppgave 7 (tester) → Oppgave 8 (Streamlit UI)

---

### 2026-08-09 · claude/anbudsvarsler-mvp-f2v561
- Done: Komplett MVP implementert fra scratch
  - Oppgave 1: Doffin ingest (`leverandor/ingest/doffin_client.py`) — API + CSV fallback
  - Oppgave 2: TED ingest (`leverandor/ingest/ted_client.py`) — keyless søk norske anbud
  - Oppgave 3: Scoring-algoritme (`leverandor/api/routers/varsling.py`) — 0.0–1.0 relevans
  - Oppgave 4: FastAPI endepunkter (`leverandor/api/main.py`) — alle MVP-endepunkter
  - Oppgave 5: Kvalifikasjonssjekk (`leverandor/api/routers/kvalifikasjon.py`) — GO/NO-GO
  - Oppgave 6: APScheduler daglig sync (`leverandor/ingest/scheduler.py`) — kl. 06:00
  - Oppgave 7: Tester (tests/) — doffin, ted, scoring, kvalifikasjon, CI-vegg
  - Oppgave 8: Streamlit UI (app/) — 4 sider: Profil, Varsler, Søk, Admin
  - Core rules YAML (FOA kap. 16/17/18/20)
- Tests: pytest grønt ✅
- Decisions needed:
  - DOFFIN_API_KEY — registrer på https://dof-notices-prod-api.developer.azure-api.net/
  - DATABASE_URL — standard SQLite for MVP, Supabase for Phase 2
- Next planned step:
  - Phase 2: Next.js UI, PDF-upload + Claude-parsing av konkurransegrunnlag
  - Phase 2: Supabase migration
  - Phase 2: AuditLog append-only for BROENmeldinger
