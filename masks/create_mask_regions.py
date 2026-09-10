# This script defines a mask for each individual sea and ocean based #
# on their official definition found in                              #
#    IHO PUBLICATION S-23, Limits of Oceans and Seas,                #
#       Draft 4th Edition, 2002                                      #
# Current link : 
#       https://legacy.iho.int/mtg_docs/com_wg/S-23WG/S-23WG_Misc/Draft_2002/Draft_2002.htm
# except for some adaptation to account for the discretization of    # 
# the coastline on the ORCA1 grid as indicated in the comments.      #
#                                                                    #
# History : 2025 - initial version by Virginie Guemas                #
######################################################################
import sys
import xarray as xr
import datetime
import getpass
#
# temporary
import numpy as np
import matplotlib.pyplot as plt
plt.figure()
#

# Input arguments
grid = 'cnrmcm7'
#grid = 'N3.2_O1L42'

# Read longitudes, latitudes and land-sea mask

if grid == 'N3.2_O1L42': 
   
   maskfile = '~/mytools/postdoc2014/MasksArctic/mesh_mask_nemo.N3.2_O1L42.nc'
   masktmp = xr.open_dataset(maskfile)
   msk_name = 'tmask'
   maskvar = masktmp[msk_name].isel(t = 0,z = 0).squeeze(drop=True)

   gridfile = '~/mytools/postdoc2014/MasksArctic/mesh_mask_nemo.N3.2_O1L42.nc'
   lon_name = 'nav_lon'
   lat_name = 'nav_lat'
  
   outfile = 'mask.ArcticSeas.N3.2_O1L42.nc'

elif grid == 'cnrmcm7':

   maskfile  = '~/mytools/cnrmcm7/masks/mesh_mask.nc'
   masktmp   = xr.open_dataset(maskfile)
   msk_name  = 'tmaskutil'
   umsk_name = 'umaskutil'
   vmsk_name = 'vmaskutil'
   maskvar   = masktmp[msk_name].squeeze(drop=True)
   umaskvar  = masktmp[umsk_name].squeeze(drop=True)
   vmaskvar  = masktmp[vmsk_name].squeeze(drop=True)

   gridfile = '/home/guemas/mytools/cnrmcm7/masks/mesh_mask.nc'
   lon_name = 'glamt'
   lat_name = 'gphit'

   outfile = 'mask.ArcticSeas.cnrmcm7.nc'

else:

   sys.exit('unknown input grid')

gridtmp = xr.open_dataset(gridfile)
longitude = gridtmp[lon_name].squeeze(drop=True)
latitude = gridtmp[lat_name].squeeze(drop=True)

if (latitude.shape != longitude.shape):
    sys.exit('Latitudes, longitudes and mask don\'t have the same dimensions')

# Define output dataset containing all new masks
#
newmask = xr.Dataset(attrs=dict(description = 'Masks for individual seas and regions', initial_gridfile = gridfile, based_on_latitude = lat_name, based_on_longitude=lon_name, initial_maskfile = maskfile, based_on_mask_variable = msk_name, creation_date = str(datetime.datetime.now()), created_by = getpass.getuser()))
#
# Define each new mask for each region
#
# 1. Global ocean
newmask['globocea'] = xr.DataArray(maskvar, attrs=dict(long_name = 'Global Ocean'))
#
# 2. Northern Hemisphere
nhemisph = xr.where(latitude > 0, maskvar, 0) 
newmask['nhemisph'] = xr.DataArray(nhemisph, attrs=dict(long_name = 'Northern Hemisphere'))
#
# 3. Southern Hemisphere
shemisph = xr.where(latitude < 0, maskvar, 0)
newmask['shemisph'] = xr.DataArray(shemisph, attrs=dict(long_name = 'Southern Hemisphere'))
#
# 4. Antarctic Ocean
antarct = xr.where(latitude < -60, maskvar, 0)
newmask['antarcti'] = xr.DataArray(antarct, attrs=dict(long_name = 'Antarctic Ocean'))
#
# 4a. Ross Sea (S-23 10.10)
# 72S defined arbitrarily to follow the western coastline
# 165.3E changed to 163 to follow the ORCA1 coastline which advances further into the land than reality
rossseax = xr.where(((latitude < -71.30) & ((longitude > 170.23) | (longitude < -157.83))) | ((longitude > 162) & (longitude < 170.23) & (latitude < -72)), maskvar, 0)
newmask['rossseax'] = xr.DataArray(rossseax, attrs=dict(long_name = 'Ross Sea'))
#
# 4b. Amundsen Sea (S-23 10.11)
# Eastern limit shifted eastward to follow the ORCA1 coast -102.47 -> -102.25
amundsen = xr.where((latitude < -72.10) & (longitude > -126.25) & (longitude < -102.25), maskvar, 0)
newmask['amundsen'] = xr.DataArray(amundsen, attrs=dict(long_name = 'Amundsen Sea'))
#
# 4c. Bellingshausen Sea (S-23 10.12)
# Western limit shifted eastward as for the Amundsen sea
# northern limit tilted northeastward between Cape Flying Fish and Peter I island represented with staircase here
bellings = xr.where(((latitude < -72.10) & (longitude > -102.25) & (longitude < -90.62)), maskvar, 0)
latlim = -72.10
for xlon in np.arange(-101.47,-90.62):
  latlim = latlim +0.307
  bellings = xr.where((latitude < latlim) & (longitude > xlon) & (longitude < (xlon+1)), maskvar, bellings)
for xlon in np.arange(-90.62,-67.80,2):
  latlim = latlim +0.174
  bellings = xr.where((latitude < latlim) & (longitude > xlon) & (longitude < (xlon+2)), maskvar, bellings)

newmask['bellings'] = xr.DataArray(bellings, attrs=dict(long_name = 'Bellingshausen Sea'))
#
# 4d. Weddell Sea (S-23 10.1)
#  northern limit tilted close to 60S and set to 60S here
#  eastern limit tilted westward with its southernmost point at 12.27W, set to 12.27W here
#  western limit follows coastline near 60W until the tip of the Antartic Peninsula where it goes north
#     tip of Antartic Peninsula in ORCA1 is 57W
#  65S and 62W set to follow the ORCA1 coastline
weddells = xr.where(((latitude < -60) & (longitude > -57) & (longitude < -12.27)) | ((latitude < -65) & (longitude > -62) & (longitude < -57)) | ((latitude < -64) & (longitude > -60) & (longitude < -57)), maskvar, 0)
newmask['weddells'] = xr.DataArray(weddells, attrs=dict(long_name = 'Weddell Sea'))
#
# 4e. Lazarev Sea (S-23 10.2)
lazarevs = xr.where((latitude < -65) & (longitude > 0) & (longitude < 14), maskvar, 0)
newmask['lazarevs'] = xr.DataArray(lazarevs, attrs=dict(long_name = 'Lazarev Sea'))
#
# 4f. Riiser-Larsen Sea (S-23 10.3)
riiserla = xr.where((latitude < -65) & (longitude > 14) & (longitude < 33.75), maskvar, 0)
newmask['riiserla'] = xr.DataArray(riiserla, attrs=dict(long_name = 'Riiser-Larsen Sea'))
#
# 4g. Cosmonauts Sea (S-23 10.4)
cosmauno = xr.where((latitude < -65) & (longitude > 33.75) & (longitude < 53.80), maskvar, 0)
newmask['cosmonau'] = xr.DataArray(cosmauno, attrs=dict(long_name = 'Cosmonauts Sea'))
#
# 4h. Cooperation Sea (S-23 10.5)
cooperat = xr.where((latitude < -65) & (longitude > 53.80) & (longitude < 81.67), maskvar, 0)
newmask['cooperat'] = xr.DataArray(cooperat, attrs=dict(long_name = 'Cooperation Sea'))
#
# 4i. Davis Sea (S-23 10.6)
#  northern limit tilted from 65S on the west to 64S on the east, set to 65S
davissea = xr.where((latitude < -65) & (longitude > 81.67) & (longitude < 95.58), maskvar, 0)
newmask['davissea'] = xr.DataArray(davissea, attrs=dict(long_name = 'Davis Sea'))
#
# 4ibis. Tryoshnikova Gulf (S-23 10.6.1)
tryoshni = xr.where((latitude < -65) & (longitude > 88.02) & (longitude < 95.58), maskvar, 0)
newmask['tryoshni'] = xr.DataArray(tryoshni, attrs=dict(long_name = 'Tryoshnikova Gulf'))
#
# 4j. Mawson sea (S-23 10.7)
mawsonse = xr.where((latitude < -64) & (longitude > 95.58) & (longitude < 113.20), maskvar, 0)
newmask['mawsonse'] = xr.DataArray(mawsonse, attrs=dict(long_name = 'Mawson Sea'))
#
# 4k. Dumont d'Urville Sea
dumontdu = xr.where((latitude < -64) & (longitude > 136.20) & (longitude < 146.83), maskvar, 0)
newmask['dumontdu'] = xr.DataArray(dumontdu, attrs=dict(long_name = 'Dumont d\'Urville Sea'))
#
# 4l. Somov Sea
# northern limit tilted from 64S on the west to 66.27S on the east (Cape Ellsworthy), set to 65S here
somovsea = xr.where((latitude < -65) & (longitude > 146.83) & (longitude < 162.32), maskvar, 0)
# eastern limit follows two segments: Cape Ellsworthy (66.27S-162.32E) to Smith Point
# (67.60S-164.82E), then Smith Point to Cape Adare (71.30S-170.23E, shared with the Ross Sea)
somovsea = xr.where((latitude < -66.27) & (longitude > 162.32) & (longitude < 163.32), maskvar, somovsea)
latlim = -66.27
for xlon in np.arange(163.32,164.82):
  latlim = latlim -0.665
  somovsea = xr.where((latitude < latlim) & (longitude > xlon) & (longitude < (xlon+1)) & (longitude < 164.82), maskvar, somovsea)
