"""Kennzahlen, Verdikt-Logik und die Experimente (A Triplets, C kleines Optimum vorberechnet in fvs_precomputed.json; B Störung live)."""

import json
import random
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import fvs_algorithm as A
import fvs_constants as C
import fvs_scenario as S
from fvs_scenario import Instance

PRECOMPUTED = Path(__file__).resolve().parent / "fvs_precomputed.json"


@dataclass(frozen=True)
class Settings:
    beispiel: int = 0
    k: int = C.DEFAULT_K
    delta: int = C.DEFAULT_DELTA
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    inst: Instance
    ffd_bins: tuple      # FFD-Packung
    ffd: int
    opt: int             # Optimum durch Konstruktion
    schranke_l1: int
    nicht_voll: int      # Zahl der nicht ganz gefüllten FFD-Container
    frei: int            # gesamter freier Platz der FFD-Packung
    grenze: int          # größte nach FFD <= 11/9 OPT + 6/9 erlaubte Containerzahl
    settings: Settings


def instanz(s: Settings) -> Instance:
    if s.beispiel == 0:
        return S.zwei_triplets()
    if s.beispiel == C.ZUFALL_TRIPLETS:
        return S.zufalls_triplets(s.k, s.seed)
    if s.beispiel == C.JOHNSON:
        return S.johnson()
    return S.gestoert(s.delta, s.seed)


def analyse(s: Settings) -> Analysis:
    inst = instanz(s)
    bins = A.ffd(inst.sizes, inst.cap)
    assert A.container_pruefen(inst.sizes, bins, inst.cap)
    nicht_voll, frei = A.freier_platz(inst.sizes, bins, inst.cap)
    return Analysis(inst, tuple(tuple(b) for b in bins), len(bins), inst.opt, A.l1(inst.sizes, inst.cap), nicht_voll, frei, A.dosa_grenze(inst.opt), s)


# ------------------------------------------------------------------------------------------------------------------------------------------
# Verdikte (reine Funktionen: (Art, Text))


def verdict_ausgang(a: Analysis) -> tuple[str, str]:
    """Kernfrage: Wie viele Container braucht FFD mehr als das Optimum, obwohl die Volumenschranke das Optimum kennt?"""
    if a.ffd == a.opt:
        return "success", f"FFD braucht **{a.ffd}** Container und findet damit das Optimum (Volumenschranke L1 = {a.schranke_l1})."
    mehr = a.ffd - a.opt
    return "warning", (f"FFD braucht **{a.ffd}** Container, das Optimum ist **{a.opt}** (gleich der Volumenschranke L1 = {a.schranke_l1}): {mehr} zu viel, "
                       f"das Verhältnis ist {a.ffd / a.opt:.3f}. Die Garantie FFD ≤ 11/9 · OPT + 6/9 erlaubt bei Optimum {a.opt} höchstens {a.grenze} Container.")


def verdict_warum(a: Analysis) -> tuple[str, str]:
    """Woran das Verfehlen sichtbar wird: die optimale Packung füllt jeden Container ganz, FFD lässt Platz frei."""
    cap = a.inst.cap
    if a.opt * cap != sum(a.inst.sizes):
        return "info", f"Die optimale Packung hat {a.opt} Container; FFD lässt in {a.nicht_voll} von {a.ffd} Containern zusammen {a.frei} Platz frei."
    return "info", (f"Die optimale Packung füllt jeden der {a.opt} Container bis zum Rand ({cap}). FFD lässt in {a.nicht_voll} von {a.ffd} Containern zusammen {a.frei} Platz frei, "
                    f"das sind {a.frei / cap:.2f} Container.")


# ------------------------------------------------------------------------------------------------------------------------------------------
# Experiment A: Triplets


