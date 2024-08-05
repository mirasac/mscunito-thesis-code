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
NA_VALUES = ("-NaN", "-nan", "N/A", "NA", "NULL", "NaN", "None", "n/a", "nan", "null")
"""Subset of default sequence at https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html."""

def load_indicators(path):
    path = pathlib.Path(path)
    return pandas.read_csv(
        path,
        index_col=INDEX_INDICATOR,
        usecols=HEADER_INDICATOR,
        dtype=DTYPE_INDICATOR,
        na_values=NA_VALUES,
        keep_default_na=False
    )
