import pathlib
import tqdm
import xarray

import settings
import thesis

def label_quantiles(filename: pathlib.Path, indicator):
    filename = filename.resolve()
    dir_bak = filename.parent / "bak_quantile_coords"
    dir_bak.mkdir(parents=True, exist_ok=True)
    filename_bak = filename.rename(dir_bak / filename.name)
    ds = xarray.load_dataset(filename_bak)
    _ds = None
    if indicator in ("heat_wave_index",):
        quantiles = [0.9, 0.97, 0.99, 0.999, 1.0]
        _ds = ds.assign_coords({"thresh_q": ("thresh", quantiles)})
    elif indicator in ("heat_wave_max_length",):
        quantiles = [0.9, 0.97, 0.99, 0.999, 1.0]
        _ds = ds.assign_coords({"thresh_tasmin_q": ("thresh_tasmin", quantiles)})
        _ds = _ds.assign_coords({"thresh_tasmax_q": ("thresh_tasmax", quantiles)})
    elif indicator in ("wetdays", "cwd"):
        quantiles = [0.9, 0.97, 0.99, 0.999, 0.9999]
        _ds = ds.assign_coords({"thresh_q": ("thresh", quantiles)})
    if _ds is not None:
        _ds.to_netcdf(filename)
    else:
        _ds = ds
        filename_bak.rename(filename)
    return _ds

if __name__ == "__main__":
    indicators = (
        "heat_wave_index",
        "heat_wave_max_length",
        "max_n_day_precipitation_amount",
        "wetdays",
        "cwd"
    )
    
    for m in tqdm.tqdm(thesis.models):
        for i in indicators:
            # Apply to historical data.
            filename = settings.dir_data / settings.site / "indicators" / "historical" / "reference" / f"{m}_{i}.nc"
            label_quantiles(filename, i)
            # Apply to scenario data.
            for s in thesis.scenarios:
                for y in thesis.time_horizons.keys():
                    filename = settings.dir_data / settings.site / "indicators" / s / y / f"{m}_{i}.nc"
                    label_quantiles(filename, i)
