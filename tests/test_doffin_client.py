from datetime import datetime

from leverandor.ingest.doffin_client import _map_api_item, _parse_decimal, _parse_dt


def test_parse_dt_iso_date():
    result = _parse_dt("2026-08-15")
    assert result is not None
    assert result == datetime(2026, 8, 15)


def test_parse_dt_iso_datetime():
    result = _parse_dt("2026-08-15T10:30:00")
    assert result is not None
    assert result.year == 2026


def test_parse_dt_norwegian_format():
    result = _parse_dt("15.08.2026")
    assert result is not None
    assert result == datetime(2026, 8, 15)


def test_parse_dt_none():
    assert _parse_dt(None) is None


def test_parse_dt_empty_string():
    assert _parse_dt("") is None


def test_map_api_item_minimal():
    item = {
        "id": "2026-123",
        "heading": "Test kunngjøring",
        "buyer": [{"name": "Oslo kommune"}],
    }
    k = _map_api_item(item)
    assert k.ekstern_id == "2026-123"
    assert k.kilde == "DOFFIN"
    assert k.tittel == "Test kunngjøring"
    assert k.oppdragsgiver == "Oslo kommune"
    assert k.cpv_koder == []


def test_map_api_item_with_cpv():
    item = {
        "id": "2026-456",
        "heading": "IT-tjenester",
        "buyer": [{"name": "Bergen kommune"}],
        "cpvCodes": ["72000000"],
    }
    k = _map_api_item(item)
    assert k.cpv_koder == ["72000000"]


def test_parse_decimal_valid():
    from decimal import Decimal

    assert _parse_decimal("1000000") == Decimal("1000000")
    assert _parse_decimal("1 000 000") == Decimal("1000000")
    assert _parse_decimal("1000,50") == Decimal("1000.50")


def test_parse_decimal_invalid():
    assert _parse_decimal("ikke et tall") is None
    assert _parse_decimal("") is None
