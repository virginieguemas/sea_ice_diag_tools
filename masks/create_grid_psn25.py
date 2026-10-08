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
parser.add_argument('--checkfile', type=str, default=None, help='Optional netcdf file on the same grid (e.g. a CryoSat-2 RDEFT4 file) whose latitudes/longitudes are compared to the computed ones')
parser.add_argument('--checklon', type=str, default='lon', help='Name of the longitude variable in checkfile')
parser.add_argument('--checklat', type=str, default='lat', help='Name of the latitude variable in checkfile')
parser.add_argument('--out', type=str, default='grid.psn25.nc', help='Path to the output netcdf file')
args = parser.parse_args()

cdrfile     = args.cdrfile
ocean_types = args.ocean_types.split(',')
checkfile   = args.checkfile
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

# We need to account for the ellipsoid shape of Earth instead of a sphere, otherwise we could have a shift of
# about 20km, about 1 grid cell. We read the parameters of the stereographic projection inside the NSIDC file
# in case they change those parameters in next versions.
#
# a is the radius of the Earth from the Earth center to the equator
a     = float(crs['semi_major_axis'])
# b is the radius of the Earth from the Earth center to the north/south pole
# (difference of about 21km between a and b)
# b is not read directly : the file gives the flattening f = (a-b)/a instead
f     = 1. / float(crs['inverse_flattening'])
# With a and b, we can convert the x and y distance of the nsidc psn25 files into
# correct longitudes and latitudes on the Earth
# NEMO considers the Earth to be a sphere, rather than an ellipsoid. No such problem.

# eccentricity
e2    = 2. * f - f * f
e     = np.sqrt(e2)

# phi_c is the latitude at which the map is true to scale (k = 1): grid cells
# are 25 km x 25 km on the Earth there. Cells are squares everywhere (conformal
# projection) but larger on the Earth closer to the pole, smaller further south
phi_c = np.radians(float(crs['standard_parallel']))
# lam0 is the longitude that goes toward the bottom when plotted. We need it to 
# find the longitude of the x, y points (incorrect lam0 would mean systematic shift)
lam0  = np.radians(float(crs['straight_vertical_longitude_from_pole']))

x = cdr['x'].values
y = cdr['y'].values
# Rows follow y and columns follow x, as for the data variables (time, y, x)
xx, yy = np.meshgrid(x, y)

# Snyder (1987), polar stereographic ellipsoidal formulas (t and m functions)
def t_of(phi):
# tan(pi/4 -pi/2) is the distance between a point and the center of the stereographic
#       projection for a sphere
# (1 - e * sin phi) / 1 + e * sin phi)
  return np.tan(np.pi / 4. - phi / 2.) / ((1. - e * np.sin(phi)) / (1. + e * np.sin(phi))) ** (e / 2.)

def m_of(phi):
# R cos phi would be the distance between the Earth rotation axis and a latitude 
#           circle if Earth was a sphere
# sqrt(1 - e2*sin phi ^2) is a correction factor for the ellipsoid
# R m_of(phi) is the actual distance between the Earth rotation axis and a latitude circle
  return np.cos(phi) / np.sqrt(1. - e2 * np.sin(phi) ** 2)

# Inverse projection, Snyder (1987) ellipsoidal polar stereographic (north polar case)
rho = np.hypot(xx, yy)
t   = rho * t_of(phi_c) / (a * m_of(phi_c))
chi = np.pi / 2. - 2. * np.arctan(t)
phi = chi + (e2 / 2. + 5. * e2 ** 2 / 24. + e2 ** 3 / 12. + 13. * e2 ** 4 / 360.) * np.sin(2. * chi) \
          + (7. * e2 ** 2 / 48. + 29. * e2 ** 3 / 240. + 811. * e2 ** 4 / 11520.) * np.sin(4. * chi) \
          + (7. * e2 ** 3 / 120. + 81. * e2 ** 4 / 1120.) * np.sin(6. * chi) \
          + (4279. * e2 ** 4 / 161280.) * np.sin(8. * chi)
