# This script builds a NEMO mesh_mask-like grid description file for the     #
# NSIDC polar stereographic north 25 km grid (psn25), used by the            #
# NOAA/NSIDC CDR of sea ice concentration (G02202) and by the CryoSat-2      #
# RDEFT4 sea ice thickness product. The output file contains :               #
#   glamt / gphit : longitude / latitude of the cell centres (degrees)       #
#   tmaskutil     : land-sea mask (1 ocean, 0 elsewhere)                     #
#   e1t / e2t     : length of the cells along x / y (m)                      #
#                                                                            #
# The cell centres (x, y in m) and the projection parameters are read from   #
# a NOAA/NSIDC CDR V6 monthly file; latitudes, longitudes and map scale      #
# factor are computed with the ellipsoidal polar stereographic formulas of   #
# Snyder (1987), Map Projections - A Working Manual, USGS Prof. Paper 1395.  #
# The land-sea mask is taken from the surface_type_mask of the               #
# same file (group cdr_supplementary).                                       #
#                                                                            #
# History : 2026 - initial version by Virginie Guemas                        #
##############################################################################
import sys
import os
import argparse
import datetime
import getpass
import numpy as np
import xarray as xr

# Input arguments
parser = argparse.ArgumentParser(description='Builds a NEMO mesh_mask-like grid description file (glamt, gphit, tmaskutil, e1t, e2t) for the NSIDC polar stereographic north 25 km grid')
parser.add_argument('--cdrfile', type=str, required=True, help='Path to a NOAA/NSIDC CDR V6 monthly north netcdf file (sic_psn25_YYYYMM_*_v06r00.nc)')
parser.add_argument('--ocean_types', type=str, default='ocean,polehole_mask', help='Comma-separated surface_type_mask flags for surface types counted as ocean in tmaskutil (default: ocean,polehole_mask ; lake and coast are left out)')
# coast should be excluded because the land pollutes the radiation and sea ice concentration appears to be falsely high
# This phenomenon is calles spillover.
parser.add_argument('--out', type=str, default='grid.psn25.nc', help='Path to the output netcdf file')
args = parser.parse_args()

cdrfile     = args.cdrfile
ocean_types = args.ocean_types.split(',')
outfile     = args.out

# Read the cell centre positions in meters and the projection parameters
if os.path.exists(cdrfile):
  cdr = xr.open_dataset(cdrfile)
else:
  sys.exit('CDR file is missing')

if 'crs' not in cdr or 'x' not in cdr or 'y' not in cdr:
  sys.exit('crs, x or y missing from CDR file')

crs = cdr['crs'].attrs
if crs.get('grid_mapping_name') != 'polar_stereographic' or float(crs['latitude_of_projection_origin']) != 90.:
  sys.exit('Only the north polar stereographic projection is handled')

# We need to account for the ellipsoid shape of Earth instead of a sphere, 
# otherwise positions would be shifted by a few km (up to about a quarter of
# a grid cell). We read the parameters of the stereographic projection inside
# the NSIDC file in case they change those parameters in next versions.
#
# A is the radius of the Earth from the Earth center to the equator
A     = float(crs['semi_major_axis'])
# B is the radius of the Earth from the Earth center to the north/south pole
# (difference of about 21km between A and B)
# B is not read directly : the file gives the flattening f = (A-B)/A instead
f     = 1. / float(crs['inverse_flattening'])
# With A and B, we can convert the x and y distance of the nsidc psn25 files into
# correct longitudes and latitudes on the Earth
# NEMO considers the Earth to be a sphere, rather than an ellipsoid. No such problem.

# eccentricity
e2    = 2. * f - f * f
e     = np.sqrt(e2)

