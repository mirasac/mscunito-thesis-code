import pathlib

import cartopy.mpl.geoaxes
import matplotlib.pyplot as plt
import xarray

import plots
import settings
import thesis

def plot_field_sided(model, indicator, experiment, period):
    path_leaf = pathlib.Path(settings.site) / "indicators" / experiment / period / "field"
    filename = settings.dir_data / path_leaf / f"{model}_{indicator}.nc"
    filename_std = filename.parent / "std" / filename.name
    ds = xarray.load_dataset(filename, decode_timedelta=False)
    ds_std = xarray.load_dataset(filename_std, decode_timedelta=False)
    #_ds = ds.assign({f"{indicator}_std": ds_std[indicator]})  # Alternative way to manage data.
    _ds = xarray.concat([ds, ds_std], dim='a')
    parameters = list(_ds.sizes.keys())
    parameters.remove("latitude")
    parameters.remove("longitude")
    parameters.remove('a')
    _ds = _ds.stack(dim={'c': parameters})
    
    projection = cartopy.crs.PlateCarree()
    crs = cartopy.crs.PlateCarree()
    
    for i_combination, _ in enumerate(_ds['c']):
        fg = _ds[indicator].isel(c=i_combination).plot(
            x="longitude",
            y="latitude",
            col='a',
            figsize=plots.FIGSIZE,
            transform=crs,
            subplot_kws={"projection": projection},
            robust=True,
            alpha=0.5,
            cbar_kwargs={"label": f"{indicator} / {ds[indicator].attrs['units']}", "pad": 0.05, "shrink": 0.8}
        )
        fig = fg.fig
        
        # Apply to all projection axes.
        for ax in fg.axs.ravel():
            plots.set_map(ax, extent=plots.EXTENT)
            plots.plot_site(thesis.coords[settings.site][1], thesis.coords[settings.site][0], ax=ax, label="Torino-Caselle")
        
        ax_mean = fg.axs.ravel()[0]
        ax_mean.set_title("Mean")
        ax_mean.gridlines(
            crs=crs,
            draw_labels={"bottom": "x", "left": "y"},
            xlocs=ds["longitude"].values,
            ylocs=ds["latitude"].values,
            color="grey",
            alpha=0.5,
            linestyle="dashed"
        )
        
        ax_std = fg.axs.ravel()[1]
        ax_std.set_title("Standard deviation")
        ax_std.gridlines(
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
        filename = f"{i_combination}.pdf"
        path_out = path_leaf / f"{model}_{indicator}"
        dir_out = settings.dir_figures / path_out
        dir_out.mkdir(parents=True, exist_ok=True)
        fig.savefig(dir_out / filename)
        
        # Print parameter data.
        print(path_out / filename)
        str_parameters = ",\n".join((f"{p}={_ds.isel(c=i_combination)[p].values}" for p in ds.coords))
        print(str_parameters)
        
        # Clear memory, both are necessary because
        # the xarray plotting facility is not well under control.
        fig.clear()
        plt.close(fig)

if __name__ == "__main__":
    for m in thesis.models:
        for i in thesis.INDICATORS:
            print("historical - reference")  # TODO better in a logging system.
            plot_field_sided(model=m, indicator=i, experiment="historical", period="reference")
            print()
            for s in thesis.scenarios:
                for y in tuple(thesis.time_horizons.keys()):
                    print(f"{s} - {y}")  # TODO better in a logging system.
                    plot_field_sided(model=m, indicator=i, experiment=s, period=y)
                    print()