for xlon in np.arange(164.82,170.23):
  latlim = latlim -0.6167
  somovsea = xr.where((latitude < latlim) & (longitude > xlon) & (longitude < (xlon+1)) & (longitude < 170.23) & (latitude > -72), maskvar, somovsea)
newmask['somovsea'] = xr.DataArray(somovsea, attrs=dict(long_name = 'Somov Sea'))

# 4m Drake Passage

# To be filled here

# 4n Bransfield Strait

# To be filled here

# 5. Arctic Ocean (S-23 9, opening definition)
arc_atl_lon = [-64.17, -44.83, -44.83, -32.18, -24.53, -14.97, -6.25, -0.88, 4.67]
arc_atl_lat = [60.0, 60.0, 67.85, 67.85, 65.5, 64.23, 62.35, 60.85, 60.85]
arc_ame_lon = [-180.,-170.58, -164.23, -100., -100., -72. , -72., -64.17, -64.17]
arc_ame_lat = [66.37, 66.37, 66.18, 66.18, 50., 50., 57.5  ,57.5 ,60.0]
arc_rus_lon = [4.67, 15., 30., 30., 90., 90., 180.]
arc_rus_lat = [60.85, 67., 67., 60., 60., 66.37, 66.37]
arc_south_lim_lon = arc_ame_lon + arc_atl_lon + arc_rus_lon
arc_south_lim_lat = arc_ame_lat + arc_atl_lat + arc_rus_lat
arcticoc = xr.where(latitude > np.interp(longitude, arc_south_lim_lon, arc_south_lim_lat), maskvar, 0)
newmask['arcticoc'] = xr.DataArray(arcticoc, attrs=dict(long_name = 'Arctic Ocean'))
#
# 5a. Fram Strait
#
# I could not find an official definition for Fram Strait. Here, it is 
# chosen as following 80N between Greenland (20W) and Svalbard (18E)

framstra = xr.where((longitude > -20) & (longitude < 18), maskvar, 0)
for jx in np.arange(latitude.shape[1]):
  jy = np.argmin(np.abs(latitude[:,jx].values-80))
  addpoint = False
  if framstra[jy, jx] > 0.5: 
    addpoint = True
  framstra[: , jx] = 0.
  if addpoint:
    framstra[jy, jx] = 1.
framstru = xr.where(framstra, umaskvar, 0)
framstrv = xr.where(framstra, vmaskvar, 0)
newmask['framstra'] = xr.DataArray(framstra, attrs=dict(long_name = 'Fram Strait on t-grid'))
newmask['framstru'] = xr.DataArray(framstru, attrs=dict(long_name = 'Fram Strait on u-grid'))
newmask['framstrv'] = xr.DataArray(framstrv, attrs=dict(long_name = 'Fram Strait on v-grid'))

