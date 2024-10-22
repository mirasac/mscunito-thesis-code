import pathlib

import matplotlib.pyplot as plt
import numpy
import xarray

import braun.utils.generic
import plots
import settings
import thesis

def ax_window(ax, scenario, period, indexers=None, norm=None, **norm_kwargs):
    """Plot risk values depending on heat_wave_index_window,
    heat_wave_max_length_window and max_n_day_precipitation_amount_window,
    the first two are set to the same values.
    Other coordinates are restricted with the indices specified in `indexers`,
    by default they are set to the median index or the lowest of the
    two median indices in case of even dimension.
    
    Beware that no check is made to ensure that all coordinates are
    present in `indexers`, the restriction must result in a 2D plot.
    
    Return the array of points where parameters have same values,
    risk values are normalised as specified by parameter `norm`.
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
    indexers.pop("heat_wave_index_window")
    indexers.pop("heat_wave_max_length_window")
    indexers.pop("max_n_day_precipitation_amount_window")
    ds = ds.isel(indexers=indexers)
    # Check actual parameters values.
    print("window")
    print(dict(ds.coords))
    print()
    
    # TODO very inefficient way to prepare data,
    # use parallelisation instead, e.g. numpy.meshgrid.
    x = ds["heat_wave_index_window"].values
    y = ds["max_n_day_precipitation_amount_window"].values
    xx, yy = numpy.meshgrid(x, y)
    x_2D = []
    y_2D = []
    z_2D = []
    z_same = []
    zerr_2D = []
    zerr_same = []
    for i, v in enumerate(ds["heat_wave_index_window"].values):
        x_2D.append(ds.sizes["max_n_day_precipitation_amount_window"] * [v])
        y_2D.append(y)
        z_2D.append(ds["mean"].isel(indexers={"heat_wave_index_window": i, "heat_wave_max_length_window": i}, drop=True).values)
        zerr_2D.append(ds["std"].isel(indexers={"heat_wave_index_window": i, "heat_wave_max_length_window": i}, drop=True).values)
        # Values are integers, hence selection by value is exact.
        z_same.append(ds["mean"].sel(indexers={"heat_wave_index_window": v, "heat_wave_max_length_window": v, "max_n_day_precipitation_amount_window": v}, drop=True).values)
        zerr_same.append(ds["std"].sel(indexers={"heat_wave_index_window": v, "heat_wave_max_length_window": v, "max_n_day_precipitation_amount_window": v}, drop=True).values)
    x = numpy.asarray(x_2D).flatten()
    y = numpy.asarray(y_2D).flatten()
    z = numpy.asarray(z_2D).flatten()
    zerr = numpy.asarray(zerr_2D).flatten()
    z_same = numpy.asarray(z_same).flatten()
    zerr_same = numpy.asarray(zerr_same).flatten()
    if norm == "minmax":
        z = braun.utils.generic.minmax(z, **norm_kwargs)
        zerr = zerr / (norm_kwargs["max_value"] - norm_kwargs["min_value"])
        z_same = braun.utils.generic.minmax(z_same, **norm_kwargs)
        zerr_same = zerr_same / (norm_kwargs["max_value"] - norm_kwargs["min_value"])
    elif norm == "standardize":
        z = braun.utils.generic.standardize(z, **norm_kwargs)
        zerr = zerr / norm_kwargs["sigma"]
        z_same = braun.utils.generic.standardize(z_same, **norm_kwargs)
        zerr_same = zerr_same / norm_kwargs["sigma"]
    
    ax.errorbar(x, y, z, zerr=zerr, errorevery=3, marker='.', color="black", linestyle="")
    
    x = ds["heat_wave_index_window"].values
    
    xx, zz = numpy.meshgrid(x, ax.get_zlim())#[z.min(), z.max()])
    ax.plot_surface(xx, xx, zz, color="grey", alpha=0.5)
    ax.plot(x, x, z_same, color="black")
    
    ax.view_init(elev=20, azim=-60)
    ax.set_title(period)
    
    return numpy.stack((x, z_same, zerr_same), axis=0)

def plot_window_all(scenario, xlabel="", ylabel="", indexers=None, norm=None):
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
    
    periods = tuple(thesis.time_horizons.keys())
    axes = fig.subplots(nrows=1, ncols=len(periods), sharex=True, sharey=True, squeeze=False, subplot_kw={"projection": "3d"})
    
    for y, ax in zip(periods, axes[0]):
        ax_window(ax, scenario, y, indexers=indexers, norm=norm, **norm_kwargs)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    
    zlabel = "Risk value"
    if norm is not None:
        zlabel = f"{zlabel} (rescaled)"
    axes[0][0].set_zlabel(zlabel)
    
    w_pad = fig.get_layout_engine().get().get("w_pad")
    fig.get_layout_engine().set(wspace=w_pad)
    
    # Show interactive plot.
    #plt.show()
    
    # Save plot to file.
    dir_out = settings.dir_figures / path_leaf / scenario / "risk"
    dir_out.mkdir(parents=True, exist_ok=True)
    fig.savefig(dir_out / "window.pdf")
    
    # Be sure to free memory.
    fig.clear()
    plt.close(fig)

def plot_window(scenario, period, xlabel="", ylabel="", indexers=None, norm=None):
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
    
    fig.add_subplot(1, 2, 1, projection="3d")
    fig.add_subplot(1, 2, 2)
    axes = fig.get_axes()
    
    array_same = ax_window(axes[0], scenario, period, indexers=indexers, norm=norm, **norm_kwargs)
    axes[0].set_title("")
    axes[0].set_xlabel(xlabel)
    axes[0].set_ylabel(ylabel)
    zlabel = "Risk value"
    if norm is not None:
        zlabel = f"{zlabel} (rescaled)"
    #axes[0].set_zlabel(zlabel)  # Overlaps with the y axis label of the next plot.
    
    axes[1].errorbar(array_same[0], array_same[1], yerr=array_same[2], color="black")
    axes[1].set_xlim(axes[1].get_xlim())  # Fix axis limits manually.
    axes[1].set_ylim(axes[1].get_ylim())  # Fix axis limits manually.
    plots.ax_risk_categories(axes[1], thresholds)  # Put here to use final axes size.
    axes[1].grid(visible=True, which="major", axis="both")
    axes[1].set_ylabel(zlabel)
    axes[1].set_xlabel("Consecutive days")
    axes[1].legend(loc="upper right", title="Risk", reverse=True)
    
    # Show interactive plot.
    #plt.show()
    
    # Save plot to file.
    dir_out = settings.dir_figures / path_leaf / scenario / "risk"
    dir_out.mkdir(parents=True, exist_ok=True)
    f = f"window_{period}"
    fig.savefig(dir_out / f"{f}.pdf")
    fig.savefig(dir_out / f"{f}.png", transparent=False, dpi=300.0)
    
    # Be sure to free memory.
    fig.clear()
    plt.close(fig)

def plot1(indexers=None):
    for s in thesis.scenarios:
        #plot_window_all(s, xlabel="p1 / day", ylabel="p4 / day", indexers=indexers, norm="minmax")
        for y in thesis.time_horizons.keys():
            plot_window(s, y, xlabel="p1 / day", ylabel="p4 / day", indexers=indexers, norm="minmax")

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
