import pathlib

import matplotlib.pyplot as plt
import xarray

# Set up default directory for generated figures.
_dir_document = pathlib.Path.home() / "mscunito-thesis-document"
_dir_figures = _dir_document / "figures"
if not _dir_document.exists():
    _dir_figures = pathlib.Path.cwd() / "figures"
_dir_figures.mkdir(parents=False, exist_ok=True)

def savefig(fname, format=None, **kwargs):
    """Similar to matplotlib.pyplot.savefig but with files stored
    in the default directories for the thesis figures.
    """
    if fname is not None and len(plt.get_fignums()) > 0:
        path = _dir_figures / fname
        plt.savefig(path, format=format, **kwargs)
        #plt.show()  # TODO probably this is needed outside Jupyter notebooks.

def autosavefig(func):
    def wrapper(*args, **kwargs):
        # Manage default arguments for saving, by default do not save figure.
        fname = kwargs.pop("fname", None)
        format = kwargs.pop("format", None)
        # Call plotting function.
        _return = func(*args, **kwargs)
        # Sometimes the returned object is not a Figure object but a wrapper,
        # hence use the current figure, which should be always correct to save.
        savefig(fname, format)
        return _return
    return wrapper

def _coordinates_facet(xobject: xarray.Dataset | xarray.DataArray):
    # Assume coordinates are in ascending order, hence facet plot is created
    # by assigning lowest index to top left axes. Align axes position
    # with spatial position for a more intuitive reading of the figure by
    # inverting order of latitude, cf. https://stackoverflow.com/a/72970086.
    return xobject.isel(latitude=slice(None, None, -1))

@autosavefig
def coordinates_facet(da, **kwargs):
    da = _coordinates_facet(da)
    row = kwargs.pop("row", "latitude")
    col = kwargs.pop("col", "longitude")
    _plot = da.plot(col=col, row=row, **kwargs)
    for ax in _plot.axs.ravel():
        ax.grid(which="both")
    return _plot

@autosavefig
def yearly_mean_time_series_facet(da, resample_frequency="YS", window_size=5, **kwargs):
    da = da.resample(time=resample_frequency).mean()
    da = da.rolling(time=window_size).mean()
    _plot = coordinates_facet(da, **kwargs)
    for ax in _plot.axs.ravel():
        # Make more readable the x axis labels, cf. https://stackoverflow.com/a/49714879,
        # actually performs better than xarray.plot.FacetGrid.set_ticks.
        for i, label in enumerate(ax.xaxis.get_ticklabels()):
            if i % 2 != 0:
                label.set_visible(False)
    return _plot

@autosavefig
def scatter_facet(ds, x, y, **kwargs):
    ds = _coordinates_facet(ds)
    row = kwargs.pop("row", "latitude")
    col = kwargs.pop("col", "longitude")
    _plot = ds.plot.scatter(x=x, y=y, col=col, row=row, **kwargs)
    for ax in _plot.axs.ravel():
        ax.grid(which="both")
    return _plot

@autosavefig
def daily_anomaly(da_model, da_climatology):
    _plot = yearly_mean_time_series_facet(da_model.groupby("time.dayofyear") - da_climatology.sel(quantity="mean"))
    return _plot

@autosavefig
def data_vars_1d(ds, data_vars=None, label_attrs_key=None, **kwargs):
    if data_vars is None:
        data_vars = ds.data_vars
    label = kwargs.pop("label", None)
    _plot = plt.figure()
    for v in data_vars:
        if label is None:
            label = ds[v].name
        if label_attrs_key is not None:
            label = ds[v].attrs[label_attrs_key]
        ds[v].plot(label=label, **kwargs)
    _plot.axes[0].grid(which="both")
    return _plot
