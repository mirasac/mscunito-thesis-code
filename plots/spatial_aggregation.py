import pathlib

import cartopy.crs
import matplotlib
import matplotlib.pyplot as plt
import numpy

import braun.packages.xeofs
import plots
import settings
import thesis

def ax_EOF_explained(ax, model, indicator, experiment, period):
    filename = settings.dir_data / settings.site / "indicators" / experiment / period / "hazard" / f"{model}_{indicator}.nc.xeofs"
    model = braun.packages.xeofs.load(filename)
    da = model.explained_variance_ratio()
    x = da["mode"].values
    y = da.values
    y_cumsum = numpy.cumsum(y)
    
    ax.plot(x, y_cumsum, marker='.', label=indicator)

def plot_EOF_explained(model, experiment, period):
    evr_threshold = 0.95
    
    fig = plt.figure(num=1, figsize=plots.FIGSIZE, clear=True, layout="constrained")
    ax = fig.add_subplot()
    for i in thesis.INDICATORS:
        ax_EOF_explained(ax, model, i, experiment, period)
    ax.legend()
    ax.axhline(y=evr_threshold, linestyle="dashed", color="black")
    
    ax.grid(visible=True, which="major", axis='x')
    ax.set_xlabel("Number of PCs")
    ax.locator_params(axis='x', integer=True)
    
    ax.grid(visible=True, which="both", axis='y')
    ax.set_ylabel("Cumulative explained variance ratio")
    
    # Interactive blocking plot.
    #plt.show()
    
    # Save plot to file.
    dir_out = settings.dir_figures / settings.site / "indicators" / experiment / period / "hazard" / "explained"
    dir_out.mkdir(parents=True, exist_ok=True)
    f = model
    fig.savefig(dir_out / f"{f}.pdf")
    fig.savefig(dir_out / f"{f}.png", transparent=False, dpi=300.0)
    
    # Clear memory.
    fig.clear()
    plt.close(fig)

def plot_EOF_EOF_map(model, indicator, experiment, period, mode=1):
    """Plot the EOF selected by `mode` on a map,
    the vector components are normalised with L2 norm.
    """
    path_leaf = pathlib.Path(settings.site) / "indicators" / experiment / period / "hazard"
    filename = settings.dir_data / path_leaf / f"{model}_{indicator}.nc.xeofs"
    model_xeofs = braun.packages.xeofs.load(filename)
    da = model_xeofs.components(normalized=True)[i].sel(mode=mode, drop=True)
    
    projection = cartopy.crs.PlateCarree()
    crs = cartopy.crs.PlateCarree()
    
    fig = plt.figure(num=1, figsize=(plots.FIGSIZE[0] * 2.0 / 3.0, plots.FIGSIZE[1]), clear=True, layout="constrained")
    
    ax = fig.add_subplot(projection=projection)
    da.plot(
        ax=ax,
        x="longitude",
        y="latitude",
        transform=crs,
        robust=False,
        alpha=0.5,
        cbar_kwargs={"label": "L2-normalised component", "shrink": 0.8}
    )
    plots.set_map(ax=ax, extent=plots.EXTENT)
    plots.plot_site(thesis.coords[settings.site][1], thesis.coords[settings.site][0], ax=ax, label="Torino-Caselle")
    ax.gridlines(
        crs=crs,
        draw_labels={"bottom": 'x', "left": 'y'},
        xlocs=da["longitude"].values,
        ylocs=da["latitude"].values,
        color="grey",
        alpha=0.5,
        linestyle="dashed"
    )
    
    # Save plot to file.
    dir_out = settings.dir_figures / path_leaf / "EOF"
    dir_out.mkdir(parents=True, exist_ok=True)
    fig.savefig(dir_out / f"{model}_{indicator}.pdf")
    
    # Free memory.
    plt.close(fig)

