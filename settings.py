import pathlib

import xarray

xarray.set_options(keep_attrs=True)

dir_data = pathlib.Path.cwd() / "data"

location = "torino"  # Select the spatial center of the analysis, cf. thesis.coords keys.
