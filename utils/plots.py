import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import missingno as msno


def graficado_plotly(esolmet, columns=None):
    # Copiar y normalizar datos
    df = esolmet.copy()
    # Convertir TIMESTAMP con coerción de errores
    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], errors='coerce')
    # Eliminar filas donde TIMESTAMP sea NaT
    df = df.dropna(subset=['TIMESTAMP'])
    # Formatear TIMESTAMP a string
    df['TIMESTAMP'] = df['TIMESTAMP'].dt.strftime("%Y-%m-%d %H:%M:%S")
    # Coercionar todas las columnas numéricas
    for col in df.columns:
        if col != 'TIMESTAMP':
            df[col] = pd.to_numeric(df[col], errors='coerce')

    columnas = columns or [col for col in df.columns if col != 'TIMESTAMP']
    fig = go.Figure()
    for columna in columnas:
        # Filtrar filas donde la columna no sea NaN
        valid_data = df.dropna(subset=[columna])
        x_vals = valid_data['TIMESTAMP'].tolist()
        y_vals = valid_data[columna].tolist()
        fig.add_trace(go.Scattergl(
            x=x_vals,
            y=y_vals,
            mode='markers',
            name=columna,
            marker=dict(size=5),
        ))
    fig.update_xaxes(
        tickformat="%Y-%m-%d %H:%M",
        tickmode="auto",
    )
    fig.update_layout(
        hovermode='x unified',
        showlegend=True,
        xaxis_title="TIMESTAMP",
        yaxis_title="Valores",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
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
