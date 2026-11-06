"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen; jedes Preset liefert die erwarteten Kennzahlen."""

import pytest

import fvs_constants as C
import fvs_evaluation as ev
import fvs_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for preset in C.PRESETS.values():
        for key, state_key in P.PRESET_KEYS.items():
            lo, hi = P.bounds(state_key)
            assert lo <= preset[key] <= hi, (key, preset)


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**next(iter(C.PRESETS.values()))) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS) and set(P.PRESET_KEYS_INV) == set(P.SETTING_SPECS)


def test_beispielauswahl_deckt_alle_beispiele_ab():
    assert set(C.BEISPIEL_NAMEN) == {0, C.ZUFALL_TRIPLETS, C.JOHNSON, C.GESTOERT} and P.bounds("beispiel_select") == (0, 3)


ERWARTET = {          # Preset -> (FFD, Optimum)
    "Zwei Triplets von Hand": (3, 2),
    "Zehn zufällige Triplets": (None, 10),
    "Die 11/9-Instanz": (11, 9),
    "Gestörte 11/9-Instanz": (None, 9),
}


@pytest.mark.parametrize("name", list(ERWARTET))
def test_jedes_preset_liefert_das_erwartete_optimum_und_eine_zulaessige_packung(name):
    a = ev.analyse(ev.Settings(**C.PRESETS[name]))
    f, opt = ERWARTET[name]
    assert a.opt == opt == a.schranke_l1
    if f is not None:
        assert a.ffd == f
    assert a.opt <= a.ffd <= a.grenze


def test_jedes_preset_ist_ein_verfehlen_und_die_art_ist_eine_warnung():
    for name in ERWARTET:
        a = ev.analyse(ev.Settings(**C.PRESETS[name]))
        assert a.ffd > a.opt and ev.verdict_ausgang(a)[0] == "warning", name
