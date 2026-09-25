import dash
from dash import html, dcc, dash_table, Input, Output, State
import plotly.graph_objs as go

app = dash.Dash(__name__)

# Paleta Oficial Analyzers Experts (Manual v2.0)
NAVY_DARK = "#0D1B2A"
NAVY_MID = "#16293D"
CARD_BG = "#07101E"
GOLD = "#D4AF37"
TEXT_WHITE = "#FFFFFF"
TEXT_GRAY = "#CBD5E1"

app.layout = html.Div(
    style={"backgroundColor": NAVY_DARK, "color": TEXT_WHITE, "minHeight": "100vh", "padding": "20px", "fontFamily": "inherit"},
    children=[
        # Cabeçalho
        html.H2("ProcessGas Health Monitor — Radar Multivariável de Saúde", style={"color": GOLD, "marginBottom": "15px"}),
        
        # Painel de Entradas do Operador
        html.Div(
            style={"background": CARD_BG, "border": f"1.5px solid {GOLD}", "borderRadius": "12px", "padding": "20px", "marginBottom": "20px", "boxShadow": "0 10px 20px rgba(0,0,0,0.5)"},
            children=[
                html.H4("🎛️ Ajuste de Parâmetros de Campo", style={"color": GOLD, "marginBottom": "15px"}),
                html.Div(
                    style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
                    children=[
                        html.Div([
                            html.Label("Pressão Arraste (% do Nominal):", style={"color": TEXT_GRAY, "fontSize": "13px"}),
                            dcc.Input(id="input-arraste-p", type="number", value=92.8, min=0, max=100, step=0.5, style={"width": "100%", "padding": "8px", "background": NAVY_MID, "color": TEXT_WHITE, "border": f"1px solid {GOLD}", "borderRadius": "6px"})
                        ], style={"flex": "1", "minWidth": "200px"}),
                        
                        html.Div([
                            html.Label("Pressão Válvulas (% do Nominal):", style={"color": TEXT_GRAY, "fontSize": "13px"}),
                            dcc.Input(id="input-valvulas-p", type="number", value=90.0, min=0, max=100, step=0.5, style={"width": "100%", "padding": "8px", "background": NAVY_MID, "color": TEXT_WHITE, "border": f"1px solid {GOLD}", "borderRadius": "6px"})
                        ], style={"flex": "1", "minWidth": "200px"}),
                        
                        html.Div([
                            html.Label("Fluxo Measure Vent (% do Nominal):", style={"color": TEXT_GRAY, "fontSize": "13px"}),
                            dcc.Input(id="input-vent-p", type="number", value=72.0, min=0, max=100, step=0.5, style={"width": "100%", "padding": "8px", "background": NAVY_MID, "color": TEXT_WHITE, "border": f"1px solid {GOLD}", "borderRadius": "6px"})
                        ], style={"flex": "1", "minWidth": "200px"}),
                        
                        html.Div([
                            html.Label("Estabilidade Térmica (%):", style={"color": TEXT_GRAY, "fontSize": "13px"}),
                            dcc.Input(id="input-term-p", type="number", value=99.0, min=0, max=100, step=0.5, style={"width": "100%", "padding": "8px", "background": NAVY_MID, "color": TEXT_WHITE, "border": f"1px solid {GOLD}", "borderRadius": "6px"})
                        ], style={"flex": "1", "minWidth": "200px"})
                    ]
                ),
                html.Br(),
                html.Button("Atualizar Índice de Saúde Global", id="btn-radar", n_clicks=0, style={"background": GOLD, "color": NAVY_DARK, "fontWeight": "bold", "padding": "10px 20px", "border": "none", "borderRadius": "6px", "cursor": "pointer"})
            ]
        ),
        
        # Grid Principal: Gráfico de Radar + Tabela Diagnóstica
        html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap"},
            children=[
                # Coluna Esquerda: Gráfico de Radar
                html.Div(
                    style={"flex": "1", "minWidth": "400px", "background": CARD_BG, "border": f"1.5px solid {GOLD}", "borderRadius": "12px", "padding": "20px"},
                    children=[
                        html.H4("🕸️ Índice de Saúde Multivariável (Radar)", style={"color": GOLD, "marginBottom": "10px"}),
                        dcc.Graph(id="radar-chart")
                    ]
                ),
                
                # Coluna Direita: Tabela de Estado
                html.Div(
                    style={"flex": "1", "minWidth": "400px", "background": CARD_BG, "border": f"1.5px solid {GOLD}", "borderRadius": "12px", "padding": "20px"},
                    children=[
                        html.H4("📊 Matriz de Desvios Analíticos", style={"color": GOLD, "marginBottom": "15px"}),
                        html.Div(id="tabela-radar-container")
                    ]
                )
            ]
        )
    ]
)

