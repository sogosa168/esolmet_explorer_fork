from shiny import ui


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


def panel_documentacion():
    return ui.nav_panel("Documentación", "Inserte aquí la documentacion")