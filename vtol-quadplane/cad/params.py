"""Choix de la version : HUARD_VERSION=dfr (défaut, 1,8 m) ou HUARD_VERSION=mini (1,2 m)."""
import os

VERSION = os.environ.get("HUARD_VERSION", "dfr")
if VERSION == "mini":
    from params_mini import *  # noqa: F401,F403
elif VERSION == "dfr":
    from params_dfr import *  # noqa: F401,F403
else:
    raise SystemExit(f"HUARD_VERSION inconnue : {VERSION} (dfr ou mini)")
