import numpy as np
import pandas as pd
import data_testing as dt


def carga_csv(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            first_row = file.readline()
            if 'TIMESTAMP' in first_row:
                esolmet = pd.read_csv(
                    filepath,
                    index_col=0,
                    parse_dates=True,
                    dayfirst=True,
                    encoding='utf-8'
                )
            else:
                esolmet = pd.read_csv(
                    filepath,
                    skiprows=[0, 2, 3],
                    index_col=0,
                    parse_dates=True,
                    dayfirst=True,
                    encoding='utf-8'
                )
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='ANSI') as file:
            first_row = file.readline()
            if 'TIMESTAMP' in first_row:
                esolmet = pd.read_csv(
                    filepath,
                    index_col=0,
                    parse_dates=True,
                    dayfirst=True,
                    encoding='ANSI'
                )
            else:
                esolmet = pd.read_csv(
                    filepath,
                    skiprows=[0, 2, 3],
                    index_col=0,
                    parse_dates=True,
                    dayfirst=True,
                    encoding='ANSI'
                )
    
    esolmet.sort_index(inplace=True)
    esolmet.reset_index(inplace=True)
    esolmet.drop(columns=['RECORD'], inplace=True)
    esolmet['TIMESTAMP'] = pd.to_datetime(esolmet['TIMESTAMP'])
    for col in esolmet.columns:
        if col != 'TIMESTAMP':
            esolmet[col] = pd.to_numeric(esolmet[col], errors='coerce')
    return esolmet


def run_tests(filepath):
    """
    Executes a set of tests on the file using raw and formatted data:
      - Extension .csv
      - Encoding utf-8
      - No null values (after formatting)
      - No duplicates (after formatting)
      - Correct type: TIMESTAMP raw as datetime64[ns], others raw as float64
    Returns a dictionary with the test name and a boolean.
    """
    # Extensión y encoding
    ext = dt.detect_endswith(filepath)
    _, enc = dt.import_data(filepath)

    # DataFrame raw para tipo
    raw_df, _ = dt.import_data(filepath)
    raw_df = raw_df.reset_index().rename(columns={'index': 'TIMESTAMP'})

    # DataFrame formateado para nans y duplicados
    formatted_df = carga_csv(filepath)

    # Tests nulos y duplicados en formatted
    nans = dt.detect_nans(formatted_df)
    dup = dt.detect_duplicates(formatted_df)

    # Test de tipos sobre raw
    expected = {col: 'float64' for col in raw_df.columns if col != 'TIMESTAMP'}
    expected['TIMESTAMP'] = 'datetime64[ns]'
    types = dt.detect_dtype(expected, raw_df)

    return {
        'Extensión .CSV': ext,
        'Encoding UTF-8': enc,
        'Sin valores nulos': nans,
        'Sin duplicados': dup,
        'Tipo correcto': types,
    }

def exporta_database(filepath):
    """
    Reads the CSV, cleans, transforms to long format, and returns a DataFrame ready for insertion into DuckDB:
      - Removes the RECORD column
      - Removes columns starting with 'Unnamed'
      - Converts TIMESTAMP to datetime and normalizes it to 'YYYY-MM-DD HH:MM:SS'
      - Uses 'melt' for variables and values
      - Cleans 'Na', 'nan', '' as NaN and removes duplicates
      - Final cast of 'valor' to float
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            first = f.readline()
        enc = 'utf-8'
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='ANSI') as f:
            first = f.readline()
        enc = 'ANSI'

    try:
        if 'TIMESTAMP' in first:
            df = pd.read_csv(filepath, low_memory=False, encoding=enc)
        else:
            df = pd.read_csv(filepath, low_memory=False, encoding=enc, skiprows=[0,2,3])
    except UnicodeDecodeError:
        fallback = 'ANSI' if enc == 'utf-8' else 'utf-8'
        if 'TIMESTAMP' in first:
            df = pd.read_csv(filepath, low_memory=False, encoding=fallback)
        else:
            df = pd.read_csv(filepath, low_memory=False, encoding=fallback, skiprows=[0,2,3])

    if df.index.name == 'TIMESTAMP':
        df = df.reset_index()
    if df.columns[0] != 'TIMESTAMP':
        df = df.rename(columns={df.columns[0]: 'TIMESTAMP'})
    if 'RECORD' in df.columns:
        del df['RECORD']
    df = df.loc[:, ~df.columns.str.startswith('Unnamed')]

    df['TIMESTAMP'] = pd.to_datetime(
        df['TIMESTAMP'],
        format='%d/%m/%Y %H:%M',
        errors='coerce'
    ).dt.strftime('%Y-%m-%d %H:%M:%S')

    df = df.melt(
        id_vars=['TIMESTAMP'],
        var_name='variable',
        value_name='valor'
    )
    df.columns = ['fecha', 'variable', 'valor']

    df.replace(['Na', 'nan', 'NaN', '-', ''], np.nan, inplace=True)
    df.dropna(subset=['fecha', 'valor'], inplace=True)
    df.drop_duplicates(subset=['fecha', 'variable'], keep='first', inplace=True)
    df['valor'] = df['valor'].astype(float)

    return df