"""Kern an den Mini-Instanzen von Hand (Rechnung in tests/conftest.py), an der 11/9-Instanz und an der Garantie."""

from collections import Counter

import pytest

import fvs_algorithm as A
import fvs_constants as C
import fvs_evaluation as ev
import fvs_scenario as S


def test_zwei_triplets_ffd_von_hand(zwei_triplets):
    inst = zwei_triplets
    assert inst.sizes == (36, 34, 30, 36, 33, 31) and inst.cap == 100 and inst.opt_bins == ((0, 1, 2), (3, 4, 5))
    assert A.ffd(inst.sizes, 100) == [[0, 3], [1, 4, 5], [2]]
    assert A.freier_platz(inst.sizes, A.ffd(inst.sizes, 100), 100) == (3, 100)
    assert A.l1(inst.sizes, 100) == 2 == inst.opt == A.optimum(inst.sizes, 100)


def test_zwei_triplets_andere_verfahren_von_hand(zwei_triplets):
    sz = zwei_triplets.sizes
    # Lieferreihenfolge Triplet für Triplet (36, 34, 30, 36, 33, 31): First Fit setzt jedes Triplet in einen Container und findet das Optimum; die Reihenfolge entscheidet.
    assert A.first_fit(sz, A.ordnung_liefer(sz), 100) == [[0, 1, 2], [3, 4, 5]]
    # In der Reihenfolge 36, 36, 34, 33, 31, 30 (Nummern 0, 3, 1, 4, 5, 2; das ist die von FFD gewählte) braucht First Fit dagegen 3 Container.
    assert len(A.first_fit(sz, A.ordnung_gross_zuerst(sz), 100)) == 3
    assert A.fuellregel(sz, 100) == [[0, 1, 2], [3, 4, 5]]      # die Füllregel findet das Optimum


def test_first_fit_ordnungen_von_hand(mini_ordnung):
    sizes, cap = mini_ordnung
    assert A.first_fit(sizes, A.ordnung_liefer(sizes), cap) == [[0, 3], [1, 2]]
    assert A.ordnung_aufsteigend(sizes) == [3, 1, 2, 0]
    assert A.first_fit(sizes, A.ordnung_aufsteigend(sizes), cap) == [[3, 1], [2], [0]]
    assert A.ordnung_gross_zuerst(sizes) == [0, 1, 2, 3] and A.ffd(sizes, cap) == [[0, 3], [1, 2]]


def test_fuellregel_von_hand(mini_fuell):
    sizes, cap = mini_fuell
    assert A.fuellregel(sizes, cap) == [[0, 1], [2, 3, 4]]


def test_zufallsordnung_ist_eine_feste_permutation_je_startzahl():
    erste = A.ordnung_zufall(12, 7)
    assert sorted(erste) == list(range(12)) and erste == A.ordnung_zufall(12, 7)


# --- 11/9-Instanz ---------------------------------------------------------------------------------------------------------------------------


def test_johnson_instanz_optimum_neun_ffd_elf():
    inst = S.johnson()
    assert inst.n == 30 and inst.cap == 1000 and sum(inst.sizes) == 9000 and inst.opt == 9 == A.l1(inst.sizes, 1000)
    assert Counter(inst.sizes) == {502: 6, 254: 6, 252: 6, 246: 12}
    bins = A.ffd(inst.sizes, 1000)
    assert len(bins) == 11
    # FFD von Hand: sechs Container (502, 254), zwei Container (252, 252, 252), drei Container (246 x 4)
    assert Counter(tuple(sorted(inst.sizes[i] for i in b)) for b in bins) == {(254, 502): 6, (252, 252, 252): 2, (246, 246, 246, 246): 3}


@pytest.mark.parametrize("k", [1, 2, 3, 4])
def test_johnson_familie_waechst_mit_dem_vielfachen(k):
    inst = S.johnson(k)
    assert inst.opt == 9 * k and len(A.ffd(inst.sizes, 1000)) == 11 * k


def test_dosa_grenze_tabelle():
    assert [A.dosa_grenze(o) for o in range(1, 12)] == [1, 3, 4, 5, 6, 8, 9, 10, 11, 12, 14]


def test_dosa_grenze_bei_optimum_neun_wird_erreicht():
    assert A.dosa_grenze(9) == 11 == len(A.ffd(S.johnson().sizes, 1000))


# --- Analyse -----------------------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("beispiel,ffd,opt,nicht_voll,frei", [(0, 3, 2, 3, 100), (2, 11, 9, 11, 2000)])
def test_analyse_der_festen_beispiele(beispiel, ffd, opt, nicht_voll, frei):
    a = ev.analyse(ev.Settings(beispiel))
    assert (a.ffd, a.opt, a.schranke_l1, a.nicht_voll, a.frei) == (ffd, opt, opt, nicht_voll, frei)
    assert a.grenze == A.dosa_grenze(opt)


def test_analyse_der_zufaelligen_und_gestoerten_beispiele():
    a = ev.analyse(ev.Settings(C.ZUFALL_TRIPLETS, k=10, seed=7))
    assert a.inst.n == 30 and a.opt == 10 == a.schranke_l1 and a.ffd > a.opt
    b = ev.analyse(ev.Settings(C.GESTOERT, delta=3, seed=7))
    assert b.inst.n == 30 and b.opt == 9 and 9 <= b.ffd <= A.dosa_grenze(9)


def test_alle_ffd_packungen_sind_zulaessig_und_die_optimale_packung_auch():
    for beispiel in C.BEISPIEL_NAMEN:
        a = ev.analyse(ev.Settings(beispiel))
        assert A.container_pruefen(a.inst.sizes, a.ffd_bins, a.inst.cap) and A.container_pruefen(a.inst.sizes, a.inst.opt_bins, a.inst.cap)
