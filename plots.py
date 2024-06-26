import xarray

def _coordinates_facet(xobject: xarray.Dataset | xarray.DataArray):
    # Assume coordinates are in ascending order, hence facet plot is created
    # by assigning lowest index to top left axes. Align axes position
    # with spatial position for a more intuitive reading of the figure by
    # inverting order of latitude, cf. https://stackoverflow.com/a/72970086.
    return xobject.isel(latitude=slice(None, None, -1))

def coordinates_facet(da, **kwargs):
    da = _coordinates_facet(da)
    row = kwargs.pop("row", "latitude")
    col = kwargs.pop("col", "longitude")
    _plot = da.plot(col=col, row=row, **kwargs)
    return _plot

def yearly_mean_time_series_facet(da, resample_frequency="YS", window_size=5, **kwargs):
    da = da.resample(time=resample_frequency).mean()
    da = da.rolling(time=window_size).mean()
    _plot = coordinates_facet(da, **kwargs)
    for ax in _plot.axs.ravel():
        ax.grid(which="both")
        # Make more readable the x axis labels, cf. https://stackoverflow.com/a/49714879,
        # actually performs better than xarray.plot.FacetGrid.set_ticks.
        for i, label in enumerate(ax.xaxis.get_ticklabels()):
            if i % 2 != 0:
                label.set_visible(False)
    return _plot

def scatter_facet(ds, x, y, **kwargs):
    ds = _coordinates_facet(ds)
    row = kwargs.pop("row", "latitude")
    col = kwargs.pop("col", "longitude")
    _plot = ds.plot.scatter(x=x, y=y, col=col, row=row, **kwargs)
    for ax in _plot.axs.ravel():
        ax.grid(which="both")
    return _plot

def daily_anomaly(da_model, da_climatology):
    _plot = yearly_mean_time_series_facet(da_model.groupby("time.dayofyear") - da_climatology.sel(quantity="mean"))
    return _plot
