from shiny import ui, reactive, render

def panel_explorador():
    return ui.nav_panel(
        "Explorador",
        ui.input_date_range(
            "fechas",
            "Fechas:",
            start="2010-01-01",
            end="2010-12-31",
            min="2010-01-01",
            max="2010-12-31",
            language="es",
            separator="a",
        ),
        ui.output_plot("plot_matplotlib"),
    )


def panel_estadistica():
    return ui.nav_panel(
        "Estadística",
        "Aquí irá tu contenido estadístico"
    )