"""Wo FFD versagt: Triplets und die 11/9-Instanz - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 3 der Reihe „Packen: Reihenfolge und Platzierungsregel“. Instanzen mit bekanntem Optimum (Triplets, die 11/9-Instanz): FFD verfehlt es, die Reihenfolge zu
ändern verringert die Lücke nur, und das Verfehlen überlebt kleine Störungen. Experiment A und C sind vorberechnet (fvs_precomputed.json), B rechnet live.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import fvs_constants as C
from fvs_evaluation import (
    Settings,
    analyse,
    klein_tabelle,
    klein_zeile,
    stoerung_verteilung,
    triplet_zeile,
    verdict_ausgang,
    verdict_klein,
    verdict_stoerung,
    verdict_triplets,
    verdict_warum,
)
from fvs_layout import dunkles_design, kopf_css
from fvs_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from fvs_visualization import build_container, build_stoerung, build_triplets

st.set_page_config(page_title="FFD versagt – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _stoerung(delta):
    return stoerung_verteilung(delta)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in fvs_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧱 Wo FFD versagt: Triplets und die 11/9-Instanz")
st.markdown(
    """
**FFD** (First Fit Decreasing) braucht manchmal mehr Container als nötig. Diese Demo baut Instanzen, bei denen das Optimum **durch Konstruktion bekannt** ist: **Triplets** sind drei Pakete, die zusammen genau einen Container füllen, und jede optimale Packung füllt jeden Container ganz. Die Volumenschranke kennt dann das Optimum, FFD verfehlt es meist (im Experiment in allen 1000 Instanzen), und eine andere Reihenfolge der Pakete verringert die Lücke, schließt sie aber nicht.

