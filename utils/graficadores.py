import matplotlib.pyplot as plt
import duckdb 
from windrose import WindroseAxes
from matplotlib.gridspec import GridSpec

from utils.config import load_settings


# Desestructuramos 
variables, latitude, longitude, gmt, name, alias_map, \
    site_id, data_tz, wind_speed_height, air_temperature_height, air_pressure_height \
    = load_settings()

con = duckdb.connect('esolmet.db')

def graficado_Is_matplotlib(fechas):
    query = f"""
    SELECT *
      FROM lecturas
     WHERE fecha >= TIMESTAMP '{fechas[0]}'
       AND fecha <= TIMESTAMP '{fechas[1]}'
     ORDER BY fecha
    """
    df = con.execute(query).fetchdf()
    df = df.pivot(index='fecha', columns='variable', values='valor')
    df = df.rename(columns=alias_map)


    fig = plt.figure()
    gs  = GridSpec(nrows=4, ncols=2,
                   width_ratios=[4, 1],
                   height_ratios=[1, 1, 1, 1],
                   figure=fig)

    ax_te   = fig.add_subplot(gs[0, 0])
    ax_hr   = fig.add_subplot(gs[1, 0], sharex=ax_te)
    ax_p    = fig.add_subplot(gs[2, 0], sharex=ax_te)
    ax_is   = fig.add_subplot(gs[3, 0], sharex=ax_te)
    ax_wind = fig.add_subplot(gs[:, 1], projection='windrose')

    ax_te.plot(df.index, df["tdb"], label="Te", color="k", alpha=0.8)
    ax_te.set_ylabel("Te [°C]")
    ax_te.legend(loc="upper left")

    ax_p.plot(df["p_atm"], label="p", alpha=0.8)
    ax_p.set_ylabel("P [–]")
    ax_p.legend(loc="upper left")

    ax_hr.plot(df["rh"], label="HR", alpha=0.8)
    ax_hr.set_ylim(0, 100)
    ax_hr.set_ylabel("HR [%]")
    ax_hr.legend(loc="upper left")

    for col in df.columns:
        if col.startswith("dni") or col.startswith("ghi") or col.startswith("dhi"):
            ax_is.plot(df.index, df[col], label=col)
    ax_is.set_ylabel("I [W/m²]")
    ax_is.legend(loc="upper left")

    ax_wind.bar(df["wd"], df["ws"],
                normed=True, opening=0.8,
                edgecolor="white")
    ax_wind.set_title("Rosa de Vientos")

    fig.autofmt_xdate()
    return fig
