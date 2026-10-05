"""
ProcessGas Health Monitor — Radar Multivariável de Saúde
=========================================================
Analyzers Experts — demonstração 50 s com retorno à página do site.

Visitante : https://pgc-health-monitor.analyzersexperts.com/
Full      : https://pgc-health-monitor.analyzersexperts.com/?full=Ae2026FullLab
Retorno   : https://analyzersexperts.com/monitor-de-saude-do-cromatografo/
"""

from __future__ import annotations

import os

from dash import (
    Dash,
    html,
    dcc,
    Input,
    Output,
    State,
    clientside_callback,
    dash_table,
)
import plotly.graph_objs as go

# ---------------------------------------------------------------------------
# Tema Analyzers Experts
# ---------------------------------------------------------------------------
NAVY_DARK = "#0D1B2A"
NAVY_MID = "#16293D"
CARD_BG = "#07101E"
GOLD = "#D4AF37"
GOLD_LIGHT = "#E0B84A"
TEXT_WHITE = "#F3F5F7"
TEXT_GRAY = "#A9B4C2"
GREEN = "#2ECC71"
ORANGE = "#F39C12"
RED = "#E74C3C"
PURPLE = "#9B59B6"

TOKEN_FULL = "Ae2026FullLab"
URL_RETORNO = "https://analyzersexperts.com/monitor-de-saude-do-cromatografo/"
TEMPO_DEMO_S = 50

# Eixos do radar (ordem fechada no gráfico)
AXES = [
    "Pressão Arraste",
    "Pressão Válvulas",
    "Fluxo Measure Vent",
    "Estabilidade Térmica",
    "Integridade TNN",
]

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "ProcessGas Health Monitor | Analyzers Experts"


def _status_from_score(score: float) -> str:
    if score < 75:
        return "CRÍTICO"
    if score < 85:
        return "ALERTA"
    if score < 95:
        return "DESVIO"
    return "NORMAL"


def _build_radar(values: list[float]) -> go.Figure:
    """values: 5 números 0–100 na ordem de AXES."""
    closed = values + [values[0]]
    labels = AXES + [AXES[0]]
    ideal = [100] * len(labels)

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=ideal,
            theta=labels,
            fill="toself",
            name="Nominal Ideal (100%)",
            line=dict(color="#5DADE2", width=2),
            fillcolor="rgba(93, 173, 226, 0.12)",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=closed,
            theta=labels,
            fill="toself",
            name="Estado Atual de Campo",
            line=dict(color=GOLD, width=2.5),
            fillcolor="rgba(212, 175, 55, 0.18)",
        )
    )
    fig.update_layout(
        paper_bgcolor=CARD_BG,
        plot_bgcolor=NAVY_MID,
        font=dict(color=TEXT_GRAY, size=12),
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.08,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
        ),
        polar=dict(
            bgcolor=NAVY_MID,
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color=TEXT_GRAY),
                gridcolor="rgba(255,255,255,0.08)",
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color=GOLD_LIGHT),
                gridcolor="rgba(255,255,255,0.08)",
            ),
        ),
        height=420,
        showlegend=True,
    )
    return fig


def _table_data(scores: dict[str, float]) -> list[dict]:
    rows = []
    for name, score in scores.items():
        rows.append(
            {
                "subsistema": name,
                "score": f"{score:.1f}%".replace(".", ",")
                if name == "Pressão Arraste"
                else f"{score:.0f}%",
                "estado": _status_from_score(score),
            }
        )
    return rows


# Valores iniciais (iguais à captura de referência)
_INIT = {
    "arraste": 92.8,
    "valvulas": 90.0,
    "measure_vent": 72.0,
    "termica": 99.0,
    "tnn": 98.0,
}


def _slider_block(label: str, slider_id: str, value: float) -> html.Div:
    return html.Div(
        style={"flex": "1", "minWidth": "160px"},
        children=[
            html.Label(
                label,
                style={
                    "color": TEXT_GRAY,
                    "fontSize": "12px",
                    "display": "block",
                    "marginBottom": "6px",
                },
            ),
            dcc.Slider(
                id=slider_id,
                min=0,
                max=100,
                step=0.1,
                value=value,
                marks=None,
                tooltip={"placement": "bottom", "always_visible": True},
                updatemode="drag",
            ),
        ],
    )


