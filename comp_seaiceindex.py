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

# Input arguments
parser = argparse.ArgumentParser(description='Area-Averages or area-integrates a variable (2d/3d/4d) in each of the seas described into the mask file')
parser.add_argument('--data', type=str, required=True, help='Path to the input data netcdf file')
parser.add_argument('--var', type=str, required=True, help='Name of the variable to average')
parser.add_argument('--mask', type=str, default="/home/guemas/tmp/test_regions/mask.ArcticSeas.cnrmcm7.nc", help='Path to the mask netcdf file (containing various sea masks (1/0)')
parser.add_argument('--grid', type=str, default="/home/guemas/mytools/cnrmcm7/masks/mesh_mask.nc", help='Path to the grid description netcdf file')
parser.add_argument('--dxvar', type=str, default="e1t", help='Name of the variable containing the length of grid cells along x dimension (in m)')
parser.add_argument('--dyvar', type=str, default="e2t", help='Name of the variable containing the length of grid cells along y dimension (in m)')
parser.add_argument('--out', type=str, default="sia_per_sea.nc", help='Path to the output netcdf file')
parser.add_argument('--meanORsum', type=str, default="sum", help='mean for an area-average / sum for an integration (default : sum)')
args = parser.parse_args()

datafile  = args.data
variable  = args.var
maskfile  = args.mask
gridfile  = args.grid
dxvar     = args.dxvar
dyvar     = args.dyvar
outfile   = args.out
meanORsum = args.meanORsum

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

# Define output dataset containing the average over each sea
# coords_to_keep = {coord_name: field[coord_name] for coord_name in field.coords if coord_name not in dims_to_reduce}
# This line does not seem to work - to sort out
outdataset = xr.Dataset(attrs=dict(description = 'Area-average of variable ' + variable + ' for individual seas and regions', based_on_mask = maskfile, using_variable_file = datafile, creation_date = str(datetime.datetime.now()), created_by = getpass.getuser()))

# Define the operation to be applied
area=dx*dy
operation = {
  'mean' : lambda readyfield: readyfield.weighted(area).mean(dim=dims_to_reduce, skipna=True),
  'sum'  : lambda readyfield: readyfield.weighted(area).sum(dim=dims_to_reduce, skipna=True) 
  }

# Check meanORsum
if meanORsum not in operation:
  sys.exit(" meanOrsum must be either 'mean' or 'sum' ")

# Compute the area-averaged variable over each sea
for sea in lstmasks:
  mask = maskdataset[sea].squeeze()
  # Apply mask
  masked_field = field.where(mask == 1)
  # Check that field has no missing values within the sea (mask == 1)
  missing_in_sea = (mask == 1) & field.isnull()
  if missing_in_sea.any():
    warnings.warn("Missing values found in field for sea '" + sea + "' where mask == 1")
  # Compute the average or the sum over the dimensions common between field and mask
  outdataset[sea]= operation[meanORsum](masked_field).assign_attrs(dict(sea_name = mask.long_name))

# Copy the attributes of the time and depth dimensions from the input data file
for dim in extra_dims:
  if dim in outdataset.coords and dim in field.coords:
    outdataset[dim].attrs = dict(field.coords[dim].attrs)

# Write the output netcdf file
outdataset.to_netcdf(outfile)
#sys.exit()
