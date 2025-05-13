from shiny import App, Inputs, Outputs, Session, render, ui, req, reactive
import faicons as fa  
from components.panels import panel_subir_archivo, panel_cargar_datos
from components.helper_text import info_modal
from utils.data_processing import _load_csv, run_tests, exporta_database
from utils.plots import graficado_matplotlib, graficado_nulos
import pandas as pd
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
        f = req(input.archivo())[0]["datapath"]
        return _load_csv(f)

    @reactive.Calc
    def df():
        df0 = loaded().copy()
        df0["TIMESTAMP"] = pd.to_datetime(df0["TIMESTAMP"])
        for col in df0.columns:
            if col != "TIMESTAMP":
                df0[col] = pd.to_numeric(df0[col], errors="coerce")
        return df0

    @reactive.effect
    def update_columns():
        data = df()
        cols = [c for c in data.columns if c != "TIMESTAMP"]
        ui.update_selectize(
            "col_selector",
            choices=cols,
            selected=cols,
            server=False,
        )

    @render.plot
    def plot_matplotlib():
        data = df()
        selected = input.col_selector() or []
        return graficado_matplotlib(data, columns=selected)

    @render.plot
    def plot_missing():
        return graficado_nulos(df())

    @reactive.Calc
    def tests_dict():
        f = req(input.archivo())[0]["datapath"]
        return run_tests(f)

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

    @reactive.Calc
    def raw_df():
        df0 = loaded()
        df0["TIMESTAMP"] = pd.to_datetime(df0["TIMESTAMP"])
        return df0

    @render.data_frame
    def df_types():
        df0 = raw_df()
        return pd.DataFrame({
            "Columna": df0.columns,
            "Tipo":     df0.dtypes.astype(str),
        })
    
    @reactive.Calc
    def df_to_load():
        path = req(input.archivo())[0]["datapath"]
        return exporta_database(path)

    @render.data_frame
    def df_loaded():
        df_load = df_to_load()
        return df_load

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

            # Insertamos por chunks:
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