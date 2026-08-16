import httpx
import logging
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from leverandor.api.models import Kunngjoring

TED_SEARCH_URL = "https://api.ted.europa.eu/v3/notices/search"


def fetch_recent_ted(days_back: int = 2, cpv_codes: list[str] | None = None) -> list[Kunngjoring]:
    """Hent norske TED-kunngjøringer de siste N dagene."""
    from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y%m%d")

    query = f"buyer-country=NOR AND PD>={from_date}"
    if cpv_codes:
        cpv_filter = " OR ".join([f"classification-cpv={c}" for c in cpv_codes[:10]])
        query += f" AND ({cpv_filter})"

    payload = {
        "query": query,
        "fields": [
            "publication-number",
            "notice-title",
            "buyer-name",
            "classification-cpv",
            "total-value",
            "deadline",
            "publication-date",
        ],
        "limit": 50,
        "scope": "ACTIVE",
        "paginationMode": "ITERATION",
    }

    with httpx.Client(timeout=30) as client:
        try:
            resp = client.post(TED_SEARCH_URL, json=payload)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            logging.warning(f"TED API error {e.response.status_code}: {e.response.text[:500]}")
            return []
        except httpx.RequestError as e:
            logging.warning(f"TED API connection error: {e}")
            return []

        data = resp.json()
        notices = data.get("notices", data.get("results", []))
        return [_map_ted_notice(n) for n in notices]


def _get_multilingual(val, langs: tuple[str, ...] = ("ENG", "NOR", "NOB", "MUL")) -> str:
    """Hent tekst fra flerspråklig TED-felt.

    Prøver languages i prioritert rekkefølge (case-insensitive); faller tilbake
    til første tilgjengelige språk hvis ingen av preferansene finnes.
    """
    if isinstance(val, dict):
        # TED v3 may return lowercase or uppercase language codes
        val_upper = {k.upper(): v for k, v in val.items()}
        for lang in langs:
            v = val_upper.get(lang.upper())
            if v:
                return v[0] if isinstance(v, list) else str(v)
        first = next(iter(val.values()), "")
        return first[0] if isinstance(first, list) else str(first)
    if isinstance(val, list):
        return val[0] if val else ""
    return str(val) if val else ""


def _map_ted_notice(n: dict) -> Kunngjoring:
    pub_nr = n.get("publication-number", "")

    total_value = n.get("total-value", {})
    estimert = None
    if isinstance(total_value, dict) and total_value.get("amount") is not None:
        try:
            estimert = Decimal(str(total_value["amount"]))
        except (InvalidOperation, TypeError):
            pass

    cpv_raw = n.get("classification-cpv", [])
    cpv_koder = [str(c) for c in cpv_raw] if isinstance(cpv_raw, list) else []

    return Kunngjoring(
        kilde="TED",
        ekstern_id=pub_nr,
        tittel=_get_multilingual(n.get("notice-title", "")),
        oppdragsgiver=_get_multilingual(n.get("buyer-name", "")),
        cpv_koder=cpv_koder,
        estimert_verdi=estimert,
        tilbudsfrist=_parse_ted_date(n.get("deadline")),
        publisert=_parse_ted_date(n.get("publication-date")) or datetime.utcnow(),
        url=f"https://ted.europa.eu/en/notice/-/detail/{pub_nr}",
        raa_data=n,
    )


def _parse_ted_date(val) -> datetime | None:
    if not val:
        return None
    s = val[0] if isinstance(val, list) else str(val)
    formats = [("%Y%m%d", 8), ("%Y-%m-%dT%H:%M:%S", 19), ("%Y-%m-%d", 10)]
    for fmt, length in formats:
        try:
            return datetime.strptime(s[:length], fmt)
        except ValueError:
            continue
    return None
