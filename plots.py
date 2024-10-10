from cartopy.io import shapereader
import matplotlib.pyplot as plt
import numpy
import xarray

import settings
import thesis

SIZE_A4 = (8.3, 11.7)
"""Units are in inches, correspond to 210 mm x 297 mm."""

# TODO these are thesis-specific values, better put them in settings of thesis.
FIGSIZE = (SIZE_A4[0], SIZE_A4[1] / 3.0)
_half_width = 0.5  # Units: decimal degrees.
EXTENT = (
    thesis.coords[settings.site][1] - _half_width,
    thesis.coords[settings.site][1] + _half_width,
    thesis.coords[settings.site][0] - _half_width,
    thesis.coords[settings.site][0] + _half_width
)

# TODO instead of using this dictionary, load the palette from
# palette.json at startup using the settings for the file path.
PALETTE = {
    "very_low": "#00FF00",
    "low": "#40BF00",
    "intermediate": "#807F00",
    "high": "#C03F00",
    "very_high": "#FF0000"
}

CACHE_SHAPEFILES = {}

# Set up default directory for generated figures.
_dir_figures = settings.dir_figures

def savefig(fname, format=None, **kwargs):
    """Similar to matplotlib.pyplot.savefig but with files stored
    in the default directories for the thesis figures.
    """
    if fname is not None and len(plt.get_fignums()) > 0:
        # Default value.
        bbox_inches = kwargs.pop("bbox_inches", "tight")
        path = _dir_figures / fname
        plt.savefig(path, format=format, bbox_inches=bbox_inches, **kwargs)
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
        savefig(fname, format, bbox_inches="tight")
        return _return
    return wrapper

def cache_shapefile(filename: str):
    if filename not in CACHE_SHAPEFILES:
        CACHE_SHAPEFILES[filename] = list(shapereader.Reader(filename).geometries())
    return CACHE_SHAPEFILES[filename]










######### Utility functions which should go in braun.utils.generic but loading of generic settings is needed #########

def loop_models_indicators(func, models=None, indicators=None, **func_kwargs):
    """Loop for each item in `models` and `indicators` function `func` called
    with arguments `func_kwargs`.
    """
    if models is None:
        models = thesis.models
    if indicators is None:
        indicators = thesis.INDICATORS
    for m in models:
        for i in indicators:
            func(m, i, **func_kwargs)

# TODO improve implementation with recursion, see itertools for inspiration.
def loop_models_indicators_experiments(func, models=None, indicators=None, experiments=None, **func_kwargs):
    """Loop for each item in `models`, `indicators` and `experiments` function
    `func` called with arguments `func_kwargs`.
    """
    if models is None:
        models = thesis.models
    if indicators is None:
        indicators = thesis.INDICATORS
    if experiments is None:
        experiments = ["historical"]
        experiments.extend(thesis.scenarios)
    for m in models:
        for i in indicators:
            for e in experiments:
                func(m, i, e, **func_kwargs)

def is_available_period(experiment, period):
    """Thesis-specific restrictions on temporal dimension.
    It could be performed directly on datasets but
    by design it is applied prior to any coordinate selection.
    """
    _return = False
    if experiment in ("historical",):
        if period in ("reference",):
            _return = True
    elif experiment in thesis.scenarios:
        if period in thesis.time_horizons.keys():
            _return = True
    return _return









######### Generic plots using xarray #########

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
def daily_anomaly_facet(da_model, da_climatology, resample_frequency="YS", window_size=5, **kwargs):
    _plot = yearly_mean_time_series_facet(
        da_model.groupby("time.dayofyear") - da_climatology.sel(quantity="mean"),
        resample_frequency=resample_frequency,
        window_size=window_size,
        **kwargs
    )
    return _plot

@autosavefig
def daily_anomaly(da_model, da_climatology, resample_frequency="YS", window_size=5, **kwargs):
    da = da_model.groupby("time.dayofyear") - da_climatology.sel(quantity="mean")
    da = da.resample(time=resample_frequency).mean()
    da = da.rolling(time=window_size).mean()
    _plot = plt.figure()
    da.plot(**kwargs)
    ax = _plot.axes[0]
    ax.grid(which="both")
    ax.set_ylabel(f"{ax.get_ylabel()} anomaly")
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









######### Plot maps #########

import cartopy.crs
import matplotlib.transforms as trn

