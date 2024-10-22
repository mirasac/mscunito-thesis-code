import cartopy.crs
import matplotlib
import matplotlib.pyplot as plt

import plots
import settings
import thesis

def plot_site_map():
    projection = cartopy.crs.PlateCarree()
    crs = cartopy.crs.PlateCarree()
    
    fig = plt.figure(num=1, figsize=(plots.FIGSIZE[1], plots.FIGSIZE[1]), clear=True, layout="constrained")
    ax = fig.add_subplot(projection=projection)
    
    extent_IT = (6, 19, 36, 48)  # Include Italy's borders.
    _half_width = 2.0
    extent = (
        thesis.coords[settings.site][1] - _half_width,
        thesis.coords[settings.site][1] + _half_width,
        thesis.coords[settings.site][0] - _half_width,
        thesis.coords[settings.site][0] + _half_width
    )
    ax.set_extent(extent, crs=crs)
    plots.add_background(ax)
    plots.add_regions(ax)
    plots.plot_site(
        thesis.coords[settings.site][1],
        thesis.coords[settings.site][0],
        ax=ax,
        label="Torino-Caselle",
        text_kwargs={"bbox": {"color": "white", "linewidth": 0, "alpha": 0.8, "boxstyle": "round"}}
    )
    ax.add_feature(cartopy.feature.BORDERS)
    ax.add_feature(cartopy.feature.COASTLINE)
    ax.gridlines(
        crs=crs,
        draw_labels={"bottom": "x", "left": "y"},
        dms=False,
        formatter_kwargs={"number_format": "#.1f"},
        color="grey",
        alpha=0.5,
        linestyle="dashed"
    )
    ax.text(
        -0.2,
        0.5,
        "latitude",
        transform=ax.transAxes,
        horizontalalignment="center",
        rotation="vertical",
        rotation_mode="anchor",
        verticalalignment="bottom"
    )
    ax.text(
        0.5,
        -0.075,
        "longitude",
        transform=ax.transAxes,
        horizontalalignment="center",
        rotation="horizontal",
        rotation_mode="anchor",
        verticalalignment="top"
    )
    
    # Interactive blocking plot.
    #plt.show()
    
    # Save plot to file.
    dir_out = settings.dir_figures
    dir_out.mkdir(parents=True, exist_ok=True)
    f = "site_country"
    fig.savefig(dir_out / f"{f}.pdf")
    fig.savefig(dir_out / f"{f}.png", transparent=False, dpi=300.0)
    
    # Clear memory.
    fig.clear()
    plt.close(fig)

if __name__ == "__main__":
    # Avoid errors about running in non-main thread.
    matplotlib.use("agg")
    
    plot_site_map()
