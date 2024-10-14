import pathlib

import cartopy.mpl.geoaxes
import matplotlib.pyplot as plt
import xarray

import plots
import settings
import thesis

def plot_field_anomaly(model, indicator, scenario, cbar_label=None):
    k = f"{model}_{indicator}"
    list_ds = []
    for y in thesis.time_horizons.keys():
        filename_ref = settings.dir_data / settings.site / "indicators" / "historical" / "reference" / "field" / f"{k}.nc"
        path_leaf = pathlib.Path(settings.site) / "indicators" / scenario / y / "field"
        filename = settings.dir_data / path_leaf / f"{k}.nc"
        ds_ref = xarray.load_dataset(filename_ref, decode_timedelta=False)
        ds = xarray.load_dataset(filename, decode_timedelta=False)
        list_ds.append(ds - ds_ref)
    if cbar_label is None:
        cbar_label = f"{indicator} / {ds[indicator].attrs['units']}"
    _ds = xarray.concat(list_ds, dim='s')
    parameters = list(_ds.sizes.keys())
    parameters.remove("latitude")
    parameters.remove("longitude")
    parameters.remove('s')
    _ds = _ds.stack(dim={'c': parameters})
    
    projection = cartopy.crs.PlateCarree()
    crs = cartopy.crs.PlateCarree()
    
    i_combination = 1
    fg = _ds[indicator].isel(c=i_combination).plot(
        x="longitude",
        y="latitude",
        col='s',
        figsize=plots.FIGSIZE, #aspect=1, size=plots.SIZE_A4[1] / 3.0,  # These are alternative.
        transform=crs,
        subplot_kws={"projection": projection},
        robust=True,
        alpha=0.5,
        cbar_kwargs={"label": cbar_label, "pad": 0.05, "shrink": 0.8}
    )
    fig = fg.fig
    
    # Apply to all projection axes, inverted to act on first one after loop.
    list_gl = []
    for s, ax in zip(thesis.time_horizons.keys(), fg.axs.ravel()):
        plots.set_map(ax, extent=plots.EXTENT)
        plots.plot_site(thesis.coords[settings.site][1], thesis.coords[settings.site][0], ax=ax, label="Torino-Caselle")
        ax.set_title(s)
        gl = ax.gridlines(
            crs=crs,
            draw_labels={"bottom": "x"},
            xlocs=ds["longitude"].values,
            ylocs=ds["latitude"].values,
            color="grey",
            alpha=0.5,
            linestyle="dashed"
        )
        list_gl.append(gl)
    
    list_gl[0].left_labels = True
    
    str_parameters = ",\n".join((f"{p}={_ds.isel(c=i_combination)[p].values}" for p in ds.coords))
    print(str_parameters)
    fig.subplots_adjust(right=0.8, left=0.1, wspace=0.1)  # Put last before rendering.
    
    # Show interactive plot.
    #plt.show()
    
    # Save plot to file.
    dir_out = settings.dir_figures / path_leaf.parent.parent / "spatial_bias" / k
    dir_out.mkdir(parents=True, exist_ok=True)
    fig.savefig(dir_out / f"{i_combination}.pdf")
    
    # Be sure to free memory.
    fig.clear()
    plt.close(fig)

if __name__ == "__main__":
    for i in thesis.INDICATORS:
        for s in thesis.scenarios:
            plot_field_anomaly(model="EC-Earth3", indicator=i, scenario=s)
