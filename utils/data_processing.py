import numpy as np
import pandas as pd
import data_testing as dt


def _load_csv(filepath: str) -> pd.DataFrame:
    use_utf8 = dt.detect_encoding(filepath)
    encoding = 'utf-8' if use_utf8 else 'ANSI'

    with open(filepath, 'r', encoding=encoding) as f:
        header = f.readline()
    skip = [] if 'TIMESTAMP' in header else [0, 2, 3]

    df = pd.read_csv(
        filepath,
        skiprows=skip,
        index_col=0,
        parse_dates=True,
        dayfirst=True,
        encoding=encoding,
    )
    df.sort_index(inplace=True)
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'TIMESTAMP'}, inplace=True)
    if 'RECORD' in df.columns:
        df.drop(columns=['RECORD'], inplace=True)
    return df


def formatted_csv(filepath: str) -> pd.DataFrame:
    df = _load_csv(filepath)

    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
    for col in df.columns:
        if col != 'TIMESTAMP':
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def raw_csv(filepath: str) -> pd.DataFrame:
    df = _load_csv(filepath)
    df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
    return df


def run_tests(filepath: str) -> dict:
    """
    Executes a set of tests on the file using raw and formatted data:
      - Extension .csv
      - Encoding utf-8
      - No null values (after formatting)
      - No duplicates (after formatting)
      - Correct dtypes: TIMESTAMP raw as datetime64[ns], others raw as float64
    """
    # Extensión y encoding
    ext = dt.detect_endswith(filepath)
    enc = dt.detect_encoding(filepath)

    # DataFrame raw para dtype tests
    raw_df = raw_csv(filepath)

    # DataFrame formateado para nans y duplicados
    formatted_df = formatted_csv(filepath)

    # Tests nulos y duplicados en formatted_df
    nans = dt.detect_nans(formatted_df)
    dup  = dt.detect_duplicates(formatted_df)

    # Test de tipos sobre raw_df
    expected = {col: 'float64' for col in raw_df.columns if col != 'TIMESTAMP'}
    expected['TIMESTAMP'] = 'datetime64[ns]'
    types_ok = dt.detect_dtype(expected, raw_df)

    return {
        'Extensión .CSV':    ext,
        'Encoding UTF-8':    enc,
        'Sin valores nulos': nans,
        'Sin duplicados':    dup,
        'Tipo correcto':     types_ok,
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