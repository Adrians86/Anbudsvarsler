import httpx
import logging
from datetime import datetime, timedelta

from leverandor.api.models import Kunngjoring

TED_SEARCH_URL = "https://api.ted.europa.eu/v3/notices/search"


def fetch_recent_ted(days_back: int = 2, cpv_codes: list[str] | None = None) -> list[Kunngjoring]:
    """Hent norske TED-kunngjøringer de siste N dagene."""
    from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y%m%d")
    query_parts = [
        "ND-CountryCode=NOR",
        f"ND-PublicationDate>={from_date}",
    ]
    if cpv_codes:
        cpv_filter = " OR ".join([f"ND-MainCpvCode={c}" for c in cpv_codes[:10]])
        query_parts.append(f"({cpv_filter})")

    payload = {
        "query": " AND ".join(query_parts),
        "fields": [
            "ND-ReferenceNumber",
            "ND-NoticeTitle",
            "ND-CaOfficialName",
            "ND-MainCpvCode",
            "ND-EstimatedTotalValue",
            "ND-SubmissionDeadline",
            "ND-PublicationDate",
            "ND-NoticePublicationId",
        ],
        "page": {"page": 1, "pageSize": 50},
        "language": "NOR",
    }
    results = []
    with httpx.Client(timeout=30) as client:
        while True:
            try:
                resp = client.post(TED_SEARCH_URL, json=payload)
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                logging.warning(f"TED API error {e.response.status_code}: {e.response.text[:500]}")
                return results
            data = resp.json()
            for notice in data.get("notices", []):
                results.append(_map_ted_notice(notice))
            total = data.get("totalNoticeCount", 0)
            fetched = payload["page"]["page"] * payload["page"]["pageSize"]
            if fetched >= total:
                break
            payload["page"]["page"] += 1
    return results


def _map_ted_notice(n: dict) -> Kunngjoring:
    pub_id = n.get("ND-NoticePublicationId", "")
    title = n.get("ND-NoticeTitle", "")
    if isinstance(title, list):
        title = title[0] if title else ""
    return Kunngjoring(
        kilde="TED",
        ekstern_id=pub_id,
        tittel=title,
        oppdragsgiver=n.get("ND-CaOfficialName", ""),
        cpv_koder=[n["ND-MainCpvCode"]] if n.get("ND-MainCpvCode") else [],
        estimert_verdi=n.get("ND-EstimatedTotalValue"),
        tilbudsfrist=_parse_ted_date(n.get("ND-SubmissionDeadline")),
        publisert=_parse_ted_date(n.get("ND-PublicationDate")) or datetime.utcnow(),
        url=f"https://ted.europa.eu/en/notice/-/detail/{pub_id}",
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
