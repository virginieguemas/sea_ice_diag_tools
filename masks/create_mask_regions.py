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
#
grid = 'NEMO 3.2 ORCA1L42'
meshfile = '~/mytools/postdoc2014/MasksArctic/mesh_mask_nemo.N3.2_O1L42.nc'
option_grid = 't'
lon_name = 'nav_lon'
lat_name = 'nav_lat'
#
# Read land-sea mask and coordinates
#
maskfile = xr.open_dataset(meshfile)
maskvar = maskfile[option_grid + 'mask'].isel(t = 0,z = 0)
longitude = maskfile[lon_name]
latitude  = maskfile[lat_name]
#
# Define output dataset containing all new masks
#
newmask = xr.Dataset(attrs=dict(description = 'Masks for individual seas and regions',grid = grid, initial_meshfile = meshfile, based_on_latitude = lat_name, based_on_longitude=lon_name, creation_date = str(datetime.datetime.now()), created_by = getpass.getuser()))
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
antarct = xr.where(latitude < -55, maskvar, 0)
newmask['antarcti'] = xr.DataArray(antarct, attrs=dict(long_name = 'Antarctic Ocean'))
#
# 5. Amundsen Sea
amundsen = xr.where((latitude < -55) & (longitude>-140) & (longitude <-90), maskvar, 0)
newmask['amundsen'] = xr.DataArray(amundsen, attrs=dict(long_name = 'Amundsen Sea'))
#

# 5. Arctic Ocean
#bool_arctic_1 = np.greater(marg,nhemisph)
#bool_arctic = np.logical_and(bool_arctic_1,latitude>0)
#arcticoc = xr.where(np.logical_or(bool_arctic,bool_centrarc),maskvar,0)
#newmask['arcticoc'] = xr.DataArray(arcticoc, attrs=dict(long_name = 'Arctic Ocean'))
#
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
newmask.to_netcdf('mask.ArcticSeas.N3.2_O1L42.nc')
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
#Weddell Sea
#
bool_weddll = np.logical_and(latitude<-55, np.logical_and(longitude>-65, longitude <-15))
weddellx = np.where(bool_weddll,maskvar,0)
dom_dict['Weddell Sea'] = weddellx
#
#
#Ross Sea
#
bool_ross_1 = np.logical_and(latitude<-55,longitude <-140)
bool_ross_2 = np.logical_and(latitude<-55, longitude>160)
bool_ross = np.logical_or(bool_ross_1,bool_ross_2)
rossxxxx = np.where(bool_ross,maskvar,0)
dom_dict['Ross Sea'] = rossxxxx
#
#
#
#Bellingshausen Sea
#
bool_bellings = np.logical_and(latitude<-55, np.logical_and(longitude>-90, longitude <-65))
bellings = np.where(bool_bellings,maskvar,0)
dom_dict['Bellingshausen Sea'] = bellings
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
