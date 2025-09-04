import warnings

from ._python_interface import (
    Linelist as Linelist,
)
from ._python_interface import (
    air_to_vacuum,
    get_APOGEE_DR17_linelist,
    get_GALAH_DR3_linelist,
    get_GES_linelist,
    get_VALD_solar_linelist,
    load_ExoMol_linelist,
    read_linelist,
    synth,
    vacuum_to_air,
)

# the _version file is generated as a part of the build process
# we re-export to avoid ruff warnings
from ._version import __version__ as __version__

__all__ = [
    "get_APOGEE_DR17_linelist",
    "get_GALAH_DR3_linelist",
    "get_GES_linelist",
    "get_VALD_solar_linelist",
    "read_linelist",
    "synth",
]

warnings.warn("korg.py is highly experimental. All functions/types can and will change")
