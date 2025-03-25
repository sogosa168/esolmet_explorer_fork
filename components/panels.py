from shiny import ui, reactive, render


def panel_explorador():
    return ui.nav_panel("ExploradorDatos",
                #  output_widget("plot"),  
                ui.input_date_range(
                    "fechas", 
                    "Fechas:", 
                    start="2010-01-01", 
                    end='2010-12-31',
                    min="2010-01-01", 
                    max="2010-12-31", 
                    language='es',
                    separator="a"
                    ),  
                ui.output_plot('plot_matplotlib')  
                )
    

def panel_estadistica():
    return ui.nav_panel("Estadística", "Panel B content")


def panel_herramientas():
    return ui.nav_panel("Herramientas", "Panel C content")

def panel_pruebas():
    return ui.nav_panel("Pruebas", "Pruebas de los datos")


def panel_documentacion():
    return ui.nav_panel("Documentación", "Inserte aquí la documentacion")





def panel_subir_datos():
    return ui.nav_panel(
        "Subir Datos", 
        # 1) Input para seleccionar el archivo CSV
        ui.input_file(
            "archivo", 
            "Selecciona el archivo CSV", 
            accept='.csv'
        ),
        ui.output_plot('plot_matplotlib')  

    )