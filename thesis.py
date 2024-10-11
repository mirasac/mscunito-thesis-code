# Units: (degrees_north, degrees_east).
coords = {
    "torino": (45.198, 7.652),  # From Google Maps, from ENAC instead: (45.203, 7.649).
    "bologna": (44.535, 11.288),  # From Google Maps.
    "ciampino": (41.799, 12.594)  # From Google Maps, from ENAC instead: (41.799, 12.597).
}

scenarios = ("ssp126", "ssp245", "ssp370")

reference_periods = {
    "torino": slice("1971-01-01", "2000-12-31"),
    "ciampino": slice("1981-01-01", "2010-12-31")
}
time_horizons = {
    "near": slice("2024-01-01", "2043-12-31"),
    "medium": slice("2044-01-01", "2063-12-31"),
    "long": slice("2081-01-01", "2100-12-31")
}

training_period = slice("1950-01-01", "1993-12-31")
test_period = slice("1994-01-01", "2023-12-31")

extension_scenario = "ssp245"
extension_period = slice("2015-01-01", "2023-12-31")

spatial_resolution = 0.25  # Units: degrees.

models = (
    "ACCESS-CM2",
    "ACCESS-ESM1-5",
    "BCC-CSM2-MR",
    "CanESM5",
    #"CESM2",  # Missing variables or scenario.
    #"CESM2-WACCM",  # Missing variables or scenario.
    #"CMCC-CM2-SR5",  # Missing variables or scenario.
    "CMCC-ESM2",
    "CNRM-CM6-1",
    "CNRM-ESM2-1",
    "EC-Earth3",
    "EC-Earth3-Veg-LR",
    "FGOALS-g3",
    #"GFDL-CM4",  # Missing variables or scenario.
    #"GFDL-CM4_gr2",  # Missing variables or scenario.
    "GFDL-ESM4",
    #"GISS-E2-1-G",  # Sub-daily values are present, almost all are NaNs.
    #"HadGEM3-GC31-LL",  # Missing variables or scenario.
    #"HadGEM3-GC31-MM",  # Missing variables or scenario.
    #"IITM-ESM",  # Missing variables or scenario.
    "INM-CM4-8",
    "INM-CM5-0",
    "IPSL-CM6A-LR",
    #"KACE-1-0-G",  # Calendar of 360 days.
    #"KIOST-ESM",  # Missing variables or scenario.
    "MIROC-ES2L",
    "MIROC6",
    "MPI-ESM1-2-HR",
    "MPI-ESM1-2-LR",
    "MRI-ESM2-0",
    #"NESM3",  # Missing variables or scenario.
    "NorESM2-LM",
    "NorESM2-MM",
    "TaiESM1",
    #"UKESM1-0-LL"  # Calendar of 360 days.
)

drivers = ("heat_wave", "heavy_precipitation")

calendar = "noleap"  # For a list of available calendars check http://cfconventions.org/Data/cf-conventions/cf-conventions-1.11/cf-conventions.html#calendar.

# TODO better implement the load of these at import of module `braun`.
INDICATORS = (
    "heat_wave_index",
    "heat_wave_max_length",
    "max_n_day_precipitation_amount",
    "wetdays",
    "cwd"
)

# TODO better implement the load of these at import of module `braun`.
INDICATORS_INTEGER = (
    "heat_wave_index",
    "heat_wave_max_length",
    "wetdays",
    "cwd"
)

# TODO better implement the load of these at import of module `braun`.
INDICATORS_INVALID = ("heat_wave_max_length",)

# TODO better implement the load of these at import of module `braun`.
p1 = list(range(1, 32, 3))
p2 = [0.9, 0.97, 0.99, 0.999, 1.0]
p3 = [0.9, 0.97, 0.99, 0.999, 1.0]
p4 = list(range(1, 32, 1))
p5 = [0.9, 0.97, 0.99, 0.999, 0.9999]

# TODO better implement the load of these at import of module `braun`.
PARAMETERS = {
    "heat_wave_index_window": p1,
    "heat_wave_index_thresh": p2,
    "heat_wave_max_length_window": p1,
    "heat_wave_max_length_thresh_tasmax": p2,
    "heat_wave_max_length_thresh_tasmin": p3,
    "max_n_day_precipitation_amount_window": p4,
    "wetdays_thresh": p5,
    "cwd_thresh": p5
}

risk_categories = {
    "very_low": "Very low",
    "low": "Low",
    "intermediate": "Intermediate",
    "high": "High",
    "very_high": "Very high"
}
