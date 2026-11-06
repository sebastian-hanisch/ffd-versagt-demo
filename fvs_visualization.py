"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import fvs_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.3), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_container(sizes, bins, cap, height=360):
    """Ein Balken je Container, darin die Pakete als gestapelte Segmente (Beschriftung = Größe), oben der freie Platz in Grau.

    Die rote Linie ist die Kapazität. Beschriftungen als Text (C1, C2 ...), damit Plotly keine lineare Achse anlegt."""
    labels = [f"C{b + 1}" for b in range(len(bins))]
    schichten = max((len(b) for b in bins), default=0)
    fig = go.Figure()
    for k in range(schichten):
        werte = [sizes[b[k]] if k < len(b) else 0 for b in bins]
        texte = [str(sizes[b[k]]) if k < len(b) else "" for b in bins]
        fig.add_trace(go.Bar(x=labels, y=werte, text=texte, textposition="inside", insidetextanchor="middle", marker=dict(color=C.COLOR_FILL, line=dict(color="white", width=1.5)),
                             showlegend=False, hovertemplate="%{x}: Paket %{text}<extra></extra>"))
    frei = [cap - sum(sizes[i] for i in b) for b in bins]
    fig.add_trace(go.Bar(x=labels, y=frei, text=[f"frei {f}" if f > 0 else "" for f in frei], textposition="inside", insidetextanchor="middle",
                         marker=dict(color=C.COLOR_FREE), showlegend=False, hovertemplate="%{x}: %{y} frei<extra></extra>"))
    fig.add_hline(y=cap, line=dict(color=C.COLOR_LINE, width=2, dash="dash"))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title_text="Füllung (Kapazität %d)" % cap, range=[0, cap * 1.05])
    return _base(fig, height)


def build_triplets(z_liste):
    """Gruppierte Balken je Zahl der Triplets: mittlere Container über dem Optimum je Verfahren (Zeilen aus fvs_evaluation.triplet_zeile)."""
    fig = go.Figure()
    farben = {"FFD": C.COLOR_BAD, "FF": C.COLOR_BARS, "AUF": C.COLOR_FREE, "ZUF": C.COLOR_OK, "FUELL": C.COLOR_MID}
    for v in C.VERFAHREN:
        xs = [str(z["k"]) + " Triplets" for z in z_liste if z["mittel"][v] is not None]
        ys = [z["mittel"][v] for z in z_liste if z["mittel"][v] is not None]
        fig.add_trace(go.Bar(name=C.VERFAHREN_NAMEN[v], x=xs, y=ys, marker_color=farben[v], hovertemplate="%{x}: %{y:.2f}<extra>" + C.VERFAHREN_NAMEN[v] + "</extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Container über dem Optimum (Mittel)")
    return _base(fig, 380)


def build_stoerung(verteilung):
    """Balken: Zahl der gestörten Varianten je FFD-Containerzahl (9, 10, 11)."""
    xs = [9, 10, 11]
    ys = [verteilung.get(c, 0) for c in xs]
    farben = [C.COLOR_OK, C.COLOR_MID, C.COLOR_BAD]
    fig = go.Figure(go.Bar(x=[f"{c} Container" for c in xs], y=ys, marker_color=farben, text=[str(y) if y else "" for y in ys], textposition="outside", cliponaxis=False,
                           hovertemplate="%{x}: %{y} Varianten<extra></extra>"))
    fig.update_yaxes(title_text="Zahl der Varianten")
    return _base(fig, 320)