# lat_c is the latitude at which grid cells have dimension 25 km x 25 km, both 
# on the map and on the Earth
# Cells are squares everywhere (conformal projection) but those squares cover a
# larger surface when closer to the pole, a smaller surface southward from lat_c
# even though the map scale states 25km (it is 25km only at lat_c)
lat_c = np.radians(float(crs['standard_parallel']))
# lon0 is the longitude that goes toward the bottom when the stereographic
# projection is plotted. We need it to find the longitude of the x, y points 
# (incorrect lon0 would mean systematic shift)
lon0  = np.radians(float(crs['straight_vertical_longitude_from_pole']))

x = cdr['x'].values
y = cdr['y'].values
# x and y are list of coordinates
# We turn those into a 2d-numpy-array, xx[j, i], yy[j, i]
# j, i because that's how NSIDC data are organized
xx, yy = np.meshgrid(x, y)

# Snyder (1987), polar stereographic ellipsoidal formulas (stereomap_dist and Earth_parallel_radius functions, t and m in Snyder)
def stereomap_dist(lat):
# tan(pi/4 -lat/2) is the distance between a point and the center of the stereographic
#       projection for a sphere, not an absolute distance but to a factor
#       This factor is deduced from the NSIDC grid description:
#       sqrt(x*x + y*y) = proj_factor * stereomap_dist(lat) at any latitude, and
#       proj_factor is chosen so that at lat_c = 70N  
#       sqrt(x*x + y*y) = A * Earth_parallel_radius(70), hence
#       proj_factor = A * Earth_parallel_radius(70) / stereomap_dist(70)
# (1 - e * sin lat) / (1 + e * sin lat) ** e/2 is a correction factor for the ellipsoid
  return np.tan(np.pi / 4. - lat / 2.) / ((1. - e * np.sin(lat)) / (1. + e * np.sin(lat))) ** (e / 2.)

def Earth_parallel_radius(lat):
# A * cos lat would be the distance between the Earth rotation axis and a latitude 
#           circle if Earth was a sphere
# sqrt(1 - e2*sin lat ^2) is a correction factor for the ellipsoid
# A * Earth_parallel_radius(lat) is the actual distance between the Earth rotation axis and a latitude circle
  return np.cos(lat) / np.sqrt(1. - e2 * np.sin(lat) ** 2)

def inv_stereomap_dist(t):
# Inverse projection, Snyder (1987) ellipsoidal polar stereographic (north polar case)
# Inverse of stereomap_dist : returns the latitude lat such that stereomap_dist(lat) = t
# chi is the latitude for a sphere (tan(pi/4 - chi/2) = t), the series in sin(2 chi),
# sin(4 chi)... corrects for the ellipsoid
  chi = np.pi / 2. - 2. * np.arctan(t)
  lat = chi + (e2 / 2. + 5. * e2 ** 2 / 24. + e2 ** 3 / 12. + 13. * e2 ** 4 / 360.) * np.sin(2. * chi) \
            + (7. * e2 ** 2 / 48. + 29. * e2 ** 3 / 240. + 811. * e2 ** 4 / 11520.) * np.sin(4. * chi) \
            + (7. * e2 ** 3 / 120. + 81. * e2 ** 4 / 1120.) * np.sin(6. * chi) \
            + (4279. * e2 ** 4 / 161280.) * np.sin(8. * chi)
  if not np.allclose(stereomap_dist(lat), t, rtol=1e-9):
    sys.exit('Inverse projection failed : stereomap_dist(lat) differs from t')
  return lat

# Distance between a point (x,y) and the center of the stereographic projection on the map
rho = np.hypot(xx, yy)
# Factor between stereomap_dist and the distance to the pole on the map (see stereomap_dist)
proj_factor = A * Earth_parallel_radius(lat_c) / stereomap_dist(lat_c)
# t is stereomap_dist(lat) for the (still unknown) latitude of each point
t   = rho / proj_factor
lat = inv_stereomap_dist(t)
# np.arctan2 (xx, -yy) gives the angle between the vertical line going from the map center 
# towards the bottom and an arrow going from the map center to the coordinates x, y
lon = lon0 + np.arctan2(xx, -yy)