Weiter unten: die Abschnitte **🔬 Experiment** (Triplets, Störung der 11/9-Instanz, kleines Optimum), **🚧 Wo die Annahmen enden**, der Expander **⚠️ Annahmen, Grenzen und bekannte Probleme** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert die Suche nach dem Versagen", expanded=True):
    st.markdown(
        """
1. **Instanz mit bekanntem Optimum bauen:** Triplets (drei Pakete, Summe gleich der Kapazität) oder die 11/9-Instanz. Die Packung „ein Triplet je Container“ ist gültig und füllt jeden Container ganz; die Volumenschranke verlangt genau so viele Container, also ist das Optimum bekannt.
2. **FFD packt dieselben Pakete:** größte zuerst, jedes in den ersten Container, in den es passt.
3. **Vergleich:** Die Demo zeigt beide Packungen nebeneinander, den Platz, den FFD verschenkt, und die Containerzahl gegen das Optimum.
4. **Variieren:** Andere Reihenfolgen, leicht verschobene Paketgrößen und kleine Instanzen zeigen, wie fest das Versagen sitzt.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Instanz**")
    beispiel = st.selectbox("Beispiel", list(C.BEISPIEL_NAMEN), format_func=C.BEISPIEL_NAMEN.get, key="beispiel_select",
                            help="Zwei Triplets von Hand, zufällige Triplets, die 11/9-Instanz oder eine gestörte 11/9-Instanz.")
    k = st.slider("Zahl der Triplets", *bounds("k_slider"), key="k_slider", help="Wirkt nur bei „Zufällige Triplets“.")
    delta = st.slider("Stärke der Störung", *bounds("delta_slider"), key="delta_slider", help="Wirkt nur bei „Gestörte 11/9-Instanz“: so weit wird in jedem optimalen Container ein Paar höchstens verschoben.")
    seed = st.number_input("Startzahl", *bounds("seed_input"), key="seed_input", step=1, help="Wirkt nur bei „Zufällige Triplets“ und „Gestörte 11/9-Instanz“.")
    st.button("🎲 Neue Startzahl würfeln", width="stretch", on_click=randomize_seed)

sync_query_params({"beispiel_select": int(beispiel), "k_slider": int(k), "delta_slider": int(delta), "seed_input": int(seed)})

settings = Settings(int(beispiel), int(k), int(delta), int(seed))
a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
# Delta immer als „mein Wert minus Referenz“; die Farbe regelt delta_color="inverse" (Vorzeichen-Falle, DEMO-PLAYBOOK §2).
m1.metric("FFD braucht", a.ffd, delta=a.ffd - a.opt, delta_color="inverse", help="Delta: FFD minus Optimum.")
m2.metric("Optimum (durch Konstruktion)", a.opt, delta="Referenz", delta_color="off")
m3.metric("Volumenschranke L1", a.schranke_l1, delta="gleich dem Optimum", delta_color="off")
m4.metric("Garantie erlaubt höchstens", a.grenze, delta="11/9 · Optimum + 6/9, abgerundet", delta_color="off")
st.caption("Pakete nach Größe geordnet: " + ", ".join(str(s) for s in sorted(a.inst.sizes, reverse=True)) + f"  (Summe {sum(a.inst.sizes)}, Kapazität {a.inst.cap}).")
c1, c2 = st.columns(2)
with c1:
    st.markdown(f"**FFD: {a.ffd} Container**")
    st.plotly_chart(build_container(a.inst.sizes, a.ffd_bins, a.inst.cap), width="stretch", key="chart_ffd")
with c2:
    st.markdown(f"**Optimale Packung: {a.opt} Container**")
    st.plotly_chart(build_container(a.inst.sizes, a.inst.opt_bins, a.inst.cap), width="stretch", key="chart_opt")
st.caption("Grün: Pakete (Beschriftung = Größe), grau: freier Platz, rot gestrichelt: Kapazität eines Containers.")
kind, text = verdict_warum(a)
getattr(st, kind)(text)

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie viele Container braucht FFD mehr als das Optimum, obwohl die Volumenschranke es kennt?")
kind, text = verdict_ausgang(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment A: Triplets ----------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Hilft eine andere Reihenfolge bei Triplets?")
st.caption(
    f"Gemessen an je {C.INSTANZEN} festen Instanzen pro Zeile (Kapazität 1000, Pakete zwischen einem Viertel und der Hälfte der Kapazität). Zahl = Container über dem Optimum, "
    f"im Mittel. Die Zahlen sind vorberechnet (`generate_precomputed.py`)."
)
exp_k = st.selectbox("Zahl der Triplets (für das Verdikt)", list(range(len(C.N_TRIPLETS))), index=1, format_func=lambda i: str(C.N_TRIPLETS[i]), key="exp_k")
zeilen = [triplet_zeile(kk) for kk in C.N_TRIPLETS]
st.plotly_chart(build_triplets(zeilen), width="stretch", key="chart_triplets")
tabelle = ["| k | FFD | FF | auf | zuf | füll |", "|---|---|---|---|---|---|"]
for z in zeilen:
    m = z["mittel"]
    fuell = "–" if m["FUELL"] is None else f"{m['FUELL']:.2f}"
    tabelle.append(f"| {z['k']} | {m['FFD']:.2f} | {m['FF']:.2f} | {m['AUF']:.2f} | {m['ZUF']:.2f} | {fuell} |")
st.markdown("\n".join(tabelle))
st.caption(
    f"**k:** Zahl der Triplets. **FFD:** größte zuerst. **FF:** First Fit in Lieferreihenfolge. **auf:** First Fit, aufsteigend. **zuf:** bester von {C.ZUFALLSORDNUNGEN} Zufallsordnungen. "
    f"**füll:** eigene Füllregel (nur bis {C.FUELL_LIMIT} Triplets gerechnet). FFD erreicht das Optimum in {sum(z['ffd_optimal'] for z in zeilen)} von {sum(z['instanzen'] for z in zeilen)} Instanzen."
)
kind, text = verdict_triplets(zeilen[int(exp_k)])
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment B: Störung ------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Wie fest sitzt das Versagen bei der 11/9-Instanz?")
st.caption(
    f"In jedem der 9 optimalen Container der 11/9-Instanz wird ein zufälliges Paar um höchstens die gewählte Stärke verschoben (die Summe je Container und damit das Optimum 9 bleiben). "
    f"{C.STOERUNGEN} feste Störungen je Stärke, live gerechnet."
)
exp_delta = st.selectbox("Stärke der Störung", list(C.DELTAS), index=2, key="exp_delta")
verteilung = _stoerung(int(exp_delta))
st.plotly_chart(build_stoerung(verteilung), width="stretch", key="chart_stoerung")
kind, text = verdict_stoerung(int(exp_delta), verteilung, C.STOERUNGEN)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment C: kleines Optimum ----------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Wie schlecht kann FFD bei kleinem Optimum sein?")
st.caption(
    f"Je {C.KLEIN_INSTANZEN} zufällige Instanzen mit 6, 8, 10 und 12 Paketen (Kapazität {C.KLEIN_CAP}, Größen {C.KLEIN_MIN} bis {C.KLEIN_MAX}), Optimum exakt per Teilmengen-DP; vorberechnet."
)
klein = [klein_zeile(n) for n in C.KLEIN_N]
tab = ["| Optimum | Garantie erlaubt | gemessen größtes FFD |", "|---|---|---|"]
for z in klein_tabelle():
    tab.append(f"| {z['opt']} | {z['erlaubt']} | {'–' if z['gemessen'] is None else z['gemessen']} |")
st.markdown("\n".join(tab))
st.caption("Garantie erlaubt: abgerundet (11 · Optimum + 6) / 9, nach FFD ≤ 11/9 · OPT + 6/9. „–“: ein solches Optimum kam in den Instanzen nicht vor.")
kind, text = verdict_klein(klein)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Das Optimum ist durch Konstruktion bekannt** | Bei zufälligen oder praktischen Instanzen kennt man es nicht; die Demo zeigt nur gezielt gebaute Instanzen. Wie oft FFD dort verfehlt, zeigt das Experiment mit dem kleinen Optimum nur für höchstens 12 Pakete. | Stück 2 dieser Reihe |
| **Nur FFD, andere Reihenfolgen und eine eigene Füllregel** | Eine Suche nach der besten Reihenfolge und andere Regeln kommen später; die Füllregel ist eine eigene Heuristik, kein Verfahren aus der Literatur. | spätere Stücke dieser Reihe |
| **Pakete zwischen einem Viertel und der Hälfte der Kapazität** | Für Triplets mit anderen Größen gelten die gemessenen Zahlen nicht; die Demo hat sie nicht untersucht. | - |
| **Die Garantie ist eine Obergrenze** | Sie sagt, was höchstens vorkommt, nicht, was typisch ist: Bei Optimum 2 bis 5 wird sie erreicht, bei 6 nicht (Experiment oben), bei Zufallsinstanzen meist deutlich unterschritten (Stück 1 und 2). | Stück 1 und 2 dieser Reihe |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(C.ASSUMPTIONS_MARKDOWN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** *Gegeben:* Pakete mit ganzzahligen Größen und Container einer festen Kapazität $C$. *Gesucht:* die kleinste Zahl von Containern, in die alle Pakete passen, und die Zahl, die FFD braucht.

| Symbol | Bedeutung |
|---|---|
| $s_i$ | Größe von Paket $i$, $1 \le s_i \le C$ |
| $C$ | Kapazität eines Containers |
| $k$ | Zahl der Triplets |
| $\mathrm{FFD}$ | Containerzahl von First Fit Decreasing |
| $\mathrm{OPT}$ | kleinste mögliche Zahl von Containern |
| $L_1$ | Volumenschranke $\lceil \sum_i s_i / C \rceil$ |
| $\delta$ | Stärke der Störung |

**Triplets.** Ein Triplet sind drei Pakete $a, b, c$ mit $C/4 < a, b, c < C/2$ und $a + b + c = C$. Aus $k$ Triplets entsteht eine Instanz mit $3k$ Paketen und $\sum_i s_i = kC$, also $L_1 = k$. Die Packung „ein Triplet je Container“ braucht $k$ Container; wegen $L_1 \le \mathrm{OPT} \le k$ ist $\mathrm{OPT} = k$ bekannt, ohne einen Löser.

**11/9-Instanz** ($C = 1000$). Sechs Container $(502, 252, 246)$ und drei Container $(254, 254, 246, 246)$, jeder mit Summe 1000: $\mathrm{OPT} = 9$, 30 Pakete. FFD legt die sechs Pakete zu 502 in je einen Container, die sechs zu 254 dazu (je 756; 252 und 246 passen dann nicht mehr), die sechs zu 252 zu je dreien in zwei weitere Container (756) und die zwölf zu 246 zu je vieren (984) in drei weitere: $6 + 2 + 3 = 11$ Container. Mit $k$-facher Zahl der Pakete sind es $11k$ gegen $9k$.

**Störung.** In jedem optimalen Container wird ein Paar $(i, j)$ gewählt und um $m \in \{0, \dots, \delta\}$ verschoben: $s_i \to s_i - m$, $s_j \to s_j + m$. Die Summe je Container bleibt $C$, die optimale Packung bleibt gültig, $\mathrm{OPT} = 9$.

**Füllregel** (eigene Heuristik). Je Container das größte Restpaket, dazu die Teilmenge aus höchstens zwei weiteren Paketen, die den Container am vollsten macht.

**Garantie (Literatur, aus Suchtreffern, Originale nicht gelesen).** Johnson, Demers, Ullman, Garey und Graham (SIAM J. Comput. 3, 1974): $\mathrm{FFD} \le \tfrac{11}{9}\,\mathrm{OPT} + 4$. Dósa (2007): $\mathrm{FFD} \le \tfrac{11}{9}\,\mathrm{OPT} + \tfrac{6}{9}$, und die Konstante $\tfrac{6}{9}$ ist bestmöglich. Bei $\mathrm{OPT} = 9$ erlaubt das höchstens $\lfloor 11 + 6/9 \rfloor = 11$ Container: Die 11/9-Instanz erreicht die Grenze. Die Demo prüft die zweite Schranke an allen gestörten Varianten und an kleinen Instanzen gegen das exakte Optimum.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
