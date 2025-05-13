from shiny.ui import modal_show, modal, modal_button
from htmltools import TagList, tags


# Función para mostrar el modal de documentación
def info_modal():
    modal_show(
        modal(
            # Título
            tags.strong(tags.h3("Documentación de ESOLMET Explorer")),
            # Descripción
            tags.p(
                "Esta aplicación web permite cargar, visualizar y procesar archivos CSV con datos de ESOLMET. "
                "Los usuarios pueden realizar las siguientes acciones:"
            ),
            tags.ul(
                tags.li(
                    tags.strong("Subir archivo:"),
                    " cargar un archivo CSV y visualizar las columnas seleccionadas en gráficos."
                ),
                tags.li(
                    tags.strong("Pruebas de integridad de los datos:"),
                    " verificar aspectos como el tipo de archivo, la codificación, la existencia de valores nulos, duplicados "
                    "y el tipo de datos de cada columna."
                ),
                tags.li(
                    tags.strong("Exportar datos a una base de datos:"),
                    " los datos procesados se pueden cargar en una base de datos DuckDB, con un progreso visible durante "
                    "el proceso de carga."
                )
            ),
            # Guía rápida
            tags.h4("Guía rápida para usar la app"),
            tags.ol(
                tags.li(
                    tags.strong("Subir un archivo CSV:"),
                    tags.p(
                        "En el panel \"Subir archivo\", haz clic en Selecciona el archivo CSV para cargar un archivo desde "
                        "tu computadora."
                    )
                ),
                tags.li(
                    tags.strong("Seleccionar columnas:"),
                    tags.p(
                        "Una vez cargado, selecciona las columnas que deseas graficar desde el menú desplegable Selecciona "
                        "las columnas."
                    )
                ),
                tags.li(
                    tags.strong("Visualizar gráficos:"),
                    tags.p(
                        "Los gráficos de las columnas seleccionadas aparecerán de manera automática."
                    )
                ),
                tags.li(
                    tags.strong("Verificar la integridad de los datos:"),
                    tags.p(
                        "En el panel \"Subir archivo\", se mostrarán los resultados de diversas pruebas de calidad de los datos, "
                        "como:"
                    ),
                    tags.ul(
                        tags.li("Si el archivo es un CSV válido."),
                        tags.li("Si la codificación es UTF-8."),
                        tags.li("La presencia de valores nulos o duplicados."),
                        tags.li("La consistencia de los tipos de datos."),
                        tags.li("Además, se mostrarán estadísticas sobre los tipos de datos de cada columna.")
                    )
                ),
                tags.li(
                    tags.strong("Exportar datos en la base de datos:"),
                    tags.p(
                        "En el panel \"Exportar datos\", haz clic en el botón Cargar en base de datos para iniciar el proceso de carga. "
                        "Una barra de progreso mostrará el avance de la carga, que se realizará en bloques de datos para evitar "
                        "sobrecargar el sistema."
                    )
                ),
                tags.li(
                    tags.strong("Visualización de valores faltantes:"),
                    tags.p(
                        "En el panel \"Subir archivo\", también podrás ver un gráfico que indica las columnas con valores faltantes "
                        "en el archivo CSV."
                    )
                )
            ),
            fade=False,
            size="xl",
            easy_close=True,
            footer=modal_button("Cerrar")
        )
    )
