from shiny import ui, reactive, render


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

def panel_subir_datos():
    return ui.nav_panel(
        "Subir Datos", 
        # 1) Input para seleccionar el archivo CSV
        ui.input_file(
            "archivo", 
            "Selecciona el archivo CSV", 
            accept='.csv'
        ),
        # ui.output_plot('plot_matplotlib')  

    )