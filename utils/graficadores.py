import matplotlib.pyplot as plt

def graficado_Is_matplotlib(esolmet, fechas):
    fig, ax = plt.subplots()
    ax.plot(esolmet.TIMESTAMP, esolmet['I_glo_Avg'])
    ax.plot(esolmet.TIMESTAMP, esolmet['I_dir_Avg'])
    ax.plot(esolmet.TIMESTAMP, esolmet['I_dif_Avg'])
    ax.plot(esolmet.TIMESTAMP, esolmet['I_uv_Avg'])
    ax.set_xlim(fechas[0], fechas[1])
    return fig
