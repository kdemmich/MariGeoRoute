"""Module to create map with route."""
import numpy as np
"""Cartopy is a Python package designed for geospatial data processing in order to produce maps 
and other geospatial data analyses"""
import cartopy.crs as ccrs
import cartopy.feature as cf
from geovectorslib import geod
from matplotlib.figure import Figure

from routeparams import RouteParams


"""lat1 : initial latitude 
   lat2 : Final latitude
   lon1 : initial longitude 
   lon2 : Final Longitude """


def get_gcr_points(lat1, lon1, lat2, lon2, n_points=10):
    """Discretize gcr between two scalar coordinate points."""
    points = [(lat1, lon1)]

    inv = geod.inverse([lat1], [lon1], [lat2], [lon2])
    dist = inv['s12'] / (n_points)

    for i in range(n_points):
        dir = geod.direct(lat1, lon1, inv['azi1'], dist)
        points.append((dir['lat2'][0], dir['lon2'][0]))
        lat1 = dir['lat2'][0]
        lon1 = dir['lon2'][0]
        inv = geod.inverse([lat1], [lon1], [lat2], [lon2])

    return points


def create_maps(lat1, lon1, lat2, lon2, dpi, winds, n_maps):
    """Return map figure."""
    fig = Figure(
        figsize=(1600 / dpi, 800 * n_maps / dpi),
        dpi=dpi)
    fig.set_constrained_layout_pads(
        w_pad=4. / dpi,
        h_pad=4. / dpi)

    """Add gcrs between provided points to the map figure."""
    path = get_gcr_points(lat1, lon1, lat2, lon2, n_points=10)
    print(path)
    for i in range(n_maps):
        ax = fig.add_subplot(n_maps+1, 1, i+1, projection=ccrs.PlateCarree())
        ax.set_extent([lon1, lon2, lat1, lat2], crs=ccrs.PlateCarree())
        ax.add_feature(cf.LAND)
        ax.add_feature(cf.OCEAN)
        ax.add_feature(cf.COASTLINE)
        ax.gridlines(draw_labels=True)

        hour = i // 3 * 3
        u, v, lats, lons = winds[int(hour)]
        ax.barbs(lons, lats, u, v, length=5,
                 sizes=dict(emptybarb=0.25, spacing=0.2, height=0.5),
                 linewidth=0.95)

        lats = [x[0] for x in path]
        lons = [x[1] for x in path]
        ax = fig.get_axes()[0]
        ax.plot(lons, lats, 'r-', transform=ccrs.PlateCarree())
    return fig


def create_map(lat1, lon1, lat2, lon2, dpi):
    """Return map figure."""
    fig = Figure(
        figsize=(1200 / dpi, 420 / dpi),
        dpi=dpi)
    fig.set_constrained_layout_pads(
        w_pad=4. / dpi,
        h_pad=4. / dpi)
    ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    fig.subplots_adjust(
        left=0.05,
        right=0.95,
        bottom=0,
        top=1,
        wspace=0,
        hspace=0)
    #ax.set_extent([lon1, lon2, lat1, lat2], crs=ccrs.PlateCarree())
    ax.add_feature(cf.LAND)
    ax.add_feature(cf.OCEAN)
    ax.add_feature(cf.COASTLINE)
    ax.gridlines(draw_labels=True)
    return fig


def plot_barbs(fig, winds):
    """Add barbs to the map figure."""
    u = winds['u']
    v = winds['v']
    lats = winds['lats_u']
    lons = winds['lons_u']
	
    #comment in for CMEMS data
    u = np.delete(u,1, 0)
    v = np.delete(v, 1, 0)
    lats = np.delete(lats, 1, 0)
    lons = np.delete(lons, 1, 0)

    rebinx=5  #CMEMS
    rebiny=11

    #rebinx=1   #NCEP
    #rebiny=1

    u = rebin(u, rebinx, rebiny)
    v = rebin(v, rebinx, rebiny)
    lats = rebin(lats, rebinx, rebiny)
    lons = rebin(lons, rebinx, rebiny)

    ax = fig.get_axes()[0]
    ax.barbs(lons, lats, u, v, length=5,
             sizes=dict(emptybarb=0.25, spacing=0.2, height=0.5),
             linewidth=0.95)
    # ax.quiver(lons, lats, u, v)
    return fig


def plot_gcr(fig, lat1, lon1, lat2, lon2):
    """Add gcrs between provided points to the map figure."""
    path = get_gcr_points(lat1, lon1, lat2, lon2, n_points=10)
    lats = [x[0] for x in path]
    lons = [x[1] for x in path]

    ax = fig.get_axes()[0]
    ax.plot(lons, lats, 'g', transform=ccrs.PlateCarree())
    return fig


def plot_route(fig, route: RouteParams, colour):
    """
    Add isochrone to the map figure.
    Input: dictionary from move_boat_direct
    """
    ax = fig.get_axes()[0]
    lats = route.lats_per_step
    lons = route.lons_per_step
    ax = fig.get_axes()[0]
    # for i in range(len(lats)):
    #     ax.plot(lons[i], lats[i], 'ro')

    legend_entry = str(route.route_type) + ' (fuel: ' +  '%0.2f' % route.fuel + 't, time: ' + str(route.time) + 'h)'

    ax.plot(lons, lats, colour, label=legend_entry, transform=ccrs.PlateCarree())

    return fig

def plot_legend(fig):
    ax = fig.get_axes()[0]
    ax.legend()
    return fig

def get_colour(i):
    colours = ['darkred', 'gold', 'seagreen', 'peachpuff', 'darkviolet']
    if(i>4):
        raise ValueError('currently only 5 colours available, asking for' + str(i))
    return colours[i]

def rebin(a,rebinx, rebiny):
    if not ((a.shape[0] % rebinx) == 0): raise ValueError('Invalid rebinx')
    if not ((a.shape[1] % rebiny) == 0): raise ValueError('Invalid rebiny')

    newshape_x = int(a.shape[0]/rebinx)
    newshape_y = int(a.shape[1]/rebiny)

    sh = newshape_x, rebinx, newshape_y, rebiny
    return a.reshape(sh).mean(-1).mean(1)
