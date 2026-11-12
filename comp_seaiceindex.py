# This script computes the area-average or the area-integral of a variable or  #
# of a product of variables in each of the seas described in a mask file.      #
# The input variable(s) can be 2d/3d/4d.                                          #
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
#
# We do not put import dask because xarray can call for dask if the option --chunk_time
# is set to something else than 0 so that import dask is not necessary
# Without import dask, the script works even if dask is not there but the option chunk_time
# has no effect, only a warning if the user requests something different than 0.
# With import dask, the script would stop if dask is not installed even if
# the user does not need the chunk_time option

#===============================================================================
# Input arguments
#===============================================================================
parser = argparse.ArgumentParser(description='Area-averages or area-integrates a variable or a product of variables (2d/3d/4d) in each of the seas described into the mask file')
parser.add_argument('--data', type=str, nargs='+', required=True, help='Path to the input data netcdf file(s) : either one file containing all the variables of --var, or one file per variable, in the same order as --var')
parser.add_argument('--var', type=str, nargs='+', required=True, help='Name of the variable to average or integrate; if several names are given (e.g. --var sithic siconc), their product is averaged or integrated')
parser.add_argument('--scale', type=float, nargs='+', default=None, help='One multiplicative factor per variable of --var, in the same order, applied before the product (e.g. 0.01 for a concentration in percent); default : 1 for all variables')
parser.add_argument('--zero_if_any_zero', action='store_true', help='Set the product to 0 wherever one of the variables is 0, even if another one is missing (NaN) there (e.g. sithic x siconc : no ice volume where siconc is 0, with --zero_if_any_zero, we obtain 0, otherwise NaN)')
parser.add_argument('--mask', type=str, default="/home/guemas/tmp/test_regions/mask.ArcticSeas.cnrmcm7.nc", help='Path to the mask netcdf file (containing various sea masks (1/0)')
parser.add_argument('--grid', type=str, default="/home/guemas/mytools/cnrmcm7/masks/mesh_mask.nc", help='Path to the grid description netcdf file')
parser.add_argument('--dxvar', type=str, default="e1t", help='Name of the variable containing the length of grid cells along x dimension (in m)')
parser.add_argument('--dyvar', type=str, default="e2t", help='Name of the variable containing the length of grid cells along y dimension (in m)')
parser.add_argument('--out', type=str, default="sia_per_sea.nc", help='Path to the output netcdf file')
parser.add_argument('--meanORsum', type=str, default="sum", help='mean for an area-average / sum for an area-weighted sum (default : sum)')
parser.add_argument('--chunk_time', type=int, default=0, help='Number of time steps read at once (requires dask), to limit the memory used by long time series; 0 (default) reads the whole field at once')
args = parser.parse_args()

datafiles = args.data
variables = args.var
scales    = args.scale
zero_if_any_zero = args.zero_if_any_zero
maskfile  = args.mask
gridfile  = args.grid
dxvar     = args.dxvar
dyvar     = args.dyvar
outfile   = args.out
meanORsum = args.meanORsum
chunk_time = args.chunk_time

# One data file for all variables, or one data file per variable
if len(datafiles) == 1:
  datafiles = datafiles * len(variables)
elif len(datafiles) != len(variables):
  sys.exit('--data must give either one file for all the variables or one file per variable of --var')

# One scale factor per variable (1 by default)
if scales is None:
  scales = [1.] * len(variables)
elif len(scales) != len(variables):
  sys.exit('--scale if present, must give one factor per variable of --var')

# Open input files (each distinct data file is opened only once)
datasets = dict()
for datafile in datafiles:
  if datafile not in datasets:
    if os.path.exists(datafile):
      datasets[datafile] = xr.open_dataset(datafile)
    else:
      sys.exit('Data file is missing : ' + datafile)

if os.path.exists(maskfile):
  maskdataset = xr.open_dataset(maskfile)
else:
  sys.exit('Mask file is missing')

if os.path.exists(gridfile):
  grid = xr.open_dataset(gridfile)
else:
  sys.exit('Grid file is missing')

# Read input variables
fields = [] # fields is a list of DataArray corresponding to the input variables
for variable, datafile in zip(variables, datafiles):
  # variables and datafiles are two lists of same length (checked l. 53-54)
  # zip allows to pair them in the order they appear to loop on those pairs
  if variable in datasets[datafile]:
    fields.append(datasets[datafile][variable])
  else:
    sys.exit('Variable ' + variable + ' missing from input file ' + datafile)

