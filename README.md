# Wo FFD versagt: Triplets und die 11/9-Instanz – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-ffd-versagt-demo.streamlit.app/)** -->

Drittes Stück der Konzepte-Reihe **„Packen: Reihenfolge und Platzierungsregel“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. [Stück 1](https://sebastianhanisch-sortieren-einsetzen-demo.streamlit.app/) zeigt, dass die Reihenfolge der Pakete die Containerzahl stärker verändert als die Wahl zwischen First Fit und Best Fit, [Stück 2](https://sebastianhanisch-schranken-beweis-demo.streamlit.app/) fragt, wann FFD (First Fit, größte zuerst) bewiesen optimal ist. Dieses Stück baut Instanzen, bei denen das Optimum durch Konstruktion bekannt ist, und fragt, wo und wie fest FFD versagt.

## Warum dieses Problem

Auf Zufallsinstanzen liegt FFD meist dicht am Optimum. Es gibt aber Instanzen, bei denen die Volumenschranke das Optimum kennt und FFD es meist verfehlt, und eine andere Reihenfolge verringert die Lücke, schließt sie in den Messungen aber nicht. Die Demo zeigt das an Triplets (drei Pakete, die zusammen genau einen Container füllen), an der 11/9-Instanz und an kleinen Zufallsinstanzen.

## Modell

Ganzzahlige Paketgrößen s₁ … sₙ mit 1 ≤ sᵢ ≤ C, Container der Kapazität C, alle Pakete vorab bekannt. **Triplet:** drei Pakete a, b, c mit C/4 < a, b, c < C/2 und a + b + c = C. Aus k Triplets entsteht eine Instanz mit 3k Paketen und Summe kC, also Volumenschranke k; die Packung „ein Triplet je Container“ braucht k Container, das Optimum ist damit **durch Konstruktion** k (kein Löser). **11/9-Instanz** (C = 1000): sechs Container (502, 252, 246) und drei Container (254, 254, 246, 246), 30 Pakete, Optimum 9. **Störung:** in jedem optimalen Container wird ein zufälliges Paar um 0 bis δ verschoben (Summe je Container bleibt, das Optimum bleibt 9). **Garantie** (aus Suchtreffern): FFD ≤ 11/9 · OPT + 6/9 (Dósa 2007). Formeln im Expander 📐 der App.

## Methodik

- **Kern** (`fvs_algorithm.py`): `ffd`, `first_fit` (beliebige Reihenfolge), `ordnung_liefer`, `ordnung_aufsteigend`, `ordnung_zufall`, `fuellregel`, `triplet_instanz`, `johnson_instanz`, `stoerung`, `dosa_grenze`, `optimum` (Teilmengen-DP bis 12 Pakete), `container_pruefen` (unabhängiger Zulässigkeitsprüfer). `ffd`, `l1` und `optimum` sind Kopien der Funktionen aus `schranken-beweis-demo` (Stück 2), hier noch einmal gegen die Orakel geprüft.
- **Beispiele** (live): zwei Triplets von Hand, zufällige Triplets (2 bis 20), die 11/9-Instanz, die gestörte 11/9-Instanz. Die App zeigt die FFD-Packung und die bekannte optimale Packung nebeneinander.
- **Experiment A (Triplets):** 5, 10, 20, 40 und 100 Triplets × **200 feste Instanzen** (Kapazität 1000); verglichen werden FFD, First Fit in Lieferreihenfolge, First Fit aufsteigend, der beste von **100 Zufallsordnungen** und eine **Füllregel** (eigene Heuristik, nicht aus der Literatur: je Container das größte Restpaket plus die Teilmenge aus höchstens zwei weiteren Paketen, die ihn am vollsten macht; nur bis 40 Triplets gerechnet). Vorberechnet in `fvs_precomputed.json` (`generate_precomputed.py`, etwa zwei Minuten).
- **Experiment B (Störung):** 2000 feste Störungen je Stärke (1, 2, 3, 5, 10), live gerechnet.
- **Experiment C (kleines Optimum):** je 2000 Zufallsinstanzen mit 6, 8, 10 und 12 Paketen (Kapazität 100, Größen 5 bis 70), Optimum exakt per Teilmengen-DP; vorberechnet.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an den Instanzen dieser Demo (feste Seeds), nachgerechnet in `tests/test_claims.py`, `tests/test_algorithm.py` und `tests/test_oracle_ffd_versagt.py`.

**Experiment A: Triplets** (Zahl = Container über dem Optimum, Mittel über 200 Instanzen je Zeile):

| Triplets | FFD | First Fit, Lieferreihenfolge | First Fit, aufsteigend | bester von 100 Zufallsordnungen | Füllregel | FFD optimal (von 200) | größte Lücke von FFD |
|---|---|---|---|---|---|---|---|
| 5 | 1,00 | 1,00 | 1,12 | 0,99 | 0,10 | 0 | 1 |
| 10 | 1,77 | 1,52 | 2,42 | 1,00 | 0,62 | 0 | 2 |
| 20 | 2,83 | 2,55 | 4,69 | 1,80 | 1,00 | 0 | 4 |
| 40 | 5,36 | 4,51 | 9,16 | 3,15 | 1,07 | 0 | 6 |
| 100 | 12,88 | 10,50 | 22,39 | 8,32 | nicht gerechnet | 0 | 15 |

- **FFD ist in 0 von 1000 Instanzen optimal** (200 je Zeile, fünf Zeilen).
- **Sortieren schadet ab 10 Triplets:** FFD liegt über First Fit in Lieferreihenfolge bei 10, 20, 40 und 100 Triplets (bei 5 fast gleich: 1,000 gegen 1,005); aufsteigend sortiert ist in allen fünf Zeilen am schlechtesten.
- **Reihenfolge suchen hilft, löst es aber nicht:** Der beste von 100 Zufallsordnungen liegt in allen fünf Zeilen unter FFD, bei 100 Triplets aber noch 8,32 Container über dem Optimum.
- **Die Füllregel** erreicht das Optimum in 180 von 200 Instanzen bei 5 Triplets, in 76 bei 10 und in 0 bei 20 und 40 (mittlere Lücke 1,00 und 1,07).
- **Das größte Verhältnis FFD / Optimum** ist 1,200 bei 5, 10 und 20 Triplets und 1,150 bei 40 und 100, in allen fünf Zeilen kleiner als 11/9 (1,222).

**Experiment B: gestörte 11/9-Instanz** (2000 Störungen je Stärke, Optimum 9):

| Stärke | FFD braucht 11 | FFD braucht 10 | FFD braucht 9 |
|---|---|---|---|
| 1 | 1988 | 12 | 0 |
| 2 | 1330 | 670 | 0 |
| 3 | 811 | 1189 | 0 |
| 5 | 245 | 1755 | 0 |
| 10 | 26 | 1974 | 0 |

FFD erreicht in **0 von 10 000** gestörten Varianten das Optimum 9; der Extremwert 11 hält bei Stärke 1 in 1988 von 2000 Fällen, bei Stärke 10 nur noch in 26.

**Experiment C: kleines Optimum** (je 2000 Zufallsinstanzen mit 6, 8, 10 und 12 Paketen):

| Optimum | Garantie erlaubt höchstens | gemessen größtes FFD |
|---|---|---|
| 2 | 3 | 3 |
| 3 | 4 | 4 |
| 4 | 5 | 5 |
| 5 | 6 | 6 |
| 6 | 8 | 6 |

- In **177 von 8000** Instanzen verfehlt FFD das Optimum (31 / 32 / 51 / 63 bei 6 / 8 / 10 / 12 Paketen), in keiner um mehr als einen Container.
- Das größte Verhältnis ist **3 zu 2 (1,500)** bei 6 und 8 Paketen und 4 zu 3 bei 10 und 12.
- Die Garantiegrenze wird bei Optimum 2, 3, 4 und 5 erreicht, bei 6 nicht (gemessen 6, erlaubt 8).

**Handbeispiel (zwei Triplets, Kapazität 100):** Pakete 36, 34, 30 und 36, 33, 31. FFD packt [36, 36], [34, 33, 31], [30]: **3 Container** (100 Platz frei), das Optimum ist 2 ({36, 34, 30} und {36, 33, 31}); die Füllregel findet es. First Fit in der Lieferreihenfolge Triplet für Triplet findet es ebenfalls; in der Reihenfolge, die FFD wählt, braucht es 3 Container. **11/9-Instanz:** FFD braucht 11 Container ((502, 254) sechsmal, (252, 252, 252) zweimal, (246 × 4) dreimal), das Optimum ist 9.

## Ehrliche Grenzen

- Alle Aussagen gelten für **Instanzen mit bekanntem Optimum** (Triplets mit Paketen zwischen einem Viertel und der Hälfte der Kapazität, die 11/9-Familie); sie sind gezielt schwer für FFD gebaut. Wie oft FFD auf Zufallsinstanzen verfehlt, zeigt nur Experiment C und nur bis 12 Pakete (177 von 8000).
- „FFD ist nie optimal“ gilt für die 1000 Instanzen dieser Demo, nicht als Beweis für alle Triplets.
- Die Füllregel ist eine eigene Heuristik und wird nur bis 40 Triplets gerechnet; ihr Scheitern ab 20 Triplets sagt nichts über andere Füllregeln.
- Die Gütegarantien (FFD höchstens 11/9·OPT + 4 nach Johnson u. a. 1974, 11/9·OPT + 6/9 nach Dósa 2007) stammen aus Suchtreffern und Sekundärquellen, die Originale wurden nicht gelesen; die zweite Schranke prüft ein Test an allen gestörten Varianten und an kleinen Instanzen gegen das exakte Optimum.
- Die Demo macht keine Aussage zur Schwere des Problems (Komplexität).

### Annahmen, Grenzen und bekannte Probleme (Text wie in der App)

**Annahmen.** Ganzzahlige Paketgrößen; eine Sorte Container mit fester Kapazität; alle Pakete sind vor dem Packen bekannt; keine Geometrie, nur Größen. Es kommen nur Instanzen vor, deren Optimum durch die Konstruktion bekannt ist (Triplets und die 11/9-Familie); sie sind gezielt schwer für FFD gebaut.

**Grenzen.** Das Experiment mit Triplets deckt fünf Größen von 5 bis 100 Triplets mit je 200 Instanzen ab, das mit der Störung fünf Stärken mit je 2000 festen Störungen, das mit dem kleinen Optimum Instanzen mit höchstens 12 Paketen. Praxisdaten kommen nicht vor. Die Füllregel ist eine eigene Heuristik, kein Verfahren aus der Literatur, und wird nur bis 40 Triplets gerechnet.

**Bekannte Probleme und Unsicherheiten.** Die Aussagen gelten für diese festen Instanzen; mit anderen Startzahlen ändern sich die Mittelwerte etwas, und eine einzelne Zelle ist kein Gesetz. Dass FFD die Triplets nie optimal packt, gilt für die Instanzen dieser Demo und ist kein Beweis für alle Triplets. Die Gütegarantie FFD ≤ 11/9 · OPT + 6/9 steht nur aus Suchtreffern und Sekundärquellen, das Original wurde nicht gelesen. Die App wurde im Browser bedient (Presets, Würfel-Button und Ausklapper auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät.

## Verifikation

- **Kern:** zwei Triplets von Hand (FFD, First Fit in zwei Reihenfolgen, Füllregel); First Fit in Liefer- und aufsteigender Reihenfolge an einer Mini-Instanz; die Füllregel an einer Mini-Instanz; die 11/9-Instanz (FFD-Packung von Hand: Container (502, 254) ×6, (252 ×3) ×2, (246 ×4) ×3) und ihre Vielfachen bis 4; die Garantietabelle.
- **Orakel** (`tests/test_oracle_ffd_versagt.py`): Optimum gegen Aufzählung aller Zerlegungen (n ≤ 8, 80 Instanzen) und gegen eine zweite DP über Untermengen (n ≤ 10, 40 Instanzen); Optimum durch Konstruktion gegen die DP (Triplets, 60 Instanzen); FFD und First Fit gegen eine bewusst naive Zweitumsetzung (150 Instanzen); Füllregel gegen eine Zweitumsetzung, die alle Teilmengen aufzählt (120 Instanzen); Garantie in exakter Bruchrechnung (80 Instanzen mit exaktem Optimum) und bei Triplets mit bis zu 25 Triplets (100 Instanzen).
- **Generatoren:** jedes Triplet hat Summe C und Pakete zwischen C/4 und C/2, die Packung ist zulässig und erreicht die Volumenschranke (200 Seeds); die Störung hält die Summe je Container (150 Fälle) und ist fest.
- **Experimente:** jede Zeile von A und jede Größe von C wird frisch gerechnet und exakt mit `fvs_precomputed.json` verglichen; B wird bei jedem Aufruf frisch gerechnet und gegen die README gezählt (`tests/test_claims.py`).
- **Verdikte:** alle Zweige an von Hand gesetzten Werten (`tests/test_verdicts.py`), je Preset die erwartete Art.
- **Presets und Layout:** vollständig, Werte innerhalb der Reglergrenzen, Standard-Preset gleich Standardeinstellung; Schnellstart oben in der Seitenleiste, fester Kopf, genau das passende Preset hervorgehoben (`tests/test_layout.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jede Auswahl in jedem Wert, Regler und Startzahl an den Grenzen) und Footer-Test.
- **Tests gesamt:** 100, Laufzeit etwa zwei Minuten (ohne Parallelisierung; die frische Nachrechnung der vorberechneten Zeilen braucht den größten Teil).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `fvs_algorithm.py` | Kern: FFD, First Fit, Füllregel, Instanzen mit bekanntem Optimum, Störung, Garantie |
| `fvs_constants.py` | Beispiele, Experimente, Farben, Presets, Text der Annahmen |
| `fvs_evaluation.py` | Analyse, Verdikte, Experimente A bis C |
| `fvs_layout.py` | Fester Kopf (Stylesheet) |
| `fvs_precomputed.json` | vorberechnete Summen der Experimente A und C |
| `fvs_presets.py` | Permalink (Begrenzen), Presets (Schnellstart, aktives Preset hervorgehoben), Würfel-Button |
| `fvs_scenario.py` | Instanzen mit bekanntem Optimum und die festen Instanzen der Experimente |
| `fvs_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `generate_precomputed.py` | erzeugt `fvs_precomputed.json`; `--check` rechnet das Schnelle nach |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Instanzen und Handrechnung, Orakel, Randfälle, Verdikte, Presets, Layout, Experimente und Zahlen der README, AppTest-Rauchtest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **PDF-Export:** die Demo zeigt Packungen mit höchstens 60 Paketen; ein Export trüge nichts zur Frage bei.
- **LP-Schranke, Reihenfolge suchen, zwei Grenzen (Volumen und Gewicht):** spätere Stücke der Reihe.
- **Aussagen zur Komplexität** des Problems: ohne geprüfte Quelle kein Satz.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