# Callback para recalcular o radar e a tabela
@app.callback(
    [Output("radar-chart", "figure"),
     Output("tabela-radar-container", "children")],
    [Input("btn-radar", "n_clicks")],
    [State("input-arraste-p", "value"),
     State("input-valvulas-p", "value"),
     State("input-vent-p", "value"),
     State("input-term-p", "value")]
)
def atualizar_radar(n_clicks, p_arraste, p_valvulas, p_vent, p_term):
    
    categorias = ['Pressão Arraste', 'Pressão Válvulas', 'Fluxo Measure Vent', 'Estabilidade Térmica', 'Integridade TNN']
    valores_atuais = [p_arraste, p_valvulas, p_vent, p_term, 98.5]
    valores_ideais = [100, 100, 100, 100, 100]

    # Construção do Gráfico de Radar (Polar)
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=valores_ideais,
        theta=categorias,
        fill='toself',
        name='Nominal Ideal (100%)',
        line=dict(color='#3498DB', width=2)
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=valores_atuais,
        theta=categorias,
        fill='toself',
        name='Estado Atual de Campo',
        line=dict(color=GOLD, width=3),
        fillcolor='rgba(212, 175, 55, 0.3)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color=TEXT_GRAY),
            bgcolor=NAVY_MID
        ),
        paper_bgcolor=CARD_BG,
        font=dict(color=TEXT_GRAY),
        legend=dict(orientation="h", yanchor="bottom", y=1.12, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    tabela_dados = [
        {"parametro": "Pressão Arraste", "score": f"{p_arraste}%", "estado": "NORMAL" if p_arraste >= 90 else "DESVIO"},
        {"parametro": "Pressão Válvulas", "score": f"{p_valvulas}%", "estado": "NORMAL" if p_valvulas >= 90 else "ALERTA"},
        {"parametro": "Fluxo Measure Vent", "score": f"{p_vent}%", "estado": "NORMAL" if p_vent >= 80 else "CRÍTICO"},
        {"parametro": "Estabilidade Térmica", "score": f"{p_term}%", "estado": "NORMAL" if p_term >= 98 else "ATENÇÃO"}
    ]

    tabela_html = dash_table.DataTable(
        data=tabela_dados,
        columns=[
            {"name": "Subsistema Analítico", "id": "parametro"},
            {"name": "Índice de Saúde", "id": "score"},
            {"name": "Estado", "id": "estado"}
        ],
        style_header={"backgroundColor": NAVY_MID, "color": GOLD, "fontWeight": "bold", "border": f"1px solid {GOLD}"},
        style_cell={"backgroundColor": CARD_BG, "color": TEXT_GRAY, "border": f"1px solid {NAVY_MID}", "padding": "10px", "textAlign": "left"},
        style_data_conditional=[
            {"if": {"filter_query": '{estado} = "CRÍTICO"'}, "backgroundColor": "#512E5F", "color": "#F1948A", "fontWeight": "bold"},
            {"if": {"filter_query": '{estado} = "ALERTA"'}, "backgroundColor": "#7D6608", "color": "#F9E79F"},
            {"if": {"filter_query": '{estado} = "DESVIO"'}, "backgroundColor": "#7D6608", "color": "#F9E79F"}
        ]
    )

    return fig, tabela_html
    
server = app.server

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=True)