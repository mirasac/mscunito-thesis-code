import pathlib

import matplotlib.pyplot as plt
import xarray

import braun.utils.generic
import plots
import settings
import thesis

def plot_risk_errorbar(experiment, period):
    """Beware that it takes a lot of resources to plot and it is not informative."""
    path_leaf = pathlib.Path(settings.site) / "indicators" / experiment / period / "risk"
    ds = xarray.load_dataset(
        settings.dir_data / path_leaf / "ensemble.nc",
        decode_timedelta=False,
        drop_variables=["min", "max"]
    )
    dim_c = 'c'
    ds = ds.stack(dim={dim_c: [...]}, create_index=False)
    
    fig = plt.figure(num=1, figsize=plots.FIGSIZE, clear=True, layout="constrained")
    ax = fig.add_subplot()
    
    ax.errorbar(ds[dim_c].values, ds["mean"].values, yerr=ds["std"].values)
    ax.grid(visible=True, which="major", axis="both")
    
    # Show interactive plot.
    #plt.show()
    
    # Save plot to file.
    dir_out = settings.dir_figures / path_leaf
    dir_out.mkdir(parents=True, exist_ok=True)
    fig.savefig(dir_out / f"errorbar.pdf")
    
    fig.clear()
    plt.close(fig)

# TODO this function is very similar to ax_parameter_same,
# they could be one working only on argument `parameter`,
# which if it is a list, the function works as ax_parameter_same.
def ax_parameter(ax, scenario, period, parameter, indexers=None, norm=None, **norm_kwargs):
    """Data are restricted to a 1D array with coordinates specified by
    dict `indexers`. By default all coordinates are set to the median index,
    rounded down in case of dimension of even size, except for the coordinate
    named as `parameter` which is used as independent variable.
    """
    ds = xarray.load_dataset(
        settings.dir_data / settings.site / "indicators" / scenario / period / "risk" / "ensemble.nc",
        decode_timedelta=False,
        drop_variables=["min", "max", "category"]
    )
    if indexers is None:
        indexers = {k: v // 2 for k, v in ds.sizes.items()}
    else:
        indexers = indexers.copy()  # To avoid passing a changed dict to future calls.
    indexers.pop(parameter, None)
    ds = ds.isel(indexers=indexers)
    # Check actual parameters values.
    print(parameter)
    print(dict(ds.coords))
    print()
    
    y = ds["mean"].values
    yerr = ds["std"].values
    if norm == "minmax":
        y = braun.utils.generic.minmax(y, **norm_kwargs)
        yerr = yerr / (norm_kwargs["max_value"] - norm_kwargs["min_value"])
    elif norm == "standardize":
        y = braun.utils.generic.standardize(y, **norm_kwargs)
        yerr = yerr / norm_kwargs["sigma"]
    
    ax.errorbar(ds[parameter].values, y, yerr=yerr, marker='.', color="black", linestyle="")
    ax.grid(visible=True, which="major", axis="both")
    ax.set_title(period)

def plot_parameter_all(scenario, parameter, xlabel="", indexers=None, norm=None):
    path_leaf = pathlib.Path(settings.site) / "indicators"
    thresholds = None
    norm_kwargs = {}
    with xarray.open_dataset(settings.dir_data / path_leaf / "historical" / "reference" / "risk" / "ensemble.nc", decode_timedelta=False) as ds_ref:
        array = ds_ref["mean"].values.flatten()
        thresholds = braun.utils.generic.get_risk_thresholds(array, n_categories=len(thesis.risk_categories))
        if norm == "minmax":
            norm_kwargs["min_value"] = array.min()
            norm_kwargs["max_value"] = array.max()
            thresholds = braun.utils.generic.minmax(thresholds, **norm_kwargs)
        elif norm == "standardize":
            norm_kwargs["mu"] = array.mean()
            norm_kwargs["sigma"] = array.std(ddof=1)
            thresholds = braun.utils.generic.standardize(thresholds, **norm_kwargs)
    
    fig = plt.figure(num=1, figsize=plots.FIGSIZE, clear=True, layout="constrained")
    axes = fig.subplots(nrows=1, ncols=3, sharex=True, sharey=True, squeeze=False)
    
    for y, ax in zip(thesis.time_horizons.keys(), axes[0]):
        ax_parameter(ax, scenario, y, parameter, indexers=indexers, norm=norm, **norm_kwargs)
        ax.set_xlabel(xlabel)
    
    ylabel = "Risk value"
    if norm is not None:
        ylabel = f"{ylabel} (rescaled)"
    axes[0][0].set_ylabel(ylabel)
    for ax in axes[0]:
        ax.set_xlim(ax.get_xlim())  # Fix axis limits manually.
        ax.set_ylim(ax.get_ylim())  # Fix axis limits manually.
        plots.ax_risk_categories(ax, thresholds)  # Put here to use final axes size.
    axes[0][0].legend(title="Risk", reverse=True)
    
    # Show interactive plot.
    #plt.show()
    
    # Save plot to file.
    dir_out = settings.dir_figures / path_leaf / scenario / "risk"
    dir_out.mkdir(parents=True, exist_ok=True)
    f = parameter
    fig.savefig(dir_out / f"{f}.pdf")
    fig.savefig(dir_out / f"{f}.png", transparent=False, dpi=300.0)
    
    # Be sure to free memory.
    fig.clear()
    plt.close(fig)

def ax_parameter_same(ax, scenario, period, dimensions, indexers=None, norm=None, **norm_kwargs):
    """Plot data having same coordinates for the two values in `dimensions`.
    Other coordinates are restricted with the indices specified in `indexers`,
    by default they are set to the median index or the lowest of the
    two median indices in case of even dimension.
    
    Beware that no check is made to ensure that all coordinates are
    present in `indexers`, the restriction must result in a 2D plot.
    Also no check is made on size of dimensions with names in `dimensions`,
    values are selected base on the first dimension.
    """
    if len(dimensions) != 2:
        raise ValueError("Can plot same value of only two dimensions.")
    ds = xarray.load_dataset(
        settings.dir_data / settings.site / "indicators" / scenario / period / "risk" / "ensemble.nc",
        decode_timedelta=False,
        drop_variables=["min", "max", "category"]
    )
    if indexers is None:
        indexers = {k: v // 2 for k, v in ds.sizes.items()}
    else:
        indexers = indexers.copy()  # To avoid passing a changed dict to future calls.
    for d in dimensions:
        indexers.pop(d, None)
    ds = ds.isel(indexers=indexers)
    # Check actual parameters values.
    print('-'.join(dimensions))
    print(dict(ds.coords))
    print()
    
    x = []
    y = []
    yerr = []
    for i, v in enumerate(ds[dimensions[0]].values):
        x.append(v)
        y.append(ds["mean"].isel(indexers={dimensions[0]: i, dimensions[1]: i}, drop=True).values)
        yerr.append(ds["std"].isel(indexers={dimensions[0]: i, dimensions[1]: i}, drop=True).values)
    if norm == "minmax":
        y = braun.utils.generic.minmax(y, **norm_kwargs)
        yerr = yerr / (norm_kwargs["max_value"] - norm_kwargs["min_value"])
    elif norm == "standardize":
        y = braun.utils.generic.standardize(y, **norm_kwargs)
        yerr = yerr / norm_kwargs["sigma"]
    
    ax.errorbar(x, y, yerr=yerr, marker='.', color="black", linestyle="")
    ax.grid(visible=True, which="major", axis="both")
    ax.set_title(period)

def plot_parameter_same_all(scenario, dimensions, xlabel="", indexers=None, norm=None):
    path_leaf = pathlib.Path(settings.site) / "indicators"
    thresholds = None
    norm_kwargs = {}
    with xarray.open_dataset(settings.dir_data / path_leaf / "historical" / "reference" / "risk" / "ensemble.nc", decode_timedelta=False) as ds_ref:
        array = ds_ref["mean"].values.flatten()
        thresholds = braun.utils.generic.get_risk_thresholds(array, n_categories=len(thesis.risk_categories))
        if norm == "minmax":
            norm_kwargs["min_value"] = array.min()
            norm_kwargs["max_value"] = array.max()
            thresholds = braun.utils.generic.minmax(thresholds, **norm_kwargs)
        elif norm == "standardize":
            norm_kwargs["mu"] = array.mean()
            norm_kwargs["sigma"] = array.std(ddof=1)
            thresholds = braun.utils.generic.standardize(thresholds, **norm_kwargs)
    
    fig = plt.figure(num=1, figsize=plots.FIGSIZE, clear=True, layout="constrained")
    axes = fig.subplots(nrows=1, ncols=3, sharex=True, sharey=True, squeeze=False)
    
    for y, ax in zip(thesis.time_horizons.keys(), axes[0]):
        ax_parameter_same(ax, scenario, y, dimensions, indexers=indexers, norm=norm, **norm_kwargs)
        ax.set_xlabel(xlabel)
    
    ylabel = "Risk value"
    if norm is not None:
        ylabel = f"{ylabel} (rescaled)"
    axes[0][0].set_ylabel(ylabel)
    for ax in axes[0]:
        ax.set_xlim(ax.get_xlim())  # Fix axis limits manually.
        ax.set_ylim(ax.get_ylim())  # Fix axis limits manually.
        plots.ax_risk_categories(ax, thresholds)  # Put here to use final axes size.
    axes[0][0].legend(title="Risk", reverse=True)
    
    # Show interactive plot.
    #plt.show()
    
    # Save plot to file.
    dir_out = settings.dir_figures / path_leaf / scenario / "risk"
    dir_out.mkdir(parents=True, exist_ok=True)
    f = '-'.join(dimensions)
    fig.savefig(dir_out / f"{f}.pdf")
    fig.savefig(dir_out / f"{f}.png", transparent=False, dpi=300.0)
    
    # Be sure to free memory.
    fig.clear()
    plt.close(fig)

def plot1(indexers=None):
    for s in thesis.scenarios:
        plot_parameter_all(s, "heat_wave_max_length_window", xlabel="p1 / day", indexers=indexers, norm="minmax")
        plot_parameter_all(s, "heat_wave_max_length_thresh_tasmax", xlabel="p2 (quantile order)", indexers=indexers, norm="minmax")
        plot_parameter_all(s, "heat_wave_max_length_thresh_tasmin", xlabel="p3 (quantile order)", indexers=indexers, norm="minmax")

def plot2(indexers=None):
    for s in thesis.scenarios:
        plot_parameter_same_all(s, ["wetdays_thresh", "cwd_thresh"], xlabel="p5 (quantile order)", indexers=indexers, norm="minmax")
        plot_parameter_same_all(s, ["heat_wave_index_thresh", "heat_wave_max_length_thresh_tasmax"], xlabel="p2 (quantile order)", indexers=indexers, norm="minmax")
        plot_parameter_same_all(s, ["heat_wave_index_window", "heat_wave_max_length_window"], xlabel="p1 / day", indexers=indexers, norm="minmax")

def plot3(indexers=None):
    for s in thesis.scenarios:
        plot_parameter_all(s, "max_n_day_precipitation_amount_window", xlabel="p4 / day", indexers=indexers, norm="minmax")

def plot4(indexers=None):
    for s in thesis.scenarios:
        plot_parameter_all(s, "heat_wave_index_thresh", xlabel="p2 (quantile order)", indexers=indexers, norm="minmax")

if __name__ == "__main__":
    indexers = {
        "heat_wave_index_window": 1,  # Value of 4 day.
        "heat_wave_index_thresh": 2,  # Median value of the parameter set.
        "heat_wave_max_length_window": 1,  # Value of 4 day.
        "heat_wave_max_length_thresh_tasmax": 2,  # Median value of the parameter set.
        "heat_wave_max_length_thresh_tasmin": 2,  # Median value of the parameter set.
        "max_n_day_precipitation_amount_window": 4,  # Value of 5 day.
        "wetdays_thresh": 2,  # Median value of the parameter set.
        "cwd_thresh": 2  # Median value of the parameter set.
    }
    plot1(indexers=indexers)
    plot2(indexers=indexers)
    plot3(indexers=indexers)
    plot4(indexers=indexers)
