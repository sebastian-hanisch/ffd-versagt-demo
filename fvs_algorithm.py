"""Kern: FFD und First Fit in anderen Reihenfolgen, die Füllregel, Instanzen mit bekanntem Optimum (Triplets, 11/9-Familie), Störung, Garantie.

`ffd`, `l1` und `optimum` sind Kopien der Funktionen gleichen Namens aus schranken-beweis-demo/sbw_algorithm.py (dort gegen Aufzählung, zweite DP und ein
ganzzahliges Programm geprüft); die Orakel-Tests dieses Repos prüfen sie noch einmal. Container sind Listen von Paketnummern (Index in `sizes`)."""

import itertools
import random


def first_fit(sizes, order, cap: int) -> list[list[int]]:
    """First Fit in der Reihenfolge `order` (Permutation der Paketnummern): jedes Paket in den ersten Container mit genug Platz."""
    if sorted(order) != list(range(len(sizes))):
        raise ValueError("order muss eine Permutation der Paketnummern sein")
    if any(s <= 0 or s > cap for s in sizes):
        raise ValueError("Paketgröße muss zwischen 1 und der Kapazität liegen")
    bins: list[list[int]] = []
    loads: list[int] = []
    for i in order:
        s = sizes[i]
        for b, load in enumerate(loads):
            if load + s <= cap:
                bins[b].append(i)
                loads[b] += s
                break
        else:
            bins.append([i])
            loads.append(s)
    return bins


def ordnung_liefer(sizes) -> list[int]:
    return list(range(len(sizes)))


def ordnung_gross_zuerst(sizes) -> list[int]:
    return sorted(range(len(sizes)), key=lambda i: (-sizes[i], i))


def ordnung_aufsteigend(sizes) -> list[int]:
    return sorted(range(len(sizes)), key=lambda i: (sizes[i], i))


def ordnung_zufall(n: int, seed: int) -> list[int]:
    idx = list(range(n))
    random.Random(seed).shuffle(idx)
    return idx


def ffd(sizes, cap: int) -> list[list[int]]:
    """First Fit Decreasing: größte zuerst (Gleichstand: kleinere Nummer zuerst)."""
    return first_fit(sizes, ordnung_gross_zuerst(sizes), cap)


def container_pruefen(sizes, bins, cap: int) -> bool:
    """Unabhängiger Zulässigkeitsprüfer: jedes Paket genau einmal, keine Überfüllung, keine leeren Container."""
    gesehen = sorted(i for b in bins for i in b)
    return gesehen == list(range(len(sizes))) and all(b and sum(sizes[i] for i in b) <= cap for b in bins)


