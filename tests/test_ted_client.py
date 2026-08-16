from datetime import datetime

from leverandor.ingest.ted_client import _get_multilingual, _map_ted_notice, _parse_ted_date


def test_parse_ted_date_yyyymmdd():
    result = _parse_ted_date("20260815")
    assert result is not None
    assert result == datetime(2026, 8, 15)


def test_parse_ted_date_iso():
    result = _parse_ted_date("2026-08-15")
    assert result is not None


def test_parse_ted_date_list():
    result = _parse_ted_date(["20260901"])
    assert result is not None
    assert result.year == 2026


def test_parse_ted_date_none():
    assert _parse_ted_date(None) is None


def test_get_multilingual_dict_eng_priority():
    # ENG has highest priority — returned even when NOR is present
    assert _get_multilingual({"NOR": ["Norsk tittel"], "ENG": ["English title"]}) == "English title"


def test_get_multilingual_dict_nor_fallback():
    # NOR used when ENG is absent
    assert _get_multilingual({"NOR": ["Norsk tittel"], "FRA": ["Titre français"]}) == "Norsk tittel"


def test_get_multilingual_dict_nob_fallback():
    # NOB used when ENG and NOR are absent
    assert _get_multilingual({"NOB": ["Bokmål tittel"], "FRA": ["Titre"]}) == "Bokmål tittel"


def test_get_multilingual_dict_fallback():
    assert _get_multilingual({"ENG": ["English title"]}) == "English title"


def test_get_multilingual_list():
    assert _get_multilingual(["Tittel"]) == "Tittel"


def test_get_multilingual_string():
    assert _get_multilingual("Direkte tittel") == "Direkte tittel"


def test_get_multilingual_empty():
    assert _get_multilingual({}) == ""


def test_get_multilingual_lowercase_keys():
    # TED v3 may return lowercase ISO codes — must still prioritize ENG
    assert _get_multilingual({"nor": ["Norsk tittel"], "eng": ["English title"]}) == "English title"


def test_get_multilingual_mul_fallback():
    # MUL (multilingual) used when ENG/NOR/NOB absent
    assert _get_multilingual({"MUL": ["Multilingual tittel"]}) == "Multilingual tittel"


def test_map_ted_notice_minimal():
    notice = {
        "publication-number": "TED-2026-00001",
        "notice-title": {"NOR": ["Norsk IT-anbud"], "ENG": ["Norwegian IT tender"]},
        "buyer-name": {"NOR": ["Statens vegvesen"]},
        "publication-date": "20260810",
    }
    k = _map_ted_notice(notice)
    assert k.kilde == "TED"
    assert k.ekstern_id == "TED-2026-00001"
    assert k.tittel == "Norwegian IT tender"  # ENG prioritized over NOR
    assert k.oppdragsgiver == "Statens vegvesen"
    assert k.cpv_koder == []


def test_map_ted_notice_title_as_string():
    notice = {
        "publication-number": "TED-2026-00002",
        "notice-title": "Renholdstjenester",
        "buyer-name": "Oslo kommune",
        "publication-date": "20260810",
    }
    k = _map_ted_notice(notice)
    assert k.tittel == "Renholdstjenester"
    assert k.oppdragsgiver == "Oslo kommune"


def test_map_ted_notice_cpv():
    notice = {
        "publication-number": "TED-2026-00003",
        "notice-title": "Bygg",
        "buyer-name": "Bergen",
        "classification-cpv": ["45000000", "45100000"],
        "publication-date": "20260810",
    }
    k = _map_ted_notice(notice)
    assert k.cpv_koder == ["45000000", "45100000"]


def test_map_ted_notice_total_value():
    from decimal import Decimal

    notice = {
        "publication-number": "TED-2026-00004",
        "notice-title": "Test",
        "buyer-name": "Staten",
        "total-value": {"amount": 1500000, "currency": "NOK"},
        "publication-date": "20260810",
    }
    k = _map_ted_notice(notice)
    assert k.estimert_verdi == Decimal("1500000")