# 5b-5q. Arctic Ocean sub-divisions, based on
#
# Laptev Sea / Kara Sea, following the Severnaya Zemlya archipelago (S-23 9.2 West / 9.3 East)
#sevzem_lat = [77.53, 78.30, 79.42, 79.67, 80.17, 80.22, 81.27]
#sevzem_lon = [105.92, 104.83, 102.42, 100.33, 97.67, 97.33, 95.75]
# Adaptation for ORCA1 NEMO4.2.3
sevzem_lat = [77.53, 78.30, 79.42, 79.60, 80.17, 80.22, 81.27]
sevzem_lon = [105.92, 104.83, 102.42, 100.25, 97.67, 97.33, 95.75]
#
# Kara Sea / Barents Sea, following the Novaya Zemlya archipelago (S-23 9.3 West / 9.4 East)
novzem_lat = [69.60, 69.67, 70.25, 70.47, 73.28, 73.35, 76.95, 81.00]
novzem_lon = [60.20, 59.98, 58.43, 57.12, 53.88, 54.08, 68.58, 65.33]
#
# Barents Sea / Norwegian Sea, following Norway, Bjornoya and Svalbard (S-23 9.4 West / 9.7 Northeast)
barnor_lat = [71.17, 74.35, 74.52, 76.47, 80.07]
barnor_lon = [25.78, 19.08, 19.12, 16.62, 16.27]
#
# Greenland Sea east/southeast/south limit, following Svalbard and Jan Mayen,
# the common limit with the Norwegian Sea (S-23 9.6 East/Southeast/South)
greennor_lat = [70.15, 70.83, 71.17, 76.47, 80.07]
greennor_lon = [-22.07, -9.00, -7.97, 16.62, 16.27]
#
# Norwegian Sea / Iceland Sea, from Fugloy to Sorkapp on Jan Mayen (S-23 9.7 West / 9.8 East)
norice_lat = [62.35, 70.83]
norice_lon = [-6.25, -9.00]
#
# Northwestern Passages / Beaufort Sea, from Cape Bathurst to Griffiths Point (S-23 9.14 West / 9.15 East)
nwpbeau_lat = [70.58, 71.97, 74.35, 76.10, 76.33]
nwpbeau_lon = [-128.03, -126.02, -124.77, -123.01, -122.58]
#
# 5b. East Siberian Sea (S-23 9.1)
eastsibe = xr.where((longitude > np.interp(latitude, [79., 73., 72.5, 65.], [139., 139., 140., 140.])) & (longitude < np.interp(latitude, [69.58, 70.78, 71.53, 76], [177.5, 178.75, 180, 180])) & (latitude > 65.) & (latitude < np.interp(longitude, [139, 180], [79, 76])), maskvar, 0)
newmask['eastsibe'] = xr.DataArray(eastsibe, attrs=dict(long_name = 'East Siberian Sea'))
#
# 5c. Laptev Sea (S-23 9.2)
laptevse = xr.where((latitude > 72.88) & (latitude < np.interp(longitude, [95.75, 139], [81.27, 79])) & (longitude > np.interp(latitude, sevzem_lat, sevzem_lon)) & (longitude < np.interp(latitude, [79., 73., 72.5, 65.], [139., 139., 140., 140.])), maskvar, 0)
newmask['laptevse'] = xr.DataArray(laptevse, attrs=dict(long_name = 'Laptev Sea'))
#
# 5d. Kara Sea (S-23 9.3)
karaseax = xr.where((latitude > 69.6) & (latitude < np.interp(longitude, [65.33, 95.75], [81.0, 81.27])) & (longitude > np.interp(latitude, novzem_lat, novzem_lon)) & (longitude < np.interp(latitude, sevzem_lat, sevzem_lon)), maskvar, 0)
newmask['karaseax'] = xr.DataArray(karaseax, attrs=dict(long_name = 'Kara Sea'))
#
# 5e. Barents Sea (S-23 9.4)
barn_north_lon = [16.27, 17.77, 26.83, 28.00, 32.67, 36.75, 44.92, 65.33]
barn_north_lat = [80.07, 80.13, 80.17, 80.13, 80.17, 80.17, 80.60, 81.00]
barentse = xr.where((latitude > 68.1) & (latitude < np.interp(longitude, barn_north_lon, barn_north_lat)) & (longitude > np.interp(latitude, barnor_lat, barnor_lon)) & (longitude < np.interp(latitude, novzem_lat, novzem_lon)), maskvar, 0)
newmask['barentse'] = xr.DataArray(barentse, attrs=dict(long_name = 'Barents Sea'))
#
# 5f. White Sea (S-23 9.5)
whitesea = xr.where((latitude > 63) & (latitude < 68.1) & (longitude > 33) & (longitude < 45), maskvar, 0)
newmask['whitesea'] = xr.DataArray(whitesea, attrs=dict(long_name = 'White Sea'))
#
# 5g. Greenland Sea (S-23 9.6)
greenlds = xr.where((latitude > 70.15) & (latitude < np.interp(longitude, [-25.42, 16.27], [83.38, 80.07])) & (longitude > -40) & (longitude < np.interp(latitude, greennor_lat, greennor_lon)), maskvar, 0)
newmask['greenlds'] = xr.DataArray(greenlds, attrs=dict(long_name = 'Greenland Sea'))
#
# 5h. Norwegian Sea (S-23 9.7)
norw_north_lon = [-9.00, -7.97, 16.62, 19.10, 25.78]
norw_north_lat = [70.83, 71.17, 76.47, 74.43, 71.17]
norw_south_lon = [-6.25, -0.88, 4.67]
norw_south_lat = [62.35, 61.00, 61.00]
norwegia = xr.where((latitude > np.interp(longitude, norw_south_lon, norw_south_lat)) & (latitude < np.interp(longitude, norw_north_lon, norw_north_lat)) & (longitude > np.interp(latitude, norice_lat, norice_lon)) & (longitude < np.interp(latitude, [61., 70.], [10., 26])), maskvar, 0)
newmask['norwegia'] = xr.DataArray(norwegia, attrs=dict(long_name = 'Norwegian Sea'))
#
# 5i. Iceland Sea (S-23 9.8)
icel_west_lat = [65.50, 67.85, 70.15]
icel_west_lon = [-24.53, -32.18, -22.07]
icelands = xr.where((latitude > np.interp(longitude, [-14.97, -6.25], [64.23, 62.35])) & (latitude < np.interp(longitude, [-22.07, -9.00], [70.15, 70.83])) & (longitude < np.interp(latitude, norice_lat, norice_lon)) & (longitude > np.interp(latitude, icel_west_lat, icel_west_lon)), maskvar, 0)
newmask['icelands'] = xr.DataArray(icelands, attrs=dict(long_name = 'Iceland Sea'))
#
# 5j. Davis Strait (S-23 9.9)
ds_west_lat = [60.00, 60.40, 61.32, 61.63, 61.75, 61.78, 61.88, 63., 70.00]
ds_west_lon = [-64.17, -64.43, -64.78, -65.48, -65.67, -65.95, -65.97, -67.17, -67.17]
davisstr = xr.where((latitude > 60) & (latitude < 70) & (longitude > np.interp(latitude, ds_west_lat, ds_west_lon)) & (longitude < -44.83), maskvar, 0)
newmask['davisstr'] = xr.DataArray(davisstr, attrs=dict(long_name = 'Davis Strait'))
#
# 5k. Hudson Strait (S-23 9.10)
hs_north_lon = [-78.03, -75., -65.97]
hs_north_lat = [64.43, 65., 61.88]
hs_south_lon = [-78.10, -76., -64.43, -64.43]
hs_south_lat = [62.37,57., 57., 60.40]
hs_east_lat = [60.40, 61.32, 61.63, 61.75, 61.78, 61.88]
hs_east_lon = [-64.43, -64.78, -65.48, -65.67, -65.95, -65.97]
hs_west_lat = [62.37, 63.45, 63.78, 64.43]
hs_west_lon = [-78.10, -80.98, -80.15, -78.03]
hudsonst = xr.where((latitude > np.interp(longitude, hs_south_lon, hs_south_lat)) & (latitude < np.interp(longitude, hs_north_lon, hs_north_lat)) & (longitude > np.interp(latitude, hs_west_lat, hs_west_lon)) & (longitude < np.interp(latitude, hs_east_lat, hs_east_lon)), maskvar, 0)
newmask['hudsonst'] = xr.DataArray(hudsonst, attrs=dict(long_name = 'Hudson Strait'))
#
# 5l. Hudson Bay (S-23 9.11)
hb_north_lon = [-100., -85.87, -85.53, -80.98, -78.10, -75.]
hb_north_lat = [66.20, 66.20, 65.92, 63.45, 62.37, 62.]
hudsonba = xr.where((latitude > 51) & (latitude < np.interp(longitude, hb_north_lon, hb_north_lat)) & (longitude > -95) & (longitude < -76.), maskvar, 0)
newmask['hudsonba'] = xr.DataArray(hudsonba, attrs=dict(long_name = 'Hudson Bay'))
#
# 5m. Baffin Bay (S-23 9.12)
#  between Ellesmere/Devon/Bylot/Baffin Islands and western Greenland
baffinba = xr.where((latitude > 70) & (latitude < 82.47) & (longitude > -80.23) & (longitude < -51.75), maskvar, 0)
newmask['baffinba'] = xr.DataArray(baffinba, attrs=dict(long_name = 'Baffin Bay'))
#
# 5n. Lincoln Sea (S-23 9.13)
#  between northern Ellesmere Island and northern Greenland
lincolns = xr.where((latitude > 82.35) & (latitude < 83.63) & (longitude > -71.25) & (longitude < -33.93), maskvar, 0)
newmask['lincolns'] = xr.DataArray(lincolns, attrs=dict(long_name = 'Lincoln Sea'))
#
# 5o. Northwestern Passages (S-23 9.14)
#  north limit follows the exact chain from Griffiths Point to Lands Lokk Point
#  west limit follows the common limit with the Beaufort Sea
#  south limit follows the chain from Beach Point to Lloyd Point (the common
#  limits with the Hudson Bay and the Hudson Strait); west of Beach Point it
#  is left to the land-sea mask, which hugs the mainland coast of Canada down to Cape Bathurst
#  east limit kept as a simple envelope following the western coasts of
#  Ellesmere/Devon/Bylot/Baffin Islands, handled by the land-sea mask
nwp_north_lon = [-123.02, -116.40, -115.08, -114.33, -113.30, -110.72, -105.43, -99.77, -94.12, -91.90]
nwp_north_lat = [76.10, 77.57, 77.97, 78.08, 78.35, 78.77, 79.33, 80.15, 81.37, 81.62]
nwp_south_lon = [-85.87, -85.53, -80.15, -78.03]
nwp_south_lat = [66.20, 65.92, 63.78, 64.43]
nwpassag = xr.where((latitude > np.interp(longitude, nwp_south_lon, nwp_south_lat)) & (latitude < np.interp(longitude, nwp_north_lon, nwp_north_lat)) & (longitude > np.interp(latitude, nwpbeau_lat, nwpbeau_lon)) & (longitude < -75.17), maskvar, 0)
newmask['nwpassag'] = xr.DataArray(nwpassag, attrs=dict(long_name = 'Northwestern Passages'))
#
# 5p. Beaufort Sea (S-23 9.15)
#  north limit follows the exact line from Point Barrow (71.40N-156.47W) to Lands End (76.33N-122.58W)
#  east limit follows the common limit with the Northwestern Passages
#  south limit left to the land-sea mask, which hugs the Alaska/Canada coastline
beaufort = xr.where((latitude > 68) & (latitude < np.interp(longitude, [-156.47, -122.58], [71.4, 76.33])) & (longitude > -156.47) & (longitude < np.interp(latitude, nwpbeau_lat, nwpbeau_lon)), maskvar, 0)
newmask['beaufort'] = xr.DataArray(beaufort, attrs=dict(long_name = 'Beaufort Sea'))
#
# 5q. Chukchi Sea (S-23 9.16)
#  straddles the date line, between Ostrov Vrangelya and Point Barrow
#  western limit follows Mys Yakan (177.5E) - Mys Blossom (178.75E), the common
#  limit with the East Siberian Sea
chukchis = xr.where((latitude > 66.18) & (latitude < 71.53) & ((longitude > 177.5) | (longitude < -156.47)), maskvar, 0)
newmask['chukchis'] = xr.DataArray(chukchis, attrs=dict(long_name = 'Chukchi Sea'))


