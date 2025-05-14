from shiny import App, Inputs, Outputs, Session, render, ui, req, reactive
from shinywidgets import render_plotly
import faicons as fa  
from components.panels import panel_subir_archivo, panel_cargar_datos
from components.helper_text import info_modal
from utils.data_processing import load_csv, run_tests, export_data
from utils.plots import graficado_plotly, graficado_nulos
import duckdb


app_ui = ui.page_fluid(
    ui.page_navbar(
        ui.nav_spacer(),
        panel_subir_archivo(),
        panel_cargar_datos(),
        ui.nav_control(
            ui.input_action_button(
                id="info_icon",
                label=None,
                icon=fa.icon_svg("circle-info"),
                class_=(
                    "btn "
                    "d-flex align-items-center "
                    "border-0 p-3 "
                ),
                title="Documentación"
            )
        ),
        title="ESOLMET Explorer"
    )
)


def server(input: Inputs, output: Outputs, session: Session):

    @reactive.Effect
    @reactive.event(input.info_icon)
    def _():
        info_modal()

    @reactive.Calc
    def loaded():
        path = req(input.archivo())[0]["datapath"]
        return load_csv(path, formatted=True)

    @reactive.Calc
    def raw_df():
        path = req(input.archivo())[0]["datapath"]
        return load_csv(path, formatted=False)

    @render_plotly
    def plot_plotly():
        data = loaded()
        return graficado_plotly(data)

    @render.plot
    def plot_missing():
        return graficado_nulos(loaded())

    @reactive.Calc
    def tests_dict():
        path = req(input.archivo())[0]["datapath"]
        return run_tests(path)

    @render.ui
    def table_tests():
        tests = tests_dict()
        filas = []
        for prueba, ok in tests.items():
            icon = "circle-check" if ok else "circle-exclamation"
            color = "text-success" if ok else "text-danger"
            icono = fa.icon_svg(icon).add_class(color)
            filas.append(
                ui.tags.tr(
                    ui.tags.td(prueba, style="text-align:left;"),
                    ui.tags.td(icono, style="text-align:center;"),
                )
            )
        return ui.tags.table(
            ui.tags.thead(
                ui.tags.tr(
                    ui.tags.th("Prueba", style="text-align:left;"),
                    ui.tags.th("Estado", style="text-align:center;"),
                )
            ),
            ui.tags.tbody(*filas),
            class_="table table-sm table-striped w-auto",
        )

    @render.data_frame
    def df_types():
        df0 = raw_df()
        return df0.dtypes.rename_axis('Columna').reset_index(name='Tipo')

    @reactive.Calc
    def df_to_load():
        path = req(input.archivo())[0]["datapath"]
        return export_data(path)

    @render.data_frame
    def df_loaded():
        return df_to_load()

    @output
    @render.ui
    @reactive.event(input.btn_load)
    async def load_status():
        df_load = df_to_load()

        # Progreso ficticio
        with ui.Progress(min=1, max=len(df_load)) as p:
            p.set(message="Iniciando carga...", detail=None)
            # Conexión a DuckDB
            con = duckdb.connect('esolmet.db')
            con.execute("""
            CREATE TABLE IF NOT EXISTS lecturas (
                fecha TIMESTAMP,
                variable VARCHAR,
                valor DOUBLE,
                PRIMARY KEY (fecha, variable)
            );
            """)
            con.execute("BEGIN TRANSACTION;")

            chunk_size = 5000
            for i in range(0, len(df_load), chunk_size):
                chunk = df_load.iloc[i : i + chunk_size]
                con.register('tmp_chunk', chunk)
                con.execute("INSERT INTO lecturas SELECT * FROM tmp_chunk;")
                p.set(i + chunk_size, message=f"Cargando registros {i+1}-{min(i+chunk_size, len(df_load))}...")

            con.execute("COMMIT;")
            con.close()

        return ui.tags.div("Datos cargados correctamente")


app = App(app_ui, server, debug=True)
