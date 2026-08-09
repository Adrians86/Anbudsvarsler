# Anbudsvarsler

AI-drevet verktøy som hjelper private leverandører å finne, kvalifisere og følge opp
offentlige anbud i Norge.

**Produkteier:** Adrian Śliwa (AS North Advisory)

## Kom i gang

```bash
# Installer avhengigheter
pip install -e ".[dev]"

# Konfigurer miljøvariabler
cp .env.example .env
# Rediger .env og legg til DOFFIN_API_KEY (valgfri)

# Start API
uvicorn leverandor.api.main:app --reload

# Start Streamlit UI (i nytt terminal)
streamlit run app/Hjem.py
```

## Arkitektur

```
anbudsvarsler/
├── core/               Felles regler (FOA YAML)
├── leverandor/         Leverandørmodul
│   ├── api/            FastAPI + SQLModel
│   └── ingest/         Doffin + TED klienter, scheduler
├── app/                Streamlit UI (4 sider)
├── tests/              pytest-tester
└── ci/                 Import-vegg test
```

## Testing

```bash
pytest
```

## Datakilde

- **Doffin**: Norsk kunngjøringsdatabase (doffin.no)
  - API: https://dof-notices-prod-api.developer.azure-api.net/ (krever gratis API-nøkkel)
  - Fallback: CSV-nedlasting fra DFØ
- **TED**: EUs kunngjøringsdatabase for anbud over EØS-terskler
  - API v3: https://api.ted.europa.eu/v3/ (ingen nøkkel nødvendig)

## Status

Se [docs/STATUS.md](docs/STATUS.md) for session-logg.
