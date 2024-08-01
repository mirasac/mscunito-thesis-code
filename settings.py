import pathlib

import xarray

xarray.set_options(keep_attrs=True)

dir_data = pathlib.Path.cwd() / "data"  # Directory inside the repository where data is stored.

location = "torino"  # Select the spatial center of the analysis, cf. thesis.coords keys.

sep = '.'  # Directory separator in file names.
