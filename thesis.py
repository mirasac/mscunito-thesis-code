# Units: (degrees_north, degrees_east).
coords = {
    "torino": (45.198, 7.652),
    "bologna": (44.535, 11.288),
    "ciampino": (41.799, 12.594)
}

scenario = ("ssp126", "ssp245", "ssp370", "ssp585")

baseline_period = slice("1994-01-01", "2023-12-31")
training_period = slice("1950-01-01", "1999-12-31")
test_period = slice("2000-01-01", "2014-12-31")
time_horizons = {
    "near": slice("2021-01-01", "2040-12-31"),
    "medium": slice("2051-01-01", "2070-12-31"),
    "long": slice("2081-01-01", "2100-12-31")
}

spatial_resolution = 0.25  # Units: degrees.

models = (
    "ACCESS-CM2",
    "ACCESS-ESM1-5",
    "BCC-CSM2-MR",
    "CanESM5",
    #"CESM2",
    #"CESM2-WACCM",
    #"CMCC-CM2-SR5",
    "CMCC-ESM2",
    "CNRM-CM6-1",
    "CNRM-ESM2-1",
    "EC-Earth3",
    "EC-Earth3-Veg-LR",
    "FGOALS-g3",
    #"GFDL-CM4",
    #"GFDL-CM4_gr2",
    "GFDL-ESM4",
    "GISS-E2-1-G",
    #"HadGEM3-GC31-LL",
    #"HadGEM3-GC31-MM",
    #"IITM-ESM",
    "INM-CM4-8",
    "INM-CM5-0",
    "IPSL-CM6A-LR",
    "KACE-1-0-G",
    #"KIOST-ESM",
    "MIROC-ES2L",
    "MIROC6",
    "MPI-ESM1-2-HR",
    "MPI-ESM1-2-LR",
    "MRI-ESM2-0",
    #"NESM3",
    "NorESM2-LM",
    "NorESM2-MM",
    "TaiESM1",
    "UKESM1-0-LL"
)

drivers = ("heat_wave", "heavy_precipitation")
