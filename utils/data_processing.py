import glob
import pandas as pd


def load_esolmet_data():
    archivos = glob.glob('data/*2010*.csv')
    
    def importa_esolmet(archivo):
        # Usamos el parámetro archivo para leer cada CSV
        return pd.read_csv(archivo, skiprows=[0,2,3],
                           index_col=0, parse_dates=True, dayfirst=True)
    
    esolmet = pd.concat([importa_esolmet(archivo) for archivo in archivos])
    esolmet.sort_index(inplace=True)
    # esolmet.reset_index(inplace=True)
    esolmet.I_dir_Avg = esolmet.I_dir_Avg.astype(float)
    print(esolmet.info())
    return esolmet


def carga_csv(filepath):
    esolmet = pd.read_csv(filepath, skiprows=[0,2,3],index_col=0, parse_dates=True, dayfirst=True)
    esolmet.sort_index(inplace=True)
    esolmet.reset_index(inplace=True)
    esolmet.I_dir_Avg = esolmet.I_dir_Avg.astype(float)
    print("carga",esolmet.info())
    return esolmet