# We finally obtain the latitudes and longitudes of each point in degrees
latitude  = np.degrees(lat)
# We make sure that we end in [-180, 180[ 
longitude = (np.degrees(lon) + 180.) % 360. - 180.

# Map scale factor scale_factor = rho / (A Earth_parallel_radius(lat)) (Snyder 1987): the projection is conformal, so the
# Cell dimensions are the nominal ones divided by scale_factor along x and y
scale_factor = rho / (A * Earth_parallel_radius(lat))
# scale_factor = 1 at lat = 70N
dx = np.abs(x[1] - x[0])
dy = np.abs(y[1] - y[0])
# psn25 grid is regular, always 25km in our example
e1t = dx / scale_factor
e2t = dy / scale_factor
# The scale_factor accounts for the correction of the 25km as a function of the distance
# to the pole

# Land-sea mask from the surface type of the CDR file
stmfile = xr.open_dataset(cdrfile, group='cdr_supplementary')
# cdr_supplementary is a group of variables in the CDF file
if 'surface_type_mask' not in stmfile:
  sys.exit('surface_type_mask missing from the cdr_supplementary group of the CDR file')

# surface_type_mask is an Xarray with one value per surface type 
# (squeeze(drop=True) allows to remove the time dimension)
stm      = stmfile['surface_type_mask'].squeeze(drop=True)
# meanings are the names of the surface types that are associated with a value
# flag_meanings = ocean lake polehole_mask coast land in the current file
meanings = stm.attrs['flag_meanings'].split()
# flag_values are stored in the same order as the flag_meanings = value for each surface type 
values   = list(stm.attrs['flag_values'])
for ocean_type in ocean_types:
  if ocean_type not in meanings:
# ocean_types are written by the users so we check they are indeed in the list of available types
    sys.exit('Surface type ' + ocean_type + ' not found in surface_type_mask flag_meanings : ' + ' '.join(meanings))
# meanings.index(ocean_type) is the position of the value associated with ocean_type
# with the line below, we build a list of the flag values that will tell us a point is valid in our field
ocean_values = [values[meanings.index(ocean_type)] for ocean_type in ocean_types]
# if stm.values take one of the values listed in ocean_values, it becomes True, otherwise False
# .astype('int8') converts to 1/0
tmaskutil    = np.isin(stm.values, ocean_values).astype('int8')

if tmaskutil.shape != latitude.shape:
  sys.exit('surface_type_mask and x/y don\'t have the same dimensions')

# Define the observational meshmask 
dims = ('y', 'x')
grid = xr.Dataset(attrs=dict(description = 'NEMO mesh_mask-like grid description of the NSIDC polar stereographic north 25 km grid (psn25)', projection = crs.get('proj4text', ''), initial_cdrfile = cdrfile, ocean_types = ','.join(ocean_types), creation_date = str(datetime.datetime.now()), created_by = getpass.getuser()))
# 'proj4text' is an attributes describing the NSIDC projection (lat_c = 70 ...), if absent this attributes is empty
grid['glamt']     = xr.DataArray(longitude, dims=dims, attrs=dict(long_name = 'Longitude of the cell centres', units = 'degrees_east'))
grid['gphit']     = xr.DataArray(latitude, dims=dims, attrs=dict(long_name = 'Latitude of the cell centres', units = 'degrees_north'))
grid['tmaskutil'] = xr.DataArray(tmaskutil, dims=dims, attrs=dict(long_name = 'Land-sea mask (1 for ' + ', '.join(ocean_types) + ', 0 elsewhere)'))
grid['e1t']       = xr.DataArray(e1t, dims=dims, attrs=dict(long_name = 'Cell length along x', units = 'm'))
grid['e2t']       = xr.DataArray(e2t, dims=dims, attrs=dict(long_name = 'Cell length along y', units = 'm'))

# Write the output netcdf file
grid.to_netcdf(outfile)
