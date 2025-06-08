from shiny import ui
from shinywidgets import output_widget
import faicons as fa  
from utils.data_processing import load_esolmet_data
import pandas as pd
import duckdb

conn = duckdb.connect(database="esolmet.db")

df_lect = conn.execute(
    "SELECT fecha, variable, valor FROM lecturas"
).df()

esolmet = df_lect.pivot(index="fecha", columns="variable", values="valor")
esolmet.index = pd.to_datetime(esolmet.index)
esolmet = esolmet.sort_index()



def panel_estadistica():
    return ui.nav_panel(
        "Estadística",
        "Aquí irá tu contenido estadístico"
    )

def panel_trayectoriasolar():
    return ui.nav_panel(
        "SunPath",
        "Inserta aquí la figura de sunpath"
    )

def panel_fotovoltaica():
    return ui.nav_panel(
        "FotoVoltaica",
        "Inserta aquí la Produccion solar"
    )

def panel_confort():
    return ui.nav_panel(
        "Confort térmico",
        "Inserta aquí todo  sobre confort"
    )


def panel_eolica():
    min_year = esolmet.index.year.min()# Calculamos maximos i minimos 
    max_year = esolmet.index.year.max()
    min_date = str(esolmet.index.min().date())
    max_date = str(esolmet.index.max().date())
    return ui.nav_panel(
        "Eólica",
        ui.navset_tab(
            ui.nav_panel(
                "Rosas de Viento",
                ui.h3(" "),
                ui.input_date_range(
                    "wind_period_range",
                    "Selecciona periodo:",
                    start=min_date, end=max_date,
                    min=min_date,   max=max_date
                ),
          ui.row(
            ui.column(
              6,
              ui.h4("Rosa diurna", style="text-align:center;"),
              output_widget("wind_rose_day")
            ),
            ui.column(
              6,
              ui.h4("Rosa nocturna", style="text-align:center;"),
              output_widget("wind_rose_night")
            ),
          ),

                # Rosa por periodo
                ui.h3("Rosas de viento promedio anual"),
                ui.input_date_range(
                    "wind_date_range",
                    "Selecciona periodo:",
                    start=min_date,  # fecha de inicio por defecto
                    end=max_date,    # fecha de fin por defecto
                    min=min_date,    # límite mínimo seleccionable
                    max=max_date     # límite máximo seleccionable
                ),
                output_widget("wind_rose_speed_period"),

                ui.h3("Rosa de viento promedio estacional"),
                ui.input_slider(
                    "season_year_range",
                    "Selecciona rango de años:",
                    min=min_year,
                    max=max_year,
                    value=(min_year, max_year),
                    step=1
                ),

                ui.div(
                    ui.div(ui.h4("Primavera"), output_widget("rose_spring")),
                    ui.div(ui.h4("Verano"),    output_widget("rose_summer")),
                    ui.div(ui.h4("Otoño"),     output_widget("rose_autumn")),
                    ui.div(ui.h4("Invierno"),  output_widget("rose_winter")),
                    style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;"
                ),
            ),

            ui.nav_panel(
                "Heatmaps velocidad",
                ui.h3("Velocidad de viento anual y estacional"),
                ui.input_date_range(
                    "heatmap_speed_range",
                    "Selecciona periodo:",
                    start=min_date, end=max_date,
                    min=min_date,   max=max_date
                ),
                ui.row(
                    ui.column(
                    12,
                    ui.h4("Heatmap anual"),
                    output_widget("heatmap_wind_annual")
                    )
                ),

                ui.row(
                    ui.column(6,
                        ui.h4("Primavera", style="text-align:center;"),
                        output_widget("heatmap_wind_primavera")
                    ),
                    ui.column(6,
                        ui.h4("Verano", style="text-align:center;"),
                        output_widget("heatmap_wind_verano")
                    ),
                ),
                ui.row(
                    ui.column(6,
                        ui.h4("Otoño", style="text-align:center;"),
                        output_widget("heatmap_wind_otono")
                    ),
                    ui.column(6,
                        ui.h4("Invierno", style="text-align:center;"),
                        output_widget("heatmap_wind_invierno")
                    ),
                ),
            ),

                        # NUEVA SUB-PESTAÑA
            ui.nav_panel(
                "Energía eólica",
                ui.h3("Generación de energía eólica"),
                ui.row(
                    ui.column(4,

                        ui.input_select("turbine_model",
                            "Selecciona modelo de turbina:",

                            choices=[
                                "GE 1.5MWsle",
                                "Nordex S77 1.5MW",
                                "Fuhrlander FL 1.5MW",
                                "BergeyExcel 8.9kW-7 (Distributed)",
                                "NREL2019COE 100kW-27.6(Distributed)",
                                "VestasV29 225kW-29(Distributed)",
                                "NREL2019COE 20kW-12.4(Distributed)",
                                "NREL2017COE 2.3MW-113",
                                "VestasV47 660kW-47",
                                "Ampair600 0.73kW-1.7"
                            ]
                        ),
                        ui.input_action_button("run_sim", "Ejecutar simulación"),
                        # 2) Botón para “correr” la simulación con PySAM


                        # 3) Salidas de texto donde mostraremos los resultados
                        
                        ui.output_table("prod_results_table"),
                    ),
                    ui.column(8,
                        ui.h5("Energía mensual (kWh)"),
                        output_widget("prod_monthly_plot"),
                    ),
                ),
                ui.row(
                    ui.column(3,
                        ui.h5("Primavera"),
                        ui.output_ui("seasonal_primavera")
                    ),
                    ui.column(3,
                        ui.h5("Verano"),
                        ui.output_ui("seasonal_verano")
                    ),
                    ui.column(3,
                        ui.h5("Otoño"),
                        ui.output_ui("seasonal_otono")
                    ),
                    ui.column(3,
                        ui.h5("Invierno"),
                        ui.output_ui("seasonal_invierno")
                    ),
                ),
                    ui.row(
                        ui.column(
                            12,
                            ui.h5("Heatmap: Generación horaria anual"),
                            output_widget("prod_heatmap")
                        ),
                    ),
            ),
        ),
    )
 
