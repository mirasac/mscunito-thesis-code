import pathlib

import matplotlib.pyplot as plt
import xarray

import braun.utils.generic
import plots
import settings
import thesis

def ax_distribution(ax, model, experiment, period, thresholds, bins=None, cumulative=False, norm=None, **norm_kwargs):
    ds = xarray.load_dataset(settings.dir_data / settings.site / "indicators" / experiment / period / "risk" / f"{model}.nc", decode_timedelta=False)
    x = ds["risk"].values.flatten()
    if norm == "minmax":
        x = braun.utils.generic.minmax(x, **norm_kwargs)
        thresholds = braun.utils.generic.minmax(thresholds, **norm_kwargs)
    elif norm == "standardize":
        x = braun.utils.generic.standardize(x, **norm_kwargs)
        thresholds = braun.utils.generic.standardize(thresholds, **norm_kwargs)
    ax.hist(x, bins=bins, density=True, cumulative=cumulative, orientation="horizontal", color="black")
    if cumulative:
        ax.set_xlabel("Frequency")
    else:
        ax.set_xlabel("Density")
    ax.grid(visible=True, which="major", axis="both")
    ax.set_title(period)
    plots.ax_risk_categories(ax, thresholds)

def plot_compare_distribution(model, experiment, period, bins=None, cumulative=False, norm=False, **norm_kwargs):
    path_leaf = pathlib.Path(settings.site) / "indicators" / experiment / period / "risk"
    thresholds = None
    with xarray.open_dataset(settings.dir_data / settings.site / "indicators" / "historical" / "reference" / "risk" / f"{model}.nc", decode_timedelta=False) as ds_ref:
        thresholds = braun.utils.generic.get_risk_thresholds(ds_ref["risk"].values.flatten(), n_categories=len(thesis.risk_categories))
    
    fig = plt.figure(num=1, figsize=plots.FIGSIZE, clear=True, layout="constrained")
    axes = fig.subplots(nrows=1, ncols=2, sharex=True, sharey=True, squeeze=False)
    
    ax_distribution(axes[0][0], model, "historical", "reference", thresholds, bins=bins, cumulative=cumulative, norm=norm, **norm_kwargs)
    ylabel = "Risk value"
    if norm == "minmax":
        ylabel = f"{ylabel} (min-max normalised)"
    elif norm == "standardize":
        ylabel = f"{ylabel} (standardised)"
    axes[0][0].set_ylabel(ylabel)
    axes[0][0].legend(title="Risk")
    ax_distribution(axes[0][1], model, experiment, period, thresholds, bins=bins, cumulative=cumulative, norm=norm, **norm_kwargs)
    
    # Show interactive plot.
    #plt.show()
    
    # Save plot to file.
    dir_cumulative = ""
    if cumulative:
        dir_cumulative = "cumulative"
    dir_out = settings.dir_figures / path_leaf / "distribution" / dir_cumulative
    dir_out.mkdir(parents=True, exist_ok=True)
    fig.savefig(dir_out / f"{model}.pdf")
    
    fig.clear()
    plt.close(fig)

def plot_compare_distribution_all(model, experiment, bins=None, cumulative=False, norm=False, **norm_kwargs):
    path_leaf = pathlib.Path(settings.site) / "indicators"
    thresholds = None
    with xarray.open_dataset(settings.dir_data / path_leaf / "historical" / "reference" / "risk" / f"{model}.nc", decode_timedelta=False) as ds_ref:
        thresholds = braun.utils.generic.get_risk_thresholds(ds_ref["risk"].values.flatten(), n_categories=len(thesis.risk_categories))
    
    fig = plt.figure(num=1, figsize=plots.FIGSIZE, clear=True, layout="constrained")
    axes = fig.subplots(nrows=1, ncols=4, sharex=True, sharey=True, squeeze=False)
    
    ax_distribution(axes[0][0], model, "historical", "reference", thresholds, bins=bins, cumulative=cumulative, norm=norm, **norm_kwargs)
    ylabel = "Risk value"
    if norm == "minmax":
        ylabel = f"{ylabel} (min-max normalised)"
    elif norm == "standardize":
        ylabel = f"{ylabel} (standardised)"
    axes[0][0].set_ylabel(ylabel)
    axes[0][0].legend(title="Risk")
    
    for y, ax in zip(thesis.time_horizons.keys(), axes[0][1:]):
        ax_distribution(ax, model, experiment, y, thresholds, bins=bins, cumulative=cumulative, norm=norm, **norm_kwargs)
    
    # Show interactive plot.
    #plt.show()
    
    # Save plot to file.
    dir_cumulative = ""
    if cumulative:
        dir_cumulative = "cumulative"
    dir_out = settings.dir_figures / path_leaf / experiment / "risk" / "distribution" / dir_cumulative
    dir_out.mkdir(parents=True, exist_ok=True)
    fig.savefig(dir_out / f"{model}.pdf")
    
    fig.clear()
    plt.close(fig)

if __name__ == "__main__":
    for m in thesis.models:
        for s in thesis.scenarios:
            plot_compare_distribution_all(m, s, bins=200, cumulative=False)
            plot_compare_distribution_all(m, s, bins=200, cumulative=True)
            for y in thesis.time_horizons.keys():
                plot_compare_distribution(m, s, y, bins=200, cumulative=False)
                plot_compare_distribution(m, s, y, bins=200, cumulative=True)
