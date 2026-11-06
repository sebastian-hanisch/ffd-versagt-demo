"""Orakel-Tests (DEMO-PLAYBOOK §12): jede Kernroutine gegen einen anderen Rechenweg, feste Seeds, zusammen unter 10 Sekunden.

  Optimum (Teilmengen-DP)      gegen  (a) Aufzählung aller Zerlegungen (n <= 8), (b) zweite DP über Untermengen (n <= 10); bei Triplets zusätzlich gegen das Optimum durch Konstruktion.
  FFD und First Fit            gegen  eine bewusst naive Zweitumsetzung (Pakete als Listen, Füllung jedes Mal neu summiert).
  Füllregel                    gegen  eine Zweitumsetzung, die alle Teilmengen aus einem und zwei Paketen aufzählt und nach (-Summe, Größe, Lage) sortiert.
  Eigenschaften mit exaktem Optimum: Garantie FFD <= 11/9 OPT + 6/9 in exakter Bruchrechnung, FFD >= OPT, Triplets: FFD >= k.
"""

import itertools
import random
from fractions import Fraction

import fvs_algorithm as A
import fvs_scenario as S


def instanzen(anzahl, n_lo, n_hi, cap_lo=5, cap_hi=40, seed0=0):
    for seed in range(seed0, seed0 + anzahl):
        rng = random.Random(seed)
        cap = rng.randint(cap_lo, cap_hi)
        n = rng.randint(n_lo, n_hi)
        yield cap, [rng.randint(1, cap) for _ in range(n)]


def optimum_aufzaehlung(sizes, cap):
    n = len(sizes)
    if n == 0:
        return 0
    best = n

    def rec(i, loads):
        nonlocal best
        if len(loads) >= best:
            return
        if i == n:
            best = len(loads)
            return
        for b in range(len(loads)):
            if loads[b] + sizes[i] <= cap:
                loads[b] += sizes[i]
                rec(i + 1, loads)
                loads[b] -= sizes[i]
        loads.append(sizes[i])
        rec(i + 1, loads)
        loads.pop()

    rec(0, [])
    return best


def optimum_untermengen(sizes, cap):
    n = len(sizes)
    full = (1 << n) - 1
    summe = [0] * (full + 1)
    for m in range(1, full + 1):
        low = (m & -m).bit_length() - 1
        summe[m] = summe[m & (m - 1)] + sizes[low]
    g = [0] * (full + 1)
    for m in range(1, full + 1):
        low = m & -m
        rest = m ^ low
        sub = rest
        beste = n + 1
        while True:
            t = sub | low
            if summe[t] <= cap and g[m ^ t] + 1 < beste:
                beste = g[m ^ t] + 1
            if sub == 0:
                break
            sub = (sub - 1) & rest
        g[m] = beste
    return g[full]


def test_optimum_stimmt_mit_der_aufzaehlung_ueberein():
    for cap, sizes in instanzen(80, 1, 8):
        assert A.optimum(sizes, cap) == optimum_aufzaehlung(sizes, cap), (cap, sizes)


def test_optimum_stimmt_mit_der_untermengen_dp_ueberein():
    for cap, sizes in instanzen(40, 1, 10, seed0=1000):
        assert A.optimum(sizes, cap) == optimum_untermengen(sizes, cap), (cap, sizes)


def test_optimum_randfaelle():
    assert A.optimum([], 10) == 0 and A.optimum([10, 10, 10], 10) == 3 and A.optimum([5, 5, 5, 5], 10) == 2
    assert A.optimum([1] * 13, 12, limit=12) is None


def test_optimum_durch_konstruktion_stimmt_mit_der_dp_bei_kleinen_triplets_ueberein():
    for seed in range(60):
        k = random.Random(seed).randint(1, 4)
        inst = S.zufalls_triplets(k, seed)
        assert A.optimum(inst.sizes, inst.cap) == inst.opt == k, (k, seed)


def ffd_naiv(sizes, cap):
    container = []
    for i in sorted(range(len(sizes)), key=lambda i: (-sizes[i], i)):
        for c in container:
            if sum(c) + sizes[i] <= cap:
                c.append(sizes[i])
                break
        else:
            container.append([sizes[i]])
    return sorted(sorted(c) for c in container)


def first_fit_naiv(sizes, order, cap):
    container = []
    for i in order:
        for c in container:
            if sum(c) + sizes[i] <= cap:
                c.append(sizes[i])
                break
        else:
            container.append([sizes[i]])
    return sorted(sorted(c) for c in container)


def test_ffd_und_first_fit_stimmen_mit_der_naiven_zweitumsetzung_ueberein():
    for cap, sizes in instanzen(150, 0, 14, seed0=2000):
        assert sorted(sorted(sizes[i] for i in b) for b in A.ffd(sizes, cap)) == ffd_naiv(sizes, cap), (cap, sizes)
        rng = random.Random(len(sizes) + cap)
        order = list(range(len(sizes)))
        rng.shuffle(order)
        bins = A.first_fit(sizes, order, cap)
        assert sorted(sorted(sizes[i] for i in b) for b in bins) == first_fit_naiv(sizes, order, cap)
        assert A.container_pruefen(sizes, bins, cap)


def fuellregel_naiv(sizes, cap):
    """Zweitumsetzung: je Container das größte Restpaket, dann alle Teilmengen aus einem und zwei der übrigen Pakete (die passen) aufzählen und nach
    (-Summe, Zahl der Pakete, Lage in der Restliste) sortieren; die erste gewinnt."""
    rest = sorted(range(len(sizes)), key=lambda i: (-sizes[i], i))
    bins = []
    while rest:
        first, rest = rest[0], rest[1:]
        frei = cap - sizes[first]
        kandidaten = []
        for r in (1, 2):
            for lagen in itertools.combinations(range(len(rest)), r):
                s = sum(sizes[rest[p]] for p in lagen)
                if s <= frei and all(sizes[rest[p]] <= frei for p in lagen):
                    kandidaten.append((-s, r, lagen))
        gewaehlt = min(kandidaten)[2] if kandidaten else ()
        bins.append([first] + [rest[p] for p in gewaehlt])
        rest = [x for p, x in enumerate(rest) if p not in gewaehlt]
    return bins


def test_fuellregel_stimmt_mit_der_zweitumsetzung_ueberein():
    for cap, sizes in instanzen(120, 0, 12, seed0=3000):
        bins = A.fuellregel(sizes, cap)
        assert bins == fuellregel_naiv(sizes, cap), (cap, sizes)
        assert A.container_pruefen(sizes, bins, cap)


def test_garantie_und_untergrenze_an_kleinen_instanzen_mit_exaktem_optimum():
    for cap, sizes in instanzen(80, 1, 12, seed0=4000):
        f = len(A.ffd(sizes, cap))
        opt = A.optimum(sizes, cap)
        assert opt <= f and Fraction(f) <= Fraction(11, 9) * opt + Fraction(6, 9), (cap, sizes)
        assert A.l1(sizes, cap) <= opt
        assert f <= A.dosa_grenze(opt)


def test_ffd_bei_triplets_nie_unter_der_zahl_der_triplets_und_nie_ueber_der_garantie():
    for seed in range(100):
        k = random.Random(seed).randint(1, 25)
        inst = S.zufalls_triplets(k, seed)
        f = len(A.ffd(inst.sizes, inst.cap))
        assert k <= f <= A.dosa_grenze(k), (k, seed)