# 6. Mediterranean Sea
bool_medit_1 = (latitude > 30) & (latitude < 40) & (longitude > -5) & (longitude <  0)
bool_medit_2 = (latitude > 30) & (latitude < 46) & (longitude >  0) & (longitude < 28)
bool_medit_3 = (latitude > 30) & (latitude < 40) & (longitude > 28) & (longitude < 40)
mediterr = xr.where(bool_medit_1 | bool_medit_2 | bool_medit_3, maskvar, 0)
newmask['mediterr'] = xr.DataArray(mediterr, attrs=dict(long_name = 'Mediterranean Sea'))
#
#
# Write the output netcdf file
#
newmask.to_netcdf(outfile)
sys.exit()

#Baltic Sea
#bool_baltic = np.
#
#North Atlantic
bool_natl_1 = np.logical_and(np.logical_and(latitude > 32,latitude < 73), np.logical_and(longitude>-95, longitude <26))
bool_natl_2 = np.logical_and(np.logical_and(latitude > 73,latitude < 75), np.logical_and(longitude>-30, longitude <24))
bool_natl_3 = np.logical_and(np.logical_and(latitude > 75,latitude < 77), np.logical_and(longitude>-30, longitude <22))
bool_natl_4 = np.logical_and(np.logical_and(latitude > 77,latitude < 79), np.logical_and(longitude>-30, longitude <18))
#Fram Strait!!!
bool_natl_5 = np.logical_and(np.logical_and(latitude > 79,latitude < 81), np.logical_and(longitude>-30, longitude <17))
#
bool_natl_6 = np.logical_and(np.logical_and(latitude > 73,latitude <= 82), np.logical_and(longitude>-83, longitude <-35))
bool_natl = np.logical_or(np.logical_or(bool_natl_1,bool_natl_2),bool_natl_3)
bool_natl = np.logical_or(bool_natl,bool_natl_4)
bool_natl = np.logical_or(bool_natl,bool_natl_5)
bool_natl = np.logical_or(bool_natl,bool_natl_6)
bool_natl = np.logical_and(bool_natl,np.logical_not(bool_medit))
northatl = np.where(bool_natl,maskvar,0)
dom_dict['North Atlantic Ocean'] = northatl
#
#Greenland Sea
bool_green_1 = np.logical_and(np.logical_and(latitude > 76,latitude < 81), np.logical_and(longitude>-30, longitude <17))
bool_green_2 = np.logical_and(np.logical_and(latitude > 75,latitude < 76), np.logical_and(longitude>-30, longitude <12))
bool_green_3 = np.logical_and(np.logical_and(latitude > 74,latitude < 75), np.logical_and(longitude>-30, longitude <9))
bool_green_4 = np.logical_and(np.logical_and(latitude > 73,latitude < 74), np.logical_and(longitude>-30, longitude <4))
bool_green_5 = np.logical_and(np.logical_and(latitude > 72,latitude < 73), np.logical_and(longitude>-30, longitude <0))
bool_green_6 = np.logical_and(np.logical_and(latitude > 71,latitude < 72), np.logical_and(longitude>-30, longitude <-3))
bool_green_7 = np.logical_and(np.logical_and(latitude > 70,latitude < 71), np.logical_and(longitude>-30, longitude <-8))
bool_green = bool_green_1
for i in range(2,8):
 exec('bool_green = np.logical_or(bool_green,bool_green_'+ str(i) +')')

#
greenlan = np.where(bool_green,maskvar,0)
dom_dict['Greenland Sea'] = greenlan
#
#Icelandic Sea: N->S, Jan Mayen is SE corner
bool_icel_1 = np.logical_and(np.logical_and(latitude > 69,latitude < 70), np.logical_and(longitude>-29, longitude <-9))
bool_icel_2 = np.logical_and(np.logical_and(latitude > 68,latitude < 69), np.logical_and(longitude>-28, longitude <-10))
bool_icel_3 = np.logical_and(np.logical_and(latitude > 67,latitude < 68), np.logical_and(longitude>-25, longitude <-11))
bool_icel_4 = np.logical_and(np.logical_and(latitude > 66,latitude < 67), np.logical_and(longitude>-23, longitude <-12))
bool_icel_5 = np.logical_and(np.logical_and(latitude > 65,latitude < 66), np.logical_and(longitude>-20, longitude <-13))
bool_icel = bool_icel_1 
for i in range(2,6):
 exec('bool_icel=np.logical_or(bool_icel,bool_icel_'+ str(i) +')')

icelands = np.where(bool_icel,maskvar,0)
dom_dict['Icelandic Sea'] = icelands
#
#Norwegian Sea: N->S, Bjornoya is E corner, then North Cape
bool_norw_1 = np.logical_and(np.logical_and(latitude > 75,latitude < 76), np.logical_and(longitude>12, longitude <17))
bool_norw_2 = np.logical_and(np.logical_and(latitude > 74,latitude < 75), np.logical_and(longitude>9, longitude <18))
bool_norw_3 = np.logical_and(np.logical_and(latitude > 73,latitude < 74), np.logical_and(longitude>4, longitude <19))
#I reached Bjornoya
bool_norw_4 = np.logical_and(np.logical_and(latitude > 72,latitude < 73), np.logical_and(longitude>0, longitude <21))
bool_norw_5 = np.logical_and(np.logical_and(latitude > 71,latitude < 72), np.logical_and(longitude>-3, longitude <23))
bool_norw_6 = np.logical_and(np.logical_and(latitude > 70,latitude < 71), np.logical_and(longitude>-8, longitude <25))
#I reached North Cape
bool_norw_7 = np.logical_and(np.logical_and(latitude > 66,latitude < 70), np.logical_and(longitude>-13, longitude <25))
bool_norw_7 = np.logical_and(bool_norw_7, np.logical_not(bool_icel))
bool_norw_8 = np.logical_and(np.logical_and(latitude > 62,latitude < 66), np.logical_and(longitude>-6, longitude <15))
bool_norw_9 = np.logical_and(np.logical_and(latitude > 61,latitude < 62), np.logical_and(longitude>0, longitude <15))
bool_norw_10 = np.logical_and(np.logical_and(latitude > 63,latitude < 64), np.logical_and(longitude>-8, longitude <-6))
bool_norw_11 = np.logical_and(np.logical_and(latitude > 64,latitude < 65), np.logical_and(longitude>-10, longitude <-6))
bool_norw_12 = np.logical_and(np.logical_and(latitude > 65,latitude < 66), np.logical_and(longitude>-13, longitude <-6))
bool_norw = bool_norw_1
for i in range(2,13):
 exec('bool_norw=np.logical_or(bool_norw,bool_norw_'+ str(i) +')')

