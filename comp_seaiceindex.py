# This script computes the area-average or the area-integral of a variable in  #
# each of the seas described in a mask file. The input variable can be         # 
# 2d/3d/4d.                                                                    #
#                                                                              #
# History : 2026 - initial version by Virginie Guemas                          #
################################################################################
import xarray as xr
import sys
import os
import datetime
import getpass
import argparse
import warnings
# We do not put import dask because xarray can call for dask if the option --chunk_time
# is set to something else than 0 so that import dask is not necessary
# Without import dask, the script works even if dask is not there but the option chunk_time
# has no effect, only a warning if the user requests something different than 0.
# With import dask, the script would stop if dask is not installed even if 
# the user does not need the chunk_time option

#===============================================================================
# Input arguments
#===============================================================================
parser = argparse.ArgumentParser(description='Area-averages or area-integrates a variable (2d/3d/4d) in each of the seas described into the mask file')
parser.add_argument('--data', type=str, required=True, help='Path to the input data netcdf file')
parser.add_argument('--var', type=str, required=True, help='Name of the variable to average')
parser.add_argument('--mask', type=str, default="/home/guemas/tmp/test_regions/mask.ArcticSeas.cnrmcm7.nc", help='Path to the mask netcdf file (containing various sea masks (1/0)')
parser.add_argument('--grid', type=str, default="/home/guemas/mytools/cnrmcm7/masks/mesh_mask.nc", help='Path to the grid description netcdf file')
parser.add_argument('--dxvar', type=str, default="e1t", help='Name of the variable containing the length of grid cells along x dimension (in m)')
parser.add_argument('--dyvar', type=str, default="e2t", help='Name of the variable containing the length of grid cells along y dimension (in m)')
parser.add_argument('--out', type=str, default="sia_per_sea.nc", help='Path to the output netcdf file')
parser.add_argument('--meanORsum', type=str, default="sum", help='mean for an area-average / sum for an area-weighted sum (default : sum)')
parser.add_argument('--chunk_time', type=int, default=0, help='Number of time steps read at once (requires dask), to limit the memory used by long time series; 0 (default) reads the whole field at once')
args = parser.parse_args()

datafile  = args.data
variable  = args.var
maskfile  = args.mask
gridfile  = args.grid
dxvar     = args.dxvar
dyvar     = args.dyvar
outfile   = args.out
meanORsum = args.meanORsum
chunk_time = args.chunk_time

# Open input files
if os.path.exists(datafile):
  data = xr.open_dataset(datafile)
else:
  sys.exit('Data file is missing')

if os.path.exists(maskfile):
  maskdataset = xr.open_dataset(maskfile)
else:
  sys.exit('Mask file is missing')

if os.path.exists(gridfile):
  grid = xr.open_dataset(gridfile)
else:
  sys.exit('Grid file is missing')

# Read input variables
if variable in data:
  field = data[variable]
else:
  sys.exit('Variable missing from input file')

if dxvar in grid:
  dx = grid[dxvar].squeeze()
else:
  sys.exit('dxvar missing from input file')

if dyvar in grid:
  dy = grid[dyvar].squeeze()
else:
  sys.exit('dyvar missing from input file')

# List of sea masks
lstmasks = maskdataset.data_vars

# Check that all masks are bi-dimensional with the same x and y dimensions
ref_dims = None
for sea in lstmasks:
  mask = maskdataset[sea].squeeze()
  if mask.ndim != 2:
    sys.exit("Mask " + sea + " is not bi-dimensional")
  if ref_dims is None:
    ref_dims = mask.dims
  elif mask.dims != ref_dims:
    sys.exit("Mask " + sea + " does not share the same dimensions as the other masks")

# Check that the grid descrption file is bi-dimensional with the same x and y dimensions
if dx.ndim != 2 or dy.ndim != 2:
  sys.exit("dxvar or dyvar is not bi-dimensional")
elif dx.dims != ref_dims or dy.dims!= ref_dims:
  sys.exit("dxvar or dyvar does not share the same dimensions as the masks")

