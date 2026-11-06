"""Randfälle: leere Eingabe, ein Container, ungültige Eingaben, Instanzen ohne bekanntes Optimum, Instanzgeneratoren mit festen Seeds."""

import random

import pytest

import fvs_algorithm as A
import fvs_constants as C
import fvs_scenario as S
from fvs_scenario import Instance


def test_leere_eingabe():
    assert A.ffd((), 10) == [] and A.fuellregel((), 10) == [] and A.l1((), 10) == 0 and A.optimum((), 10) == 0
    assert A.freier_platz((), [], 10) == (0, 0)


def test_freier_platz_zaehlt_nur_nicht_ganz_gefuellte_container():
    assert A.freier_platz((50, 50, 30), [[0, 1], [2]], 100) == (1, 70)          # C1 voll (100), C2 mit 70 frei
    assert A.freier_platz((50, 50), [[0, 1]], 100) == (0, 0)


def test_ein_paket_und_paket_gleich_kapazitaet():
    assert A.ffd((7,), 10) == [[0]] and A.fuellregel((7,), 10) == [[0]]
    assert A.ffd((10, 10), 10) == [[0], [1]] and A.optimum((10, 10), 10) == 2


def test_ungueltige_eingaben_werfen():
    with pytest.raises(ValueError):
        A.ffd((11,), 10)
    with pytest.raises(ValueError):
        A.first_fit((3, 4), [0, 0], 10)         # keine Permutation
    with pytest.raises(ValueError):
        Instance((3, 4), 0, ((0, 1),))          # Kapazität null
    with pytest.raises(ValueError):
        Instance((3, 12), 10, ((0,), (1,)))     # Paket größer als die Kapazität
    with pytest.raises(ValueError):
        Instance((3.5,), 10, ((0,),))           # keine ganze Zahl
    with pytest.raises(ValueError):
        Instance((6, 6), 10, ((0, 1),))         # Packung überfüllt
    with pytest.raises(ValueError):
        Instance((6, 4), 10, ((0,),))           # Paket 1 fehlt in der Packung


def test_instanz_ohne_bekanntes_optimum_wird_abgelehnt():
    """Eine zulässige Packung, die die Volumenschranke nicht erreicht, beweist das Optimum nicht."""
    with pytest.raises(ValueError):
        S._mit_optimum((4, 4, 4), ((0,), (1,), (2,)), 10)


def test_triplet_generator_ist_fest_und_hat_die_eigenschaften():
    for seed in range(200):
        k = random.Random(seed).randint(1, 15)
        sizes, bins = A.triplet_instanz(k, 100, random.Random(seed))
        assert (sizes, bins) == A.triplet_instanz(k, 100, random.Random(seed))
        assert len(sizes) == 3 * k and sum(sizes) == 100 * k and len(bins) == k
        assert all(25 < s < 50 for s in sizes)                     # jedes Paket zwischen einem Viertel und der Hälfte
        assert all(len(b) == 3 and sum(sizes[i] for i in b) == 100 for b in bins)
        assert A.container_pruefen(sizes, bins, 100) and A.l1(sizes, 100) == k


def test_ffd_ist_bei_triplets_nie_unter_dem_optimum_und_liegt_in_den_instanzen_darueber():
    for seed in range(100):
        inst = S.zufalls_triplets(10, seed)
        f = len(A.ffd(inst.sizes, inst.cap))
        assert f >= inst.opt
    assert all(len(A.ffd(S.zufalls_triplets(10, seed).sizes, 100)) > 10 for seed in range(30))      # in diesen 30 Instanzen verfehlt FFD das Optimum


def test_stoerung_haelt_die_summe_je_container_und_ist_fest():
    for delta in (1, 3, 10):
        for seed in range(50):
            sizes, bins = A.stoerung(A.johnson_behaelter(), delta, random.Random(seed))
            assert (sizes, bins) == A.stoerung(A.johnson_behaelter(), delta, random.Random(seed))
            assert len(bins) == 9 and all(sum(sizes[i] for i in b) == 1000 for b in bins) and A.container_pruefen(sizes, bins, 1000)
            assert all(abs(s - o) <= delta for s, o in zip(sizes, [x for b in A.johnson_behaelter() for x in b]))


def test_stoerung_mit_delta_null_aendert_nichts():
    sizes, _ = A.stoerung(A.johnson_behaelter(), 0, random.Random(1))
    assert sizes == S.johnson().sizes


def test_instanz_seeds_der_experimente_sind_verschieden():
    seeds = {S.triplet_seed(k, j) for k in C.N_TRIPLETS for j in range(C.INSTANZEN)}
    assert len(seeds) == len(C.N_TRIPLETS) * C.INSTANZEN
    assert S.kleine_instanz(8, 3) == S.kleine_instanz(8, 3) and S.kleine_instanz(8, 3) != S.kleine_instanz(8, 4)
    assert all(C.KLEIN_MIN <= s <= C.KLEIN_MAX for s in S.kleine_instanz(12, 5))
