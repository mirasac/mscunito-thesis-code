import pathlib
import sys

import xarray

DIR_ROOT = "../"

def append_path(path):
    sys.path.append(str(pathlib.Path(path).resolve()))

def open_dataset():
    baseline_period = slice("1980", "2010")
    path_data = pathlib.Path(DIR_ROOT, "data/era5-2km/2m_temperature")
    ds_hourly = xarray.open_mfdataset(path_data.iterdir())
    ds_hourly = ds_hourly.sel(time=baseline_period, drop=True)
    ds_hourly = ds_hourly.rename({"T_2M": "tas"})
    return ds_hourly

append_path("..")