def add_background(ax=None):
    # First version: this does not load high-res images.
    #ax.stock_img()
    # Second version: slower except if some caching is implemented.
    #filename_raster = settings.dir_data / "maps" / "backgrounds" / "NE1_HR_LC_SR_W_DR" / "NE1_HR_LC_SR_W_DR.tif"
    #img = plt.imread(filename_raster)
    #with Image.open(filename_raster) as img:
    #    ax.imshow(img, origin="upper", extent=EXTENT, transform=crs)
    from PIL import Image
    
    if ax is None:
        ax = plt.gca()
    max_image_pixels_tmp = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = None
    ax.background_img(name="NaturalEarth1ReliefWaterDrainages", resolution="medium", extent=ax.get_extent(), cache=True)
    Image.MAX_IMAGE_PIXELS = max_image_pixels_tmp
    return ax

def add_borders(ax=None):    
    if ax is None:
        ax = plt.gca()
    filename_regions = settings.dir_data / "maps" / "gadm41_ITA" / "gadm41_ITA_1.shp"
    shapes = cache_shapefile(str(filename_regions.resolve()))
    ax.add_geometries(shapes, cartopy.crs.PlateCarree(), edgecolor=("black", 1.0), facecolor=("grey", 0.0), linestyle="dotted")
    filename_borders = settings.dir_data / "maps" / "gadm41_ITA" / "gadm41_ITA_0.shp"
    shapes = cache_shapefile(str(filename_borders.resolve()))
    ax.add_geometries(shapes, cartopy.crs.PlateCarree(), edgecolor=("black", 1.0), facecolor=("grey", 0.0), linestyle="solid")
    return ax

def set_map(ax=None, extent=None, crs=None):
    if ax is None:
        ax = plt.gca()
    if extent is None:
        ax.set_global()
    else:
        ax.set_extent(extent, crs=crs)
    add_background(ax=ax)
    add_borders(ax=ax)
    return ax

def plot_site(x_site, y_site, ax=None, label=None):
    if ax is None:
        ax = plt.gca()
    markersize = 5
    ax.plot(
        x_site,
        y_site,
        marker='.',
        color="black",
        markersize=markersize,
        alpha=1
    )
    if label is not None:
        geodetic_transform = cartopy.crs.Geodetic()._as_mpl_transform(ax)
        ax.text(
            x_site,
            y_site,
            label,
            verticalalignment="top",
            horizontalalignment="center",
            transform=trn.offset_copy(geodetic_transform, units="dots", y=-1.5 * markersize)
        )
    return ax









######### Other plots #########

def plot_norm_sided(model, indicator, experiment, period):
    """Plot normalised indicator value alongside the original one."""
    dir_data = settings.dir_data / settings.site / "indicators" / experiment / period
    filename = f"{model}_{indicator}.nc"
    ds = xarray.load_dataset(dir_data / "hazard_anomaly" / filename, decode_timedelta=False)
    ds_norm = xarray.load_dataset(dir_data / "normalized" / filename, decode_timedelta=False)
    
    dim_c = 'c'
    ds = ds.stack(dim={dim_c: [...]})
    ds_norm = ds_norm.stack(dim={dim_c: [...]})
    x = numpy.arange(0, ds.sizes[dim_c], 1)
    
    fig = plt.figure(num=1, figsize=FIGSIZE, clear=True, layout="constrained")
    
    axes = fig.subplots(nrows=1, ncols=2, sharex=True, sharey=True, squeeze=False)
    axes[0][0].plot(x, ds[indicator].values, color="black", marker='.', linestyle="dotted")
    axes[0][1].plot(x, ds_norm[indicator].values, color="black", marker='.', linestyle="dotted")

def ax_risk_categories(ax, thresholds):
    """Fill background with colors of risk categories,
    boundaries on y axis are given by values in `thresholds`.
    """
    colors = tuple(PALETTE.values())
    categories = tuple(PALETTE.keys())
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    ax.fill_between(xlim, thresholds[0], y2=ylim[0], edgecolor=None, facecolor=colors[0], alpha=0.8, zorder=0.1)
    for i, y1 in enumerate(thresholds[1:], start=1):
        ax.fill_between(
            xlim,
            y1,
            y2=thresholds[i - 1],
            edgecolor=None,
            facecolor=colors[i - 1],
            alpha=0.8,
            zorder=0.1,
            label=categories[i - 1].replace('_', ' ').capitalize()
        )
    ax.fill_between(
        xlim,
        ylim[1],
        y2=thresholds[-1],
        edgecolor=None,
        facecolor=colors[-1],
        alpha=0.8,
        zorder=0.1
    )
