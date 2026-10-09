# This script checks whether a netcdf file is on the NSIDC polar stereographic #
# north 25 km grid (psn25), by comparing its latitudes/longitudes to those of  #
# the grid description file built by create_grid_psn25.py. The comparison is   #
# also done against the north-south flipped latitudes/longitudes of the file   #
# to detect an inverted y axis (e.g. CryoSat-2 RDEFT4 files).                  #
#                                                                              #
# History : 2026 - initial version by Virginie Guemas                          #
################################################################################
import sys
import os
import argparse
import numpy as np
import xarray as xr

# Input arguments
parser = argparse.ArgumentParser(description='Checks whether a netcdf file is on the NSIDC polar stereographic north 25 km grid by comparing its latitudes/longitudes to those of the grid description file built by create_grid_psn25.py')
parser.add_argument('--checkfile', type=str, required=True, help='Path to the netcdf file to check (e.g. a CryoSat-2 RDEFT4 file)')
parser.add_argument('--checklon', type=str, default='lon', help='Name of the longitude variable in checkfile')
parser.add_argument('--checklat', type=str, default='lat', help='Name of the latitude variable in checkfile')
parser.add_argument('--gridfile', type=str, default='grid.psn25.nc', help='Path to the psn25 grid description file built by create_grid_psn25.py')
parser.add_argument('--lon', type=str, default='glamt', help='Name of the longitude variable in gridfile')
parser.add_argument('--lat', type=str, default='gphit', help='Name of the latitude variable in gridfile')
args = parser.parse_args()

checkfile = args.checkfile
gridfile  = args.gridfile

# Read the latitudes/longitudes of the psn25 grid
if os.path.exists(gridfile):
  grid = xr.open_dataset(gridfile)
else:
  sys.exit('Grid file is missing')

if args.lon not in grid or args.lat not in grid:
  sys.exit('Longitude or latitude variable missing from grid file')

longitude = grid[args.lon].squeeze(drop=True).values
latitude  = grid[args.lat].squeeze(drop=True).values

# Read the latitudes/longitudes of the file to check
if os.path.exists(checkfile):
  check = xr.open_dataset(checkfile)
else:
  sys.exit('Check file is missing')

if args.checklon not in check or args.checklat not in check:
  sys.exit('Longitude or latitude variable missing from check file')

checklon = check[args.checklon].squeeze(drop=True).values
checklat = check[args.checklat].squeeze(drop=True).values

# Compare, as is and flipped along y. Longitude differences are brought back
# into [-180, 180[ and both differences are expressed as distances in km
if checklat.shape != latitude.shape:
  sys.exit('Check file : latitudes have shape ' + str(checklat.shape) + ' instead of ' + str(latitude.shape))

if checklon.shape != longitude.shape:
  sys.exit('Check file : longitudes have shape ' + str(checklon.shape) + ' instead of ' + str(longitude.shape))

# orientation is only a flag to be printed with the results and allows to repeat the verification in the following loop
for orientation, clat, clon in [('as is', checklat, checklon), ('flipped along y', checklat[::-1, :], checklon[::-1, :])]:
  # Differences converted into distances (1 degree of latitude ~ 111 km; 1 degree of
  # longitude ~ 111 km * cos(latitude), which vanishes near the pole where longitude
  # is ill-defined)
  dlat = np.nanmax(np.abs(clat - latitude)) * 111.
  dlon = np.nanmax(np.abs((clon - longitude + 180.) % 360. - 180.) * np.cos(np.radians(latitude))) * 111.
  print('Check file (' + orientation + ') : max distance along latitude = %.3f km, along longitude = %.3f km' % (dlat, dlon))
