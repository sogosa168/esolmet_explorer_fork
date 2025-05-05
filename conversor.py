from pathlib import Path
import pandas as pd

def convert(sep: str = ","):
    carpeta_entrada = Path("data/csv")
    carpeta_salida = Path("data/parquet")

    for archivo_csv in carpeta_entrada.glob("*.csv"):
        try:
            df = pd.read_csv(archivo_csv, encoding="utf-8", sep=sep, low_memory=False)
        except UnicodeDecodeError:
            df = pd.read_csv(archivo_csv, encoding="ANSI", sep=sep, low_memory=False)
        
        archivo_parquet = carpeta_salida / (archivo_csv.stem + ".parquet")
        df.to_parquet(archivo_parquet, index=False)


if __name__ == "__main__":
    convert()