def l1(sizes, cap: int) -> int:
    """Volumenschranke: Summe der Größen durch die Kapazität, aufgerundet."""
    return -(-sum(sizes) // cap) if sizes else 0


def fuellregel(sizes, cap: int) -> list[list[int]]:
    """Eigene Heuristik (kein Verfahren aus der Literatur): Je Container das größte Restpaket, dazu aus den übrigen die Teilmenge von höchstens zwei Paketen, die den
    Container am vollsten macht (erste gefundene bei Gleichstand, Reihenfolge der Restliste nach (-Größe, Nummer))."""
    rest = sorted(range(len(sizes)), key=lambda i: (-sizes[i], i))
    bins = []
    while rest:
        first = rest.pop(0)
        load = sizes[first]
        best = (0, ())
        cand = [i for i in rest if load + sizes[i] <= cap]
        for r in (1, 2):
            for comb in itertools.combinations(cand, r):
                s = sum(sizes[i] for i in comb)
                if load + s <= cap and s > best[0]:
                    best = (s, comb)
        for i in best[1]:
            rest.remove(i)
        bins.append([first, *best[1]])
    return bins


def optimum(sizes, cap: int, limit: int = 12):
    """Kleinste mögliche Containerzahl per Teilmengen-DP, oder None, wenn mehr als `limit` Pakete vorliegen."""
    n = len(sizes)
    if n > limit:
        return None
    if n == 0:
        return 0
    full = (1 << n) - 1
    inf = (n + 1, cap + 1)
    dp = [inf] * (full + 1)
    dp[0] = (1, 0)
    for mask in range(full + 1):
        b, last = dp[mask]
        if b > n:
            continue
        for i in range(n):
            if mask >> i & 1:
                continue
            s = sizes[i]
            nxt = (b, last + s) if last + s <= cap else (b + 1, s)
            m2 = mask | (1 << i)
            if nxt < dp[m2]:
                dp[m2] = nxt
    return dp[full][0]


# ------------------------------------------------------------------------------------------------------------------------------------------
# Instanzen mit bekanntem Optimum


def triplet_instanz(k: int, cap: int, rng: random.Random):
    """k Triplets: je drei Pakete in (cap/4, cap/2) mit Summe cap (Rückweisung), dann gemischt. Gibt (Größen, optimale Packung) zurück; die Packung setzt
    je ein Triplet in einen Container, und die Volumenschranke ist k, also ist das Optimum k."""
    paare = []
    for t in range(k):
        while True:
            a = rng.randint(cap // 4 + 1, cap // 2 - 1)
            b = rng.randint(cap // 4 + 1, cap // 2 - 1)
            c = cap - a - b
            if cap // 4 < c < cap // 2:
                break
        paare += [(a, t), (b, t), (c, t)]
    rng.shuffle(paare)
    sizes = tuple(s for s, _ in paare)
    bins = tuple(tuple(i for i, (_, t) in enumerate(paare) if t == tt) for tt in range(k))
    return sizes, bins


def triplets_von_hand(triplets, cap: int):
    """Triplets in der angegebenen Reihenfolge der Pakete (Triplet 1 zuerst); gibt (Größen, optimale Packung) zurück."""
    sizes = tuple(s for t in triplets for s in t)
    bins = tuple(tuple(range(3 * i, 3 * i + 3)) for i in range(len(triplets)))
    return sizes, bins


def johnson_instanz(k: int = 1):
    """Die 11/9-Instanz: 6k Container (502, 252, 246) und 3k Container (254, 254, 246, 246), Kapazität 1000; Optimum 9k, FFD 11k."""
    behaelter = [(502, 252, 246)] * (6 * k) + [(254, 254, 246, 246)] * (3 * k)
    return _aus_behaeltern(behaelter)


def _aus_behaeltern(behaelter):
    sizes = tuple(s for b in behaelter for s in b)
    bins, start = [], 0
    for b in behaelter:
        bins.append(tuple(range(start, start + len(b))))
        start += len(b)
    return sizes, tuple(bins)


def stoerung(behaelter, delta: int, rng: random.Random):
    """Verschiebt in jedem Container ein zufälliges Paar um 0 bis delta (ein Paket kleiner, das andere größer): die Summe je Container bleibt, die optimale
    Packung bleibt gültig. Gibt (Größen, optimale Packung) zurück."""
    neu = []
    for b in behaelter:
        b = list(b)
        i, j = rng.sample(range(len(b)), 2)
        m = rng.randint(0, delta)
        b[i] -= m
        b[j] += m
        neu.append(tuple(b))
    return _aus_behaeltern(neu)


def johnson_behaelter(k: int = 1):
    return [(502, 252, 246)] * (6 * k) + [(254, 254, 246, 246)] * (3 * k)


def dosa_grenze(opt: int) -> int:
    """Größte Containerzahl, die FFD nach FFD <= 11/9 OPT + 6/9 haben darf: ganzzahlig abgerundet (11 OPT + 6) / 9."""
    return (11 * opt + 6) // 9


def freier_platz(sizes, bins, cap: int) -> tuple[int, int]:
    """(Zahl der nicht ganz gefüllten Container, gesamter freier Platz)."""
    frei = [cap - sum(sizes[i] for i in b) for b in bins]
    return sum(1 for f in frei if f > 0), sum(frei)
