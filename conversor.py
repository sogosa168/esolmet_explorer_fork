from pathlib import Path
import pandas as pd
import numpy as np

def convert(sep: str = ","):
    carpeta_entrada = Path("data/csv")
    carpeta_salida = Path("data/parquet")
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    for archivo_csv in carpeta_entrada.glob("*.csv"):
        # Determinar encoding leyendo la primera línea
        try:
            with open(archivo_csv, 'r', encoding='utf-8') as f:
                first_row = f.readline()
            enc_initial = 'utf-8'
        except UnicodeDecodeError:
            enc_initial = 'ANSI'
            with open(archivo_csv, 'r', encoding=enc_initial) as f:
                first_row = f.readline()

        # Decidir filas de encabezado
        use_skip = 'TIMESTAMP' not in first_row
        skiprows = [0,2,3] if use_skip else None

        # Intentar lectura con diferentes encodings
        read_args = dict(
            filepath_or_buffer=archivo_csv,
            index_col=0,
            parse_dates=True,
            dayfirst=True,
            sep=sep,
            low_memory=False,
            skiprows=skiprows
        )
        for enc in (enc_initial, 'latin1'):
            try:
                df = pd.read_csv(**read_args, encoding=enc)
                break
            except UnicodeDecodeError:
                continue
        else:
            # última oportunidad con engine python
            df = pd.read_csv(**read_args, encoding=enc_initial, engine='python')

        # limpieza de columnas
        df.sort_index(inplace=True)
        df.reset_index(inplace=True)
        if 'RECORD' in df.columns:
            df.drop(columns=['RECORD'], inplace=True)
        df = df.loc[:, ~df.columns.str.startswith('Unnamed')]

        # conversión de TIMESTAMP y establecimiento como índice
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], errors='coerce')
        df.dropna(subset=['TIMESTAMP'], inplace=True)
        df.set_index('TIMESTAMP', inplace=True)

        # limpiar valores y convertir a float
        df.replace(['Na', 'nan', 'NaN', '-', ''], np.nan, inplace=True)
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # exportar a Parquet conservando índice datetime
        archivo_parquet = carpeta_salida / (archivo_csv.stem + ".parquet")
        df.to_parquet(archivo_parquet)


if __name__ == "__main__":
    convert()
