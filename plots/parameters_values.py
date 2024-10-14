import pathlib

import matplotlib.pyplot as plt
import xarray

import plots
import settings

def plot_parameter(indicator, parameter, xlabel="", ylabel=""):
    path_leaf = pathlib.Path(settings.site) / "indicators" / "historical" / "reference" / "parameters"
    k = f"{indicator}_{parameter}"
    ds = xarray.open_dataset(settings.dir_data / path_leaf / f"{k}.nc")
    
    fig = plt.figure(num=1, figsize=plots.FIGSIZE, clear=True, layout="constrained")
    ax = fig.add_subplot()
    
    dim_m = "model"
    x = ds["quantile"].values
    handle = None
    for i_m in range(ds.sizes[dim_m]):
       y = ds[k].isel({dim_m: i_m}).values
       handle = ax.plot(x, y, alpha=0.33, color="cyan")
    handle[0].set_label("Ensemble members")
    #y_max = ds[k].max(dim=dim_m, skipna=True).values
    #y_min = ds[k].min(dim=dim_m, skipna=True).values
    #ax.fill_between(x, y_max, y_min, alpha=0.33)
    y = ds[k].mean(dim=dim_m, skipna=True).values
    yerr = ds[k].std(dim=dim_m, ddof=1, skipna=True).values
    ax.errorbar(x, y=y, yerr=yerr, color="black", label="Ensemble average")
    
    ax.grid(visible=True, which="both", axis="both")
    ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    # Show interactive plot.
    #plt.show()
    
    # Save plot to file.
    dir_out = settings.dir_figures / path_leaf
    dir_out.mkdir(parents=True, exist_ok=True)
    fig.savefig(dir_out / f"{k}.pdf")
    
    # Be sure to free memory.
    fig.clear()
    plt.close(fig)

if __name__ == "__main__":
    plot_parameter("heat_wave_index", "thresh", xlabel="p2 (quantile order)", ylabel="tasmax / °C")
    plot_parameter("heat_wave_max_length", "thresh_tasmin", xlabel="p3 (quantile order)", ylabel="tasmin / °C")
    plot_parameter("wetdays", "thresh", xlabel="p5 (quantile order)", ylabel="pr / (mm/day)")
