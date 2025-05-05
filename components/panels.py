from shiny import ui


def panel_documentacion():
    return ui.nav_panel(
        "Documentación",
        ui.h4("Descripción de la app"),
        ui.p(
            "Esta aplicación web permite cargar, visualizar y procesar archivos CSV con datos de ESOLMET. "
            "Los usuarios pueden realizar las siguientes acciones:"
        ),
        ui.tags.ul(
            ui.tags.li(
                ui.tags.strong("Subir datos:"),
                " cargar un archivo CSV y visualizar las columnas seleccionadas en gráficos."
            ),
            ui.tags.li(
                ui.tags.strong("Pruebas de integridad de los datos:"),
                " verificar aspectos como el tipo de archivo, la codificación, la existencia de valores nulos, duplicados "
                "y el tipo de datos de cada columna."
            ),
            ui.tags.li(
                ui.tags.strong("Cargar datos a una base de datos:"),
                " los datos procesados se pueden cargar en una base de datos DuckDB, con un progreso visible durante "
                "el proceso de carga."
            )
        ),
        ui.h4("Guía rápida para usar la app"),
        ui.tags.ol(
            ui.tags.li(
                ui.tags.strong("Subir un archivo CSV:"),
                ui.p(
                    "En el panel \"Subir datos\", haz clic en Selecciona el archivo CSV para cargar un archivo desde "
                    "tu computadora."
                )
            ),
            ui.tags.li(
                ui.tags.strong("Seleccionar columnas:"),
                ui.p(
                    "Una vez cargado, selecciona las columnas que deseas graficar desde el menú desplegable Selecciona "
                    "las columnas."
                )
            ),
            ui.tags.li(
                ui.tags.strong("Visualizar gráficos:"),
                ui.p(
                    "Los gráficos de las columnas seleccionadas aparecerán de manera automática."
                )
            ),
            ui.tags.li(
                ui.tags.strong("Verificar la integridad de los datos:"),
                ui.p(
                    "En el panel \"Pruebas\", se mostrarán los resultados de diversas pruebas de calidad de los datos, "
                    "como:"
                ),
                ui.tags.ul(
                    ui.tags.li("Si el archivo es un CSV válido."),
                    ui.tags.li("Si la codificación es UTF-8."),
                    ui.tags.li("La presencia de valores nulos o duplicados."),
                    ui.tags.li("La consistencia de los tipos de datos."),
                    ui.tags.li("Además, se mostrarán estadísticas sobre los tipos de datos de cada columna.")
                )
            ),
            ui.tags.li(
                ui.tags.strong("Cargar datos en la base de datos:"),
                ui.p(
                    "En el panel \"Cargar datos\", haz clic en el botón Cargar en base de datos para iniciar el proceso de carga. "
                    "Una barra de progreso mostrará el avance de la carga, que se realizará en bloques de datos para evitar "
                    "sobrecargar el sistema."
                )
            ),
            ui.tags.li(
                ui.tags.strong("Visualización de valores faltantes:"),
                ui.p(
                    "En el panel \"Pruebas\", también podrás ver un gráfico que indica las columnas con valores faltantes "
                    "en el archivo CSV."
                )
            )
        )
    )


def panel_subir_datos():
    return ui.nav_panel(
        "Subir datos",
        ui.h4("Visualización de datos"),
        ui.layout_columns( 
            #Input para seleccionar el archivo CSV
            ui.input_file(
                "archivo", 
                "Selecciona el archivo CSV", 
                accept='.csv'
            ),
            # Input para seleccionar columnas a graficar
            ui.input_selectize(
                "col_selector",
                "Selecciona las columnas",
                {}, 
                multiple=True,
            ),
        ),
        ui.output_plot('plot_matplotlib')  
    )


def panel_pruebas():
    return ui.nav_panel(
        "Pruebas",
        ui.h4("Integridad de los datos"),
        ui.layout_columns(
            # Tabla de resultados de pruebas
            ui.column(
                6,
                ui.h5("Resultados"),
                ui.output_table("table_tests"),
            ),
            # Tabla de tipos
            ui.column(
                6,
                ui.h5("Columnas y tipos"),
                ui.output_data_frame("df_types"),
            ),
            # Plot de valores faltantes
            ui.column(
                8,
                ui.h5("Valores faltantes"),
                ui.output_plot("plot_missing"),
            ),
        ),
    )


def panel_cargar_datos():
    return ui.nav_panel(
        "Cargar datos",
        ui.h4("Datos preparados"),
        ui.input_action_button("btn_load", "Cargar en base de datos"),
        ui.output_ui("load_status"),
        ui.output_data_frame("df_loaded")
    )

