import configparser
import ast

def load_settings(path: str = "configuration.ini"):
    """
    Lee el archivo INI y devuelve:
      - variables: list[str]
      - latitude: float
      - longitude: float
      - tz: str
      - name: str
    """
    config = configparser.ConfigParser()
    config.read(path)

    sec = config["settings"]
    variables = ast.literal_eval(sec.get("variables", "[]"))
    latitude  = sec.getfloat("latitude", fallback=0.0)
    longitude = sec.getfloat("longitude", fallback=0.0)
    tz        = sec.get("gmt", fallback="Etc/GMT+0")
    name      = sec.get("name", fallback="")

    return variables, latitude, longitude, tz, name

