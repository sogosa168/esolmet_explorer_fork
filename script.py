# %%
import pandas as pd
import glob

# %%

archivos = glob.glob('data/*.csv')

def importa_esolmet(archivo):
    esolmet = pd.read_csv('data/2010_ESOLMET.csv',skiprows=[0,2,3],
                        index_col=0,parse_dates=True,dayfirst=True)
    return esolmet
esolmet.index

# %%
