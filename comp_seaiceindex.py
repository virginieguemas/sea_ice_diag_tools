# This script averages a variable on each of the seas described into a mask    ## file.                                                                        #
#                                                                              #
# History : 2026 - initial version by Virginie Guemas                          #
################################################################################
import xarray as xr
import sys
import os
import datetime
import getpass

# Input arguments
maskfile = "/home/guemas/tmp/test_regions/mask.ArcticSeas.cnrmcm7.nc"  
datafile = "/cnrm/ioga/Users/voldoire/NO_SAVE/NEMO4/LR/AOGCM_drv632_NEMO422_LR_t7/AOGCM_drv632_NEMO422_LR_t7_seaice_monthly_siconc_185001-194912.nc"  
variable = "siconc"  
outfile = "sia_per_sea.nc"  

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

# Define output dataset containing average over each sea
outdataset = xr.Dataset(attrs=dict(description = 'Average of variable ' + variable + ' for individual seas and regions', based_on_mask = maskfile, using_variable_file = datafile, creation_date = str(datetime.datetime.now()), created_by = getpass.getuser()))

# CHERCHER LES DIMENSIONS COMMUNES ENTRE MASK ET FIELD !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# Compute the average over each sea
for sea in lstmasks:
  mask = maskdataset[sea]
  # Check dimension
  if mask.shape == field.shape:
    # Apply mask 
    masked_field = field.where(mask == 1)
    # Compute the average 
    mean_on_sea = masked_field.mean(dim=dims_to_reduce, skipna=True)
    # Store in the output dataset
    outdataset[sea] = xr.DataArray(mean_on_sea.values, attrs = dict(sea_name = mask.long_name)) 
  else:
    sys.exit("Mask dimensions do not correspond with field dimensions")

# Write the output netcdf file
outdataset.to_netcdf(outfile)
sys.exit()
