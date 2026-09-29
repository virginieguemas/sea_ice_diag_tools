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
# History : 2026 - initial version by Virginie Guemas 
######################################################################
import sys
import os
import argparse
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap, BoundaryNorm

# Input arguments
parser = argparse.ArgumentParser(description='Checks the sea masks produced by create_mask_regions.py by plotting them on a polar stereographic projection')
parser.add_argument('--gridfile', type=str, default='/cnrm/ioga/Users/guemas/gridfiles/meshmask/mesh_mask.cnrmcm7.nc', help='Path to the netcdf file containing the longitudes and latitudes')
# For grid N3.2_O1L42, use : /home/guemas/mytools/postdoc2014/MasksArctic/mesh_mask_nemo.N3.2_O1L42.nc
parser.add_argument('--lon', type=str, default='glamt', help='Name of the longitude variable')
# For grid N3.2_O1L42, use : nav_lon
parser.add_argument('--lat', type=str, default='gphit', help='Name of the latitude variable')
# For grid N3.2_O1L42, use : nav_lat
parser.add_argument('--mask', type=str, default='/cnrm/ioga/Users/guemas/gridfiles/seas/mask.ArcticSeas.cnrmcm7.nc', help='Path to the mask netcdf file produced by create_mask_regions.py')
# For grid N3.2_O1L42, use : mask.ArcticSeas.N3.2_O1L42.nc
parser.add_argument('--label', type=str, default='cnrmcm7', help='Grid label used in the plot titles')
# For grid N3.2_O1L42, use : N3.2_O1L42
parser.add_argument('--latcutoff', type=float, default=45, help='Absolute latitude (degrees) at which each polar plot is cut off')
args = parser.parse_args()

gridfile   = args.gridfile
lon_name   = args.lon
lat_name   = args.lat
maskfile   = args.mask
label      = args.label
lat_cutoff = args.latcutoff

if os.path.exists(gridfile):
   gridtmp = xr.open_dataset(gridfile)
else:
   sys.exit('Grid file is missing')

if lon_name not in gridtmp or lat_name not in gridtmp:
   sys.exit('Longitude or latitude variable missing from grid file')

longitude = gridtmp[lon_name].squeeze(drop=True).values
latitude = gridtmp[lat_name].squeeze(drop=True).values

if latitude.shape != longitude.shape:
   sys.exit('Latitudes and longitudes don\'t have the same dimensions')

if os.path.exists(maskfile):
   masks = xr.open_dataset(maskfile)
else:
   sys.exit('Mask file is missing')

if 'globocea' not in masks:
   sys.exit('globocea mask missing from mask file')

if masks['globocea'].squeeze(drop=True).shape != latitude.shape:
   sys.exit('Mask and latitude/longitude don\'t have the same dimensions')

# globocea, nhemisph, shemisph, antarcti, arcticoc, centrarc, margseas, 
# mediterr are left out
# framstra, framstru, framstrv, tryoshni are left out
antarctic_seas = ['rossseax', 'amundsen', 'bellings', 'weddells', 'lazarevs',
                   'riiserla', 'cosmonau', 'cooperat', 'davissea', 
                   'mawsonse', 'dumontdu', 'somovsea']
arctic_seas = ['wcentarc', 'ecentarc', 'eastsibe', 'laptevse', 'karaseax', 
               'barentse', 'whitesea', 'greenlds', 'norwegia', 'icelands', 
               'davisstr', 'hudsonst', 'hudsonba', 'baffinba', 'lincolns', 
               'nwpassag', 'beaufort', 'chukchis']


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


plot_hemisphere('north', arctic_seas, lat_cutoff, 'Arctic seas (' + label + ')', 'check_masks_arctic.png')
plot_hemisphere('south', antarctic_seas, -lat_cutoff, 'Antarctic seas (' + label + ')', 'check_masks_antarctic.png')
plt.show()
