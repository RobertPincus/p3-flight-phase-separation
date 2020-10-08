#! /usr/bin/env python

import xarray as xr
import numpy as np
import datetime
import yaml
import pathlib
from intake import open_catalog

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from   matplotlib.offsetbox import AnchoredText
from   matplotlib.backends.backend_pdf import PdfPages

import cartopy as cp
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from   cartopy.feature import LAND
from   cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

from   mpl_toolkits.axes_grid1.inset_locator import inset_axes
from   mpl_toolkits.axes_grid1 import make_axes_locatable

import seaborn as sns
import colorcet as cc

########

seg_dir  = pathlib.Path('./flight_phase_files')
cat_dir  = pathlib.Path('/Users/robert/Dropbox/Scientific/Papers/ATOMIC-P3-data/Figures/p3-intake-catalog/')

#
# Can I get the list of dates automatically? Until then...
#
flight_dates = [datetime.date(2020, 1, 17),
                datetime.date(2020, 1, 19),
                datetime.date(2020, 1, 23),
                datetime.date(2020, 1, 24),
                datetime.date(2020, 1, 31),
                datetime.date(2020, 2,  3),
                datetime.date(2020, 2,  4),
                datetime.date(2020, 2,  5),
                datetime.date(2020, 2,  9),
                datetime.date(2020, 2, 10),
                datetime.date(2020, 2, 11)]

seg_col_dict = {"circle":cc.glasbey_cool[1],
                "profile":cc.glasbey_cool[2],
                "transit":cc.glasbey_cool[3],
                "cloud":cc.glasbey_cool[5],
                "axbt":cc.glasbey_cool[7]}

##########################
def set_up_map(plt, lon_w = -60.5, lon_e = -49, lat_s = 10, lat_n = 16.5):
    ax  = plt.axes(projection=ccrs.PlateCarree())
    # Defining boundaries of the plot

    ax.set_extent([lon_w,lon_e,lat_s,lat_n]) # lon west, lon east, lat south, lat north
    ax.coastlines(resolution='10m',linewidth=1.5,zorder=1);
    ax.add_feature(LAND,facecolor='0.9')
    return(ax)


def add_gridlines(ax):
    # Assigning axes ticks
    xticks = np.arange(-65,0,2.5)
    yticks = np.arange(0,25,2.5)
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,linewidth=1, color='black', alpha=0.5, linestyle='dotted')
    gl.xlocator = mticker.FixedLocator(xticks)
    gl.ylocator = mticker.FixedLocator(yticks)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 10, 'color': 'k'}
    gl.ylabel_style = {'size': 10, 'color': 'k'}
#    gl.ylabels_right = False
#    gl.xlabels_bottom = False
    gl.xlabel = {'Latitude'}

if __name__ == "__main__":
    #
    # Graphical choices
    #
    mpl.rcParams['pdf.fonttype'] = 42
    mpl.rcParams['ps.fonttype'] = 42
    mpl.rcParams['font.sans-serif'] = "Arial"
    mpl.rcParams['font.family'] = "sans-serif"
    mpl.rcParams["legend.frameon"] = False

    p3data = open_catalog(str(cat_dir.joinpath('main.yaml')))
    with open("sondes_for_flightphase.yaml") as infile:
        p3_sondes = [s for s in yaml.safe_load(infile) if s["platform"]  == "P3"]
    print("P3 dropped", len(p3_sondes), "total sondes")

    with PdfPages('flight-segment-figures.pdf') as pdf:
        for d in flight_dates:
            #
            # Open data, flight segment files
            #
            print('Flight RF{:02d}'.format(flight_dates.index(d) + 1))
            f1 = p3data.flight_level[d.strftime("P3-%m%d")].to_dask()
            f1 = f1.where(f1.alt > 0, drop=True)
            f1.load()
            todays_sondes = [s for s in p3_sondes if s["launch_time"].date() == d]

            #
            # Plan view
            #
            sns.set_context("paper")
            fig = plt.figure(figsize = (7.5,8.5))
            ax  = set_up_map(plt)
            add_gridlines(ax)

            ax.plot(f1.lon, f1.lat,lw=2,alpha=0.5,c="grey",
                    transform=ccrs.PlateCarree(),zorder=7)

            for s in todays_sondes:
                print("    ", s["sonde_id"], s["launch_time"])
                fld = f1.sel(time=s["launch_time"], method="nearest")
                ax.annotate(s["sonde_id"][8:], (fld.lon, fld.lat),
                            horizontalalignment='left',verticalalignment='top',
                            transform=ccrs.PlateCarree(),zorder=7)

            fl_sonde_times = f1.sel(time = [s["launch_time"] for s in todays_sondes], method = "nearest")
            ax.scatter(fl_sonde_times.lon, fl_sonde_times.lat,
                       lw=2,alpha=0.5,c="red", transform=ccrs.PlateCarree(),zorder=7)

            plt.title('Flight RF{:02d}, '.format(flight_dates.index(d) + 1) + d.strftime('%Y-%m-%d'))
            pdf.savefig()
