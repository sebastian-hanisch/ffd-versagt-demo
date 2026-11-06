"""Konstanten: Regler-Grenzen, Beispiele, Experimente, Farben und Presets."""

CAP = 100                 # Kapazität in den Live-Beispielen mit Triplets
JOHNSON_CAP = 1000        # Kapazität der 11/9-Instanz (Teile 502, 254, 252, 246)
SEED_MAX, DEFAULT_SEED = 999999, 7

# --- Beispiele ------------------------------------------------------------------------------------------------------------------------------
# 0: zwei Triplets von Hand (36 + 34 + 30 und 36 + 33 + 31, je 100); 1: zufällige Triplets; 2: die 11/9-Instanz; 3: eine gestörte 11/9-Instanz.
ZWEI_TRIPLETS = ((36, 34, 30), (36, 33, 31))
BEISPIEL_NAMEN = {
    0: "Zwei Triplets (6 Pakete)",
    1: "Zufällige Triplets",
    2: "Die 11/9-Instanz (30 Pakete)",
    3: "Gestörte 11/9-Instanz",
}
ZUFALL_TRIPLETS, JOHNSON, GESTOERT = 1, 2, 3
K_MIN, K_MAX, DEFAULT_K = 2, 20, 10          # Zahl der Triplets der zufälligen Live-Instanz
DELTA_MIN, DELTA_MAX, DEFAULT_DELTA = 1, 10, 3   # Stärke der Störung der 11/9-Instanz

# --- Experiment A: Triplets ----------------------------------------------------------------------------------------------------------------
N_TRIPLETS = (5, 10, 20, 40, 100)
INSTANZEN = 200           # Instanzen je Zelle
ZUFALLSORDNUNGEN = 100    # Zahl der zufälligen Reihenfolgen für „bester von 100“
FUELL_LIMIT = 40          # die Füllregel wird nur bis zu dieser Zahl von Triplets gerechnet
VERFAHREN = ("FFD", "FF", "AUF", "ZUF", "FUELL")
VERFAHREN_NAMEN = {
    "FFD": "FFD (größte zuerst)",
    "FF": "First Fit, Lieferreihenfolge",
    "AUF": "First Fit, aufsteigend",
    "ZUF": "bester von 100 Zufallsordnungen",
    "FUELL": "Füllregel (eigene Heuristik)",
}

# --- Experiment B: Störung der 11/9-Instanz ------------------------------------------------------------------------------------------------
DELTAS = (1, 2, 3, 5, 10)
STOERUNGEN = 2000         # feste Störungen je Stufe (Random(70 + delta), der Reihe nach)

# --- Experiment C: kleines Optimum ---------------------------------------------------------------------------------------------------------
KLEIN_N = (6, 8, 10, 12)
KLEIN_INSTANZEN = 2000    # Instanzen je Größe
KLEIN_CAP = 100
KLEIN_MIN, KLEIN_MAX = 5, 70   # Paketgrößen gleichverteilt
OPT_TABELLE = range(2, 7)  # Optimum der Tabelle (mit n <= 12 erreichbar)

COLOR_FILL = "#2F6B65"
COLOR_FREE = "rgba(150,150,150,0.35)"
COLOR_LINE = "#c0392b"
COLOR_BARS = "#4c78a8"
COLOR_BAD = "#c0392b"
COLOR_OK = "#2F6B65"
COLOR_MID = "#e0a030"

PRESETS = {
    "Zwei Triplets von Hand": {"beispiel": 0, "k": DEFAULT_K, "delta": DEFAULT_DELTA, "seed": DEFAULT_SEED},
    "Zehn zufällige Triplets": {"beispiel": ZUFALL_TRIPLETS, "k": DEFAULT_K, "delta": DEFAULT_DELTA, "seed": DEFAULT_SEED},
    "Die 11/9-Instanz": {"beispiel": JOHNSON, "k": DEFAULT_K, "delta": DEFAULT_DELTA, "seed": DEFAULT_SEED},
    "Gestörte 11/9-Instanz": {"beispiel": GESTOERT, "k": DEFAULT_K, "delta": DEFAULT_DELTA, "seed": DEFAULT_SEED},
}
PRESET_HELP = {
    "Zwei Triplets von Hand": "Sechs Pakete, die sich genau zu zwei Containern zusammensetzen lassen. FFD braucht drei.",
    "Zehn zufällige Triplets": "Dreißig Pakete aus zehn Triplets: Das Optimum ist zehn Container. Wie viele braucht FFD?",
    "Die 11/9-Instanz": "Dreißig Pakete (502, 254, 252, 246), Optimum 9 Container. FFD braucht 11.",
    "Gestörte 11/9-Instanz": "Dieselbe Instanz, in jedem optimalen Container ein Paar leicht verschoben (Stärke und Startzahl in der Seitenleiste). Das Optimum bleibt 9.",
}

# Text des Expanders „Annahmen, Grenzen und bekannte Probleme“; derselbe Wortlaut steht in der README (tests/test_claims.py vergleicht beide).
ASSUMPTIONS_MARKDOWN = f"""**Annahmen.** Ganzzahlige Paketgrößen; eine Sorte Container mit fester Kapazität; alle Pakete sind vor dem Packen bekannt; keine Geometrie, nur Größen. Es kommen nur Instanzen vor, deren Optimum durch die Konstruktion bekannt ist (Triplets und die 11/9-Familie); sie sind gezielt schwer für FFD gebaut.

**Grenzen.** Das Experiment mit Triplets deckt fünf Größen von 5 bis 100 Triplets mit je {INSTANZEN} Instanzen ab, das mit der Störung fünf Stärken mit je {STOERUNGEN} festen Störungen, das mit dem kleinen Optimum Instanzen mit höchstens 12 Paketen. Praxisdaten kommen nicht vor. Die Füllregel ist eine eigene Heuristik, kein Verfahren aus der Literatur, und wird nur bis {FUELL_LIMIT} Triplets gerechnet.

**Bekannte Probleme und Unsicherheiten.** Die Aussagen gelten für diese festen Instanzen; mit anderen Startzahlen ändern sich die Mittelwerte etwas, und eine einzelne Zelle ist kein Gesetz. Dass FFD die Triplets nie optimal packt, gilt für die Instanzen dieser Demo und ist kein Beweis für alle Triplets. Die Gütegarantie FFD ≤ 11/9 · OPT + 6/9 steht nur aus Suchtreffern und Sekundärquellen, das Original wurde nicht gelesen. Die App wurde im Browser bedient (Presets, Würfel-Button und Ausklapper auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät."""
