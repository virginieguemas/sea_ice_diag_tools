# This script defines a mask for each individual sea and ocean based #
# on their official definition found in                              #
#    IHO PUBLICATION S-23, Limits of Oceans and Seas,                #
#       Draft 4th Edition, 2002                                      #
# Current link : 
#       https://legacy.iho.int/mtg_docs/com_wg/S-23WG/S-23WG_Misc/Draft_2002/Draft_2002.htm
# except for some adaptation to account for the discretization of    # 
# the coastline on the ORCA1 grid as indicated in the comments.      #
#                                                                    #
# History : 2026 - initial version by Virginie Guemas                #
######################################################################
import sys
import xarray as xr
import datetime
import getpass
import numpy as np

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
# Eastern limit along the coast
bell_north_lon = [-102.25, -90.62, -67.80, -65. ]
bell_north_lat = [-72.10, -68.72, -66.63, -66.63]
bellings = xr.where((latitude < np.interp(longitude, bell_north_lon, bell_north_lat)) & (longitude > -102.25) & (longitude < -65.), maskvar, 0)
newmask['bellings'] = xr.DataArray(bellings, attrs=dict(long_name = 'Bellingshausen Sea'))
#
# 4d. Weddell Sea (S-23 10.1)
wedd_north_lon = [-55.15, -54.10, -53.98, -46.05, -44.43, -27.37]
wedd_north_lat = [-63.18, -61.30, -61.13, -60.63, -60.73, -59.45]
wedd_east_lat = [-71.38, -59.45]
wedd_east_lon = [-12.27, -27.37]
weddells = xr.where(((latitude < np.interp(longitude, wedd_north_lon, wedd_north_lat)) & (longitude > -57) & (longitude < np.interp(latitude, wedd_east_lat, wedd_east_lon))) | ((latitude < -65) & (longitude > -62) & (longitude < -57)) | ((latitude < -64) & (longitude > -60) & (longitude < -57)), maskvar, 0)
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
davissea = xr.where((latitude < np.interp(longitude, [81.67, 95.58], [-65.0, -64.0])) & (longitude > 81.67) & (longitude < 95.58), maskvar, 0)
newmask['davissea'] = xr.DataArray(davissea, attrs=dict(long_name = 'Davis Sea'))
#
# 4ibis. Tryoshnikova Gulf (S-23 10.6.1)
tryoshni = xr.where((latitude < np.interp(longitude, [88.02, 95.58], [-65.92, -64.93])) & (longitude > 88.02) & (longitude < 95.58), maskvar, 0)
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
# 72S set to avoid capturing part of Ross sea
somov_north_lon = [146.83, 162.32]
somov_north_lat = [-64.0, -66.27]
somov_east_lon = [162.32, 164.82, 170.23]
somov_east_lat = [-66.27, -67.60, -71.30]
somovsea = xr.where((latitude < np.interp(longitude, somov_north_lon, somov_north_lat)) & (longitude > 146.83) & (longitude <= 162.32), maskvar, 0)
somovsea = xr.where((latitude < np.interp(longitude, somov_east_lon, somov_east_lat)) & (longitude > 162.32) & (longitude < 170.23) & (latitude > -72), maskvar, somovsea)
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
# Kara Sea / Laptev Sea (S-23 9.2 West / 9.3 East)
#sevzem_lat = [77.53, 78.30, 79.42, 79.67, 80.17, 80.22, 81.27]
#sevzem_lon = [105.92, 104.83, 102.42, 100.33, 97.67, 97.33, 95.75]
# Adaptation for ORCA1 NEMO4.2.3
sevzem_lat = [77.53, 78.30, 79.42, 79.60, 80.17, 80.22, 81.27]
sevzem_lon = [105.92, 104.83, 102.42, 100.25, 97.67, 97.33, 95.75]
#
# Barents Sea / Kara Sea (S-23 9.3 West / 9.4 East)
novzem_lat = [69.60, 69.67, 70.25, 70.47, 73.28, 73.35, 76.95, 81.00]
novzem_lon = [60.20, 59.98, 58.43, 57.12, 53.88, 54.08, 68.58, 65.33]
#
# Norwegian Sea / Barents Sea (S-23 9.4 West / 9.7 Northeast)
barnor_lat = [71.17, 74.35, 74.52, 76.47, 80.07]
barnor_lon = [25.78, 19.08, 19.12, 16.62, 16.27]
#
# Greenland Sea east/southeast/south limit
# the common limit with the Norwegian Sea (S-23 9.6 East/Southeast/South)
greennor_lat = [70.15, 70.83, 71.17, 76.47, 80.07]
greennor_lon = [-22.07, -9.00, -7.97, 16.62, 16.27]
#
# Iceland Sea / Norwegian Sea (S-23 9.7 West / 9.8 East)
norice_lat = [62.35, 70.83]
norice_lon = [-6.25, -9.00]
#
# Beaufort Sea / Northwestern Passages (S-23 9.14 West / 9.15 East)
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
hs_north_lon = [-80.98, -78.03, -75., -65.97, -64.78]
hs_north_lat = [63.45, 64.43, 65., 61.88, 61.32]
hs_south_lon = [-80.98, -78.10, -76., -64.43, -64.43]
hs_south_lat = [63.45, 62.37, 57., 57., 60.40]
hs_east_lat = [57.5, 60.40, 61.32, 61.63, 61.75, 61.78, 61.88]
hs_east_lon = [-64.43, -64.43, -64.78, -65.48, -65.67, -65.95, -65.97]
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
baff_west_lat = [70.00, 74.60, 80., 82.47]
baff_west_lon = [-71., -80.23, -80.23,  -61.52]
baff_north_lat = [82.47, 82.35]
baff_north_lon = [-61.52, -55.17]
baffinba = xr.where((latitude > 70) & (latitude < np.interp(longitude, baff_north_lon, baff_north_lat)) & (longitude > np.interp(latitude, baff_west_lat, baff_west_lon)) & (longitude < -51.75), maskvar, 0)
newmask['baffinba'] = xr.DataArray(baffinba, attrs=dict(long_name = 'Baffin Bay'))
#
# 5n. Lincoln Sea (S-23 9.13)
linc_south_lon = [-70] + baff_north_lon + [-55.17, -33.93]
linc_south_lat =  [82.47] + baff_north_lat + [81., 81.]
lincolns = xr.where((latitude > np.interp(longitude, linc_south_lon, linc_south_lat)) & (latitude < np.interp(longitude, [33.93, 71.25], [83.63, 83.15])) & (longitude > -71.25) & (longitude < -33.93), maskvar, 0)
newmask['lincolns'] = xr.DataArray(lincolns, attrs=dict(long_name = 'Lincoln Sea'))
#
# 5o. Northwestern Passages (S-23 9.14)
nwp_north_lon = [-116.40, -115.08, -114.33, -113.30, -110.72, -105.43, -99.77, -94.12, -91.90]
nwp_north_lat = [77.57, 77.97, 78.08, 78.35, 78.77, 79.33, 80.15, 81.37, 81.62]
nwp_south_lon = [-130., -85.87, -85.53]
nwp_south_lat = [66.20, 66.20, 65.92]
nwp_east_lon = baff_west_lon[::-1] + [-67.17, -67.17] + hs_north_lon[1::-1]
nwp_east_lat = baff_west_lat[::-1] + [70.0, 65.0] + hs_north_lat[1::-1]
nwpassag = xr.where((latitude > np.interp(longitude, nwp_south_lon + hs_north_lon[:2] + ds_west_lon[-2:], nwp_south_lat + hs_north_lat[:2] + ds_west_lat[-2:])) & (latitude < np.interp(longitude, nwpbeau_lon + nwp_north_lon + baff_west_lon[::-1], nwpbeau_lat + nwp_north_lat + baff_west_lat[::-1])) & (longitude > np.interp(latitude, [65.] + nwpbeau_lat + nwp_north_lat, [-128.03] + nwpbeau_lon +  nwp_north_lon)) & (longitude < np.interp(latitude, nwp_east_lat[::-1], nwp_east_lon[::-1])), maskvar, 0)
newmask['nwpassag'] = xr.DataArray(nwpassag, attrs=dict(long_name = 'Northwestern Passages'))
#
# 5p. Beaufort Sea (S-23 9.15)
beaufort = xr.where((latitude > 68) & (latitude < np.interp(longitude, [-156.47, -122.58], [71.4, 76.33])) & (longitude > -156.47) & (longitude < np.interp(latitude, nwpbeau_lat, nwpbeau_lon)), maskvar, 0)
newmask['beaufort'] = xr.DataArray(beaufort, attrs=dict(long_name = 'Beaufort Sea'))
#
# 5q. Chukchi Sea (S-23 9.16)
chukchis = xr.where((latitude > 66.18) & (latitude < 71.53) & ((longitude > np.interp(latitude, [70.78, 71.53], [178.75, 180.])) | (longitude < -156.47)), maskvar, 0)
newmask['chukchis'] = xr.DataArray(chukchis, attrs=dict(long_name = 'Chukchi Sea'))

