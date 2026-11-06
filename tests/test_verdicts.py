"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Die Analysen und Zeilen werden von Hand gebaut, nicht aus Seeds gerechnet."""

import fvs_algorithm as A
import fvs_evaluation as ev
from fvs_scenario import Instance


def _analyse(ffd, opt, nicht_voll=3, frei=100, cap=100, summe=None):
    sizes = (10, 20)
    inst = Instance(sizes, cap, ((0, 1),))
    return ev.Analysis(inst, ((0,), (1,)), ffd, opt, opt, nicht_voll, frei, A.dosa_grenze(opt), ev.Settings())


# --- verdict_ausgang ------------------------------------------------------------------------------------------------------------------------


def test_ausgang_ffd_verfehlt_das_optimum_ist_eine_warnung_mit_allen_zahlen():
    kind, text = ev.verdict_ausgang(_analyse(11, 9))
    assert kind == "warning"
    assert "FFD braucht **11** Container" in text and "das Optimum ist **9**" in text and "L1 = 9" in text and "2 zu viel" in text
    assert "Verhältnis ist 1.222" in text and "erlaubt bei Optimum 9 höchstens 11 Container" in text


def test_ausgang_ein_container_zu_viel():
    kind, text = ev.verdict_ausgang(_analyse(3, 2))
    assert kind == "warning" and "1 zu viel" in text and "Verhältnis ist 1.500" in text and "erlaubt bei Optimum 2 höchstens 3 Container" in text


def test_ausgang_ffd_findet_das_optimum_ist_ein_erfolg():
    kind, text = ev.verdict_ausgang(_analyse(9, 9))
    assert kind == "success" and "**9** Container und findet damit das Optimum" in text and "L1 = 9" in text


# --- verdict_warum ---------------------------------------------------------------------------------------------------------------------------


def test_warum_perfekte_packung_nennt_nicht_volle_container_und_freien_platz():
    a = _analyse(11, 9, nicht_voll=11, frei=2000, cap=1000)
    a = ev.Analysis(Instance((500, 500), 1000, ((0, 1),)), a.ffd_bins, 11, 9, 9, 11, 2000, 11, a.settings)
    # Summe 1000, Optimum 9 -> nicht gleich opt * cap: Zweig ohne „bis zum Rand“
    kind, text = ev.verdict_warum(a)
    assert kind == "info" and "Die optimale Packung hat 9 Container" in text and "in 11 von 11 Containern zusammen 2000 Platz frei" in text


def test_warum_perfekte_packung_bis_zum_rand():
    sizes = (50, 50, 50, 50)
    inst = Instance(sizes, 100, ((0, 1), (2, 3)))
    a = ev.Analysis(inst, ((0,), (1,), (2,), (3,)), 4, 2, 2, 4, 200, 3, ev.Settings())
    kind, text = ev.verdict_warum(a)
    assert kind == "info"
    assert "füllt jeden der 2 Container bis zum Rand (100)" in text and "in 4 von 4 Containern zusammen 200 Platz frei" in text and "das sind 2.00 Container" in text


# --- verdict_triplets ------------------------------------------------------------------------------------------------------------------------


def _zeile(ffd=2.0, ff=1.5, auf=3.0, zuf=1.0, fuell=0.5, ffd_opt=0, fuell_opt=60, k=10):
    return {"k": k, "pakete": 3 * k, "instanzen": 200, "zufallsordnungen": 100, "mittel": {"FFD": ffd, "FF": ff, "AUF": auf, "ZUF": zuf, "FUELL": fuell},
            "ffd_optimal": ffd_opt, "fuell_optimal": fuell_opt, "max_luecke": 3}


def test_triplets_sortieren_schadet_ist_eine_warnung_und_nennt_alle_zahlen():
    kind, text = ev.verdict_triplets(_zeile())
    assert kind == "warning"
    assert "Bei 10 Triplets (30 Paketen)" in text and "über 200 Instanzen 2.00 Container über dem Optimum" in text and "in 0 von 200 Instanzen optimal" in text
    assert "Lieferreihenfolge liegt bei 1.50" in text and "aufsteigend sortiert bei 3.00" in text and "beste von 100 Zufallsordnungen bei 1.00" in text
    assert "die Füllregel bei 0.50 (optimal in 60 Instanzen)" in text and "Sortieren schadet hier" in text


def test_triplets_gleich_gut_wird_auf_angezeigte_stellen_verglichen():
    kind, text = ev.verdict_triplets(_zeile(ffd=1.000, ff=1.004))     # 1.00 gegen 1.00
    assert kind == "info" and "gleich gut" in text
    kind, text = ev.verdict_triplets(_zeile(ffd=1.000, ff=1.006))     # 1.00 gegen 1.01
    assert kind == "info" and "Sortieren hilft hier" in text


def test_triplets_ohne_fuellregel_nennt_sie_nicht():
    kind, text = ev.verdict_triplets(_zeile(fuell=None, fuell_opt=None, k=100))
    assert "Füllregel" not in text and text.endswith("Sortieren schadet hier gegenüber der Lieferreihenfolge.") and "Bei 100 Triplets (300 Paketen)" in text


# --- verdict_stoerung ------------------------------------------------------------------------------------------------------------------------


def test_stoerung_ohne_optimum_ist_eine_warnung_mit_den_drei_zahlen():
    kind, text = ev.verdict_stoerung(3, {10: 1189, 11: 811}, 2000)
    assert kind == "warning"
    assert "Von 2000 gestörten Varianten (Stärke 3)" in text and "in 811 Fällen 11 Container, in 1189 Fällen 10 und in 0 Fällen 9" in text and "in keiner Variante" in text


def test_stoerung_mit_genau_einem_treffer_ist_info_und_nennt_ihn():
    kind, text = ev.verdict_stoerung(2, {9: 1, 10: 9, 11: 90}, 100)
    assert kind == "info" and "in 1 Varianten" in text and "keiner" not in text


def test_stoerung_mit_optimum_ist_info():
    kind, text = ev.verdict_stoerung(1, {9: 5, 10: 10, 11: 85}, 100)
    assert kind == "info" and "in 85 Fällen 11 Container, in 10 Fällen 10 und in 5 Fällen 9" in text and "Das Optimum erreicht FFD in 5 Varianten." in text


# --- verdict_klein ---------------------------------------------------------------------------------------------------------------------------


def test_klein_nennt_gesamtzahl_luecke_und_groesstes_verhaeltnis():
    zeilen = [{"n": 6, "instanzen": 100, "mit_luecke": 3, "max_luecke": 1, "verhaeltnis": [3, 2]},
              {"n": 12, "instanzen": 100, "mit_luecke": 5, "max_luecke": 2, "verhaeltnis": [4, 3]}]
    kind, text = ev.verdict_klein(zeilen)
    assert kind == "info"
    assert "In 200 Zufallsinstanzen mit höchstens 12 Paketen" in text and "höchstens 2 Container über dem Optimum, in 8 Instanzen überhaupt" in text
    assert "größte gemessene Verhältnis ist 3 zu 2 (1.500)" in text and "bei Optimum 2 bis zu 3 Container" in text