app.layout = html.Div(
    style={
        "backgroundColor": NAVY_DARK,
        "color": TEXT_WHITE,
        "minHeight": "100vh",
        "padding": "20px 24px 32px",
        "fontFamily": "Segoe UI, system-ui, Arial, sans-serif",
    },
    children=[
        html.H2(
            "ProcessGas Health Monitor — Radar Multivariável de Saúde",
            style={"color": GOLD, "margin": "0 0 18px", "fontWeight": "800", "fontSize": "22px"},
        ),
        # Controles
        html.Div(
            style={
                "background": CARD_BG,
                "border": f"1.5px solid {GOLD}",
                "borderRadius": "12px",
                "padding": "16px 18px",
                "marginBottom": "16px",
                "boxShadow": "0 8px 20px rgba(0,0,0,0.35)",
            },
            children=[
                html.Div(
                    "⚙  Ajuste de Parâmetros de Campo",
                    style={"color": GOLD, "fontWeight": "700", "marginBottom": "12px", "fontSize": "14px"},
                ),
                html.Div(
                    style={
                        "display": "flex",
                        "flexWrap": "wrap",
                        "gap": "16px",
                        "alignItems": "flex-end",
                    },
                    children=[
                        _slider_block("Pressão Arraste (% do Nominal):", "slider-arraste", _INIT["arraste"]),
                        _slider_block("Pressão Válvulas (% do Nominal):", "slider-valvulas", _INIT["valvulas"]),
                        _slider_block("Fluxo Measure Vent (% do Nominal):", "slider-vent", _INIT["measure_vent"]),
                        _slider_block("Estabilidade Térmica (%):", "slider-termica", _INIT["termica"]),
                    ],
                ),
                html.Button(
                    "Atualizar Índice de Saúde Global",
                    id="btn-atualizar",
                    n_clicks=0,
                    style={
                        "marginTop": "14px",
                        "background": GOLD,
                        "color": NAVY_DARK,
                        "border": "none",
                        "fontWeight": "800",
                        "padding": "10px 20px",
                        "borderRadius": "8px",
                        "cursor": "pointer",
                        "fontSize": "13px",
                    },
                ),
            ],
        ),
        # Radar + tabela
        html.Div(
            style={"display": "flex", "flexWrap": "wrap", "gap": "16px"},
            children=[
                html.Div(
                    style={
                        "flex": "1.4",
                        "minWidth": "300px",
                        "background": CARD_BG,
                        "border": f"1.5px solid {GOLD}",
                        "borderRadius": "12px",
                        "padding": "14px 16px",
                    },
                    children=[
                        html.Div(
                            "❄  Índice de Saúde Multivariável (Radar)",
                            style={"color": GOLD, "fontWeight": "700", "marginBottom": "8px", "fontSize": "13px"},
                        ),
                        dcc.Graph(
                            id="radar-graph",
                            figure=_build_radar(
                                [
                                    _INIT["arraste"],
                                    _INIT["valvulas"],
                                    _INIT["measure_vent"],
                                    _INIT["termica"],
                                    _INIT["tnn"],
                                ]
                            ),
                            config={"displayModeBar": False},
                        ),
                    ],
                ),
                html.Div(
                    style={
                        "flex": "1",
                        "minWidth": "280px",
                        "background": CARD_BG,
                        "border": f"1.5px solid {GOLD}",
                        "borderRadius": "12px",
                        "padding": "14px 16px",
                    },
                    children=[
                        html.Div(
                            "▣  Matriz de Desvios Analíticos",
                            style={"color": GOLD, "fontWeight": "700", "marginBottom": "10px", "fontSize": "13px"},
                        ),
                        dash_table.DataTable(
                            id="matriz-desvios",
                            columns=[
                                {"name": "Subsistema Analítico", "id": "subsistema"},
                                {"name": "Índice de Saúde", "id": "score"},
                                {"name": "Estado", "id": "estado"},
                            ],
                            data=_table_data(
                                {
                                    "Pressão Arraste": _INIT["arraste"],
                                    "Pressão Válvulas": _INIT["valvulas"],
                                    "Fluxo Measure Vent": _INIT["measure_vent"],
                                    "Estabilidade Térmica": _INIT["termica"],
                                }
                            ),
                            style_header={
                                "backgroundColor": NAVY_MID,
                                "color": GOLD,
                                "fontWeight": "bold",
                                "border": f"1px solid {GOLD}",
                            },
                            style_cell={
                                "backgroundColor": CARD_BG,
                                "color": TEXT_GRAY,
                                "border": f"1px solid {NAVY_MID}",
                                "padding": "10px",
                                "textAlign": "left",
                                "fontFamily": "Segoe UI, Arial, sans-serif",
                                "fontSize": "13px",
                            },
                            style_data_conditional=[
                                {
                                    "if": {"filter_query": '{estado} = "CRÍTICO"'},
                                    "backgroundColor": "#512E5F",
                                    "color": "#F1948A",
                                    "fontWeight": "bold",
                                },
                                {
                                    "if": {"filter_query": '{estado} = "ALERTA"'},
                                    "backgroundColor": "#7D6608",
                                    "color": "#F9E79F",
                                },
                                {
                                    "if": {"filter_query": '{estado} = "DESVIO"'},
                                    "backgroundColor": "#7D6608",
                                    "color": "#F9E79F",
                                },
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Footer(
            "AnalyzersExperts.com — ProcessGas Health Monitor · Demonstração técnica",
            style={
                "textAlign": "center",
                "color": TEXT_GRAY,
                "fontSize": "11px",
                "marginTop": "24px",
                "paddingTop": "12px",
                "borderTop": "1px solid rgba(212,175,55,0.25)",
            },
        ),
        # --- Modo demonstração 50 s ---
        dcc.Location(id="url-demo", refresh=False),
        dcc.Store(id="store-modo-full", data=False),
        dcc.Interval(id="interval-demo", interval=1000, n_intervals=0, disabled=False),
        html.Div(
            id="badge-demo",
            children="DEMO · 50 s",
            style={
                "display": "block",
                "position": "fixed",
                "top": "12px",
                "right": "12px",
                "zIndex": 99990,
                "background": "rgba(13,27,46,0.92)",
                "border": "1px solid rgba(212,175,55,0.55)",
                "color": GOLD_LIGHT,
                "fontSize": "12px",
                "fontWeight": "700",
                "padding": "6px 14px",
                "borderRadius": "20px",
                "letterSpacing": "0.5px",
            },
        ),
        html.Div(
            id="overlay-demo-fim",
            style={
                "display": "none",
                "position": "fixed",
                "inset": 0,
                "background": "rgba(7,16,30,0.94)",
                "zIndex": 99999,
                "alignItems": "center",
                "justifyContent": "center",
                "flexDirection": "column",
                "textAlign": "center",
                "padding": "24px",
            },
            children=[
                html.Div(
                    style={
                        "maxWidth": "480px",
                        "border": f"1.5px solid {GOLD}",
                        "borderRadius": "14px",
                        "background": CARD_BG,
                        "padding": "36px 32px",
                        "boxShadow": "0 0 28px rgba(212,175,55,0.15)",
                    },
                    children=[
                        html.Div(
                            "SESSÃO DE DEMONSTRAÇÃO ENCERRADA",
                            style={
                                "color": GOLD,
                                "fontWeight": "800",
                                "fontSize": "12px",
                                "letterSpacing": "1.5px",
                                "marginBottom": "14px",
                            },
                        ),
                        html.H2(
                            "Limite de 50 segundos atingido",
                            style={"color": TEXT_WHITE, "margin": "0 0 12px", "fontSize": "22px"},
                        ),
                        html.P(
                            "Esta é uma demonstração gratuita do ProcessGas Health Monitor. "
                            "Para acesso operacional completo, solicite liberação em AnalyzersExperts.com.",
                            style={
                                "color": TEXT_GRAY,
                                "fontSize": "15px",
                                "lineHeight": "1.55",
                                "margin": "0 0 22px",
                            },
                        ),
                        html.A(
                            "Voltar à página do monitor",
                            href=URL_RETORNO,
                            id="btn-voltar-site",
                            style={
                                "display": "inline-block",
                                "background": GOLD,
                                "color": NAVY_DARK,
                                "fontWeight": "800",
                                "padding": "12px 28px",
                                "borderRadius": "28px",
                                "textDecoration": "none",
                                "fontSize": "14px",
                            },
                        ),
                    ],
                )
            ],
        ),
    ],
)


# ---- Callback do radar / matriz ----
@app.callback(
    Output("radar-graph", "figure"),
    Output("matriz-desvios", "data"),
    Input("btn-atualizar", "n_clicks"),
    State("slider-arraste", "value"),
    State("slider-valvulas", "value"),
    State("slider-vent", "value"),
    State("slider-termica", "value"),
    prevent_initial_call=False,
)
def atualizar_saude(_n, arraste, valvulas, vent, termica):
    arraste = float(arraste if arraste is not None else 92.8)
    valvulas = float(valvulas if valvulas is not None else 90)
    vent = float(vent if vent is not None else 72)
    termica = float(termica if termica is not None else 99)
    # TNN derivado levemente da estabilidade térmica (didático)
    tnn = max(90.0, min(100.0, 0.55 * termica + 0.45 * 100))

    fig = _build_radar([arraste, valvulas, vent, termica, tnn])
    data = _table_data(
        {
            "Pressão Arraste": arraste,
            "Pressão Válvulas": valvulas,
            "Fluxo Measure Vent": vent,
            "Estabilidade Térmica": termica,
        }
    )
    return fig, data


# ---- Demo 50 s / full access ----
@app.callback(
    Output("store-modo-full", "data"),
    Output("interval-demo", "disabled"),
    Output("badge-demo", "style"),
    Input("url-demo", "search"),
)
def detectar_modo_demo(search):
    search = search or ""
    is_full = f"full={TOKEN_FULL}" in search
    badge = {
        "display": "none" if is_full else "block",
        "position": "fixed",
        "top": "12px",
        "right": "12px",
        "zIndex": 99990,
        "background": "rgba(13,27,46,0.92)",
        "border": "1px solid rgba(212,175,55,0.55)",
        "color": GOLD_LIGHT,
        "fontSize": "12px",
        "fontWeight": "700",
        "padding": "6px 14px",
        "borderRadius": "20px",
        "letterSpacing": "0.5px",
    }
    return is_full, is_full, badge


app.clientside_callback(
    """
    function(n, isFull) {
        if (isFull) { return "ACESSO COMPLETO"; }
        var rest = Math.max(0, 50 - (n || 0));
        return "DEMO · " + rest + " s";
    }
    """,
    Output("badge-demo", "children"),
    Input("interval-demo", "n_intervals"),
    State("store-modo-full", "data"),
)

app.clientside_callback(
    """
    function(n, isFull) {
        var base = {
            "position": "fixed",
            "inset": "0",
            "background": "rgba(7,16,30,0.94)",
            "zIndex": "99999",
            "alignItems": "center",
            "justifyContent": "center",
            "flexDirection": "column",
            "fontFamily": "Segoe UI, Arial, sans-serif",
            "textAlign": "center",
            "padding": "24px"
        };
        if (isFull) {
            base["display"] = "none";
            return base;
        }
        if ((n || 0) >= 50) {
            setTimeout(function() {
                window.location.href = "https://analyzersexperts.com/monitor-de-saude-do-cromatografo/";
            }, 4000);
            base["display"] = "flex";
            return base;
        }
        base["display"] = "none";
        return base;
    }
    """,
    Output("overlay-demo-fim", "style"),
    Input("interval-demo", "n_intervals"),
    State("store-modo-full", "data"),
)

server = app.server

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=True)
