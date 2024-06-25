import pathlib



"""Useful variables about the code."""

dir_data = pathlib.Path.cwd() / "data"



"""Data related to the thesis."""

# Units: (degrees_north, degrees_east).
coords = {
    "torino": (45.198, 7.652),
    "bologna": (44.535, 11.288),
    "ciampino": (41.799, 12.594)
}

scenario = ("ssp126", "ssp245", "ssp585")

baseline_period = slice("1994-01-01", "2023-12-31")
training_period = slice("1950-01-01", "1999-12-31")
test_period = slice("2000-01-01", "2023-12-31")

spatial_resolution = 0.25  # Units: degrees.

models = ("EC-Earth3",)
