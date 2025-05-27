import numpy as np
import pandas as pd
import validation_tools as vt
from utils.config import load_settings
import glob

variables, latitude, longitude, gmt, name = load_settings()
ALLOWED_VARS = variables
MIN_YEAR = 2010


def _detect_csv(filepath: str) -> dict:
    """
    Detecta encoding y filas a omitir según el header.
    """
    use_utf8 = vt.detect_encoding(filepath)
    encoding = "utf-8" if use_utf8 else "latin-1"
    with open(filepath, "r", encoding=encoding, errors="replace") as f:
        header = f.readline()
    skiprows = [] if "TIMESTAMP" in header else [0, 2, 3]
    return {"encoding": encoding, "skiprows": skiprows}


def _read_raw(filepath: str) -> pd.DataFrame:
    """
    Lee el CSV sin formatear, manteniendo tipos iniciales.
    """
    params = _detect_csv(filepath)
    common_kwargs = dict(
        filepath_or_buffer=filepath,
        skiprows=params["skiprows"],
        parse_dates=[0],
        dayfirst=True,
        low_memory=False,
    )

    # 1) Intenta con el encoding detectado
    try:
        df = pd.read_csv(**common_kwargs, encoding=params["encoding"])
    except UnicodeDecodeError:
        # 2) Si falla, reintenta con latin-1
        df = pd.read_csv(**common_kwargs, encoding="latin-1")

    # renombra columna de fecha y fuerza datetime
    if df.columns[0] != "TIMESTAMP":
        df.rename(columns={df.columns[0]: "TIMESTAMP"}, inplace=True)
    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"], errors="coerce")

    return df


def load_csv(filepath: str, formatted: bool = True, sort: bool = True) -> pd.DataFrame:
    """
    Carga CSV y opcionalmente formatea:
      - formatted=True: convierte columnas no-TIMESTAMP a float
      - sort=True: ordena por TIMESTAMP
      - elimina columna 'RECORD' si existe
      - filtra solo columnas permitidas en configuración
    """
    df = _read_raw(filepath)

    if 'RECORD' in df.columns:
        df.drop(columns=['RECORD'], inplace=True)

    # filtrar columnas extras y mantener el orden de configuración
    keep = ['TIMESTAMP'] + [col for col in ALLOWED_VARS if col in df.columns]
    df = df.loc[:, keep]

    if formatted:
        for col in df.columns:
            if col != 'TIMESTAMP':
                df[col] = pd.to_numeric(df[col], errors='coerce')
        if sort:
            df.sort_values('TIMESTAMP', inplace=True)
            df.reset_index(drop=True, inplace=True)
    return df


def run_tests(filepath: str) -> dict:
    """
    Ejecuta pruebas de calidad sobre el CSV.
    """
    ext_ok = vt.detect_endswith(filepath)
    enc_ok = vt.detect_encoding(filepath)

    fmt_df = load_csv(filepath, formatted=True, sort=True)
    nans_ok = vt.detect_nans(fmt_df)
    dup_ok  = vt.detect_duplicates(fmt_df)
    nats_ok = vt.detect_nats(fmt_df)

    rad_df = fmt_df.copy()
    if not isinstance(rad_df.index, pd.DatetimeIndex):
        rad_df['TIMESTAMP'] = pd.to_datetime(rad_df['TIMESTAMP'], errors='coerce')
        rad_df = rad_df.set_index('TIMESTAMP')
    rad_df = vt.detect_radiation(rad_df, config_path="configuration.ini")
    rad_ok = rad_df["radiation_ok"].all()

    raw_df = load_csv(filepath, formatted=False, sort=False)
    expected_types = {'TIMESTAMP': 'datetime64[ns]'}
    for col in raw_df.columns:
        if col != 'TIMESTAMP':
            expected_types[col] = 'float64'
    types_ok = vt.detect_dtype(expected_types, raw_df)

    return {
        "Extensión .CSV":         ext_ok,
        "Encoding UTF-8":         enc_ok,
        # "Sin valores NaN":        nans_ok,
        "Sin valores NaT":        nats_ok,
        "Sin duplicados":         dup_ok,
        "Tipo correcto":          types_ok,
        # "Sin radiación en noche": rad_ok,
    }


