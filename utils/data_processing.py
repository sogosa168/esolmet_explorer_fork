import numpy as np
import pandas as pd
import data_testing as dt


def _detect_csv(filepath: str) -> dict:
    """
    Detecta encoding y filas a omitir según el header.
    """
    use_utf8 = dt.detect_encoding(filepath)
    encoding = 'utf-8' if use_utf8 else 'ANSI'
    with open(filepath, 'r', encoding=encoding) as f:
        header = f.readline()
    skiprows = [] if 'TIMESTAMP' in header else [0, 2, 3]
    return {'encoding': encoding, 'skiprows': skiprows}


def _read_raw(filepath: str) -> pd.DataFrame:
    """
    Lee el CSV sin formatear, manteniendo tipos iniciales.
    """
    params = _detect_csv(filepath)
    try:
        df = pd.read_csv(
            filepath,
            skiprows=params['skiprows'],
            parse_dates=[0],
            dayfirst=True,
            low_memory=False,
            encoding=params['encoding']
        )
    except Exception as e:
        raise ValueError(f"Error al leer CSV: {e}")
    if df.columns[0] != 'TIMESTAMP':
        df.rename(columns={df.columns[0]: 'TIMESTAMP'}, inplace=True)
    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], errors='coerce')
    return df


def load_csv(filepath: str, formatted: bool = True, sort: bool = True) -> pd.DataFrame:
    """
    Carga CSV y opcionalmente formatea:
      - formatted=True: convierte columnas no-TIMESTAMP a float
      - sort=True: ordena por TIMESTAMP
      - elimina columna 'RECORD' si existe
    """
    df = _read_raw(filepath)
    if 'RECORD' in df.columns:
        df.drop(columns=['RECORD'], inplace=True)
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
    Ejecuta pruebas de:
      - extensión .csv
      - encoding utf-8
      - sin NaN en columnas
      - sin NaT en columnas datetime
      - sin duplicados
      - tipos correctos: todas las columnas no-TIMESTAMP deben ser float64
      - sin valores positivos de radiación si la altura solar es negativa 
    """
    # 1. extensión y encoding
    ext_ok = dt.detect_endswith(filepath)
    enc_ok = dt.detect_encoding(filepath)

    # 2. carga formateada para tests de NaN, NaT y duplicados
    fmt_df = load_csv(filepath, formatted=True, sort=True)

    nans_ok = dt.detect_nans(fmt_df)
    dup_ok  = dt.detect_duplicates(fmt_df)
    nats_ok = dt.detect_nats(fmt_df)

    # 3. prueba de radiación: creamos un DataFrame separado
    rad_df = fmt_df.copy()
    # asegurarnos de DatetimeIndex en rad_df
    if not isinstance(rad_df.index, pd.DatetimeIndex):
        rad_df['TIMESTAMP'] = pd.to_datetime(
            rad_df['TIMESTAMP'], errors='coerce'
        )
        rad_df = rad_df.set_index('TIMESTAMP')

    rad_df = dt.detect_radiation(rad_df, config_path="configuration.ini")
    rad_ok = rad_df["radiation_ok"].all()

    # 4. carga cruda para test de tipos
    raw_df = load_csv(filepath, formatted=False, sort=False)
    expected_types = {"TIMESTAMP": "datetime64[ns]"}
    for col in raw_df.columns:
        if col != "TIMESTAMP":
            expected_types[col] = "float64"
    types_ok = dt.detect_dtype(expected_types, raw_df)

    return {
        "Extensión .CSV":         ext_ok,
        "Encoding UTF-8":         enc_ok,
        "Sin valores NaN":        nans_ok,
        "Sin valores NaT":        nats_ok,
        "Sin duplicados":         dup_ok,
        "Tipo correcto":          types_ok,
        "Sin radiación nocturna": rad_ok,
    }


def export_data(filepath: str) -> pd.DataFrame:
    """
    Prepara DF en formato largo para carga en BD:
      - elimina columnas 'RECORD' y 'Unnamed'
      - convierte TIMESTAMP a string 'YYYY-MM-DD HH:MM:SS'
      - melt a ['fecha','variable','valor']
      - limpia nulls y duplicados
    """
    df = load_csv(filepath, formatted=False, sort=False)
    drop_cols = [c for c in df.columns if c.startswith('Unnamed') or c == 'RECORD']
    if drop_cols:
        df.drop(columns=drop_cols, inplace=True)
    df['TIMESTAMP'] = df['TIMESTAMP'].dt.strftime('%Y-%m-%d %H:%M:%S')
    long_df = df.melt(
        id_vars=['TIMESTAMP'],
        var_name='variable',
        value_name='valor'
    )
    long_df.columns = ['fecha', 'variable', 'valor']
    long_df.replace(['Na', 'nan', 'NaN', '-', ''], np.nan, inplace=True)
    long_df.dropna(subset=['fecha', 'valor'], inplace=True)
    long_df.drop_duplicates(subset=['fecha', 'variable'], inplace=True)
    long_df['valor'] = long_df['valor'].astype(float)
    return long_df

def radiacion(df, rad_columns=None):
    # 1. preparar índice datetime
    df_copy = df.copy()
    if 'TIMESTAMP' in df_copy.columns:
        df_copy['TIMESTAMP'] = pd.to_datetime(df_copy['TIMESTAMP'], errors='coerce')
        df_copy = df_copy.dropna(subset=['TIMESTAMP']).set_index('TIMESTAMP')

    # 2. obtener solar_altitude y radiation_ok
    rad_df = dt.detect_radiation(df_copy)

    # 3. renombrar para usar español
    rad_df = rad_df.rename(columns={'solar_altitude': 'altura_solar'})

    # 4. columnas de radiación
    cols = rad_columns or ['I_dir_Avg', 'I_glo_Avg', 'I_dif_Avg', 'I_uv_Avg']
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