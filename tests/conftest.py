"""Gemeinsame Fixtures: Mini-Instanzen mit Handrechnung (DEMO-PLAYBOOK §1b).

* zwei_triplets (Kapazität 100): Triplets (36, 34, 30) und (36, 33, 31), Pakete in dieser Reihenfolge (Nummern 0 bis 5), Summe 200, L1 = 2, Optimum 2 durch die Packung
  [[0, 1, 2], [3, 4, 5]] (je 100). FFD (größte zuerst, Gleichstand: kleinere Nummer): 36 (0) und 36 (3) in C1 (72); 34 (1) passt nicht in C1 (106) -> C2; 33 (4) -> C2 (67);
  31 (5) passt nicht in C1 (103), aber in C2 (98); 30 (2) passt weder in C1 (102) noch in C2 (128) -> C3. FFD = [[0, 3], [1, 4, 5], [2]], 3 Container, freier Platz 28 + 2 + 70 = 100.
* mini_ordnung (Kapazität 10): Größen (6, 5, 5, 4), Nummern 0 bis 3. First Fit in Lieferreihenfolge: 6 -> C1; 5 -> C2; 5 -> C2 (10); 4 -> C1 (10): [[0, 3], [1, 2]]. Aufsteigend
  (4, 5, 5, 6 mit Nummern 3, 1, 2, 0): 4 -> C1; 5 -> C1 (9); 5 -> C2; 6 passt weder in C1 (15) noch in C2 (11) -> C3: [[3, 1], [2], [0]].
* mini_fuell (Kapazität 10): Größen (5, 5, 4, 3, 3). Füllregel: C1 mit dem größten Paket 5 (Nr. 0); einzelnes Partnerpaket 5 (Nr. 1) füllt auf 10, kein Paar passt besser -> [0, 1];
  C2 mit 4 (Nr. 2) plus dem Paar 3 + 3 (Nr. 3, 4) = 10 -> [2, 3, 4]. Zwei Container.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fvs_scenario as S  # noqa: E402


@pytest.fixture
def zwei_triplets():
    return S.zwei_triplets()


@pytest.fixture
def mini_ordnung():
    return (6, 5, 5, 4), 10


@pytest.fixture
def mini_fuell():
    return (5, 5, 4, 3, 3), 10