def export_data(filepath: str) -> pd.DataFrame:
    """
    Prepara DF en formato largo para carga en BD:
      - elimina columnas 'RECORD' y 'Unnamed'
      - filtra registros con TIMESTAMP año ≥ 2010
      - convierte TIMESTAMP a string 'YYYY-MM-DD HH:MM:SS'
      - melt a ['fecha','variable','valor']
      - limpia nulls y duplicados
    """
    df = load_csv(filepath, formatted=False, sort=False)

    # eliminar columnas innecesarias
    drop_cols = [c for c in df.columns if c.startswith('Unnamed') or c == 'RECORD']
    if drop_cols:
        df.drop(columns=drop_cols, inplace=True)

    # asegurar que TIMESTAMP sea datetime
    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], errors='coerce')
    # filtrar año mínimo
    df = df[df['TIMESTAMP'].dt.year >= MIN_YEAR]
    
    # formatear TIMESTAMP a string
    df['TIMESTAMP'] = df['TIMESTAMP'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # melt a formato largo
    long_df = df.melt(
        id_vars=['TIMESTAMP'],
        var_name='variable',
        value_name='valor'
    )
    # renombrar columnas
    long_df.columns = ['fecha', 'variable', 'valor']
    # limpiar nulos en fecha y valor
    long_df.replace(['Na', 'nan', 'NaN', '-', ''], np.nan, inplace=True)
    long_df.dropna(subset=['fecha', 'valor'], inplace=True)
    # eliminar duplicados
    long_df.drop_duplicates(subset=['fecha', 'variable'], inplace=True)
    # asegurar tipo float en valor
    long_df['valor'] = long_df['valor'].astype(float)
    return long_df


def radiacion(df, rad_columns=None):
    """
    Detecta eventos de radiación nocturna manteniendo solo las columnas configuradas.
    """
    # 0. filtrar columnas extras
    keep = ['TIMESTAMP'] + [c for c in ALLOWED_VARS if c in df.columns]
    df = df.loc[:, keep].copy()
    
    # 1. preparar índice datetime
    if 'TIMESTAMP' in df.columns:
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], errors='coerce')
        df = df.dropna(subset=['TIMESTAMP']).set_index('TIMESTAMP')

    # 2. obtener solar_altitude y radiation_ok
    rad_df = vt.detect_radiation(df)

    # 3. renombrar para usar español
    rad_df = rad_df.rename(columns={'solar_altitude': 'altura_solar'})

    # 4. columnas de radiación
    cols = rad_columns or ['I_dir_Avg', 'I_glo_Avg', 'I_dif_Avg', 'I_dif_Calc', 'I_uv_Avg']
    cols = [c for c in cols if c in rad_df.columns]
    if not cols:
        raise KeyError("No hay columnas de radiación para filtrar.")

    # 5. filtrar registros nocturnos con radiación > 0
    mask_noche = rad_df['altura_solar'] <= 0
    mask_rad   = rad_df[cols].gt(0).any(axis=1)
    nocturna   = rad_df.loc[mask_noche & mask_rad, cols + ['altura_solar']]

    # 6. redondear altura solar a 2 decimales
    nocturna['altura_solar'] = nocturna['altura_solar'].round(2)

    return nocturna

def _df_nans(df: pd.DataFrame, filepath: str) -> pd.DataFrame:
    # 1. Calcula offset según skiprows
    csv_opts   = _detect_csv(filepath)
    skip_count = len(csv_opts["skiprows"]) - 1
    offset     = skip_count + 3  # +2 líneas de cabecera +1 para 1-based

    # 2. Encuentra los NaN en columnas no datetime
    non_dt = df.select_dtypes(exclude=["datetime64[ns]", "datetimetz"]).columns
    mask   = df[non_dt].isna()
    nans   = mask.stack()[lambda s: s]

    # 3. Si no hay NaN, devuelve mensaje
    if nans.empty:
        return pd.DataFrame({"Info": ["No se encontró ningún NaN en las columnas de datos."]})

    # 4. Reconstruye posiciones y aplica offset
    loc = nans.reset_index()
    loc.columns      = ["Fila_idx", "Columna", "is_nan"]
    loc["fila_original"] = loc["Fila_idx"] + offset

    # 5. Devuelve sólo fila y columna
    return (
        loc[["fila_original", "Columna"]]
        .rename(columns={"fila_original": "Fila"})
    )


def _df_nats(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Encuentra NaT en columnas datetime
    datetime_cols = df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns
    mask          = df[datetime_cols].isna()
    nats          = mask.stack()[lambda s: s]

    # 2. Si no hay NaT, devuelve mensaje
    if nats.empty:
        return pd.DataFrame({"Info": ["No se encontró ningún NaT en la estampa temporal."]})

    # 3. Reconstruye posiciones
    loc = nats.reset_index()
    loc.columns = ["Fila", "Columna", "is_nat"]

    # 4. Devuelve sólo la fila original
    return loc[["Fila"]]

def load_esolmet_data():
    archivos = glob.glob('data/2023*.csv')
    
    def importa_esolmet(archivo):
        # Usamos el parámetro archivo para leer cada CSV
        return pd.read_csv(archivo,
                           index_col=0, parse_dates=True, dayfirst=True)
    
    esolmet = pd.concat([importa_esolmet(archivo) for archivo in archivos])
    esolmet.sort_index(inplace=True)
    # esolmet.reset_index(inplace=True)
    esolmet.I_dir_Avg = esolmet.I_dir_Avg.astype(float)
    print(esolmet.info())
    return esolmet
