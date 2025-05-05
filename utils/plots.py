import pandas as pd
import matplotlib.pyplot as plt


def graficado_matplotlib(esolmet, columns=None):
    fig, ax = plt.subplots()
    columnas = columns or [col for col in esolmet.columns if col != 'TIMESTAMP']
    for columna in columnas:
        ax.scatter(esolmet['TIMESTAMP'], esolmet[columna], label=columna, s=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.2)
    ax.legend()
    return fig


def graficado_nulos(df):
    na_counts = df.isna().sum()
    na_counts = na_counts[na_counts > 0]

    fig_width = max(14, 0.6 * len(na_counts))
    fig, ax = plt.subplots(figsize=(fig_width, 8))
    na_counts.plot(kind='bar', color='tomato', ax=ax)
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    return fig
