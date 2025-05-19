import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import missingno as msno
from utils.config import load_settings


# cargar configuración y definir variables permitidas para gráficas
variables, latitude, longitude, gmt, name = load_settings()
ALLOWED_VARS = variables

def graficado_plotly(esolmet, columns=None):
    # Copiar y normalizar datos
    df = esolmet.copy()
    # Filtrar solo columnas permitidas
    keep = ['TIMESTAMP'] + [c for c in ALLOWED_VARS if c in df.columns]
    df = df.loc[:, keep]

    # Convertir TIMESTAMP con coerción de errores
    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], errors='coerce')
    df = df.dropna(subset=['TIMESTAMP'])
    df['TIMESTAMP'] = df['TIMESTAMP'].dt.strftime("%Y-%m-%d %H:%M:%S")
    for col in df.columns:
        if col != 'TIMESTAMP':
            df[col] = pd.to_numeric(df[col], errors='coerce')

    columnas = columns or [col for col in df.columns if col != 'TIMESTAMP']
    fig = go.Figure()
    for columna in columnas:
        valid_data = df.dropna(subset=[columna])
        fig.add_trace(go.Scattergl(
            x=valid_data['TIMESTAMP'].tolist(),
            y=valid_data[columna].tolist(),
            mode='markers', name=columna, marker=dict(size=5)
        ))
    fig.update_xaxes(tickformat="%Y-%m-%d %H:%M", tickmode="auto")
    fig.update_layout(
        hovermode='x unified', showlegend=True,
        xaxis_title="TIMESTAMP", yaxis_title="Valores",
        xaxis=dict(showgrid=True), yaxis=dict(showgrid=True)
    )
    return fig


def graficado_nulos(df):
    na_counts = df.isna().sum()
    cols_with_na = na_counts[na_counts > 0].index.tolist()
    if not cols_with_na:
        fig = plt.figure(figsize=(8, 4))
        fig.suptitle("Sin valores nulos")
        return fig

    fig_width = max(14, 0.6 * len(cols_with_na))
    fig_height = 8

    ax = msno.bar(
        df[cols_with_na],
        figsize=(fig_width, fig_height),
        fontsize=10,
        sort="descending"
    )
    fig = ax.get_figure()

    plt.setp(ax.get_xticklabels(), ha="right")
    ax.grid(axis="y", alpha=0.3)

    ax.set_ylabel("Proporción")

    if len(fig.axes) > 1:
        fig.axes[1].set_ylabel("Conteo")

    return fig