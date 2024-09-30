import xeofs

def _aggregate_temporal(ds, **kwargs):
    """Implementation of aggregation on the temporal dimension."""
    return ds.mean(dim="time", **kwargs)

def aggregate_temporal(ds, path=None, **kwargs):
    """Perform aggregation on temporal dimension `time`.
    
    Parameters
    ----------
    ds : xarray.Dataset
        Dataset containing a single indicator as variable and
        time, latitude, longitude and parameters as dimensions.
    path : str, pathlib.Path
        Filename of the aggregated dataset to save it to disk.
        By default no saving is performed.
    
    Return
    ------
    Tuple of objects, the first one is the aggregated dataset.
    """
    _ds = ds.chunk(chunks={"time": -1})
    _ds = _aggregate_temporal(_ds, **kwargs)
    if path is not None:
        _ds.to_netcdf(path)
    return (_ds,)

def _aggregate_spatial(ds, latitude, longitude):
    """Implementation of aggregation on the spatial dimensions."""
    dim = list(ds.sizes.keys())
    dim.remove(latitude)
    dim.remove(longitude)
    model = xeofs.models.EOF(n_modes=5, compute=False, solver="full", use_coslat=True)
    model.fit(ds, dim=dim)
    _da = model.scores(normalized=False).sel(mode=1, drop=True)
    _da.attrs.pop("solver_kwargs", None)  # This variable gives problems when saving NetCDF. 
    _ds = _da.to_dataset(name=list(ds.data_vars.keys())[0])
    return (_ds, model)

def aggregate_spatial(ds, path=None, latitude="latitude", longitude="longitude"):
    """Perform aggregation on spatial dimensions `latitude` and `longitude`.
    
    Parameters
    ----------
    ds : xarray.Dataset
        Dataset containing a single indicator as variable and
        latitude, longitude and parameters as dimensions.
    path : str, pathlib.Path
        Filename of the aggregated dataset to save it to disk.
        By default no saving is performed.
    latitude : str
        Name of the latitude dimension, specify if the dataset uses a different one.
    longitude : str
        Name of the longitude dimension, specify if the dataset uses a different one.
    
    Return
    ------
    Tuple of objects, the first one is the aggregated dataset.
    """
    _ds = ds.chunk(chunks={latitude: -1, longitude: -1})
    _ds, model = _aggregate_spatial(_ds, latitude, longitude)
    if path is not None:
        _ds.to_netcdf(path)
    return (_ds, model)
