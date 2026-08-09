from datetime import datetime

from leverandor.ingest.ted_client import _map_ted_notice, _parse_ted_date


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


def test_map_ted_notice_minimal():
    notice = {
        "ND-NoticePublicationId": "TED-2026-00001",
        "ND-NoticeTitle": "Norsk IT-anbud",
        "ND-CaOfficialName": "Statens vegvesen",
        "ND-PublicationDate": "20260810",
    }
    k = _map_ted_notice(notice)
    assert k.kilde == "TED"
    assert k.ekstern_id == "TED-2026-00001"
    assert k.tittel == "Norsk IT-anbud"
    assert k.oppdragsgiver == "Statens vegvesen"


def test_map_ted_notice_title_as_list():
    notice = {
        "ND-NoticePublicationId": "TED-2026-00002",
        "ND-NoticeTitle": ["Renholdstjenester"],
        "ND-CaOfficialName": "Oslo kommune",
        "ND-PublicationDate": "20260810",
    }
    k = _map_ted_notice(notice)
    assert k.tittel == "Renholdstjenester"


def test_map_ted_notice_cpv():
    notice = {
        "ND-NoticePublicationId": "TED-2026-00003",
        "ND-NoticeTitle": "Bygg",
        "ND-CaOfficialName": "Bergen",
        "ND-MainCpvCode": "45000000",
        "ND-PublicationDate": "20260810",
    }
    k = _map_ted_notice(notice)
    assert k.cpv_koder == ["45000000"]