norskhav = np.where(bool_norw,maskvar,0)
dom_dict['Norwegian Sea'] = norskhav
#
#GIN seas: simple one!!!
bool_gins = np.logical_or(np.logical_or(bool_green,bool_icel),bool_norw)
ginseasx = np.where(bool_gins,maskvar,0)
dom_dict['Nordic Seas'] = ginseasx
dom_dict['Grnland']=ginseasx
dom_arct['GINSEASX'] = ginseasx
#
#
#Barents Sea (including White Sea)
#E limit of Greenland Sea -> FJL -> Cape Zhelanya
bool_barnts_1 = np.logical_and(np.logical_and(latitude > 76,latitude < 80), np.logical_and(longitude>17, longitude <65))
#E limit of Norwegian Sea -> Novaya Zemlya
bool_barnts_2 = np.logical_and(np.logical_and(latitude > 75,latitude < 76), np.logical_and(longitude>17, longitude <62))
bool_barnts_3 = np.logical_and(np.logical_and(latitude > 74,latitude < 75), np.logical_and(longitude>18, longitude <59))
bool_barnts_4 = np.logical_and(np.logical_and(latitude > 73,latitude < 74), np.logical_and(longitude>19, longitude <58))
bool_barnts_5 = np.logical_and(np.logical_and(latitude > 72,latitude < 73), np.logical_and(longitude>21, longitude <56))
bool_barnts_6 = np.logical_and(np.logical_and(latitude > 71,latitude < 72), np.logical_and(longitude>23, longitude <56))
bool_barnts_7 = np.logical_and(np.logical_and(latitude > 70,latitude < 71), np.logical_and(longitude>25, longitude <57))
#I reached North Cape and Kara Gate Strait
bool_barnts_8 = np.logical_and(np.logical_and(latitude > 66,latitude < 70), np.logical_and(longitude>25, longitude <60))
#I fill the White Sea
bool_barnts_9 = np.logical_and(np.logical_and(latitude > 63,latitude < 66), np.logical_and(longitude>30, longitude <45))
bool_barnts = bool_barnts_1
for i in range(2,10):
 exec('bool_barnts=np.logical_or(bool_barnts,bool_barnts_'+ str(i) +')')

barentsx = np.where(bool_barnts, maskvar, 0)
dom_dict['Barents Sea'] = barentsx
dom_arct['BARENTSX'] = barentsx
#
#
#Kara Sea
#Northern part: FJL - Svernya Zemlya - Cape Chelyuskin - Cape Zhelanya
bool_kara_1 = np.logical_and(np.logical_and(latitude > 79,latitude < 80), np.logical_and(longitude>65, longitude <96))
bool_kara_2 = np.logical_and(np.logical_and(latitude > 76,latitude <= 79), np.logical_and(longitude>65, longitude <105))
#I fill southwestern part of the sea
bool_kara_3 = np.logical_and(np.logical_and(latitude > 75,latitude < 76), np.logical_and(longitude>62, longitude <100))
bool_kara_4 = np.logical_and(np.logical_and(latitude > 74,latitude < 75), np.logical_and(longitude>59, longitude <100))
bool_kara_5 = np.logical_and(np.logical_and(latitude > 73,latitude < 74), np.logical_and(longitude>58, longitude <100))
bool_kara_6 = np.logical_and(np.logical_and(latitude > 71,latitude < 73), np.logical_and(longitude>56, longitude <100))
bool_kara_7 = np.logical_and(np.logical_and(latitude > 70,latitude < 71), np.logical_and(longitude>57, longitude <100))
#I reached Kara Gate Strait and Yamal coast
bool_kara_8 = np.logical_and(np.logical_and(latitude > 66,latitude < 70), np.logical_and(longitude>60, longitude <90))
bool_kara = bool_kara_1
for i in range(2,9):
 exec('bool_kara=np.logical_or(bool_kara,bool_kara_'+ str(i) +')')

karaxxxx = np.where(bool_kara, maskvar, 0)
dom_dict['Kara Sea'] = karaxxxx
dom_arct['KARAXXXX'] = karaxxxx
#
#
#Laptev Sea
#
bool_lapt_1 =  np.logical_and(np.logical_and(latitude > 80,latitude < 81), np.logical_and(longitude>96, longitude <102))
bool_lapt_2 =  np.logical_and(np.logical_and(latitude > 79,latitude < 80), np.logical_and(longitude>100, longitude <111))
bool_lapt_3 =  np.logical_and(np.logical_and(latitude > 78,latitude < 79), np.logical_and(longitude>105, longitude <120))
bool_lapt_4 =  np.logical_and(np.logical_and(latitude > 77,latitude < 78), np.logical_and(longitude>105, longitude <129))
bool_lapt_5 =  np.logical_and(np.logical_and(latitude > 76,latitude < 77), np.logical_and(longitude>100, longitude <138))
#I reached Novaya Zemlya Archipelago: now cross Laptev Strait
bool_lapt_6 =  np.logical_and(np.logical_and(latitude > 70,latitude < 76), np.logical_and(longitude>105, longitude <140))
bool_lapt = bool_lapt_1
for i in range(2,7):
 exec('bool_lapt=np.logical_or(bool_lapt,bool_lapt_'+ str(i) +')')

laptevxx = np.where(bool_lapt, maskvar, 0)
dom_dict['Laptev Sea'] = laptevxx
dom_arct['LAPTEVXX'] = laptevxx
#
#
#East Siberian Sea
#
bool_easib_1 = np.logical_and(np.logical_and(latitude > 74,latitude < 75), np.logical_and(longitude>140, longitude <146))
bool_easib_2 = np.logical_and(np.logical_and(latitude > 73,latitude < 74), np.logical_and(longitude>140, longitude <154))
bool_easib_3 = np.logical_and(np.logical_and(latitude > 72,latitude < 73), np.logical_and(longitude>140, longitude <162))
bool_easib_4 = np.logical_and(np.logical_and(latitude > 71,latitude < 72), np.logical_and(longitude>140, longitude <170))
bool_easib_5 = np.logical_and(np.logical_and(latitude > 70,latitude < 71), np.logical_and(longitude>140, longitude <179))
#I reached Wrangel Island (and it is so beautiful)
bool_easib_6 = np.logical_and(np.logical_and(latitude > 69,latitude < 70), np.logical_and(longitude>140, longitude <178))
bool_easib_7 = np.logical_and(np.logical_and(latitude > 68,latitude < 69), np.logical_and(longitude>140, longitude <178))
bool_easib = bool_easib_1
for i in range(2,8):
 exec('bool_easib=np.logical_or(bool_easib,bool_easib_'+ str(i) +')')

eastsibe = np.where(bool_easib,maskvar,0)
dom_dict['East Siberian Sea'] = eastsibe
dom_arct['EASTSIBE'] = eastsibe
#
#
#Chukchi Sea
#
bool_chuk_1 = np.logical_and(np.logical_and(latitude > 66,latitude < 71), longitude <-156)
bool_chuk_2 = np.logical_and(np.logical_and(latitude > 66,latitude < 71), longitude>179)
bool_chuk_3 = np.logical_and(np.logical_and(latitude > 69,latitude < 70), longitude>178)
bool_chuk = np.logical_or(bool_chuk_1,bool_chuk_2)
bool_chuk = np.logical_or(bool_chuk,bool_chuk_3)
chukchis = np.where(bool_chuk,maskvar,0)
dom_dict['Chukchi Sea'] = chukchis
dom_arct['CHUKCHIS'] = chukchis
#
#
#Bering Sea
#
bool_bering_1 = np.logical_and(np.logical_and(latitude > 58,latitude < 66), longitude <-154)
bool_bering_2 = np.logical_and(np.logical_and(latitude > 60,latitude < 66), longitude>164)
bool_bering_3 = np.logical_and(np.logical_and(latitude > 57,latitude < 60), longitude>163)
bool_bering_4 = np.logical_and(np.logical_and(latitude > 58,latitude < 60), longitude<-155)
bool_bering_5 = np.logical_and(np.logical_and(latitude > 57,latitude < 58), np.logical_or(longitude<-157, longitude>163))
bool_bering_6 = np.logical_and(np.logical_and(latitude > 56,latitude < 57), np.logical_or(longitude<-160, longitude>167))
bool_bering_7 = np.logical_and(np.logical_and(latitude > 55,latitude < 56), np.logical_or(longitude<-165, longitude>171))
bool_bering_8 = np.logical_and(np.logical_and(latitude > 54,latitude < 55), np.logical_or(longitude<-170, longitude>174))
bool_bering_9 = np.logical_and(np.logical_and(latitude > 53,latitude < 54), np.logical_or(longitude<-174, longitude>177))
bool_bering_10 = np.logical_and(np.logical_and(latitude > 52,latitude < 53), longitude<-178)

bool_bering = bool_bering_1
for i in range(2,11):
 exec('bool_bering=np.logical_or(bool_bering,bool_bering_'+ str(i) +')')

