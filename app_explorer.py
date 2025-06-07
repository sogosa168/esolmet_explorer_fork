from shiny import App, ui, render, reactive
import shinyswatch  
from components.explorador import panel_explorador, panel_estadistica
from components.panels import panel_documentacion, panel_trayectoriasolar, panel_fotovoltaica, panel_eolica, panel_confort
from utils.data_processing import load_esolmet_data
from utils.graficadores import graficado_Is_matplotlib
from utils.config import load_settings
from shinywidgets import render_widget
from shiny import ui
import pandas as pd 
from utils.wind_rose import  create_wind_rose_period_plotly, create_wind_rose_by_speed_period,create_seasonal_wind_roses_by_speed_plotly,  run_wind_simulation, create_seasonal_generation_figures, create_generation_heatmap,create_monthly_energy_figure, create_wind_rose_by_speed_day,create_wind_rose_by_speed_night, create_typical_wind_heatmap,create_seasonal_wind_heatmaps
import duckdb
import PySAM.Windpower as wp
import json
import plotly.graph_objects as go


# importamos
variables, latitude, longitude, gmt, name, alias, \
    wind_speed_height, air_temperature_height, air_pressure_height, \
    site_id, data_tz = load_settings()
conn = duckdb.connect(database="esolmet.db")

# Leemos la tabla 'lecturas' y hacemos el df
df_lect = conn.execute(
    "SELECT fecha, variable, valor FROM lecturas"
).df()

# Pivotamos para obtener el DataFrame ancho índice = fecha, columnas = variable
esolmet = df_lect.pivot(index="fecha", columns="variable", values="valor")
esolmet.index = pd.to_datetime(esolmet.index)
esolmet = esolmet.sort_index()
print(">>> Columnas en esolmet:", list(esolmet.columns))



app_ui = ui.page_fillable(
    ui.navset_card_tab( 
        ui.nav_panel(
            "ESOLMET",
            ui.navset_card_tab(
                panel_explorador(),
                panel_estadistica(),
                id="esolmet_subtabs"
            )
        ),
        ui.nav_panel(
            'HERRAMIENTAS',
            ui.navset_card_tab(
                panel_trayectoriasolar(),
                panel_fotovoltaica(),
                panel_eolica(),
                panel_confort(),
                id="herramientas"
            )
        ),
    ),
    theme=shinyswatch.theme.spacelab
)


