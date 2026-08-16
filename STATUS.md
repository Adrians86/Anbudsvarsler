# Anbudsvarsler — Status

Sist oppdatert: 2026-08-16

## v2.2 DoD

| # | Oppgave | Status |
|---|---------|--------|
| 1 | pytest grønn etter Fix 1 (TED multilingual) | ✅ 17/17 pass |
| 2 | TED-titler vises på engelsk/norsk (case-insensitive, ENG→NOR→NOB→MUL) | ✅ Kode levert |
| 3 | Sync-knapp synlig på Hjem, identisk med Admin | ✅ Levert |
| 4 | Deploy Netlify (Next.js) + Render (FastAPI) oppdatert | ⏳ Automatisk ved push |
| 5 | STATUS.md oppdatert | ✅ Denne filen |
| 6 | HQ fullført end-to-end flow og bekreftet GO/NO-GO | ⬜ Manuell test (Fix 3) |

## Nåværende branch

`claude/anbudsvarsler-mvp-f2v561`

## Siste endringer

### v2.2 (2026-08-16)
- `leverandor/ingest/ted_client.py` — `_get_multilingual` er nå case-insensitiv og prioriterer ENG→NOR→NOB→MUL
- `tests/test_ted_client.py` — 2 nye tester: lowercase-nøkler og MUL-fallback (17 tester totalt)
- `web/src/app/page.tsx` — "Oppdater kunngjøringer"-knapp lagt til under KPI-radene på Hjem
- `web/src/app/*/page.tsx` (6 filer) — sessionStorage-tekst erstattet med lenker til /profil

### v2.1 (2026-08-14)
- Next.js 14 frontend i `web/` med 13 ruter + ProfileContext
- CORS-middleware lagt til i FastAPI (`leverandor/api/main.py`)
- TED-klient: ENG/NOR/NOB-prioritet i multilingual-felt
- Estimert verdi: `Optional[Decimal]` → `Optional[float]` (JSON-serialisering)

## Kjente begrensninger (manuell verifisering gjenstår)

- GO/NO-GO-logikk ved fullt utfylt profil (Fix 3 steg 5 i spec)
- Live TED API-respons med faktiske språkkoder ikke verifisert på testmiljø