def panel_documentacion():
    return ui.nav_panel(
        "Documentación",
        "Inserta aquí la documentación"
    )


def panel_subir_archivo():
    return ui.nav_panel(
        "Paso 1",
        ui.layout_columns(
            ui.card(
                ui.card_header("Archivo"),
                ui.input_file(
                    "archivo",
                    "Selecciona el archivo CSV",
                    button_label="Examinar",
                    placeholder="Sin archivo",
                    accept='.csv'
                ),
                ui.output_ui("upload_status"),
                ui.output_table("table_tests"),
            ),
            ui.card(
                ui.card_header("Gráfico"),
                output_widget("plot_plotly"),
                full_screen=True,
            ),
            col_widths=[3, 9],
        ),
    )


def panel_pruebas_archivo():
    return ui.nav_panel(
        "Paso 2",
        ui.layout_columns(
            ui.card(
                ui.card_header("Inconsistencias de radiación"),
                ui.output_data_frame("df_radiacion"),
            ),
            ui.card(
                ui.card_header("Gráfico de radiación"),
                output_widget("plot_radiacion"),
                full_screen=True,
            ),
            col_widths=[5, 7],
        ),
        
    )


def panel_cargar_datos():
    return ui.nav_panel(
        "Paso 3",
        ui.card(
            ui.card_header("Datos preparados"),
            ui.card_body(
                ui.layout_column_wrap(
                    ui.div(
                        ui.p("Selecciona una acción para proceder."),
                        ui.output_ui("load_status"),
                        ui.output_ui("delete_status"),
                        class_="flex-grow-1"
                    ),
                    ui.div(
                        ui.input_action_button(
                            "btn_load",
                            "Cargar en base de datos",
                            icon=fa.icon_svg("file-export"),
                            class_="btn btn-outline-success w-100 mb-2"
                        ),
                        ui.input_action_button(
                            "btn_delete",
                            "Eliminar base de datos",
                            icon=fa.icon_svg("trash"),
                            class_="btn btn-outline-danger w-100"
                        ),
                        class_="d-flex flex-column align-items-end",
                        style="min-width: 200px;"
                    ),
                    class_="d-flex gap-3 align-items-start"
                )
            )
        )
    )