beringx = np.where(bool_bering,maskvar,0)
dom_dict['Bering'] = beringx
dom_arct['BERINGXX'] = beringx
#
#
#Okhotsk Sea
#First step: Kuriles archipelago and Sakhaline Island
bool_okhot_1 = np.logical_and(np.logical_and(latitude > 43,latitude < 44), np.logical_and(longitude>142, longitude <145))
bool_okhot_2 = np.logical_and(np.logical_and(latitude > 44,latitude < 45), np.logical_and(longitude>142, longitude <146.5))
bool_okhot_3 = np.logical_and(np.logical_and(latitude > 45,latitude < 46), np.logical_and(longitude>142, longitude <148))
bool_okhot_4 = np.logical_and(np.logical_and(latitude > 46,latitude < 47), np.logical_and(longitude>142, longitude <149.5))
bool_okhot_5 = np.logical_and(np.logical_and(latitude > 47,latitude < 48), np.logical_and(longitude>143, longitude <151))
bool_okhot_6 = np.logical_and(np.logical_and(latitude > 48,latitude < 49), np.logical_and(longitude>143, longitude <152.5))
bool_okhot_7 = np.logical_and(np.logical_and(latitude > 49,latitude < 50), np.logical_and(longitude>143, longitude <154))
bool_okhot_8 = np.logical_and(np.logical_and(latitude > 50,latitude < 51), np.logical_and(longitude>143, longitude <155.5))
bool_okhot_9 = np.logical_and(np.logical_and(latitude > 51,latitude < 52), np.logical_and(longitude>143, longitude <157))
#I am at the southernmost point of Kamtchatka
bool_okhot_10 = np.logical_and(np.logical_and(latitude > 52,latitude < 63), np.logical_and(longitude>135, longitude <157))
bool_okhot_11 = np.logical_and(np.logical_and(latitude > 58,latitude < 63), np.logical_and(longitude>157, longitude <163))
bool_okhot_12 = np.logical_and(np.logical_and(latitude > 60,latitude < 63), np.logical_and(longitude>162, longitude <164))
bool_okhot = bool_okhot_1
for i in range(2,13):
 exec('bool_okhot=np.logical_or(bool_okhot,bool_okhot_'+ str(i) +')')

okhotskx = np.where(bool_okhot, maskvar, 0)
dom_dict['Okhotsk'] = okhotskx
dom_arct['OKHOTSKX'] = okhotskx
#
#Beaufort Sea !!!!Peut etre a revoir (NW PASSAGE)!!!!
#
bool_beauf_1 = np.logical_and(np.logical_and(latitude > 75,latitude < 76), np.logical_and(longitude>-130, longitude <-124))
bool_beauf_2 = np.logical_and(np.logical_and(latitude > 74,latitude < 75), np.logical_and(longitude>-136, longitude <-124))
bool_beauf_3 = np.logical_and(np.logical_and(latitude > 73,latitude < 74), np.logical_and(longitude>-143, longitude <-125))
bool_beauf_4 = np.logical_and(np.logical_and(latitude > 72,latitude < 73), np.logical_and(longitude>-149, longitude <-125))
bool_beauf_5 = np.logical_and(np.logical_and(latitude > 71,latitude < 72), np.logical_and(longitude>-156, longitude <-126))
bool_beauf_6 = np.logical_and(np.logical_and(latitude > 70,latitude < 71), np.logical_and(longitude>-156, longitude <-126))
bool_beauf_7 = np.logical_and(np.logical_and(latitude > 69,latitude < 70), np.logical_and(longitude>-156, longitude <-127))
bool_beauf_8 = np.logical_and(np.logical_and(latitude > 73,latitude < 77), np.logical_and(longitude>-124, longitude <-120))
bool_beauf_9 = np.logical_and(np.logical_and(latitude > 73,latitude < 75), np.logical_and(longitude>-125, longitude <-124))
bool_beauf_10 = np.logical_and(np.logical_and(latitude > 69,latitude < 73), np.logical_and(longitude>-127, longitude <-124))
bool_beauf = bool_beauf_1
for i in range(2,11):
 exec('bool_beauf=np.logical_or(bool_beauf,bool_beauf_'+ str(i) +')')

beaufort = np.where(bool_beauf, maskvar, 0)
dom_dict['Beaufort Sea'] = beaufort
dom_arct['BEAUFORT'] = beaufort
#
#
#Baffin Bay (including Kennedy Passage and Davis Strait)
#
bool_baff_1 = np.logical_and(np.logical_and(latitude > 70,latitude < 81), np.logical_and(longitude>-84, longitude <-45))
#Now, it is the official definition of Davis Strait...
bool_baff_2 = np.logical_and(np.logical_and(latitude > 66,latitude < 70), np.logical_and(longitude>-70, longitude <-45))
bool_baff_3 = np.logical_and(np.logical_and(latitude > 62,latitude < 66), np.logical_and(longitude>-66, longitude <-45))
bool_baff_4 = np.logical_and(np.logical_and(latitude > 61,latitude < 62), np.logical_and(longitude>-65, longitude <-45))
bool_baff = bool_baff_1
for i in range(2,5):
 exec('bool_baff=np.logical_or(bool_baff,bool_baff_'+ str(i) +')')

baffinxx = np.where(bool_baff,maskvar,0)
dom_dict['Baffin Bay'] = baffinxx
dom_arct['BAFFINXX'] = baffinxx
#
#
#Hudson Bay (including Hudson Strait and Foxe Basin)
#
bool_huds_1 = np.logical_and(np.logical_and(latitude > 50,latitude < 67), np.logical_and(longitude>-95, longitude <-66))
bool_huds_2 = np.logical_and(np.logical_and(latitude > 67,latitude < 70), np.logical_and(longitude>-85, longitude <-70))
bool_huds_3 = np.logical_and(np.logical_and(latitude > 59,latitude < 62), np.logical_and(longitude>-66, longitude <-65))
bool_huds = bool_huds_1
for i in range(2,4):
 exec('bool_huds=np.logical_or(bool_huds,bool_huds_'+ str(i) +')')

hudsonxx = np.where(bool_huds,maskvar,0)
dom_dict['Hudson'] = hudsonxx
dom_arct['HUDSONXX'] = hudsonxx
#
#
#Labrador Sea
#
bool_labr_1 = np.logical_and(np.logical_and(latitude > 60,latitude < 61), np.logical_and(longitude>-65, longitude <-45))
bool_labr_2 = np.logical_and(np.logical_and(latitude > 59,latitude < 60), np.logical_and(longitude>-65, longitude <-46))
bool_labr_3 = np.logical_and(np.logical_and(latitude > 58,latitude < 59), np.logical_and(longitude>-64, longitude <-46))
bool_labr_4 = np.logical_and(np.logical_and(latitude > 57,latitude < 58), np.logical_and(longitude>-63, longitude <-47))
bool_labr_5 = np.logical_and(np.logical_and(latitude > 56,latitude < 57), np.logical_and(longitude>-62, longitude <-47))
bool_labr_6 = np.logical_and(np.logical_and(latitude > 55,latitude < 56), np.logical_and(longitude>-61, longitude <-48))
bool_labr_7 = np.logical_and(np.logical_and(latitude > 54,latitude < 55), np.logical_and(longitude>-60, longitude <-48))
bool_labr_8 = np.logical_and(np.logical_and(latitude > 53,latitude < 54), np.logical_and(longitude>-59, longitude <-49))
bool_labr_9 = np.logical_and(np.logical_and(latitude > 52,latitude < 53), np.logical_and(longitude>-58, longitude <-49))
bool_labr_10 = np.logical_and(np.logical_and(latitude > 51,latitude < 52), np.logical_and(longitude>-57, longitude <-50))
bool_labr_11 = np.logical_and(np.logical_and(latitude > 50,latitude < 51), np.logical_and(longitude>-56, longitude <-50))
bool_labr_12 = np.logical_and(np.logical_and(latitude > 49,latitude < 50), np.logical_and(longitude>-56, longitude <-51))
#bool_labr_13 = np.logical_and(np.logical_and(latitude > 48,latitude < 49), np.logical_and(longitude>-54, longitude <-51))
bool_labr = bool_labr_1
for i in range(2,13):
 exec('bool_labr=np.logical_or(bool_labr,bool_labr_'+ str(i) +')')

