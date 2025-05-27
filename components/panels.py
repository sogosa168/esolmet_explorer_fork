from shiny import ui
from shinywidgets import output_widget
import faicons as fa  


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
    return ui.nav_panel(
        "Eolica",
        "Inserta aquí la Produccion eólica"
    )
def panel_documentacion():
    return ui.nav_panel(
        "Documentación",
        "Inserta aquí la documentación"
    )


def panel_subir_archivo():
    return ui.nav_panel(
        "Subir archivo",
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
                ui.output_data_frame("df_radiacion"),
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
                ui.div(
                    ui.input_action_button(
                        "btn_load",
                        "Cargar en base de datos",
                        icon=fa.icon_svg("file-export"),
                        class_="btn btn-outline-success ms-2"
                    ),
                    ui.input_action_button(
                        "btn_delete",
                        "Eliminar base de datos",
                        icon=fa.icon_svg("trash"),
                        class_="btn btn-outline-danger ms-2"
                    ),
                    class_="d-flex ms-auto"
                ),
                class_="d-flex align-items-center"
            ),
            ui.output_ui("load_status"),
            ui.output_ui("delete_status"),
            ui.output_data_frame("df_loaded"),
        ),
    )