def server(input, output, session):

    @render.plot(alt='Irradiancia')
    def plot_matplotlib():
        return graficado_Is_matplotlib( input.fechas())
    @render_widget
    def wind_rose_period():
        start_date, end_date = input.wind_date_range()
        return create_wind_rose_period_plotly(
            esolmet,
            dir_col='WindDir',
            start=start_date,
            end=end_date
        )

    @render_widget
    def wind_rose_day():

        return create_wind_rose_by_speed_day(
            esolmet,
            dir_col="WindDir",
            speed_col="WS_ms_Avg",
            dir_bins=16,
            speed_bins=None
        )


    @render_widget
    def wind_rose_night():
        return create_wind_rose_by_speed_night(
            esolmet,
            dir_col="WindDir",
            speed_col="WS_ms_Avg",
            dir_bins=16,
            speed_bins=None
        )


    @render_widget
    def wind_rose_speed_period():
        start_date, end_date = input.wind_date_range()
        return create_wind_rose_by_speed_period(
            esolmet, dir_col='WindDir', speed_col='WS_ms_Avg',
            start=start_date, end=end_date
        )

    @render_widget
    def rose_spring():
        start_year, end_year = input.season_year_range()
        df = esolmet.loc[f"{start_year}-01-01": f"{end_year}-12-31"]
        figs = create_seasonal_wind_roses_by_speed_plotly(df)
        return figs["Primavera"]

    @render_widget
    def rose_summer():
        start_year, end_year = input.season_year_range()
        df = esolmet.loc[f"{start_year}-01-01": f"{end_year}-12-31"]
        figs = create_seasonal_wind_roses_by_speed_plotly(df)
        return figs["Verano"]

    @render_widget
    def rose_autumn():
        start_year, end_year = input.season_year_range()
        df = esolmet.loc[f"{start_year}-01-01": f"{end_year}-12-31"]
        figs = create_seasonal_wind_roses_by_speed_plotly(df)
        return figs["Otoño"]

    @render_widget
    def rose_winter():
        start_year, end_year = input.season_year_range()
        df = esolmet.loc[f"{start_year}-01-01": f"{end_year}-12-31"]
        figs = create_seasonal_wind_roses_by_speed_plotly(df)
        return figs["Invierno"]
    
    @output
    @render_widget
    def heatmap_wind_annual():
        if esolmet is None or esolmet.empty:
            return None

        return create_typical_wind_heatmap(esolmet, speed_col="WS_ms_Avg")

    @output
    @render_widget
    def heatmap_wind_primavera():
        figs = create_seasonal_wind_heatmaps(esolmet, speed_col="WS_ms_Avg")
        return figs["Primavera"]

    @output
    @render_widget
    def heatmap_wind_verano():
        figs = create_seasonal_wind_heatmaps(esolmet, speed_col="WS_ms_Avg")
        return figs["Verano"]

    @output
    @render_widget
    def heatmap_wind_otono():
        figs = create_seasonal_wind_heatmaps(esolmet, speed_col="WS_ms_Avg")
        return figs["Otoño"]

    @output
    @render_widget
    def heatmap_wind_invierno():
        figs = create_seasonal_wind_heatmaps(esolmet, speed_col="WS_ms_Avg")
        return figs["Invierno"]


    @reactive.Calc
    def sim_results():
        n_clicks = input.run_sim()
        if n_clicks is None or n_clicks == 0:
            return None

        with reactive.isolate():
            modelo = input.turbine_model()

        return run_wind_simulation(
            esolmet_df=esolmet,
            turbine_name=modelo,
            ini_path="configuration.ini",
            wind_turbine_file="wind-turbines2.json",
            wind_inputs_file="windpower-inputs.json",
            output_csv="sam_wind.csv",
        )

    @output
    @render.table
    def prod_results_table():
        results = sim_results()
        if results is None:
            return None

        if "error" in results:
            return pd.DataFrame([{"Resultado": "Error", "Valor": results["error"]}])

        ae = results.get("Energia Anual (kWh)", None)
        cf = results.get("Factor de Capacidad", None)
        wl = results.get("Perdida por estela (kWh)", None)
        tl = results.get("Perdida por turbina (kWh)", None)

        df = pd.DataFrame({
            "Parametro": [
                "Energía anual (kWh)",
                "Factor de capacidad",
                "Pérdida por estela (kWh)",
                "Pérdida por turbina (kWh)",
            ],
            "Valor": [
                ae if ae is not None else float("nan"),
                cf if cf is not None else float("nan"),
                wl if wl is not None else float("nan"),
                tl if tl is not None else float("nan"),
            ],
        })
        return df
    @output
    @render_widget
    def prod_monthly_plot():
        results = sim_results()
        if results is None:
            return None

        if "error" in results:
            return ui.tags.pre(results["error"])

        monthly = results.get("Monthly Energy")
        if monthly is None:
            return ui.tags.pre("No hay datos mensuales disponibles.")

        try:
            fig = create_monthly_energy_figure(monthly)
        except ValueError as e:
            return ui.tags.pre(str(e))

        return fig
    @output
    @render.ui
    def seasonal_primavera():
        results = sim_results()
        if results is None:
            return None

        if "error" in results:
            return ui.tags.pre(results["error"])

        gen_array = results.get("gen")
        if gen_array is None:
            return ui.tags.pre("No hay datos horarios de generación.")

        figures = create_seasonal_generation_figures(gen_array)
        return figures["Primavera"]


    @output
    @render.ui
    def seasonal_verano():
        results = sim_results()
        if results is None:
            return None

        if "error" in results:
            return ui.tags.pre(results["error"])

        gen_array = results.get("gen")
        if gen_array is None:
            return ui.tags.pre("No hay datos horarios de generación.")

        figures = create_seasonal_generation_figures(gen_array)
        return figures["Verano"]


    @output
    @render.ui
    def seasonal_otono():
        results = sim_results()
        if results is None:
            return None

        if "error" in results:
            return ui.tags.pre(results["error"])

        gen_array = results.get("gen")
        if gen_array is None:
            return ui.tags.pre("No hay datos horarios de generación.")

        figures = create_seasonal_generation_figures(gen_array)
        return figures["Otoño"]


    @output
    @render.ui
    def seasonal_invierno():
        results = sim_results()
        if results is None:
            return None

        if "error" in results:
            return ui.tags.pre(results["error"])

        gen_array = results.get("gen")
        if gen_array is None:
            return ui.tags.pre("No hay datos horarios de generación.")

        figures = create_seasonal_generation_figures(gen_array)
        return figures["Invierno"]


    @output
    @render_widget
    def prod_heatmap():
        results = sim_results()
        if results is None:
            return None

        if "error" in results:
            return ui.tags.pre(results["error"])

        gen_array = results.get("gen")
        if gen_array is None:
            return ui.tags.pre("No hay datos horarios de generación.")

        fig = create_generation_heatmap(gen_array)
        return fig
app = App(app_ui, server)
