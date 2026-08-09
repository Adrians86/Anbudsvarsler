from datetime import datetime, timedelta
from decimal import Decimal

from leverandor.api.models import Kunngjoring, LeverandorProfil
from leverandor.api.routers.varsling import score_match


def _profil(**kwargs) -> LeverandorProfil:
    defaults = {"org_nr": "123456789", "navn": "Test AS", "cpv_koder": []}
    defaults.update(kwargs)
    return LeverandorProfil(**defaults)


def _kunngjoring(**kwargs) -> Kunngjoring:
    defaults = {
        "kilde": "DOFFIN",
        "ekstern_id": "test-001",
        "tittel": "Test kunngjøring",
        "oppdragsgiver": "Test kommune",
        "cpv_koder": [],
        "publisert": datetime.utcnow(),
        "url": "https://doffin.no/test",
    }
    defaults.update(kwargs)
    return Kunngjoring(**defaults)


def test_score_cpv_match():
    profil = _profil(cpv_koder=["72000000"])
    k = _kunngjoring(cpv_koder=["72000000"])
    assert score_match(k, profil) >= 0.4


def test_score_no_cpv_match():
    profil = _profil(cpv_koder=["72000000"])
    no_cpv = _kunngjoring(cpv_koder=["45000000"])
    with_cpv = _kunngjoring(ekstern_id="test-002", cpv_koder=["72000000"])
    # No CPV overlap still gets region+value+source (0.5); CPV match adds up to 0.4 on top
    assert score_match(no_cpv, profil) < score_match(with_cpv, profil)


def test_score_full_match():
    """CPV match + ingen region filter + verdi i range + frist ok."""
    profil = _profil(
        cpv_koder=["72000000"],
        nuts_regioner=[],
        min_verdi=None,
        max_verdi=None,
    )
    k = _kunngjoring(
        cpv_koder=["72000000"],
        tilbudsfrist=datetime.utcnow() + timedelta(days=30),
    )
    score = score_match(k, profil)
    assert score == 1.0


def test_score_no_cpv_no_region():
    profil = _profil(cpv_koder=[], nuts_regioner=[])
    k = _kunngjoring(cpv_koder=[])
    score = score_match(k, profil)
    assert score >= 0.3


def test_score_region_mismatch():
    profil = _profil(cpv_koder=[], nuts_regioner=["NO020"])
    k = _kunngjoring(cpv_koder=[], nuts_region="NO030")
    score = score_match(k, profil)
    assert score < 0.5


def test_score_value_out_of_range():
    profil = _profil(
        cpv_koder=["72000000"],
        min_verdi=Decimal("100000"),
        max_verdi=Decimal("500000"),
    )
    k = _kunngjoring(cpv_koder=["72000000"], estimert_verdi=Decimal("999999999"))
    score = score_match(k, profil)
    assert score < 0.8


def test_score_is_rounded():
    profil = _profil(cpv_koder=["72000000"])
    k = _kunngjoring(cpv_koder=["72000000"])
    score = score_match(k, profil)
    assert score == round(score, 3)
