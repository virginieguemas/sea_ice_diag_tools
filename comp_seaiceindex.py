# This script averages a variable on each of the seas described into a mask    #
# file.                                                                        #
#                                                                              #
# History : 2026 - initial version by Virginie Guemas                          #
################################################################################
import xarray as xr
import sys
import os
import datetime
import getpass
import argparse

# Input arguments
parser = argparse.ArgumentParser(description='Average a variable on each of the seas described into a mask file.')
parser.add_argument('--maskfile', type=str, default="/home/guemas/tmp/test_regions/mask.ArcticSeas.cnrmcm7.nc", help='Path to the mask netcdf file')
parser.add_argument('--datafile', type=str, required=True, help='Path to the input data netcdf file')
parser.add_argument('--variable', type=str, required=True, help='Name of the variable to average')
parser.add_argument('--outfile', type=str, default="sia_per_sea.nc", help='Path to the output netcdf file')
args = parser.parse_args()

maskfile = args.maskfile
datafile = args.datafile
variable = args.variable
outfile = args.outfile

# Open input files
if os.path.exists(maskfile):
  maskdataset = xr.open_dataset(maskfile)
else:
  sys.exit('Mask file is missing')

if os.path.exists(datafile):
  data = xr.open_dataset(datafile)
else:
  sys.exit('Data file is missing')

# Read input variable
if variable in data:
  field = data[variable]
else:
  sys.exit('Variable missing from input file')

# List of sea masks
lstmasks = maskdataset.data_vars

# Check that all masks are bi-dimensional with the same x and y dimensions
ref_dims = None
for sea in lstmasks:
  mask = maskdataset[sea]
  if mask.ndim != 2:
    sys.exit("Mask " + sea + " is not bi-dimensional")
  if ref_dims is None:
    ref_dims = mask.dims
  elif mask.dims != ref_dims:
    sys.exit("Mask " + sea + " does not share the same dimensions as the other masks")

# Find the dimensions common between field and the masks
dims_to_reduce = [dim for dim in ref_dims if dim in field.dims]
if len(dims_to_reduce) != 2:
  sys.exit("Field and masks do not share two common dimensions")

# Define output dataset containing average over each sea
outdataset = xr.Dataset(attrs=dict(description = 'Average of variable ' + variable + ' for individual seas and regions', based_on_mask = maskfile, using_variable_file = datafile, creation_date = str(datetime.datetime.now()), created_by = getpass.getuser()))

# Compute the average over each sea
for sea in lstmasks:
  mask = maskdataset[sea]
  # Apply mask
  masked_field = field.where(mask == 1)
  # Compute the average over the dimensions common between field and mask
  mean_on_sea = masked_field.mean(dim=dims_to_reduce, skipna=True)
  # Store in the output dataset
  outdataset[sea] = xr.DataArray(mean_on_sea.values, attrs = dict(sea_name = mask.long_name))

# Write the output netcdf file
outdataset.to_netcdf(outfile)
sys.exit()
