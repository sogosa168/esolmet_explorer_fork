from shiny import ui


def panel_explorador():
    return ui.nav_panel("ExploradorDatos",
                #  output_widget("plot"),  
                ui.input_date_range("fechas", "Selecciona fechas:", start="2010-03-03", end='2010-03-10'),  
                ui.output_plot('plot_matplotlib')  
                )
    

def panel_estadistica():
    return ui.nav_panel("Estadística", "Panel B content")


def panel_herramientas():
    return ui.nav_panel("Herramientas", "Panel C content")