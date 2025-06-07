import configparser
import ast

def load_settings(path: str = "configuration.ini"):
    """
    Lee el archivo INI y devuelve:
      - variables: list[str]
      - latitude: float
      - longitude: float
      - gmt: int                 (UTC offset del sitio)
      - name: str
      - alias: dict[str,str]
      - wind_speed_height: float (altura en m de WS_ms_Avg & WindDir)
      - air_temperature_height: float (altura en m de AirTC_Avg)
      - air_pressure_height: float (altura en m de CS106_PB_Avg)
      - site_id: int
      - data_tz: int             (UTC offset de los datos)
    """
    config = configparser.ConfigParser()
    config.read(path)
    if "settings" not in config:
        raise ValueError(f"No se encontró la sección [settings] en {path}")
    sec = config["settings"]
    variables = ast.literal_eval(sec.get("variables", "[]"))
    latitude  = sec.getfloat("latitude", fallback=0.0)
    longitude = sec.getfloat("longitude", fallback=0.0)
    gmt       = sec.getint("gmt", fallback=0)
    name      = sec.get("name", fallback="")
    alias     = ast.literal_eval(sec.get("alias", "{}"))
    site_id            = sec.getint("site_id", fallback=0)
    data_tz            = sec.getint("data_tz", fallback=gmt)
    wind_speed_height      = sec.getfloat("wind_speed_height",      fallback=10.0)
    air_temperature_height = sec.getfloat("air_temperature_height", fallback=10.0)
    air_pressure_height    = sec.getfloat("air_pressure_height",    fallback=10.0)
    return (variables, latitude, longitude, gmt, name, alias, site_id, data_tz, wind_speed_height, air_temperature_height, air_pressure_height)