# 5r. GIN seas

# 5s. Marginal Seas
#dict_marg = ['Nordic Seas', 'Barents Sea', 'Kara Sea', 'Baffin Bay', 'Laptev Sea', 'Hudson', 'East Siberian Sea', 'Beaufort Sea', 'NorthWest Passage', 'Chukchi Sea', 'Bering', 'Okhotsk']

# 5t. Central Arctic

# 5u. West Central Arctic

# 5v. East Central Arctic

# 5w. Bering Strait

# 5x. Nares Strait

# 5y. Kara-Gate Strait

# 5z. Vilkitsky Strait

# 6. North Atlantic Ocean

# 6a. Labrador Sea

# 6b. North Sea

# 6c. Baltic Sea

# 6d. Gulf of Guinea

# 6e. Caribbean Sea

# 6f. Gulf of Mexico

# 6e. Gulf of Saint Lawrence

# 7. North Pacific Ocean

# 7a. Bering Sea
# https://www.marineregions.org/gazetteer.php?p=details&id=4310

# 7b. Okhotsk Sea
# https://www.marineregions.org/gazetteer.php?p=details&id=4309

# 8. Mediterranean Sea
bool_medit_1 = (latitude > 30) & (latitude < 40) & (longitude > -5) & (longitude <  0)
bool_medit_2 = (latitude > 30) & (latitude < 46) & (longitude >  0) & (longitude < 28)
bool_medit_3 = (latitude > 30) & (latitude < 40) & (longitude > 28) & (longitude < 40)
mediterr = xr.where(bool_medit_1 | bool_medit_2 | bool_medit_3, maskvar, 0)
newmask['mediterr'] = xr.DataArray(mediterr, attrs=dict(long_name = 'Mediterranean Sea'))
#
# 8a. Caspian Sea


#
# Write the output netcdf file
#
newmask.to_netcdf(outfile)
sys.exit()

