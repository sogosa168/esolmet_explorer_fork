from shiny import ui
from shinywidgets import output_widget
import faicons as fa  


def panel_subir_archivo():
    return ui.nav_panel(
        "Subir archivo",
        # sección de carga y visualización de datos
        ui.layout_columns(
            ui.card(
                ui.card_header("Archivo"),
                ui.input_file(
                    "archivo",
                    "Selecciona el archivo CSV",
                    accept='.csv'
                ),
                ui.output_table("table_tests"),
            ),
            ui.card(
                ui.card_header("Gráfico"),
                output_widget("plot_plotly"),
                full_screen=True,
            ),
            col_widths=[3, 9],
        ),

        # Sección de pruebas de integridad de datos
        ui.layout_columns(
            ui.card(
                ui.card_header("Columnas y tipos"),
                ui.output_data_frame("df_types"),
            ),
            ui.card(
                ui.card_header("Valores faltantes"),
                ui.output_plot("plot_missing"),
            ),
        col_widths=[3, 9],
        ),
        
        ui.layout_columns(
            ui.card(
                ui.card_header("Ubicación de NaN"),
                ui.output_data_frame("df_nans"),
            ),
            ui.card(
                ui.card_header("Ubicación de NaT"),
                ui.output_data_frame("df_nats"),
            ),
            ui.card(
                ui.card_header("Inconsistencias de radiación"),
                output_widget("plot_radiacion"),
            ),
        col_widths=[2, 2, 8],
        ),
    )


def panel_cargar_datos():
    return ui.nav_panel(
        "Exportar datos",
        ui.card(
            ui.card_header(
                ui.span("Datos preparados"),
                ui.input_action_button(
                    "btn_load", 
                    "Cargar en base de datos",
                    icon=fa.icon_svg("file-export")
                ),
                class_="d-flex justify-content-between align-items-center"
            ),
            ui.output_ui("load_status"),
            ui.output_data_frame("df_loaded"),
        ),
    )