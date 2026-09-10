# This script checks the sea masks produced by create_mask_regions.py by
# plotting them on a polar stereographic projection: North Pole for the
# Arctic seas, South Pole for the Antarctic seas. Each sea is filled with a
# different color; ocean grid points not covered by any named sea are shown
# in light blue, land is left as the grey axes background.
#
# It reads the same grid file as create_mask_regions.py for the longitude
# and latitude, and the mask file it writes (outfile there) for the sea
# masks -- run create_mask_regions.py first, from this same directory.
#
# History : 2026 - initial version by Claude Sonnet 5, at Virginie Guemas' request
######################################################################
import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap, BoundaryNorm

# Input arguments -- keep this in sync with create_mask_regions.py
grid = 'cnrmcm7'
#grid = 'N3.2_O1L42'

if grid == 'N3.2_O1L42':

   gridfile = os.path.expanduser('~/mytools/postdoc2014/MasksArctic/mesh_mask_nemo.N3.2_O1L42.nc')
   lon_name = 'nav_lon'
   lat_name = 'nav_lat'
   maskfile = 'mask.ArcticSeas.N3.2_O1L42.nc'

elif grid == 'cnrmcm7':

   gridfile = '/home/guemas/mytools/cnrmcm7/masks/mesh_mask.nc'
   lon_name = 'glamt'
   lat_name = 'gphit'
   maskfile = 'mask.ArcticSeas.cnrmcm7.nc'

else:

   raise SystemExit('unknown input grid')

gridtmp = xr.open_dataset(gridfile)
longitude = gridtmp[lon_name].squeeze(drop=True).values
latitude = gridtmp[lat_name].squeeze(drop=True).values

masks = xr.open_dataset(maskfile)

# Seas defined in create_mask_regions.py, grouped by hemisphere. The
# aggregated masks (globocea, nhemisph, shemisph, antarcti, arcticoc,
# mediterr) are left out, since coloring them too would just paint over the
# individual seas; globocea is used below for the ocean/land background.
antarctic_seas = ['rossseax', 'amundsen', 'bellings', 'weddells', 'lazarevs',
                   'riiserla', 'cosmonau', 'cooperat', 'davissea', 'tryoshni',
                   'mawsonse', 'dumontdu', 'somovsea']
arctic_seas = ['framstra', 'eastsibe', 'laptevse', 'karaseax', 'barentse',
               'whitesea', 'greenlds', 'norwegia', 'icelands', 'davisstr',
               'hudsonst', 'hudsonba', 'baffinba', 'lincolns', 'nwpassag',
               'beaufort', 'chukchis']


def stereographic(lat, lon, hemisphere):
    """Polar stereographic projection on a unit sphere, pole at the centre."""
    lat_r = np.radians(lat)
    lon_r = np.radians(lon)
    if hemisphere == 'south':
        lat_r = -lat_r
    rho = np.cos(lat_r) / (1.0 + np.sin(lat_r))
    x = rho * np.sin(lon_r)
    y = -rho * np.cos(lon_r)
    if hemisphere == 'south':
        x = -x
    return x, y


def rho_of(lat, hemisphere):
    lat_r = np.radians(-lat if hemisphere == 'south' else lat)
    return np.cos(lat_r) / (1.0 + np.sin(lat_r))


def plot_hemisphere(hemisphere, seas, lat_cutoff, title, outfig):

    x, y = stereographic(latitude, longitude, hemisphere)
    keep = (latitude > lat_cutoff) if hemisphere == 'north' else (latitude < lat_cutoff)

    ocean = masks['globocea'].squeeze(drop=True).values
    index = np.where(keep & (ocean > 0.5), 0, np.nan)

    labels = ['Ocean (unclassified)']
    for i, name in enumerate(seas, start=1):
        sea = masks[name].squeeze(drop=True).values
        index = np.where(keep & (sea > 0.5), i, index)
        labels.append(masks[name].attrs.get('long_name', name))

    cmap_colors = ['#dbeeff'] + list(plt.get_cmap('tab20').colors[:len(seas)])
    cmap = ListedColormap(cmap_colors)
    norm = BoundaryNorm(np.arange(-0.5, len(seas) + 1.5, 1), cmap.N)

    fig, ax = plt.subplots(figsize=(9, 8))
    ax.set_facecolor('#4d4d4d')
    ax.pcolormesh(x, y, index, cmap=cmap, norm=norm, shading='auto')

    theta = np.linspace(0, 2 * np.pi, 361)
    lat_refs = range(50, 90, 10) if hemisphere == 'north' else range(-50, -90, -10)
    for lat_ref in lat_refs:
        rho_ref = rho_of(lat_ref, hemisphere)
        ax.plot(rho_ref * np.cos(theta), rho_ref * np.sin(theta), color='white', lw=0.5, ls=':')

    rho_cut = rho_of(lat_cutoff, hemisphere)
    ax.set_xlim(-rho_cut, rho_cut)
    ax.set_ylim(-rho_cut, rho_cut)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title)

    handles = [mpatches.Patch(color=c, label=l) for c, l in zip(cmap_colors, labels)]
    ax.legend(handles=handles, bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=7, frameon=False)

    fig.savefig(outfig, dpi=150, bbox_inches='tight')


plot_hemisphere('north', arctic_seas, 45, 'Arctic seas (' + grid + ')', 'check_masks_arctic.png')
plot_hemisphere('south', antarctic_seas, -45, 'Antarctic seas (' + grid + ')', 'check_masks_antarctic.png')
plt.show()
