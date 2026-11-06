"""Instanzen: Beispiele mit bekanntem Optimum und die festen Instanzen der Experimente."""

import random
from dataclasses import dataclass

import fvs_algorithm as A
import fvs_constants as C


@dataclass(frozen=True)
class Instance:
    sizes: tuple          # Paketgrößen, ganzzahlig und positiv
    cap: int
    opt_bins: tuple       # bekannte optimale Packung (Tupel von Tupeln von Paketnummern)

    def __post_init__(self):
        if self.cap <= 0:
            raise ValueError("Kapazität muss positiv sein")
        for s in self.sizes:
            if not isinstance(s, int) or s <= 0 or s > self.cap:
                raise ValueError(f"Paketgröße {s!r} ungültig (ganz, 1 bis {self.cap})")
        if not A.container_pruefen(self.sizes, self.opt_bins, self.cap):
            raise ValueError("opt_bins ist keine zulässige Packung")

    @property
    def n(self) -> int:
        return len(self.sizes)

    @property
    def opt(self) -> int:
        """Optimum durch Konstruktion: die Packung hat so viele Container, wie die Volumenschranke verlangt."""
        return len(self.opt_bins)


def _mit_optimum(sizes, bins, cap) -> Instance:
    inst = Instance(sizes, cap, bins)
    if len(bins) != A.l1(sizes, cap):
        raise ValueError("Die Packung erreicht die Volumenschranke nicht: das Optimum ist nicht durch Konstruktion bekannt")
    return inst


def zwei_triplets() -> Instance:
    return _mit_optimum(*A.triplets_von_hand(C.ZWEI_TRIPLETS, C.CAP), C.CAP)


def zufalls_triplets(k: int, seed: int, cap: int = C.CAP) -> Instance:
    return _mit_optimum(*A.triplet_instanz(k, cap, random.Random(seed)), cap)


def johnson(k: int = 1) -> Instance:
    return _mit_optimum(*A.johnson_instanz(k), C.JOHNSON_CAP)


def gestoert(delta: int, seed: int) -> Instance:
    return _mit_optimum(*A.stoerung(A.johnson_behaelter(), delta, random.Random(seed)), C.JOHNSON_CAP)


def triplet_seed(k: int, j: int) -> int:
    """Fester Seed der j-ten Triplet-Instanz mit k Triplets im Experiment A; stabil über Läufe und Rechner."""
    return 1_000_000 + 1_000 * k + j


def experiment_triplets(k: int, j: int) -> Instance:
    return zufalls_triplets(k, triplet_seed(k, j), 1000)


def kleine_instanz(n: int, j: int) -> tuple:
    """Zufällige Instanz des Experiments C: n Pakete, Größen gleichverteilt, Kapazität C.KLEIN_CAP, fester Seed."""
    rng = random.Random(10_000 * n + j)
    return tuple(rng.randint(C.KLEIN_MIN, C.KLEIN_MAX) for _ in range(n))