lam = lam0 + np.arctan2(xx, -yy)

latitude  = np.degrees(phi)
longitude = (np.degrees(lam) + 180.) % 360. - 180.

# Map scale factor k = rho / (a m) (Snyder 1987): the projection is conformal, so the
# cell lengths on the ellipsoid are the nominal ones divided by k along x and y
k  = rho / (a * m_of(phi))
dx = np.abs(x[1] - x[0])
dy = np.abs(y[1] - y[0])

# Land-sea mask from the surface type of the CDR file
stmfile = xr.open_dataset(cdrfile, group='cdr_supplementary')
if 'surface_type_mask' not in stmfile:
  sys.exit('surface_type_mask missing from the cdr_supplementary group of the CDR file')

stm      = stmfile['surface_type_mask'].squeeze(drop=True)
meanings = stm.attrs['flag_meanings'].split()
values   = list(stm.attrs['flag_values'])
for ocean_type in ocean_types:
  if ocean_type not in meanings:
    sys.exit('Surface type ' + ocean_type + ' not found in surface_type_mask flag_meanings : ' + ' '.join(meanings))
ocean_values = [values[meanings.index(ocean_type)] for ocean_type in ocean_types]
tmaskutil    = np.isin(stm.values, ocean_values).astype('int8')

if tmaskutil.shape != latitude.shape:
  sys.exit('surface_type_mask and x/y don\'t have the same dimensions')

# Define the output dataset (dimensions named as in the data files, no
# coordinate values so that the sea masks align with any file on this grid)
dims = ('y', 'x')
grid = xr.Dataset(attrs=dict(description = 'NEMO mesh_mask-like grid description of the NSIDC polar stereographic north 25 km grid (psn25)', projection = crs.get('proj4text', ''), initial_cdrfile = cdrfile, ocean_types = ','.join(ocean_types), creation_date = str(datetime.datetime.now()), created_by = getpass.getuser()))
grid['glamt']     = xr.DataArray(longitude.astype('float32'), dims=dims, attrs=dict(long_name = 'Longitude of the cell centres', units = 'degrees_east'))
grid['gphit']     = xr.DataArray(latitude.astype('float32'), dims=dims, attrs=dict(long_name = 'Latitude of the cell centres', units = 'degrees_north'))
grid['tmaskutil'] = xr.DataArray(tmaskutil, dims=dims, attrs=dict(long_name = 'Land-sea mask (1 for ' + ', '.join(ocean_types) + ', 0 elsewhere)'))
grid['e1t']       = xr.DataArray((dx / k).astype('float32'), dims=dims, attrs=dict(long_name = 'Cell length along x', units = 'm'))
grid['e2t']       = xr.DataArray((dy / k).astype('float32'), dims=dims, attrs=dict(long_name = 'Cell length along y', units = 'm'))

# Optional comparison with the latitudes/longitudes of another file on the same
# grid, also against its north-south flipped version to detect an inverted y axis
if checkfile is not None:
  if os.path.exists(checkfile):
    check = xr.open_dataset(checkfile)
  else:
    sys.exit('Check file is missing')
  if args.checklon not in check or args.checklat not in check:
    sys.exit('Longitude or latitude variable missing from check file')
  checklon = check[args.checklon].squeeze(drop=True).values
  checklat = check[args.checklat].squeeze(drop=True).values
  if checklat.shape != latitude.shape:
    print('Check file : latitudes have shape ' + str(checklat.shape) + ' instead of ' + str(latitude.shape))
  else:
    for orientation, clat, clon in [('as is', checklat, checklon), ('flipped along y', checklat[::-1, :], checklon[::-1, :])]:
      dlat = np.nanmax(np.abs(clat - latitude))
      dlon = np.nanmax(np.abs((clon - longitude + 180.) % 360. - 180.) * (latitude < 89.9))
      print('Check file (' + orientation + ') : max |dlat| = %.4f deg, max |dlon| = %.4f deg' % (dlat, dlon))

# Write the output netcdf file
grid.to_netcdf(outfile)