# All the variables of a product must have the same dimensions
for variable, field in zip(variables[1:], fields[1:]):
  # fields is a list of the same length as the datafiles list because of the loop right above
  # hence of the same length as the variables list
  # zip pairs them in the order they appear from their second element since they are compared 
  # to their first counterpart
  if field.dims != fields[0].dims:
    sys.exit('Variable ' + variable + ' does not have the same dimensions as ' + variables[0])

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

# Find the dimensions common between the field(s) and the masks (all the fields have the
# same dimensions, checked above)
dims_to_reduce = [dim for dim in ref_dims if dim in fields[0].dims]
if len(dims_to_reduce) != 2:
  sys.exit("Field and masks do not share two common dimensions")

# Identify the other dimensions of the field(s) (e.g. time, depth)
extra_dims = [dim for dim in fields[0].dims if dim not in dims_to_reduce]

# Read the field(s) by pieces of chunk_time time steps along their first extra dimension
# (time), instead of loading them entirely in memory : the computations below are then
# only done when writing the output file, one piece at a time (using dask)
if chunk_time > 0 and extra_dims:
  try:
    fields = [field.chunk({extra_dims[0]: chunk_time}) for field in fields]
    # each field is cut in pieces of length chunk_time along the first dimension which is not
    # common between mask and field : it should be the time (depth might come second)
  except (ImportError, ValueError) as error:
    warnings.warn("Field could not be chunked (is dask installed ?), it is read at once : " + str(error))

# Several variables : check that they have exactly the same coordinates (mainly the same dates, 
# potentially the same depth); join='exact' stops the script if they don't, 
# Without this test, we would drop silently the times and depths which are present in only one 
# of the fields
if len(fields) > 1:
  try:
    fields = list(xr.align(*fields, join='exact'))
    # * unfolds the fields list as a list of arguments, join is an option to raise an error if the
    # coordinates are not aligned, list turns the output tuple into a list again
  except ValueError as error:
    sys.exit("The variables of --var do not have the same coordinates : " + str(error))

# Apply the scale factors (1 by default), then multiply the variables together
fields = [field * scale for field, scale in zip(fields, scales)]
field = fields[0]
for other_field in fields[1:]:
  # if fields only contain one element, fields[1:] is empty and we skip this loop  
  field = field * other_field

# With --zero_if_any_zero, the product is 0 wherever one of the variables is 0, even if another
# one is NaN there (e.g. sithic is often not defined, NaN, where there is no ice, siconc == 0) :
# otherwise these points would result in missing values
if zero_if_any_zero and len(fields) > 1:
  any_zero = fields[0] == 0
  for other_field in fields[1:]:
    any_zero = any_zero | (other_field == 0)
  field = field.where(~any_zero, 0.)
  # wherever, we do not have any zero in the field, we keep its value, otherwise 0 

# Define output dataset containing the average or the integral over each sea
if meanORsum == 'mean':
  outtitle = 'Area-average'
elif meanORsum == 'sum':
  outtitle = 'Area-integral'
else:
  sys.exit(" meanOrsum must be either 'mean' or 'sum' ")

# Description of what is averaged or integrated, e.g. 'sithic x siconc' or '0.01 x ice_con'
description = ' x '.join([variable if scale == 1. else '%g x %s' % (scale, variable)
                          for variable, scale in zip(variables, scales)])
outdataset = xr.Dataset(attrs=dict(description = outtitle + ' of ' + description + ' for individual seas and regions', based_on_mask = maskfile, using_variable_file = ', '.join(datasets.keys()), creation_date = str(datetime.datetime.now()), created_by = getpass.getuser()))

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
  # Is there at least one value in the sea for each time step (i.e. across all dims_to_reduce) ?
  has_data = masked_field.notnull().any(dim=dims_to_reduce)
  # Check that field has no missing values within the sea (mask == 1); the checks of all
  # seas are evaluated together below, in a single reading of the field when it is chunked
  # Time steps entirely missing in the sea (has_data False) are not reported: their result
  # is NaN in the output file, which already shows that they are missing
  missing_checks[sea] = ((mask == 1) & field.isnull() & has_data).any()
  # Compute the total area or the mean grid cell area of the sea, stored as an attribute
  seaarea = area.where(mask == 1)
  attrs = dict(sea_name = mask.long_name)
  attrs[area_attrs[meanORsum]] = float(area_operation[meanORsum](seaarea))
  # Compute the average or the sum over the dimensions common between field and mask
  outdataset[sea]=operation[meanORsum](masked_field).where(has_data).assign_attrs(attrs)
  # A time step without any value in the sea (e.g. a month missing in an observational
  # product) gets NaN thanks to where(has_data) which is True/False if there is at least one
  # value / none which is not NaN: the weighted sum of no value at all would otherwise be 0
  #
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