def plot_EOF_2EOF_map(model, indicator, experiment, period):
    """Plot the first two EOFs on a map,
    the vector components are normalised with L2 norm.
    """
    path_leaf = pathlib.Path(settings.site) / "indicators" / experiment / period / "hazard"
    filename = settings.dir_data / path_leaf / f"{model}_{indicator}.nc.xeofs"
    model_xeofs = braun.packages.xeofs.load(filename)
    ds = model_xeofs.components(normalized=True)
    
    projection = cartopy.crs.PlateCarree()
    crs = cartopy.crs.PlateCarree()
    
    fg = ds[i].sel(mode=[1, 2]).plot(
        x="longitude",
        y="latitude",
        col="mode",
        figsize=plots.FIGSIZE,
        transform=crs,
        subplot_kws={"projection": projection},
        robust=True,
        alpha=0.5,
        cbar_kwargs={"label": "L2-normalised vector component", "pad": 0.05, "shrink": 0.8}
    )
    fig = fg.fig
    
    # Apply to all projection axes.
    for ax in fg.axs.ravel():
        plots.set_map(ax, extent=plots.EXTENT)
        plots.plot_site(thesis.coords[settings.site][1], thesis.coords[settings.site][0], ax=ax, label="Torino-Caselle")
    
    ax_1 = fg.axs.ravel()[0]
    ax_1.set_title("First EOF")
    ax_1.gridlines(
        crs=crs,
        draw_labels={"bottom": "x", "left": "y"},
        xlocs=ds["longitude"].values,
        ylocs=ds["latitude"].values,
        color="grey",
        alpha=0.5,
        linestyle="dashed"
    )
    
    ax_2 = fg.axs.ravel()[1]
    ax_2.set_title("Second EOF")
    ax_2.gridlines(
        crs=crs,
        draw_labels={"bottom": "x"},
        xlocs=ds["longitude"].values,
        ylocs=ds["latitude"].values,
        color="grey",
        alpha=0.5,
        linestyle="dashed"
    )
    
    fig.subplots_adjust(right=0.8, left=0.1, wspace=0.1)  # Put last before rendering.
    
    # Show interactive plot.
    #plt.show()
    
    # Save plot to file.
    dir_out = settings.dir_figures / path_leaf / "EOF"
    dir_out.mkdir(parents=True, exist_ok=True)
    fig.savefig(dir_out / f"{model}_{indicator}.pdf")
    
    # Clear memory, both are necessary because
    # the xarray plotting facility is not well under control.
    fig.clear()
    plt.close(fig)

def ax_EOF_2PC(ax, model, indicator, experiment, period):
    path_leaf = pathlib.Path(settings.site) / "indicators" / experiment / period / "hazard"
    filename = settings.dir_data / path_leaf / f"{model}_{indicator}.nc.xeofs"
    model_xeofs = braun.packages.xeofs.load(filename)
    da = model_xeofs.scores(normalized=True)
    parameters = list(da.sizes.keys())
    parameters.remove("mode")
    da = da.stack(dim={'c': parameters})
    
    ax.scatter(da.sel(mode=1).values, da.sel(mode=2).values, marker='.', label=indicator)

def plot_EOF_2PC(model, experiment, period):
    """Scatter plot of the first two PCs,
    the scores are normalised with L2 norm.
    """
    fig = plt.figure(num=1, figsize=plots.FIGSIZE, clear=True, layout="constrained")
    ax = fig.add_subplot()
    for i in thesis.INDICATORS:
        ax_EOF_2PC(ax, model, i, experiment, period)
    ax.legend()
    ax.grid(visible=True, which="both", axis="both")
    ax.set_xlabel("L2-normalised first PC")
    ax.set_ylabel("L2-normalised second PC")
    
    # Interactive blocking plot.
    #plt.show()
    
    # Save plot to file.
    dir_out = settings.dir_figures / settings.site / "indicators" / experiment / period / "hazard" / "PC"
    dir_out.mkdir(parents=True, exist_ok=True)
    fig.savefig(dir_out / f"{model}.pdf")
    
    # Clear memory.
    fig.clear()
    plt.close(fig)

if __name__ == "__main__":
    # Avoid errors about running in non-main thread.
    matplotlib.use("agg")
    
    import tqdm
    
    for m in tqdm.tqdm(thesis.models):
        # Plot cumulative explained variance.
        #plot_EOF_explained(m, "historical", "reference")
        #plot_EOF_2PC(m, "historical", "reference")
        for i in thesis.INDICATORS:
            #plot_EOF_2EOF_map(m, i, "historical", "reference")
            continue
