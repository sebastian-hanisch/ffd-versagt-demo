"""Jede Zahl der README und der App-Texte, nachgerechnet (DEMO-PLAYBOOK §4 und §11a).

* Die vorberechneten Zeilen (fvs_precomputed.json) werden je Zeile frisch gerechnet und exakt verglichen (ganze Zahlen).
* Die Befunde der README werden aus denselben Auswertungsfunktionen wie in der App berechnet, über die GANZE Tabelle gezählt und als Text in der README gesucht.
* Der Text des Expanders „Annahmen, Grenzen und bekannte Probleme“ steht wörtlich in der README.
Dezimalzahlen stehen in der README mit Komma, in der App mit Punkt; `de` übersetzt."""

from pathlib import Path

import pytest

import fvs_algorithm as A
import fvs_constants as C
import fvs_evaluation as ev

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def zeilen():
    return {k: ev.triplet_zeile(k) for k in C.N_TRIPLETS}


# --- vorberechnete Tabellen ------------------------------------------------------------------------------------------------------------------


def test_vorberechnete_datei_hat_alle_zeilen_und_parameter():
    d = ev.vorberechnet()
    assert d["instanzen"] == C.INSTANZEN == 200 and d["zufallsordnungen"] == C.ZUFALLSORDNUNGEN == 100 and d["fuell_limit"] == C.FUELL_LIMIT == 40
    assert d["klein_instanzen"] == C.KLEIN_INSTANZEN == 2000
    assert set(d["triplets"]) == {str(k) for k in C.N_TRIPLETS} and set(d["klein"]) == {str(n) for n in C.KLEIN_N}


@pytest.mark.parametrize("k", C.N_TRIPLETS)
def test_experiment_a_zeile_stimmt_mit_frischer_rechnung(k):
    assert ev.triplet_zelle(k) == ev.vorberechnet()["triplets"][str(k)]


@pytest.mark.parametrize("n", C.KLEIN_N)
def test_experiment_c_groesse_stimmt_mit_frischer_rechnung(n):
    assert ev.klein_zelle(n) == ev.vorberechnet()["klein"][str(n)]


# --- Experiment A in der README --------------------------------------------------------------------------------------------------------------


def test_readme_tabelle_a_gibt_jede_zeile_wieder():
    for k, z in zeilen().items():
        m = z["mittel"]
        fuell = "nicht gerechnet" if m["FUELL"] is None else de(m["FUELL"])
        zeile = f"| {k} | {de(m['FFD'])} | {de(m['FF'])} | {de(m['AUF'])} | {de(m['ZUF'])} | {fuell} | {z['ffd_optimal']} | {z['max_luecke']} |"
        assert zeile in README, zeile


def test_ffd_ist_in_keiner_der_1000_instanzen_optimal():
    z = zeilen()
    assert sum(x["ffd_optimal"] for x in z.values()) == 0 and sum(x["instanzen"] for x in z.values()) == 1000
    assert "**FFD ist in 0 von 1000 Instanzen optimal**" in README


def test_sortieren_schadet_ab_zehn_triplets_und_ist_bei_fuenf_gleich():
    z = zeilen()
    gleich = {k: round(x["mittel"]["FFD"], 2) == round(x["mittel"]["FF"], 2) for k, x in z.items()}
    schadet = {k: round(x["mittel"]["FFD"], 2) > round(x["mittel"]["FF"], 2) for k, x in z.items()}
    assert gleich == {5: True, 10: False, 20: False, 40: False, 100: False} and schadet == {5: False, 10: True, 20: True, 40: True, 100: True}
    assert "**Sortieren schadet ab 10 Triplets:**" in README and "(bei 5 sind beide gleich, 1,00)" in README
    assert de(z[5]["mittel"]["FFD"]) == de(z[5]["mittel"]["FF"]) == "1,00"


def test_aufsteigend_ist_in_allen_fuenf_zeilen_am_schlechtesten():
    for k, z in zeilen().items():
        m = z["mittel"]
        assert m["AUF"] > max(m["FFD"], m["FF"], m["ZUF"]) and (m["FUELL"] is None or m["AUF"] > m["FUELL"]), k
    assert "aufsteigend sortiert ist in allen fünf Zeilen am schlechtesten" in README


def test_bester_von_hundert_zufallsordnungen_liegt_in_allen_zeilen_unter_ffd():
    z = zeilen()
    assert all(x["mittel"]["ZUF"] < x["mittel"]["FFD"] for x in z.values())
    assert de(z[100]["mittel"]["ZUF"]) == "8,32" and "bei 100 Triplets aber noch 8,32 Container über dem Optimum" in README
    assert "in allen fünf Zeilen unter FFD" in README