labrador = np.where(bool_labr,maskvar,0)
dom_dict['Labrador Sea'] = labrador
dom_arct['LABRADOR'] = labrador
#
#
#Northwest Passage
#Southern part (passage Amundsen + official passage)
bool_nwpa_1 = np.logical_and(np.logical_and(latitude > 73,latitude < 77), np.logical_and(longitude>-120, longitude <-84))
bool_nwpa_2 = np.logical_and(np.logical_and(latitude > 67,latitude < 73), np.logical_and(longitude>-124, longitude <-85))
#Northern part (Sverdrup Basin)
bool_nwpa_3 = np.logical_and(np.logical_and(latitude > 76,latitude < 77), np.logical_and(longitude>-120, longitude <-84))
bool_nwpa_4 = np.logical_and(np.logical_and(latitude > 77,latitude < 78), np.logical_and(longitude>-116, longitude <-84))
bool_nwpa_5 = np.logical_and(np.logical_and(latitude > 78,latitude < 79), np.logical_and(longitude>-108, longitude <-84))
bool_nwpa_6 = np.logical_and(np.logical_and(latitude > 79,latitude < 80), np.logical_and(longitude>-100, longitude <-84))
bool_nwpa_7 = np.logical_and(np.logical_and(latitude > 80,latitude < 81), np.logical_and(longitude>-93, longitude <-84))
bool_nwpa_8 = np.logical_and(np.logical_and(latitude > 81,latitude < 82), np.logical_and(longitude>-85, longitude <-84))
bool_nwpa_9 = np.logical_and(np.logical_and(latitude > 82,latitude < 83), np.logical_and(longitude>-77, longitude <-75))
#I reached Cape Columbia (Ellesmere Island): I can walk toward North Pole!!!
bool_nwpa = bool_nwpa_1
for i in range(2,10):
 exec('bool_nwpa=np.logical_or(bool_nwpa,bool_nwpa_'+ str(i) +')')

nwestpas = np.where(bool_nwpa,maskvar,0)
dom_dict['NorthWest Passage'] = nwestpas
dom_dict['CanArch']=nwestpas
dom_arct['NWESTPAS'] = nwestpas
#x.clear()
#x.plot(nhemisph + 2*hudsonxx+2*baffinxx + 2*labrador + 2*beaufort + nwestpas)
#
#
#Lincoln Sea
bool_linc_1 = np.logical_and(np.logical_and(latitude > 81,latitude < 84), np.logical_and(longitude>-60, longitude <-32))
bool_linc_2 = np.logical_and(np.logical_and(latitude > 81,latitude < 83), np.logical_and(longitude>-70, longitude <-60))
bool_linc = np.logical_or(bool_linc_1,bool_linc_2)

lincolnx = np.where(bool_linc,maskvar,0)
dom_dict['Lincoln Sea'] = lincolnx
dom_arct['LINCOLNX'] = lincolnx
#
#
#Irminger Sea

#Marginal seas
dict_marg = ['GINSEASX','BARENTSX','KARAXXXX','BAFFINXX','LAPTEVXX','HUDSONXX','EASTSIBE','BEAUFORT','NWESTPAS','CHUKCHIS','BERINGXX','OKHOTSKX']
dict_marg = ['Nordic Seas', 'Barents Sea', 'Kara Sea', 'Baffin Bay', 'Laptev Sea', 'Hudson', 'East Siberian Sea', 'Beaufort Sea', 'NorthWest Passage', 'Chukchi Sea', 'Bering', 'Okhotsk']
marg = maskvar
for sea in dict_marg:
 marg = marg + dom_dict[sea]
bool_marg=marg[0]>1
dom_dict['Arctic Marginal seas'] = np.where(bool_marg,maskvar[0],0)
dom_arct['MIZSEASX'] = np.where(bool_marg,maskvar[0],0)


#Central Arctic
bool_centrarc = np.equal(marg,nhemisph)
bool_centrarc = np.logical_and(bool_centrarc, latitude > 70)
bool_centrarc = np.logical_and(bool_centrarc, np.logical_not(bool_linc))
centrarc = np.where(bool_centrarc,maskvar, 0)
dom_dict['Central Arctic'] = centrarc[0]
dom_arct['CENTRARC'] = centrarc[0]
#
#West Central Arctic
bool_westcarc = np.logical_and(bool_centrarc, np.absolute(longitude)>=90)
wcentarc =  np.where(bool_westcarc,maskvar, 0)
dom_dict['Western Central Arctic'] = wcentarc[0]
#
#East Central Arctic
bool_eastcarc = np.logical_and(bool_centrarc, np.absolute(longitude)<90)
ecentarc =  np.where(bool_eastcarc,maskvar, 0)
dom_dict['Eastern Central Arctic'] = ecentarc[0]
#
#
#
#
#
#Baltic Sea
#Gulfs of Bothnia, Riga, Finland.
bool_balt_1 = np.logical_and(np.logical_and(latitude > 50,latitude < 66), np.logical_and(longitude>15, longitude <30))
#South of Sweden until Copenhaguen
bool_balt_2 = np.logical_and(np.logical_and(latitude > 50,latitude < 56), np.logical_and(longitude>10, longitude <15))
bool_balt = bool_balt_1
bool_balt = np.logical_or(bool_balt, bool_balt_2)
baltseax = np.where(bool_balt,maskvar,0)
dom_dict['Baltic Sea'] = baltseax
dom_arct['BALTICXX'] = baltseax
#
#
# Gulf of Saint-Lawrence
bool_slaw = np.logical_and(np.logical_and(longitude>-70, longitude<-55),np.logical_and(latitude<52,latitude>48))
bool_slaw = np.logical_or(bool_slaw, np.logical_and(np.logical_and(longitude>-70, longitude<-58),np.logical_and(latitude<=48,latitude>47)))
bool_slaw = np.logical_or(bool_slaw, np.logical_and(np.logical_and(longitude>-70, longitude<-59),np.logical_and(latitude<=47,latitude>46)))
bool_slaw = np.logical_or(bool_slaw, np.logical_and(np.logical_and(longitude>-70, longitude<-60),np.logical_and(latitude<=46,latitude>45)))
bool_slaw = np.logical_and(bool_slaw, np.logical_not(bool_labr))
slawrglf=np.where(bool_slaw,maskvar,0)
dom_dict['StLawr']=slawrglf
dom_arct['SLAWRGLF']=slawrglf

#
#
#Caspian Sea (for fun)
bool_casp = np.logical_and(np.logical_and(latitude > 35,latitude < 50), np.logical_and(longitude>45, longitude <60))
caspianx = np.where(bool_casp,maskvar,0)
dom_dict['Caspian Sea'] = caspianx
#
#
#Northern Hemisphere oceanic seas
nhemisptot = nhemisph + caspianx + baltseax
bool_nohemi = np.equal(nhemisptot,nhemisph)
nnhemisp=np.where(bool_nohemi,nhemisph,0)
dom_dict['North Hemisphere Ocean'] = nnhemisp

