from shiny import App, ui, render
from shinywidgets import output_widget, render_widget 
import shinyswatch  
import pandas as pd
import glob
import plotly.express as px
import matplotlib.pyplot as plt




archivos = glob.glob('data/*.csv')

def importa_esolmet(archivo):
    esolmet = pd.read_csv('data/2010_ESOLMET.csv',skiprows=[0,2,3],
                        index_col=0,parse_dates=True,dayfirst=True)
    return esolmet

esolmet = pd.concat([importa_esolmet(archivo) for archivo in archivos ])
esolmet.sort_index(inplace=True)
esolmet.reset_index(inplace=True)
esolmet.I_dir_Avg = esolmet.I_dir_Avg.astype(float)

app_ui = ui.page_fluid(
    ui.navset_card_tab(  
        ui.nav_panel("ExploradorDatos",
                    #  output_widget("plot"),  
                    ui.input_date_range("fechas", "Selecciona fechas:", start="2010-01-01", end='2010-12-31'),  
                    ui.output_plot('plot_matplotlib')  
                     ),
        ui.nav_panel("Estadística", "Panel B content"),
        ui.nav_panel("Herramientas", "Panel C content"),
        id="tab",  
    )  
)


def server(input, output, session):
    @render_widget  
    def plot():  
        scatterplot = px.line(
            data_frame=esolmet,
            x='TIMESTAMP',
            y='I_glo_Avg'
        ).update_layout(
            yaxis_title="Ig [W/m2]",
        )

        return scatterplot  
    
    @render.plot(alt='Irradiancia')
    def plot_matplotlib():  
        fig, ax = plt.subplots()
        
        ax.plot(esolmet.TIMESTAMP, esolmet['I_glo_Avg'])
        ax.plot(esolmet.TIMESTAMP, esolmet['I_dir_Avg'])
        ax.plot(esolmet.TIMESTAMP, esolmet['I_dif_Avg'])
        ax.plot(esolmet.TIMESTAMP, esolmet['I_uv_Avg'])
        ax.set_xlim(input.fechas()[0],input.fechas()[1])

        return fig


app = App(app_ui, server)