def test_fuellregel_zahlen():
    z = zeilen()
    assert [z[k]["fuell_optimal"] for k in (5, 10, 20, 40)] == [180, 76, 0, 0] and z[100]["fuell_optimal"] is None
    assert [de(z[k]["mittel"]["FUELL"]) for k in (20, 40)] == ["1,00", "1,07"]
    assert "in 180 von 200 Instanzen bei 5 Triplets, in 76 bei 10 und in 0 bei 20 und 40 (mittlere Lücke 1,00 und 1,07)" in README


def test_groesstes_verhaeltnis_ist_in_allen_zeilen_kleiner_als_elf_neuntel():
    verh = {k: (k + z["max_luecke"]) / k for k, z in zeilen().items()}
    assert [round(v, 3) for v in verh.values()] == [1.2, 1.2, 1.2, 1.15, 1.15] and all(v < 11 / 9 for v in verh.values())
    assert "**Das größte Verhältnis FFD / Optimum** ist 1,200 bei 5, 10 und 20 Triplets und 1,150 bei 40 und 100" in README and "kleiner als 11/9 (1,222)" in README


# --- Experiment B ----------------------------------------------------------------------------------------------------------------------------


def test_experiment_b_stimmt_mit_der_readme_und_ffd_erreicht_nie_das_optimum():
    gesamt9 = 0
    for d in C.DELTAS:
        v = ev.stoerung_verteilung(d)
        assert sum(v.values()) == C.STOERUNGEN and set(v) <= {9, 10, 11}
        assert f"| {d} | {v.get(11, 0)} | {v.get(10, 0)} | {v.get(9, 0)} |" in README
        gesamt9 += v.get(9, 0)
    assert gesamt9 == 0 and len(C.DELTAS) * C.STOERUNGEN == 10_000 and "**0 von 10 000**" in README
    assert ev.stoerung_verteilung(1)[11] == 1988 and ev.stoerung_verteilung(10)[11] == 26
    assert "bei Stärke 1 in 1988 von 2000 Fällen, bei Stärke 10 nur noch in 26" in README


# --- Experiment C ----------------------------------------------------------------------------------------------------------------------------


def test_experiment_c_tabelle_und_zaehlungen():
    for z in ev.klein_tabelle():
        assert f"| {z['opt']} | {z['erlaubt']} | {z['gemessen']} |" in README
    assert [(z["opt"], z["erlaubt"], z["gemessen"]) for z in ev.klein_tabelle()] == [(2, 3, 3), (3, 4, 4), (4, 5, 5), (5, 6, 6), (6, 8, 6)]
    zl = [ev.klein_zeile(n) for n in C.KLEIN_N]
    assert [z["mit_luecke"] for z in zl] == [31, 32, 51, 63] and sum(z["mit_luecke"] for z in zl) == 177 and sum(z["instanzen"] for z in zl) == 8000
    assert all(z["max_luecke"] == 1 for z in zl) and [z["verhaeltnis"] for z in zl] == [[3, 2], [3, 2], [4, 3], [4, 3]]
    assert "In **177 von 8000** Instanzen verfehlt FFD das Optimum (31 / 32 / 51 / 63 bei 6 / 8 / 10 / 12 Paketen), in keiner um mehr als einen Container." in README
    assert "**3 zu 2 (1,500)** bei 6 und 8 Paketen und 4 zu 3 bei 10 und 12" in README
    assert "bei Optimum 2, 3, 4 und 5 erreicht, bei 6 nicht (gemessen 6, erlaubt 8)" in README


# --- Handbeispiele und Texte -----------------------------------------------------------------------------------------------------------------


def test_readme_handbeispiele():
    a = ev.analyse(ev.Settings(0))
    assert (a.ffd, a.opt, a.frei) == (3, 2, 100) and "FFD packt [36, 36], [34, 33, 31], [30]: **3 Container** (100 Platz frei)" in README
    assert A.fuellregel(a.inst.sizes, 100) == [[0, 1, 2], [3, 4, 5]]
    assert len(A.first_fit(a.inst.sizes, A.ordnung_liefer(a.inst.sizes), 100)) == 2 and len(A.first_fit(a.inst.sizes, A.ordnung_gross_zuerst(a.inst.sizes), 100)) == 3
    j = ev.analyse(ev.Settings(C.JOHNSON))
    assert (j.ffd, j.opt) == (11, 9) and "FFD braucht 11 Container ((502, 254) sechsmal, (252, 252, 252) zweimal, (246 × 4) dreimal), das Optimum ist 9" in README


def test_annahmen_text_der_app_steht_woertlich_in_der_readme():
    assert C.ASSUMPTIONS_MARKDOWN in README


def test_zahlen_im_annahmen_text_sind_die_der_konstanten():
    t = C.ASSUMPTIONS_MARKDOWN
    assert f"{C.INSTANZEN} Instanzen" in t and f"{C.STOERUNGEN} festen Störungen" in t and f"bis {C.FUELL_LIMIT} Triplets" in t and "von 5 bis 100 Triplets" in t
    assert C.N_TRIPLETS[0] == 5 and C.N_TRIPLETS[-1] == 100
