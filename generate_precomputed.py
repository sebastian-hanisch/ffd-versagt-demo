"""Erzeugt fvs_precomputed.json: Experiment A (Triplets) und Experiment C (kleines Optimum) als ganze Zahlen.

    python generate_precomputed.py            # rechnet alles neu (ungefähr 5 bis 10 Minuten, vor allem „bester von 100 Zufallsordnungen“ bei 100 Triplets)
    python generate_precomputed.py --check    # rechnet das Schnelle nach (FFD, First Fit und aufsteigend je Zeile, kleines Optimum bei 6 und 8 Paketen) und vergleicht

Die App rechnet beides nicht selbst; tests/test_claims.py rechnet jede Zeile mit den Zahlen der README frisch nach."""

import json
import sys
import time

import fvs_constants as C
import fvs_evaluation as ev


def erzeugen() -> dict:
    daten = {"instanzen": C.INSTANZEN, "zufallsordnungen": C.ZUFALLSORDNUNGEN, "fuell_limit": C.FUELL_LIMIT, "klein_instanzen": C.KLEIN_INSTANZEN, "triplets": {}, "klein": {}}
    for k in C.N_TRIPLETS:
        t = time.perf_counter()
        daten["triplets"][str(k)] = ev.triplet_zelle(k)
        print(f"Triplets {k}: {time.perf_counter() - t:.0f} s", flush=True)
    for n in C.KLEIN_N:
        t = time.perf_counter()
        daten["klein"][str(n)] = ev.klein_zelle(n)
        print(f"klein n = {n}: {time.perf_counter() - t:.0f} s", flush=True)
    return daten


def pruefen() -> int:
    gespeichert = ev.vorberechnet()
    schlecht = 0
    for k in C.N_TRIPLETS:
        z = gespeichert["triplets"][str(k)]
        frisch = ev.triplet_zelle(k, instanzen=C.INSTANZEN) if k <= 10 else None
        if frisch is not None and frisch != z:
            schlecht += 1
            print("ABWEICHUNG Triplets", k)
    for n in (6, 8):
        if ev.klein_zelle(n) != gespeichert["klein"][str(n)]:
            schlecht += 1
            print("ABWEICHUNG klein", n)
    print("gleich" if not schlecht else f"{schlecht} Abweichungen")
    return 1 if schlecht else 0


def main() -> int:
    if "--check" in sys.argv:
        return pruefen()
    text = json.dumps(erzeugen(), indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    ev.PRECOMPUTED.write_text(text, encoding="utf-8")
    print("geschrieben:", ev.PRECOMPUTED)
    return 0


if __name__ == "__main__":
    sys.exit(main())