# Find the dimensions common between field and the masks
dims_to_reduce = [dim for dim in ref_dims if dim in field.dims]
if len(dims_to_reduce) != 2:
  sys.exit("Field and masks do not share two common dimensions")

# Identify the other dimensions of field (e.g. time, depth)
extra_dims = [dim for dim in field.dims if dim not in dims_to_reduce]

# Read the field by pieces of chunk_time time steps along its first extra dimension
# (time), instead of loading it entirely in memory : the computations below are then
# only done when writing the output file, one piece at a time (using dask)
if chunk_time > 0 and extra_dims:
  try:
    field = field.chunk({extra_dims[0]: chunk_time})
  except (ImportError, ValueError) as error:
    warnings.warn("Field could not be chunked (is dask installed ?), it is read at once : " + str(error))

# Define output dataset containing the average or the integral over each sea
if meanORsum == 'mean':
  outtitle = 'Area-average'
elif meanORsum == 'sum':
  outtitle = 'Area-integral'
else:
  sys.exit(" meanOrsum must be either 'mean' or 'sum' ")
     
outdataset = xr.Dataset(attrs=dict(description = outtitle + ' of variable ' + variable + ' for individual seas and regions', based_on_mask = maskfile, using_variable_file = datafile, creation_date = str(datetime.datetime.now()), created_by = getpass.getuser()))

# Define the operation to be applied
area=dx*dy
operation = {
  'mean' : lambda readyfield: readyfield.weighted(area).mean(dim=dims_to_reduce, skipna=True),
  'sum'  : lambda readyfield: readyfield.weighted(area).sum(dim=dims_to_reduce, skipna=True)
  }

# Define whether we will estimate the total surface of each sea (for comparison between model
# and observation) or the mean grid cell area within each sea
area_operation = {
  'mean' : lambda seaarea: seaarea.mean(),
  'sum'  : lambda seaarea: seaarea.sum()
  }
area_attrs = {
  'mean' : 'mean_cell_area_m2',
  'sum'  : 'total_area_m2'
  }

# ============================================================================================
# Compute the area-averaged or area-integrated variable over each sea
# ============================================================================================
#
missing_checks = xr.Dataset() 
# The test to check whether there is any missing value in each sea is stored in missing_checks
# with one variable per sea to be executed all seas at once after the loop on seas for an 
# optimal use of dask operations : we read all the input data only once for all seas at once
for sea in lstmasks:
  mask = maskdataset[sea].squeeze()
  # Apply mask
  masked_field = field.where(mask == 1)
  # Check that field has no missing values within the sea (mask == 1); the checks of all
  # seas are evaluated together below, in a single reading of the field when it is chunked
  missing_checks[sea] = ((mask == 1) & field.isnull()).any()
  # Compute the total area or the mean grid cell area of the sea, stored as an attribute
  seaarea = area.where(mask == 1)
  attrs = dict(sea_name = mask.long_name)
  attrs[area_attrs[meanORsum]] = float(area_operation[meanORsum](seaarea))
  # Compute the average or the sum over the dimensions common between field and mask
  outdataset[sea]= operation[meanORsum](masked_field).assign_attrs(attrs)
# If field has been chunked through dask, the operations on field in the loop above are not 
# performed just yet (only the sea areas, computed on the grid only are), these are stored by
# dask to be executed chunk by chunk when computing missing_checks and when writing the output

missing_checks = missing_checks.compute()
# All computed at once : each chunk is read and checked for missing values in all seas, then
# next chunk ... The result is True or False for each sea
for sea in lstmasks:
  if bool(missing_checks[sea]):
    warnings.warn("Missing values found in field for sea '" + sea + "' where mask == 1")

# Copy the attributes of the time and depth dimensions from the input data file
for dim in extra_dims:
  if dim in outdataset.coords and dim in field.coords:
    outdataset[dim].attrs = dict(field.coords[dim].attrs)

# Write the output netcdf file
outdataset.to_netcdf(outfile)
