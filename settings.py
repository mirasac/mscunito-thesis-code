import os
import pathlib

import xarray

xarray.set_options(keep_attrs=True)

# TODO set up in proper settings loading at startup of pipeline.
dir_code = pathlib.Path.home() / "mscunito-thesis-code"
dir_document = dir_code.parent / "mscunito-thesis-document"  # Directory where document is stored.

dir_data = dir_code / "data"  # Directory where data is stored.
dir_figures = dir_document / "figures"  # Directory where figures are stored.

site = "torino"  # Select the spatial center of the analysis, cf. thesis.coords keys.

sep = '.'  # Directory separator in file name of archives.

os.environ["CARTOPY_USER_BACKGROUNDS"] = str((dir_data / "maps" / "backgrounds").resolve())