def triplet_zelle(k: int, instanzen: int = C.INSTANZEN) -> dict:
    """Rechnet eine Zeile des Experiments A frisch: Summen (ganze Zahlen) über `instanzen` feste Instanzen mit k Triplets.

    summen[v] = Summe über die Instanzen von (Container des Verfahrens minus k); ffd_optimal = Zahl der Instanzen, in denen FFD das Optimum erreicht;
    max_luecke = größte Lücke von FFD; fuell_optimal = Zahl der Instanzen, in denen die Füllregel das Optimum erreicht (None bei k über FUELL_LIMIT)."""
    summen = {v: 0 for v in C.VERFAHREN}
    out = {"summen": summen, "ffd_optimal": 0, "max_luecke": 0, "fuell_optimal": 0}
    mit_fuell = k <= C.FUELL_LIMIT
    for j in range(instanzen):
        inst = S.experiment_triplets(k, j)
        sz, cap = inst.sizes, inst.cap
        gap = len(A.ffd(sz, cap)) - k
        summen["FFD"] += gap
        out["ffd_optimal"] += gap == 0
        out["max_luecke"] = max(out["max_luecke"], gap)
        summen["FF"] += len(A.first_fit(sz, A.ordnung_liefer(sz), cap)) - k
        summen["AUF"] += len(A.first_fit(sz, A.ordnung_aufsteigend(sz), cap)) - k
        rng = random.Random(1000 * k + j)
        summen["ZUF"] += min(len(A.first_fit(sz, rng.sample(range(inst.n), inst.n), cap)) for _ in range(C.ZUFALLSORDNUNGEN)) - k
        if mit_fuell:
            fg = len(A.fuellregel(sz, cap)) - k
            summen["FUELL"] += fg
            out["fuell_optimal"] += fg == 0
    if not mit_fuell:
        out["summen"]["FUELL"] = None
        out["fuell_optimal"] = None
    return out


@lru_cache(maxsize=1)
def vorberechnet() -> dict:
    return json.loads(PRECOMPUTED.read_text(encoding="utf-8"))


def triplet_zeile(k: int, daten: dict | None = None) -> dict:
    daten = daten or vorberechnet()
    z = daten["triplets"][str(k)]
    n = daten["instanzen"]
    return {"k": k, "pakete": 3 * k, "instanzen": n, "zufallsordnungen": daten["zufallsordnungen"],
            "mittel": {v: (None if z["summen"][v] is None else z["summen"][v] / n) for v in C.VERFAHREN},
            "ffd_optimal": z["ffd_optimal"], "fuell_optimal": z["fuell_optimal"], "max_luecke": z["max_luecke"]}


def verdict_triplets(z: dict) -> tuple[str, str]:
    """Verdikt zur gewählten Zeile: FFD gegen First Fit in Lieferreihenfolge und die anderen Ordnungen, über die festen Instanzen."""
    m = z["mittel"]
    text = (f"Bei {z['k']} Triplets ({z['pakete']} Paketen) liegt FFD im Mittel über {z['instanzen']} Instanzen {m['FFD']:.2f} Container über dem Optimum und ist in "
            f"{z['ffd_optimal']} von {z['instanzen']} Instanzen optimal. First Fit in Lieferreihenfolge liegt bei {m['FF']:.2f}, aufsteigend sortiert bei {m['AUF']:.2f}, "
            f"der beste von {z['zufallsordnungen']} Zufallsordnungen bei {m['ZUF']:.2f}")
    if m["FUELL"] is not None:
        text += f", die Füllregel bei {m['FUELL']:.2f} (optimal in {z['fuell_optimal']} Instanzen)"
    text += "."
    ffd_zahl, ff_zahl = round(m["FFD"], 2), round(m["FF"], 2)      # verglichen wird, was angezeigt wird
    if ffd_zahl > ff_zahl:
        return "warning", text + " Sortieren schadet hier gegenüber der Lieferreihenfolge."
    if ffd_zahl == ff_zahl:
        return "info", text + " Sortieren und Lieferreihenfolge sind hier gleich gut."
    return "info", text + " Sortieren hilft hier gegenüber der Lieferreihenfolge."


# ------------------------------------------------------------------------------------------------------------------------------------------
# Experiment B: Störung der 11/9-Instanz


def stoerung_verteilung(delta: int, anzahl: int = C.STOERUNGEN) -> dict:
    """FFD-Containerzahl über `anzahl` feste Störungen (Random(70 + delta), der Reihe nach); gibt {Containerzahl: Anzahl} zurück.

    Außerdem wird jede gestörte Instanz geprüft: die optimale Packung bleibt gültig (Optimum 9), FFD liegt nie unter dem Optimum und nie über der Garantie."""
    rng = random.Random(70 + delta)
    verteilung: dict[int, int] = {}
    for _ in range(anzahl):
        sizes, bins = A.stoerung(A.johnson_behaelter(), delta, rng)
        f = len(A.ffd(sizes, C.JOHNSON_CAP))
        assert A.container_pruefen(sizes, bins, C.JOHNSON_CAP) and len(bins) == 9 and 9 <= f <= A.dosa_grenze(9)
        verteilung[f] = verteilung.get(f, 0) + 1
    return dict(sorted(verteilung.items()))


