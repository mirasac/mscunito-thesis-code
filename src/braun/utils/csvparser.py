import pathlib

import pandas
import xarray

HEADER_INDICATOR = ("driver", "indicator", "value", "units", "notes")
INDEX_INDICATOR = ("driver", "indicator")
DTYPE_INDICATOR = {
    "driver": str,
    "indicator": str,
    "value": float,
    "units": str,
    "notes": str
}

def load_indicators(path):
    path = pathlib.Path(path)
    return pandas.read_csv(
        path,
        index_col=INDEX_INDICATOR,
        usecols=HEADER_INDICATOR,
        dtype=DTYPE_INDICATOR
    )
