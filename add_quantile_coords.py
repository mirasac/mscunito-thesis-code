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
    # Open function from xarray guarantees round trip even if naturals are loaded as timedelta.
    ds = xarray.load_dataset(filename_bak)
    _ds = None
    # TODO better do this in a programmatic way.
    if indicator in ("heat_wave_index",):
        _ds = ds.assign_coords({"thresh_q": ("thresh", thesis.p2)})
    elif indicator in ("heat_wave_max_length",):
        _ds = ds.assign_coords({"thresh_tasmin_q": ("thresh_tasmin",  thesis.p3)})
        _ds = _ds.assign_coords({"thresh_tasmax_q": ("thresh_tasmax",  thesis.p2)})
    elif indicator in ("wetdays", "cwd"):
        _ds = ds.assign_coords({"thresh_q": ("thresh", thesis.p5)})
    if _ds is not None:
        _ds.to_netcdf(filename)
    else:
        _ds = ds
        filename_bak.rename(filename)
    return _ds

if __name__ == "__main__":
    for m in tqdm.tqdm(thesis.models):
        for i in thesis.INDICATORS:
            # Apply to historical data.
            filename = settings.dir_data / settings.site / "indicators" / "historical" / "reference" / f"{m}_{i}.nc"
            label_quantiles(filename, i)
            # Apply to scenario data.
            for s in thesis.scenarios:
                for y in thesis.time_horizons.keys():
                    filename = settings.dir_data / settings.site / "indicators" / s / y / f"{m}_{i}.nc"
                    label_quantiles(filename, i)
