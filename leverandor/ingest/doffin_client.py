import httpx
import csv
import io
import os
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from leverandor.api.models import Kunngjoring

DOFFIN_API_KEY = os.getenv("DOFFIN_API_KEY", "")
DOFFIN_PUBLIC_URL = "https://api.doffin.no/public/v2/search"


def fetch_recent_doffin(days_back: int = 2) -> list[Kunngjoring]:
    """Hent kunngjøringer fra Doffin de siste N dagene."""
    if DOFFIN_API_KEY:
        return _fetch_via_api(days_back)
    else:
        return _fetch_via_csv()


def _fetch_via_api(days_back: int) -> list[Kunngjoring]:
    from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    params = {
        "type": "COMPETITION",
        "status": "ACTIVE",
        "issueDateFrom": from_date,
        "numHitsPerPage": "100",
        "page": "1",
    }
    headers = {"Ocp-Apim-Subscription-Key": DOFFIN_API_KEY}
    results = []
    with httpx.Client(timeout=30) as client:
        while True:
            resp = client.get(DOFFIN_PUBLIC_URL, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("hits", []):
                results.append(_map_api_item(item))
            if not data.get("hasNextPage"):
                break
            params["page"] = str(int(params["page"]) + 1)
    return results


def _map_api_item(item: dict) -> Kunngjoring:
    buyers = item.get("buyer", [])
    oppdragsgiver = buyers[0].get("name", "") if buyers else ""
    estimert_verdi_raw = item.get("estimatedValue", {})
    estimert_verdi = (
        _parse_decimal(str(estimert_verdi_raw.get("amount")))
        if estimert_verdi_raw
        else None
    )
    ekstern_id = str(item.get("id", ""))
    return Kunngjoring(
        kilde="DOFFIN",
        ekstern_id=ekstern_id,
        tittel=item.get("heading", ""),
        oppdragsgiver=oppdragsgiver,
        cpv_koder=item.get("cpvCodes", []),
        estimert_verdi=estimert_verdi,
        tilbudsfrist=_parse_dt(item.get("deadlineDate")),
        publisert=_parse_dt(item.get("publicationDate")) or datetime.utcnow(),
        url=f"https://doffin.no/Notice/Details/{ekstern_id}",
        raa_data=item,
    )


def _fetch_via_csv() -> list[Kunngjoring]:
    """Fallback: last ned årets CSV fra DFØ og returner de siste 2 dagene."""
    import urllib.request

    year = datetime.utcnow().year
    url = (
        f"https://dfo.no/nokkeltall-og-statistikk/innkjop-i-offentlig-sektor/"
        f"kunngjoringer-av-konkurranse-pa-doffin/nedlasting/{year}"
    )
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            content = resp.read().decode("utf-8-sig")
    except Exception:
        return []

    cutoff = datetime.utcnow() - timedelta(days=2)
    results = []
    for row in csv.DictReader(io.StringIO(content), delimiter=";"):
        pub = _parse_dt(row.get("Kunngjøringsdato", ""))
        if pub and pub >= cutoff:
            results.append(
                Kunngjoring(
                    kilde="DOFFIN",
                    ekstern_id=row.get("Referansenummer", ""),
                    tittel=row.get("Tittel", ""),
                    oppdragsgiver=row.get("Oppdragsgiver", ""),
                    cpv_koder=[row["CPV"]] if row.get("CPV") else [],
                    estimert_verdi=_parse_decimal(row.get("Estimert verdi", "")),
                    tilbudsfrist=_parse_dt(row.get("Tilbudsfrist", "")),
                    publisert=pub,
                    url=f"https://doffin.no/Notice/Details/{row.get('Referansenummer', '')}",
                    raa_data=dict(row),
                )
            )
    return results


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    # Map format → expected rendered length (not len(fmt) which is the format string length)
    formats = [
        ("%Y-%m-%dT%H:%M:%S", 19),
        ("%Y-%m-%d", 10),
        ("%d.%m.%Y", 10),
    ]
    for fmt, length in formats:
        try:
            return datetime.strptime(s[:length], fmt)
        except ValueError:
            continue
    return None


def _parse_decimal(s: str) -> Decimal | None:
    try:
        return Decimal(s.replace(" ", "").replace(",", "."))
    except (InvalidOperation, AttributeError):
        return None
