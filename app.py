from shiny import App, ui, render
from shinywidgets import output_widget, render_widget 
import shinyswatch  
from components.panels import panel_explorador, panel_herramientas, panel_estadistica
from utils.data_processing import load_esolmet_data
from utils.graficadores import graficado_Is_matplotlib


esolmet = load_esolmet_data()

app_ui = ui.page_fluid(
    ui.navset_card_tab(  
        panel_explorador(),
        panel_estadistica(),
        panel_herramientas(),
        id="tab",  
    )  
)


def server(input, output, session):
    
    @render.plot(alt='Irradiancia')
    def plot_matplotlib():
        return graficado_Is_matplotlib(esolmet, input.fechas())


app = App(app_ui, server)