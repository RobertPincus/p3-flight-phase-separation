#! /usr/bin/env python

import xarray as xr
import numpy as np
import seaborn as sns
import datetime
import yaml

import colorcet as cc
import pathlib

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


dataDir = pathlib.Path('/Users/robert/Dropbox/Scientific/Projects/ATOMIC:EURECA4/data')
segDir  = pathlib.Path('./flight_phase_files')
figDir = pathlib.Path('.')
#
# Can I get the list of dates automatically? Until then...
#
flight_dates = ['2020-01-17', '2020-01-19', '2020-01-23',
                '2020-01-24', '2020-01-31',
                '2020-02-03', '2020-02-04', '2020-02-05',
                '2020-02-09', '2020-02-10', '2020-02-11']

seg_col_dict = {"circle":cc.glasbey_cool[1],
                "profile":cc.glasbey_cool[2],
                "transit":cc.glasbey_cool[3],
                "cloud":cc.glasbey_cool[5]}

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
    gl.ylabels_right = False
    gl.xlabels_bottom = False
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

    with PdfPages('flight-segment-figures.pdf') as pdf:
        #
        # Open data, flight segment files
        #
        f1 = xr.open_dataset(sorted(dataDir.joinpath('flight-level-summary/Level_2').glob("*.nc"))[0])
        f1 = f1.where(f1.alt > 0, drop=True)
        f1_segments = yaml.safe_load(open('/Users/robert/Codes/p3-flight-phase-separation/flight_phase_files/example.yaml'))


        #
        # Side view
        #
        sns.set_context("paper")
        fig = plt.figure(figsize = (7.5,8.5))

        # The whole flight track
        plt.plot(f1.time, f1.alt,
                 lw=2, c = "black")

        for s in f1_segments["segments"]:
            seg = f1.sel(time = slice(s["start"], s["end"]))
            kind = s["kinds"][0]
            plt.plot(seg.time, seg.alt,
                     lw=2, c = seg_col_dict[kind], label=kind)

        plt.legend(fontsize=10,framealpha=0.8,markerscale=5)
        pdf.savefig()

        #
        # Plan view
        #
        sns.set_context("paper")
        fig = plt.figure(figsize = (7.5,8.5))
        ax  = set_up_map(plt)
        add_gridlines(ax)

        for s in f1_segments["segments"]:
            seg = f1.sel(time = slice(s["start"], s["end"]))
            kind = s["kinds"][0]
            ax.plot(seg.lon,seg.lat,lw=2,alpha=0.5,c=seg_col_dict[kind],
                    transform=ccrs.PlateCarree(),zorder=7)

        pdf.savefig()
