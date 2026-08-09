from datetime import datetime

from leverandor.api.models import Kunngjoring, LeverandorProfil
from leverandor.api.routers.kvalifikasjon import sjekk_kvalifikasjon


def _profil(**kwargs) -> LeverandorProfil:
    defaults = {
        "org_nr": "987654321",
        "navn": "Komplett AS",
        "cpv_koder": ["72000000"],
        "antall_ansatte": 10,
    }
    defaults.update(kwargs)
    return LeverandorProfil(**defaults)


def _kunngjoring() -> Kunngjoring:
    return Kunngjoring(
        kilde="DOFFIN",
        ekstern_id="k-001",
        tittel="IT-anskaffelse",
        oppdragsgiver="Staten",
        publisert=datetime.utcnow(),
        url="https://doffin.no/k-001",
    )


def test_go_full_profil():
    profil = _profil()
    k = _kunngjoring()
    resultat = sjekk_kvalifikasjon(profil, k)
    assert resultat["resultat"] == "GO"
    assert resultat["mangler"] == []


def test_ga_videre_med_forbehold_en_mangel():
    profil = _profil(antall_ansatte=None)
    k = _kunngjoring()
    resultat = sjekk_kvalifikasjon(profil, k)
    assert resultat["resultat"] == "GÅ VIDERE MED FORBEHOLD"
    assert len(resultat["mangler"]) == 1


def test_no_go_to_mangler():
    profil = _profil(antall_ansatte=None, cpv_koder=[])
    k = _kunngjoring()
    resultat = sjekk_kvalifikasjon(profil, k)
    assert resultat["resultat"] == "NO-GO"
    assert len(resultat["mangler"]) >= 2


def test_rule_hits_always_present():
    profil = _profil()
    k = _kunngjoring()
    resultat = sjekk_kvalifikasjon(profil, k)
    assert len(resultat["rule_hits"]) == 3
    rule_ids = [r["rule_id"] for r in resultat["rule_hits"]]
    assert "K1" in rule_ids
    assert "K2" in rule_ids
    assert "K3" in rule_ids