#ref_gridf = cdms.open('/data3/udc/chevalli/NEMO3.2_LIM/OCE04')
#
#MAIN STRAITS
#
#Fram Strait (Northernmost Greenland Sea)
bool_fram= np.logical_and(np.logical_and(latitude > 80,latitude < 81), np.logical_and(longitude>-30, longitude <17))
fram = np.where(bool_fram,maskvar,0)
dom_dict['Fram Strait'] = fram
#
#
#Bering Strait (Southernmost Chukchi Sea: in Chk Sea)
bool_bers= np.logical_and(np.logical_and(latitude > 65,latitude < 66), np.logical_and(longitude > -175 , longitude <-165))
beringst = np.where(bool_bers,maskvar,0)
dom_dict['Bering Strait'] = beringst
#bool_chuk_1 = np.logical_and(np.logical_and(latitude > 66,latitude < 71), longitude <-156)
#bool_chuk_2 = np.logical_and(np.logical_and(latitude > 66,latitude < 71), longitude>179)
#
#
#Nares Strait (Northernmost Baffin Bay)
bool_nares = np.logical_and(np.logical_and(latitude > 80,latitude < 81), np.logical_and(longitude > -84 , longitude <-45))
narestr = np.where(bool_nares,maskvar,0)
dom_dict['Nares Strait'] = narestr
#
#
#Kara Gate Strait 
bool_kaga_1 = np.logical_and(np.logical_and(latitude > 70,latitude < 71), np.logical_and(longitude>57, longitude <59))
bool_kaga_2 = np.logical_and(np.logical_and(latitude > 69,latitude < 70), np.logical_and(longitude>60, longitude <61))
bool_kaga = bool_kaga_1
bool_kaga = np.logical_or(bool_kaga,bool_kaga_2)
karagstr = np.where(bool_kaga,maskvar,0)
dom_dict['Kara Gate Strait'] = karagstr
#
#
#Vilkitsky Strait
bool_vilk_1 = np.logical_and(np.logical_and(latitude > 76,latitude <= 79), np.logical_and(longitude>100, longitude <105))
bool_vilk_2 = np.logical_and(np.logical_and(latitude > 70,latitude < 76), np.logical_and(longitude>99, longitude <100))
bool_vilk = bool_vilk_1
bool_vilk = np.logical_or(bool_vilk,bool_vilk_2)
vilkystr = np.where(bool_vilk,maskvar,0)
dom_dict['Vilkitsky Strait'] = vilkystr
#
#
#Simple boxes splitting the Antarctic Ocean...
#
#
#
#
#
#Atlantic-Antarctic
#
bool_atlantxx_1 = np.logical_and(latitude<-55, longitude>-15)
bool_atlantxx_2 = np.logical_and(latitude<-55, longitude <22)
bool_atlantxx = np.logical_and(bool_atlantxx_1,bool_atlantxx_2)
atlantxx = np.where(bool_atlantxx,maskvar,0)
dom_dict['Antarctic Atlantic Sector'] = atlantxx
#
#
#Indian-Antarctic
#
bool_indiant = np.logical_and(latitude<-55, np.logical_and(longitude>22, longitude <160))
indiantx = np.where(bool_indiant,maskvar,0)
dom_dict['Antarctic Indian Sector'] = indiantx
#
#
#Other domains: lat
lat80n = np.where(latitude>80.,maskvar,0.)
dom_dict['LAT80N']=lat80n
#
#
# FOR OTHER BASINS: use subbasins.nc
#
fsubname='new_maskglo.'+version+'.nc'
fsub=cdms.open(fsubname)
# Atlantic Ocean
#
matl=fsub('tmaskatl',squeeze=1)
dom_dict['Atlantic Ocean']=matl
# Pacific Ocean
mpac=fsub('tmaskpac',squeeze=1)
dom_dict['Pacific Ocean']=mpac
# Indian Ocean
mind=fsub('tmaskind',squeeze=1)
dom_dict['Indian Ocean']=mind
#
fsub.close()
#
# Indian + Pacific ocean
#
mipc=mpac+mind
mipc[:170,70:73]=dom_dict['Global Ocean'][:170,70:73]
dom_dict['Indo-Pacific Ocean']=mipc
#
# COMBINAISON DE REGION (PLUS PERTINENTE)
#
# Barents + Kara Seas
#
dom_dict['BarKara']=dom_dict['Barents Sea']+dom_dict['Kara Sea']
#
# East Sib + Laptev Seas
#
dom_dict['Laptev-East Siberian Seas']=dom_dict['East Siberian Sea']+dom_dict['Laptev Sea']
#
# Canadian Archipelago
#
dom_dict['Canadian Waters']=dom_dict['NorthWest Passage']+dom_dict['Baffin Bay']+dom_dict['Hudson']+dom_dict['Labrador Sea']
#
# Beaufort + Chukchi Seas
# 
dom_dict['Beaufort-Chukchi Sea']=dom_dict['Beaufort Sea']+dom_dict['Chukchi Sea']
#
# East Sib + Laptev + Chukchi Seas
#
dom_dict['Laptev-East Siberian-Chukchi Seas']=dom_dict['Laptev-East Siberian Seas']+dom_dict['Chukchi Sea']
#
# GIN + Barents Seas
#
dom_dict['Nordic-Barents Seas']=dom_dict['Nordic Seas']+dom_dict['Barents Sea']
#
# Mask Serreze
boolarcticxx=dom_dict['Central Arctic']+dom_dict['Barents Sea']+\
		dom_dict['Kara Sea']+dom_dict['Laptev Sea']+\
		dom_dict['East Siberian Sea']+dom_dict['Chukchi Sea']+\
		dom_dict['Beaufort Sea']+dom_dict['Lincoln Sea']
boolamundsen=np.logical_and(nwestpas,longitude<-113.)
dom_dict['Serreze Arctic']=boolarcticxx+boolamundsen
#
# =======================
# COMBINAISON POUR COMPARER AVEC LE NSIDC
# OKOTSKH OK
# BERING OK
# HUDSON OK
# BAFFIN: BAFFIN+LABRADOR
nsbaffin=baffinxx+labrador
nsbaffin.setAxisList(baffinxx.getAxisList())
dom_dict['Baffin']=nsbaffin
# GREENLAND: OK
# BARKARA: OK
# ARCTOCN: CENTRARC+LINCOLN+CHUKCHI+EASTSIB+LAPTEV+BEAUFORT
nsarcton=centrarc[0,...]+lincolnx+chukchis+eastsibe+laptevxx+beaufort
dom_dict['ArctOcn']=nsarcton
# STLAWR: OK
# OPENOCEN: NNHEMISP - ARCTICOC - LABRADOR - STLAW + BALTIC
openocen=nnhemisp-arcticoc[0] - labrador-slawrglf+baltseax
dom_dict['OpenOcean']=openocen
# 
# ARCTIC NSIDC
# 
inhnsidc=nsarcton+openocen+nsbaffin+okhotskx+beringx+\
		hudsonxx+ginseasx+\
		dom_dict['Barents Sea']+dom_dict['Kara Sea']+\
		slawrglf+nwestpas
dom_dict['TotalArc']=inhnsidc
# 
# ======================================================
# NOUVEAUX MASQUES (stage Marion)
natlarc=northatl+dom_dict['Barents Sea'] - dom_dict['Hudson']-dom_dict['CanArch']-dom_dict['Baltic Sea']
dom_dict['North Atlantic-Arctic']=np.where(natlarc>=1.,1.,0.)
#
spgyre=natlarc-dom_dict['Baffin Bay']-dom_dict['Nordic-Barents Seas']
spgyre=np.where(latitude>=70.,0.,spgyre)
dom_dict['Subpolar Gyre']=np.where(spgyre>=1.,1.,0.)

arcnatl=natlarc+nsarcton+dom_dict['Kara Sea']
dom_dict['Arctic Ocean-North Atlantic']=np.where(arcnatl>=1.,1.,0.)


#
fout = cdms.open('mask.ArcticSeas.'+version+'.nc','w')
#fout2= cdms.open('Mask_NEMO_1_image.nc','w')
i=1
dom_image = maskvar

for dom in dom_dict:
	dom_var = cdms.createVariable(np.where(dom_dict[dom]>=1.,1.,0.))
	dom_var.getAxisList()[0].designateLatitude()
	dom_var.getAxisList()[1].designateLongitude()
	dom_var.long_name = dom
	dom_var.short_name = dom
	dom_var.id = dom
	fout.write(dom_var)
#	i+=
#for dom in dom_arct:
#	dom_image = np.add(dom_image, i*dom_dict[dom])
#	i = i+1
#fout2.write(dom_image)
fout.close()
#fout2.close()
# This script defines a mask for each individual sea and ocean based #
# on their official definition found in                              #
#    IHO PUBLICATION S-23, Limits of Oceans and Seas,                #
#       Draft 4th Edition, 2002                                      #
# Current link : 
#       https://legacy.iho.int/mtg_docs/com_wg/S-23WG/S-23WG_Misc/Draft_2002/Draft_2002.htm
# except for some adaptation to account for the discretization of    # 
# the coastline on the ORCA1 grid as indicated in the comments.      #
#                                                                    #
# History : 2025 - initial version by Virginie Guemas                #
######################################################################
import sys
import xarray as xr
