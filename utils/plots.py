import matplotlib.pyplot as plt
import missingno as msno


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
    cols_with_na = na_counts[na_counts > 0].index.tolist()
    if not cols_with_na:
        fig = plt.figure(figsize=(8, 4))
        fig.suptitle("No missing values detected")
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