def verdict_stoerung(delta: int, verteilung: dict, anzahl: int) -> tuple[str, str]:
    n9, n10, n11 = (verteilung.get(c, 0) for c in (9, 10, 11))
    text = (f"Von {anzahl} gestörten Varianten (Stärke {delta}) braucht FFD in {n11} Fällen 11 Container, in {n10} Fällen 10 und in {n9} Fällen 9, das Optimum.")
    if n9 == 0:
        return "warning", text + " Das Optimum erreicht FFD in keiner Variante."
    return "info", text + f" Das Optimum erreicht FFD in {n9} Varianten."


# ------------------------------------------------------------------------------------------------------------------------------------------
# Experiment C: kleines Optimum


def klein_zelle(n: int, instanzen: int = C.KLEIN_INSTANZEN) -> dict:
    """Rechnet eine Größe des Experiments C frisch: Lücken FFD - Optimum (Teilmengen-DP), größtes Verhältnis als [FFD, Optimum] und größtes FFD je Optimum."""
    luecken: dict[int, int] = {}
    groesstes = [0, 1]
    max_je_opt: dict[int, int] = {}
    for j in range(instanzen):
        sizes = S.kleine_instanz(n, j)
        f = len(A.ffd(sizes, C.KLEIN_CAP))
        o = A.optimum(sizes, C.KLEIN_CAP, 12)
        luecken[f - o] = luecken.get(f - o, 0) + 1
        if f * groesstes[1] > groesstes[0] * o:
            groesstes = [f, o]
        max_je_opt[o] = max(max_je_opt.get(o, 0), f)
    return {"luecken": {str(g): c for g, c in sorted(luecken.items())}, "groesstes_verhaeltnis": groesstes, "max_ffd_je_opt": {str(o): f for o, f in sorted(max_je_opt.items())}}


def klein_tabelle(daten: dict | None = None) -> list[dict]:
    """Zeilen der Tabelle: je Optimum die nach Literatur erlaubte Containerzahl und das größte gemessene FFD über alle Größen (None, wenn nicht vorgekommen)."""
    daten = daten or vorberechnet()
    zeilen = []
    for o in C.OPT_TABELLE:
        gemessen = [z["max_ffd_je_opt"][str(o)] for z in daten["klein"].values() if str(o) in z["max_ffd_je_opt"]]
        zeilen.append({"opt": o, "erlaubt": A.dosa_grenze(o), "gemessen": max(gemessen) if gemessen else None})
    return zeilen


def klein_zeile(n: int, daten: dict | None = None) -> dict:
    daten = daten or vorberechnet()
    z = daten["klein"][str(n)]
    gesamt = sum(z["luecken"].values())
    return {"n": n, "instanzen": gesamt, "mit_luecke": gesamt - z["luecken"].get("0", 0), "max_luecke": max(int(g) for g in z["luecken"]),
            "verhaeltnis": z["groesstes_verhaeltnis"]}


def verdict_klein(zeilen: list[dict]) -> tuple[str, str]:
    """Verdikt zum kleinen Optimum: größte Lücke und größtes Verhältnis über alle gemessenen Größen (reine Funktion, Zeilen aus klein_zeile)."""
    gesamt = sum(z["instanzen"] for z in zeilen)
    luecke = max(z["max_luecke"] for z in zeilen)
    f, o = max((z["verhaeltnis"] for z in zeilen), key=lambda v: v[0] / v[1])
    mit = sum(z["mit_luecke"] for z in zeilen)
    return "info", (f"In {gesamt} Zufallsinstanzen mit höchstens {max(z['n'] for z in zeilen)} Paketen ist FFD höchstens {luecke} Container über dem Optimum, in {mit} Instanzen "
                    f"überhaupt. Das größte gemessene Verhältnis ist {f} zu {o} ({f / o:.3f}); die Garantie erlaubt bei Optimum {o} bis zu {A.dosa_grenze(o)} Container.")
