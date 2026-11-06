"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, stellt jede Auswahl
auf jeden ihrer Werte, die Regler und das Zahlenfeld an ihre Grenzen und prüft, dass kein Python-Fehler auftritt (insbesondere `StreamlitDuplicateElementId`
bei mehreren Diagrammen ohne key= und `StreamlitAPIException` bei Auswahlen mit ungültigem Wert)."""

import os

from streamlit.testing.v1 import AppTest

import fvs_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_selectbox_value_does_not_raise():
    keys = [s.key for s in _fresh_app().selectbox]
    assert {"beispiel_select", "exp_k", "exp_delta"} <= set(keys)
    werte = {"beispiel_select": list(C.BEISPIEL_NAMEN), "exp_k": list(range(len(C.N_TRIPLETS))), "exp_delta": list(C.DELTAS)}
    for key in keys:
        for wert in werte[key]:
            at = _fresh_app()
            at.selectbox(key=key).set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (key, wert, [str(e) for e in at.exception])


def test_sliders_and_seed_at_their_limits_do_not_raise():
    for beispiel, key, grenzen in ((C.ZUFALL_TRIPLETS, "k_slider", (C.K_MIN, C.K_MAX)), (C.GESTOERT, "delta_slider", (C.DELTA_MIN, C.DELTA_MAX))):
        for wert in grenzen:
            at = _fresh_app()
            at.selectbox(key="beispiel_select").set_value(beispiel).run(timeout=TIMEOUT)
            at.slider(key=key).set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (key, wert, [str(e) for e in at.exception])
    for beispiel in (C.ZUFALL_TRIPLETS, C.GESTOERT):
        for wert in (0, C.SEED_MAX):
            at = _fresh_app()
            at.selectbox(key="beispiel_select").set_value(beispiel).run(timeout=TIMEOUT)
            at.number_input(key="seed_input").set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (beispiel, wert, [str(e) for e in at.exception])


def test_wuerfeln_wechselt_von_festen_beispielen_zu_zufaelligen_triplets():
    for start, erwartet in ((0, C.ZUFALL_TRIPLETS), (C.JOHNSON, C.ZUFALL_TRIPLETS), (C.GESTOERT, C.GESTOERT), (C.ZUFALL_TRIPLETS, C.ZUFALL_TRIPLETS)):
        at = _fresh_app()
        at.selectbox(key="beispiel_select").set_value(start).run(timeout=TIMEOUT)
        at.button[[b.label for b in at.button].index("🎲 Neue Startzahl würfeln")].click().run(timeout=TIMEOUT)
        assert at.selectbox(key="beispiel_select").value == erwartet, start


def test_standardansicht_zeigt_das_erwartete_verdikt():
    warnungen = [w.value for w in _fresh_app().warning]
    assert any("FFD braucht **3** Container" in w and "das Optimum ist **2**" in w for w in warnungen)      # zwei Triplets von Hand


def test_expander_stehen_unter_ihren_namen():
    labels = [e.label for e in _fresh_app().expander]
    assert "📐 Mathematische Formulierung" in labels and "⚠️ Annahmen, Grenzen und bekannte Probleme" in labels
