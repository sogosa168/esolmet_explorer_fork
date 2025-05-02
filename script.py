# %%
import pandas as pd
import glob

# %%

archivos = glob.glob('data/*.csv')

def importa_esolmet(archivo):
    esolmet = pd.read_csv('data/2010_ESOLMET.csv',skiprows=[0,2,3],
                        index_col=0,parse_dates=True,dayfirst=True)
    return esolmet

esolmet = pd.concat([importa_esolmet(archivo) for archivo in archivos ])
esolmet.sort_index(inplace=True)
esolmet.reset_index(inplace=True)
esolmet.columns 
# %%
esolmet['I_dir_Avg']
# %%
esolmet.info()
# %%
